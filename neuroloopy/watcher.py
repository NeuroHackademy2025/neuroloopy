#!/usr/bin/env python3
"""
Real-time file watcher for neuroloopy fMRI processing.
Monitors incoming DICOM files and processes them for neurofeedback.
"""

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers.polling import PollingObserver
import multiprocessing as mp
import numpy as np
from scipy.signal import detrend
import nibabel as nib
import os
import glob
import time
import pickle
import requests as r

from .preproc import ref_img, rt_img
from .anal import apply_classifier
from .utils import write_log, write_log_header, send_loop_output


class InstaWatcher(PatternMatchingEventHandler):
    """
    Real-time file watcher that processes incoming DICOM files for neurofeedback.
    
    This class monitors a directory for new DICOM files, processes them through
    motion correction and normalization, applies a classifier, and sends feedback.
    """
    
    def __init__(self, config):
        """
        Initialize the watcher with configuration parameters.
        
        Parameters
        ----------
        config : dict
            Configuration dictionary containing all necessary parameters
        """
        self.config = config
        self.rep_start_times = {}
        
        # Set up file patterns
        file_pattern = '*.dcm'
        PatternMatchingEventHandler.__init__(self, 
            patterns=[file_pattern],
            ignore_patterns=[],
            ignore_directories=False)
        
        # Initialize multiprocessing pool
        self.pool = mp.Pool()
        
        # Load reference image
        self.ref_image = ref_img(config['ref_dir'])
        
        # Load classifier
        if config['clf_file'] and os.path.exists(config['clf_file']):
            self.clf = pickle.load(open(config['clf_file'], 'rb'))
            self.num_roi_voxels = np.shape(self.clf.voxel_indices)[0]
        else:
            print("Warning: No classifier file found")
            self.clf = None
            self.num_roi_voxels = 0
        
        # Initialize arrays and counters
        self.reset_img_arrays()
        
        # Set up logging if enabled
        if config.get('logging_bool', False):
            self.setup_logging()
        else:
            self.logging_bool = False
        
        print(f"Watcher initialized for subject {config['subject_id']}")
        print(f"Watching directory: {config['watch_dir']}")
        print(f"Feedback mode: {config['feedback_mode']}")
        print(f"Run TRs: {config['run_trs']}")
    
    def setup_logging(self):
        """Set up logging functionality."""
        self.logging_bool = True
        log_file_time = self.config.get('log_file_time', int(time.time()))
        log_dir = self.config.get('log_dir', os.getcwd() + '/log')
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file_name = os.path.join(log_dir, f'{log_file_time}_event.log')
        self.log_file = open(log_file_name, 'w')
        write_log_header(self.log_file)
        write_log(self.log_file, self.config['script_start_time'], 'startup', 0)
    
    def reset_img_arrays(self):
        """Reset arrays for storing volume data."""
        self.img_status_array = np.zeros(self.config['run_trs'])
        
        # Get dimensions from reference image
        ref_shape = self.ref_image.img.shape
        self.slice_dims = (ref_shape[0], ref_shape[1])
        self.num_slices = ref_shape[2]
        
        self.raw_img_array = np.zeros((self.slice_dims[0], self.slice_dims[1],
                                      self.num_slices, self.config['run_trs']), dtype=np.uint16)
        self.raw_roi_array = np.zeros((self.num_roi_voxels, self.config['run_trs']))
        self.feedback_count = -1
        self.zscore_calc = False
        self.voxel_sigmas = np.zeros(self.num_roi_voxels)
    
    def on_created(self, event):
        """
        Handle new DICOM file creation events.
        
        Parameters
        ----------
        event : FileSystemEvent
            The file system event containing the path of the new file
        """
        on_created_start = time.time()
        
        print(f'[on_created] New file detected: {event.src_path}')
        
        # Parse file information
        img_dir = event.src_path.rsplit('/', 1)[0]
        img_file = event.src_path.rsplit('/')[-1]
        
        try:
            # Create rt_img object to handle the new file
            rt_image = rt_img(img_dir)
            rep = rt_image.rep
            
            print(f'Processing rep: {rep}')
            
            # Skip SBRef images
            if 'SBRef' in rt_image.raw_nii:
                print('Skipping SBRef image')
                return
            
            print('Passed SBRef check!')
            
            # Log motion correction start
            if self.logging_bool:
                write_log(self.log_file, self.config['script_start_time'], 'mc_start', rep)
            
            # Record start time for latency calculation
            self.rep_start_times[rep] = time.time()
            
            # Process volume asynchronously
            self.pool.apply_async(
                func=self.process_volume,
                args=(rt_image, rep),
                callback=self.save_processed_roi
            )
            
        except Exception as e:
            print(f'[on_created] ERROR processing file {img_file}: {e}')
            import traceback
            traceback.print_exc()
            return
        
        # Clean up temporary files
        os.system(f'rm {self.config["proc_dir"]}/*.dcm 2>/dev/null')
        
        on_created_end = time.time()
        elapsed = on_created_end - on_created_start
        print(f'[on_created] Finished in {elapsed:.3f} seconds')
    
    def process_volume(self, rt_image, rep):
        """
        Process a single volume through motion correction and normalization.
        
        Parameters
        ----------
        rt_image : rt_img
            Real-time image object
        rep : int
            Repetition/volume number
            
        Returns
        -------
        tuple
            (roi_data, rep) where roi_data contains the processed ROI signals
        """
        try:
            print(f"Processing volume for rep: {rep}")
            
            # Motion correction
            rt_image.motion_correct(self.ref_image, self.config['mc_mode'])
            
            # Apply normalization if using MNI template
            if self.config.get('mni_template'):
                rt_image.apply_normalization(self.ref_image)
                
                # Load the normalized image and extract ROI data
                transformed_epi = os.path.join(self.config['proc_dir'], 
                                             f'img_mni_{str(rep+1).zfill(3)}.nii.gz')
                mni_img = nib.load(transformed_epi)
                roi_data = self.map_voxels_to_roi(mni_img.get_fdata(), self.clf.voxel_indices)
            else:
                # Extract ROI data directly from motion-corrected image
                roi_data = rt_image.mask(self.clf.voxel_indices)
            
            print(f'ROI data extracted for rep {rep}')
            return (roi_data, rep)
            
        except Exception as e:
            print(f'[ERROR] Exception in process_volume for rep {rep}: {e}')
            import traceback
            traceback.print_exc()
            return None
    
    def map_voxels_to_roi(self, img, roi_voxels):
        """
        Map image voxels to ROI using voxel indices.
        
        Parameters
        ----------
        img : ndarray
            3D image data
        roi_voxels : ndarray
            Array of voxel indices (n_voxels, 3)
            
        Returns
        -------
        ndarray
            ROI signal values
        """
        out_roi = np.zeros(roi_voxels.shape[0])
        for voxel in range(roi_voxels.shape[0]):
            out_roi[voxel] = img[roi_voxels[voxel, 0], 
                               roi_voxels[voxel, 1], 
                               roi_voxels[voxel, 2]]
        return out_roi
    
    def save_processed_roi(self, roi_and_rep_data):
        """
        Save processed ROI data and compute feedback if needed.
        
        Parameters
        ----------
        roi_and_rep_data : tuple
            (roi_data, rep) from process_volume
        """
        try:
            if roi_and_rep_data is None:
                print("Error: Received None from process_volume")
                return
                
            roi_data, rep = roi_and_rep_data
            
            # Log motion correction end
            if self.logging_bool:
                write_log(self.log_file, self.config['script_start_time'], 'mc_end', rep)
            
            # Save ROI data
            self.raw_roi_array[:, rep] = roi_data
            print('ROI data saved successfully!')
            
            # Calculate voxel variances after baseline period
            if rep == (self.config['baseline_trs'] - 1):
                self.voxel_sigmas = np.sqrt(np.var(self.raw_roi_array[:, :rep+1], 1))
                self.voxel_sigmas[np.where(self.voxel_sigmas == 0)] = 1e6  # ignore zero variance voxels
                print(f'Calculated voxel sigmas: min={np.min(self.voxel_sigmas):.3f}, '
                      f'max={np.max(self.voxel_sigmas):.3f}')
            
            # Compute feedback if this is a feedback TR
            if rep in self.config['feedback_calc_trs']:
                self.compute_and_send_feedback(rep)
            
            # Reset for next run if this is the last TR
            if rep == (self.config['run_trs'] - 1):
                self.reset_for_next_run()
                
        except Exception as e:
            print(f"ERROR in save_processed_roi: {e}")
            import traceback
            traceback.print_exc()
    
    def compute_and_send_feedback(self, rep):
        """
        Compute classifier output and send feedback.
        
        Parameters
        ----------
        rep : int
            Current repetition number
        """
        self.feedback_count += 1
        
        # Detrend and z-score the data
        detrend_roi_array = detrend(self.raw_roi_array[:, :rep+1], 1)
        zscore_avg_roi = (np.mean(detrend_roi_array[:, -self.config['moving_avg_trs']:], 1) / 
                         self.voxel_sigmas)
        
        # Apply classifier
        if self.clf is not None:
            clf_out = apply_classifier(self.clf, zscore_avg_roi, self.num_roi_voxels, 
                                     self.logging_bool)
            print(f'Classifier output: {clf_out}')
            
            # Send feedback
            self.config['feedback_count'] = self.feedback_count
            # Prepare output data (assuming no target class for now)
            out_data = np.append(clf_out, -1)  # -1 as placeholder for target_class
            send_loop_output(out_data, self.config)
            
            # Calculate and log latency
            feedback_time = time.time()
            if rep in self.rep_start_times:
                latency = feedback_time - self.rep_start_times[rep]
                print(f"[TIMER] Time to feedback for rep {rep}: {latency:.2f} seconds")
            
            if self.config.get('script_start_time'):
                total_runtime = time.time() - self.config['script_start_time']
                print(f"[TIMER] Total time from script start to feedback: {total_runtime:.2f} seconds")
            
            print(f'Feedback sent at {time.strftime("%H:%M:%S")}')
            
            # Log feedback sent
            if self.logging_bool:
                write_log(self.log_file, self.config['script_start_time'], 'fb_sent', rep)
    
    def reset_for_next_run(self):
        """Reset arrays and counters for the next run."""
        print("Run completed. Resetting for next run...")
        
        self.config['run_count'] += 1
        
        # Archive data if enabled
        if self.config.get('archive_bool', False):
            self.archive_run_data()
        
        # Clean up processing directory
        os.system(f'rm {self.config["proc_dir"]}/*.* 2>/dev/null')
        
        # Reset arrays
        self.reset_img_arrays()
        print(f"Ready for run {self.config['run_count'] + 1}")
    
    def archive_run_data(self):
        """Archive processed data for the current run."""
        run_dir = os.path.join(self.config['archive_dir'], 
                              f'run_{str(self.config["run_count"]).zfill(2)}')
        
        if not os.path.exists(run_dir):
            os.makedirs(run_dir)
        
        # Archive motion correction parameters
        os.system(f'cat {self.config["proc_dir"]}/*.txt > {run_dir}/mc_params.txt 2>/dev/null')
        
        # Move processed files
        os.system(f'mv {self.config["proc_dir"]}/*.* {run_dir}/ 2>/dev/null')
        
        # Archive DICOM files if available
        if os.path.exists(self.config['watch_dir']):
            os.system(f'mv {self.config["watch_dir"]}/*/*.dcm {run_dir}/ 2>/dev/null')
        
        print(f"Data archived to: {run_dir}")


def start_watcher(config, subject_id, session, config_name, debug_bool=False, 
                 logging_bool=False, dashboard_bool=False, start_run=1):
    """
    Start the real-time file watcher.
    
    Parameters
    ----------
    config : dict
        Configuration dictionary
    subject_id : str
        Subject identifier
    session : str
        Session number
    config_name : str
        Configuration file name
    debug_bool : bool
        Enable debug mode
    logging_bool : bool
        Enable logging
    dashboard_bool : bool
        Enable dashboard
    start_run : int
        Starting run number
    """
    print("Starting neuroloopy watcher...")
    
    # Update config with runtime parameters
    config['subject_id'] = subject_id
    config['session_number'] = session
    config['config_name'] = config_name
    config['debug_bool'] = debug_bool
    config['logging_bool'] = logging_bool
    config['dashboard_bool'] = dashboard_bool
    config['start_run'] = start_run
    
    # Set up watch directory based on debug mode
    if debug_bool:
        # Keep the configured watch_dir for debug mode
        print(f"Debug mode: Using configured watch directory: {config['watch_dir']}")
    else:
        # Try to find subject-specific directory
        pattern = f"{config['watch_dir']}/*.{subject_id}_{session}/"
        matching_dirs = glob.glob(pattern)
        if matching_dirs:
            config['watch_dir'] = matching_dirs[0]
            print(f"Real mode: Using subject-specific directory: {config['watch_dir']}")
        else:
            print(f"Warning: Could not find subject-specific directory matching {pattern}")
    
    # Create necessary directories
    for dir_key in ['proc_dir', 'log_dir']:
        if config.get(dir_key) and not os.path.exists(config[dir_key]):
            os.makedirs(config[dir_key])
            print(f"Created directory: {config[dir_key]}")
    
    # Set up observer
    OBS_TIMEOUT = 0.1
    event_observer = PollingObserver(OBS_TIMEOUT)
    event_handler = InstaWatcher(config)
    
    # Start watching
    event_observer.schedule(event_handler, config['watch_dir'], recursive=True)
    event_observer.start()
    
    print(f"✓ Watcher started successfully")
    print(f"  Subject: {subject_id}")
    print(f"  Session: {session}")
    print(f"  Watching: {config['watch_dir']}")
    print(f"  Processing: {config['proc_dir']}")
    
    return event_observer, event_handler
