"""
Real-time file watching and processing for fMRI neurofeedback.
"""

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers.polling import PollingObserver
import multiprocessing as mp
import numpy as np
import time
import os
import glob
import pickle
import requests
from scipy.signal import detrend
import nibabel as nib
from .preproc import process_volume, convert_dicom_to_nii
from .anal import apply_classifier
from .utils import write_log, write_log_header
from .dashboard import post_dashboard_clf_outs, post_dashboard_mc_params

REALTIME_TIMEOUT = 0.1  # seconds to HTTP post timeout

class InstaWatcher(PatternMatchingEventHandler):
    """
    Real-time file watcher for fMRI neurofeedback processing.
    Monitors for new DICOM files and triggers processing pipeline.
    """
    
    def __init__(self, config):
        """Initialize the watcher with configuration."""
        self.rep_start_times = {}
        self.script_start_time = config.get('script_start_time', None)
        
        # File pattern matching
        file_pattern = '*.dcm'
        print(f'Looking for file pattern: {file_pattern}')
        PatternMatchingEventHandler.__init__(
            self,
            patterns=[file_pattern],
            ignore_patterns=[],
            ignore_directories=False
        )
        
        # Multiprocessing pool
        self.pool = mp.Pool()
        
        # Initialize from config
        self._setup_timing(config)
        self._setup_processing(config)
        self._setup_files_and_dirs(config)
        self._setup_networking(config)
        self._setup_logging(config)
        self._setup_dashboard(config)
        
        self.reset_img_arrays()
    
    def _setup_timing(self, config):
        """Setup timing parameters for trials and feedback."""
        self.run_count = int(config['start-run']) - 1
        self.baseline_trs = config['baseline-trs']
        
        feedback_mode = config.get('feedback-mode', 'continuous').lower()
        
        if feedback_mode == 'continuous':
            self.feedback_trs = config['feedback-trs']
            self.run_trs = self.baseline_trs + self.feedback_trs
            self.feedback_calc_trs = np.arange(
                self.baseline_trs, 
                self.feedback_trs + self.baseline_trs
            )
        elif feedback_mode == 'intermittent':
            self.trials = config['trials-per-run']
            self.encoding_trs = config['encoding-trs']
            self.cue_trs = config['cue-trs']
            self.wait_trs = config['wait-trs']
            self.feedback_trs = config['feedback-trs']
            self.iti_trs = config['iti-trs']
            self.runEnd_fix_trs = config['endRun-fix-trs']
            self.trial_trs = (self.encoding_trs + self.cue_trs + 
                             self.wait_trs + self.feedback_trs + self.iti_trs)
            self.run_trs = (self.baseline_trs + self.trials * self.trial_trs) + self.runEnd_fix_trs
            self.trs_to_score_calc = self.cue_trs + self.wait_trs
            self.feedback_calc_trs = (self.baseline_trs + self.trs_to_score_calc +
                                     np.arange(self.trials) * self.trial_trs - 1)
    
    def _setup_processing(self, config):
        """Setup processing parameters."""
        self.moving_avg_trs = config['moving-avg-trs']
        self.mc_mode = config['mc-mode'].lower()
    
    def _setup_files_and_dirs(self, config):
        """Setup file paths and directories."""
        self.subject_id = config['subject-id']
        self.ref_dir = os.getcwd() + '/ref/' + self.subject_id
        self.rfi_file = glob.glob(self.ref_dir + '/*rfi.nii.gz')[0]
        self.rfi_img = nib.load(self.rfi_file)
        self.rfi_data = self.rfi_img.get_data()
        self.ref_affine = self.rfi_img.get_qform()
        self.ref_header = self.rfi_img.header
        
        self.clf_dir = os.getcwd() + '/mni_clf'
        self.clf_file = glob.glob(self.clf_dir + '/*mni_clf.p')[0]
        self.clf = pickle.load(open(self.clf_file, 'rb'))
        self.num_roi_voxels = np.shape(self.clf.voxel_indices)[0]
        
        self.dcm2niix_dir = config.get('dcm2niix-dir', '/home/cjerinic/fsl/bin')
        self.warp_file = glob.glob(self.ref_dir + '/*warp_displacement.nii.gz')[0]
        self.standard_dir = os.getcwd() + '/standard'
        self.mni_template = glob.glob(self.standard_dir + '/*2mm_brain.nii.gz')[0]
        
        try:
            self.target_class = int(np.loadtxt(self.ref_dir + '/class.txt'))
        except:
            self.target_class = -1
        
        self.proc_dir = os.getcwd() + '/proc'
        self.watch_dir = config['watch-dir']
        self.archive_bool = config['archive-data']
        self.archive_dir = config['archive-dir']
        
        # Setup slice dimensions
        self.slice_dims = (self.rfi_data.shape[0], self.rfi_data.shape[1])
        self.num_slices = self.rfi_data.shape[2]
    
    def _setup_networking(self, config):
        """Setup networking for feedback transmission."""
        self.post_url = config['post-url']
    
    def _setup_logging(self, config):
        """Setup logging if enabled."""
        if config.get('logging_bool', False):
            self.logging_bool = True
            self.log_file_time = config['log_file_time']
            log_file_name = os.getcwd() + '/log/' + str(self.log_file_time) + '_event.log'
            self.log_file = open(os.path.normpath(log_file_name), 'w')
            write_log_header(self.log_file)
            self.log_file_time = 1.539e9  # TODO: fix this
            write_log(self.log_file, self.log_file_time, 'startup', 0)
        else:
            self.logging_bool = False
    
    def _setup_dashboard(self, config):
        """Setup dashboard integration if enabled."""
        if config.get('dashboard_bool', False):
            try:
                self.dashboard_base_url = config['dashboard-base-url']
                self.dashboard_mc_url = self.dashboard_base_url + '/mc_data'
                self.dashboard_clf_url = self.dashboard_base_url + '/clf_data'
                self.dashboard_shutdown_url = self.dashboard_base_url + '/shutdown'
                self.try_dashboard_connection = True
                self.dashboard_bool = True
            except:
                self.try_dashboard_connection = False
                self.dashboard_bool = False
        else:
            self.try_dashboard_connection = False
            self.dashboard_bool = False
    
    def apply_classifier(self, data):
        """Apply classifier to volume data."""
        if not self.logging_bool:
            self.clf.predict(np.ndarray((1, self.num_roi_voxels), buffer=data))
        else:
            self.clf.predict(np.random.normal(0, 1, (1, self.num_roi_voxels)))
            print('debugging mode: classifier value is random')
        return self.clf.ca.estimates
    
    def reset_img_arrays(self):
        """Reset all metadata arrays."""
        self.img_status_array = np.zeros(self.run_trs)
        self.raw_img_array = np.zeros((
            self.slice_dims[0], self.slice_dims[1],
            self.num_slices, self.run_trs
        ), dtype=np.uint16)
        self.raw_roi_array = np.zeros((self.num_roi_voxels, self.run_trs))
        self.feedback_count = -1
        self.zscore_calc = False
        self.voxel_sigmas = np.zeros(self.num_roi_voxels)
    
    def on_created(self, event):
        """Handle new file creation events."""
        on_created_start = time.time()
        print('[on_created] New file detected:')
        print(event.src_path)
        
        img_dir = event.src_path.rsplit('/', 1)[0]
        img_file = event.src_path.rsplit('/')[-1]
        
        try:
            rep = int(img_file.split('_')[2].split('.dcm')[0]) - 1
        except Exception as e:
            print('[on_created] ERROR parsing rep number from ', img_file)
            print(e)
            return
        
        print('printing rep...')
        print(rep)
        
        self.raw_nii = convert_dicom_to_nii(
            img_file, self.proc_dir, img_dir,
            img_file.split('_')[-2].split('.dcm')[0], self.dcm2niix_dir
        )
        os.system('rm ' + self.proc_dir + '/*.dcm')
        
        if 'SBRef' not in self.raw_nii:
            print('Passed SBRef check!')
            if self.logging_bool:
                print('Writing log entry...')
                write_log(self.log_file, self.log_file_time, 'mc_start', rep)
            print('Starting async processing...')
            
            self.rep_start_times[rep] = time.time()
            
            self.pool.apply_async(
                func=process_volume,
                args=(self.raw_nii, self.clf.voxel_indices, rep, self.rfi_file,
                      self.proc_dir, self.ref_header, self.ref_affine,
                      self.mc_mode, self.warp_file, self.mni_template),
                callback=self.save_processed_roi
            )
        
        on_created_end = time.time()
        on_created_elapsed = on_created_end - on_created_start
        print('[on_created] Finished in %.3f seconds' % on_created_elapsed)
    
    def save_processed_roi(self, roi_and_rep_data):
        """Save processed ROI data and trigger feedback."""
        try:
            print('DEBUG save_processed_roi called with rep\n', roi_and_rep_data)
            (roi_data, rep) = roi_and_rep_data
            
            if self.logging_bool:
                write_log(self.log_file, self.log_file_time, 'mc_end', rep)
            
            self.raw_roi_array[:, rep] = roi_data
            print('roi_data saved into raw_roi_array successfully!')
            
            print("rep is", rep)
            print("feedback_calc_trs is", self.feedback_calc_trs)
            print("rep in feedback_calc_trs?", rep in self.feedback_calc_trs)
            
            if rep == (self.baseline_trs - 1):
                self.voxel_sigmas = np.sqrt(np.var(self.raw_roi_array[:, :rep + 1], 1))
                self.voxel_sigmas[np.where(self.voxel_sigmas == 0)] = 1e6
                print('DEBUG voxel_sigmas:', self.voxel_sigmas)
                print('DEBUG voxel_sigmas shape:', self.voxel_sigmas.shape)
                print('DEBUG min/max voxel_sigmas:', np.min(self.voxel_sigmas), np.max(self.voxel_sigmas))
            
            if rep in self.feedback_calc_trs:
                self.feedback_count += 1
                detrend_roi_array = detrend(self.raw_roi_array[:, :rep + 1], 1)
                zscore_avg_roi = np.mean(detrend_roi_array[:, -self.moving_avg_trs:], 1) / self.voxel_sigmas
                clf_out = self.apply_classifier(zscore_avg_roi)
                print('clf_out is ' + str(clf_out))
                out_data = np.append(clf_out, self.target_class)
                self.send_clf_outputs(out_data)
                
                feedback_time = time.time()
                if rep in self.rep_start_times:
                    latency = feedback_time - self.rep_start_times[rep]
                    print("[TIMER] Time to feedback for rep {}: {:.2f} seconds".format(rep, latency))
                
                print('feedback sent', time.strftime('%H:%M:%S'))
                
                if self.script_start_time is not None:
                    total_runtime = time.time() - self.script_start_time
                    print("[TIMER] Total time from script start to feedback: {:.2f} seconds".format(total_runtime))
                
                if self.logging_bool:
                    write_log(self.log_file, self.log_file_time, 'fb_sent', rep)
            
            # Dashboard outputs
            if self.dashboard_bool:
                try:
                    self.check_for_dashboard(rep)
                except Exception as e:
                    print('dashboard error:', e)
                    self.dashboard_bool = False
            
            if rep == (self.run_trs - 1):
                self.reset_for_next_run()
        
        except Exception as e:
            import traceback
            print("ERROR in save_processed_roi:")
            print(traceback.format_exc())
    
    def send_clf_outputs(self, out_data):
        """Send classifier outputs to external system."""
        payload = {
            "clf_outs": list(out_data[:-1]),
            "target_class": out_data[-1],
            "feedback_num": self.feedback_count
        }
        print('payload:', payload)
        try:
            requests.post(self.post_url, json=payload, timeout=REALTIME_TIMEOUT)
        except:
            pass
    
    def check_for_dashboard(self, rep):
        """Send data to dashboard for monitoring."""
        if rep >= (self.baseline_trs - 1):
            detrend_roi_array = detrend(self.raw_roi_array[:, :rep + 1], 1)
            print('roi array detrended')
            zscore_avg_roi = np.mean(detrend_roi_array[:, -self.moving_avg_trs:], 1) / self.voxel_sigmas
            print('zscore avg roi is ' + str(zscore_avg_roi))
            clf_out = self.apply_classifier(zscore_avg_roi)
            post_dashboard_clf_outs(clf_out[0], rep, self.dashboard_clf_url)
        
        mc_params_file = self.proc_dir + '/mc_params_' + str(rep + 1).zfill(3) + '.txt'
        mc_params = np.loadtxt(mc_params_file)
        post_dashboard_mc_params(mc_params, rep, self.dashboard_mc_url)
    
    def reset_for_next_run(self):
        """Reset for the next run."""
        if self.try_dashboard_connection:
            self.dashboard_bool = True
        
        self.run_count += 1
        
        if self.archive_bool:
            for target_dir in [self.proc_dir, self.watch_dir]:
                if self.archive_bool:
                    run_dir = self.archive_dir + '/run_' + str(self.run_count).zfill(2)
                    if not os.path.exists(run_dir):
                        os.mkdir(run_dir)
                    if target_dir == self.proc_dir:
                        os.system('cat ' + target_dir + '/*.txt > ' + run_dir + '/mc_params.txt 2>/dev/null')
                        os.system('rm ' + target_dir + '/*.txt 2>/dev/null')
                        os.system('mv ' + target_dir + '/*.* ' + run_dir + ' 2>/dev/null')
                    elif target_dir == self.watch_dir:
                        os.system('mv ' + self.watch_dir + '/*/*.dcm ' + run_dir + ' 2>/dev/null')
                os.system('rm ' + target_dir + '/*.* 2>/dev/null')
        
        self.reset_img_arrays()


def start_watcher(config, subject_id, session, config_name, debug_bool=False, 
                 logging_bool=False, dashboard_bool=False, start_run=1):
    """
    Start the real-time file watcher.
    
    Args:
        config: Configuration dictionary
        subject_id: Subject ID
        session: Session number
        config_name: Configuration name
        debug_bool: Enable debug mode
        logging_bool: Enable logging
        dashboard_bool: Enable dashboard
        start_run: Starting run number
    
    Returns:
        observer: The file observer instance
    """
    print("Starting real-time fMRI neurofeedback watcher...")
    print(f"Subject: {subject_id}")
    print(f"Session: {session}")
    print(f"Configuration: {config_name}")
    print(f"Debug mode: {debug_bool}")
    print(f"Logging: {logging_bool}")
    print(f"Dashboard: {dashboard_bool}")
    print(f"Start run: {start_run}")
    
    # Create watcher instance
    watcher = InstaWatcher(config)
    
    # Create observer
    observer = PollingObserver()
    observer.schedule(watcher, config['watch-dir'], recursive=False)
    observer.start()
    
    print(f"Watching directory: {config['watch-dir']}")
    print("Watcher started successfully!")
    
    return observer
