import os
import numpy as np
from pathlib import Path
import nibabel as nib
import glob
import time
import re

class ref_img:
    '''
    Class for handling reference image.
    '''
    def __init__(self, ref_dir, dcm2niix_dir=None):
        '''
        Initialize rfi class.
        
        Parameters
        ----------
        ref_dir : str
            Path to a folder containing the reference image.

        MAYBE REMOVE:
        dcm2niix_dir : str, default None
            Path to the binary for dcm2niix. If None, defaults to ~/fsl/bin.
        '''
        if not os.path.isdir(ref_dir):
            raise FileNotFoundError(f"Folder {ref_dir} does not exist.")
        self.proc_dir = os.getcwd() + '/proc'
        if not os.path.isdir(self.proc_dir):
            print("Creating", self.proc_dir)
            os.mkdir(self.proc_dir)
        # Load reference image
        self.dir = ref_dir
        self.file = glob.glob(self.dir + '/*rfi.nii.gz')[0] ## TODO: implement checks functional
                                                            ## reference image and/or subject specific classifier
        self.img = nib.load(self.file)
        # self.data = self.img.get_fdata()
        self.affine = self.img.get_qform() # or just self.img.affine idk
        self.header = self.img.header

        # Point to dcm2niix
        # if dcm2niix_dir is None:
        #     home = str(Path.home())
        #     self.dcm2niix_dir = os.path.join(home,"fsl","bin")
        # else:
        #     self.dcm2niix_dir = dcm2niix_dir

        # Other images -- I'm actually not sure how these are used yet so may not make sense in this class..
        self.warp_file = glob.glob(self.dir + '/*warp_displacement.nii.gz')[0]
        self.standard_dir = os.getcwd() + '/standard'
        self.mni_template = glob.glob(self.standard_dir+'/*2mm_brain.nii.gz')[0]

        ### add other functions for manipulating
        ### reference images here i guess

class rt_img:
    '''
    Class for handling real-time image.
    '''
    def __init__(self, rt_dir):
        '''
        Initialize rt_img class.

        Parameters
        ----------
        rt_dir : str
            Path to a folder containing the real-time image(s).
        '''
        self.dir = rt_dir
        self.proc_dir = os.getcwd() + '/proc'
        if not os.path.isdir(self.proc_dir):
            print("Creating", self.proc_dir)
            os.mkdir(self.proc_dir)
        # I changed this line but I think it still works as intended:
        self.file = glob.glob(self.dir + '/*dcm')[-1] # most recent DICOM in folder
        # print('dicom to convert: ' + self.file)
        try:
            # self.rep = int(self.file.split('_')[2].split('.dcm')[0])-1
            self.rep = int(re.sub(r'\D+','',self.file.split('/')[-1]))
        except Exception as e:
            print('[on_created] ERROR parsing rep number from ', self.file)
            print(e)
        print('printing rep...')
        print(self.rep)
        # Convert to NIFTI
        self.raw_nii = convert_dicom_to_nii(self.file, self.proc_dir, self.dir, self.rep)
        # Load
        self.img = nib.load(os.path.join(self.proc_dir,self.raw_nii))
        self.data = self.img.get_fdata()
        self.affine = self.img.get_qform() # or just self.img.affine idk
        self.header = self.img.header

    def mask(self, voxel_indices):
        '''
        Masks real-time image according to classifier features.

        Parameters
        ----------
        voxel_indices : array-like, shape (n_features, 3)
            The classifier output, an array of voxel indices (CRS).

        Returns
        ----------
        out_roi : array-like, shape (n_features,)
            The voxels in self.raw_nii at the specified indices in voxel_indices.
        '''
        self.voxel_indices = np.asarray(voxel_indices)
        n_features = self.voxel_indices.shape[0]
        out_roi = np.zeros((n_features))
        for voxel in np.arange(n_features):
            out_roi[voxel] = self.data[self.voxel_indices[voxel,0],
                                       self.voxel_indices[voxel,1],
                                       self.voxel_indices[voxel,2]]

        return out_roi

    def motion_correct(self, ref_img, mc_mode='afni'):
        '''
        Applies motion correction to the real-time NIFTI using FSL/AFNI.

        Parameters
        ----------
        ref_img : class preproc.ref_img
            Reference image object from preproc.py
        mc_mode : str, default 'afni'
            Mode of motion correction to use. Supported modes are: ['afni', 'fsl', 'none'].
        '''
        # Parse parameters
        mc_options = ['afni', 'fsl', 'none']
        if mc_mode not in mc_options:
            raise ValueError(f'mc_mode {mc_mode} unsupported. Options are: {mc_options}.')

        # Generate some paths
        temp_file = self.proc_dir + '/' + self.raw_nii
        mc_file = self.proc_dir + '/img_mc_' + str(self.rep+1).zfill(3) + '.nii.gz'
        mc_params_file = self.proc_dir +'/mc_params_' + str(self.rep+1).zfill(3) + '.txt'

        start_time = time.time()
        if mc_mode == 'afni':
            os.system('3dvolreg -prefix '+mc_file+' -base '+ref_img.file+' -1Dfile '+mc_params_file+' '+temp_file+' 2>/dev/null')
        elif mc_mode == 'fsl':
            os.system('mcflirt -in '+temp_file+' -dof 6 -reffile '+ref_img.file+' -out '+mc_file)
        elif mc_mode == 'none':
            os.system('cp '+temp_file+' '+mc_file)
        end_time = time.time()
        print("Time motion correct: {:.2f} seconds".format(end_time - start_time))

    def apply_normalization(self, ref_img):
        '''
        Normalizes real-time NIFTI to MNI space via ANTs/fMRIPrep transforms.

        Parameters
        ----------
        ref_img : class preproc.ref_img
            Reference image object from preproc.py
        '''
        # Generate some paths
        mc_file = self.proc_dir + '/img_mc_' + str(self.rep+1).zfill(3) + '.nii.gz'
        transformed_epi = self.proc_dir + '/img_mni_' + str(self.rep+1).zfill(3) + '.nii.gz'
        mni_template = ref_img.mni_template
        warp_file = ref_img.warp_file

        # Call ANTs
        os.system(f"antsApplyTransforms -d 3 -i {mc_file} -r {mni_template} -o {transformed_epi} -n Linear -t {warp_file}")

    def extract_roi_signals(self):
        '''
        Returns region-by-region signal from the real-time image.
        Maps the voxels of a motion-corrected/normalized rt_img to a (given?) ROI?

        Questions:
            * Should a specific ROI be passed?
            * How are regions parcellated?
            * Flexible atlas support?
            * Presumably image masking is a prerequisite to this?
        '''
        # Generate some paths
        transformed_epi = self.proc_dir + '/img_mni_' + str(self.rep+1).zfill(3) + '.nii.gz'
        mni_img = nib.load(transformed_epi)
        out_roi = np.zeros(mni_img.shape[0]) # why [0] ? isn't that just sag?
        for voxel in range(mni_img.shape[0]):
            out_roi[voxel] = mni_img[self.voxel_indices[voxel,0],
                                     self.voxel_indices[voxel,1],
                                     self.voxel_indices[voxel,2]]
        return out_roi

def convert_dicom_to_nii(dcm_file,nii_outdir,dcm_dir,TR_num):
    '''
    Takes a DICOM image and converts to NIFTI. Basically a Python wrapper for dcm2niix.

    Parameters
    ----------
    dcm_file : str
        Name of the DICOM file to be converted.
    dcm_dir : str
        Folder that contains dcm_file.
    nii_outdir : str
        Path to save the converted NIFTI to.
    
    '''
    # Copy single dicom to proc dir with a predictable name
    single_dicom_path = os.path.join(nii_outdir, 'current.dcm')
    os.system('cp ' + dcm_file + ' ' + single_dicom_path)
    # Convert
    os.system('dcm2niix -b y -z n -x n -t n -m n -f %d_%s_' + str(TR_num) + ' -o ' + nii_outdir + ' -s y -v n ' + single_dicom_path)
    proc_epis = glob.glob(nii_outdir+'/*.nii') 
    new_nii_file = max(proc_epis, key=os.path.getctime).split('/')[-1]
    print ('returning new_nii_file')
    print('[convert_dicom_to_nii] returning filename\n', new_nii_file)
    os.remove(single_dicom_path)
    return new_nii_file