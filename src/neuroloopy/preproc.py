"""
Preprocessing functions for fMRI neurofeedback.
"""

import os
import time
import nibabel as nib
import numpy as np
from scipy.signal import detrend


def convert_dicom_to_nii(dcm_file, nii_outdir, dcm_dir, TR_num, dcm2niix_dir):
    """
    Convert DICOM file to NIfTI format.
    
    Args:
        dcm_file: DICOM file path
        nii_outdir: Output directory for NIfTI files
        dcm_dir: DICOM directory
        TR_num: TR number
        dcm2niix_dir: dcm2niix executable directory
    
    Returns:
        str: Path to converted NIfTI file
    """
    print(f"Converting DICOM to NIfTI: {dcm_file}")
    
    # Create output directory if it doesn't exist
    os.makedirs(nii_outdir, exist_ok=True)
    
    # Run dcm2niix conversion
    cmd = f"{dcm2niix_dir}/dcm2niix -o {nii_outdir} -f img_{TR_num:03d} {dcm_dir}"
    print(f"Running command: {cmd}")
    os.system(cmd)
    
    # Find the converted file
    nii_files = [f for f in os.listdir(nii_outdir) if f.endswith('.nii.gz')]
    if nii_files:
        return nii_files[0]
    else:
        raise FileNotFoundError("No NIfTI file found after conversion")


def process_volume(raw_nii, roi_voxels, rep, rfi_file, proc_dir, ref_header, 
                  ref_affine, mc_mode, warp_file, mni_template):
    """
    Process a single volume through the preprocessing pipeline.
    
    Args:
        raw_nii: Raw NIfTI file path
        roi_voxels: ROI voxel indices
        rep: Repetition number
        rfi_file: Reference functional image file
        proc_dir: Processing directory
        ref_header: Reference header
        ref_affine: Reference affine matrix
        mc_mode: Motion correction mode ('fsl', 'afni', 'none')
        warp_file: Warp file for MNI transformation
        mni_template: MNI template file
    
    Returns:
        tuple: (roi_data, rep)
    """
    try:
        print(f"DEBUG process_volume started for rep: {rep}")
        
        temp_file = proc_dir + '/' + raw_nii
        mc_file = proc_dir + '/img_mc_' + str(rep + 1).zfill(3) + '.nii.gz'
        mc_params_file = proc_dir + '/mc_params_' + str(rep + 1).zfill(3) + '.txt'
        
        print(f'DEBUG temp_file: {temp_file}')
        print(f'DEBUG mc_file: {mc_file}')
        print(f'DEBUG mc_mode: {mc_mode}')
        
        # Motion correction
        print('Starting motion correction...')
        start_time = time.time()
        
        if mc_mode == 'afni':
            os.system(f'3dvolreg -prefix {mc_file} -base {rfi_file} -1Dfile {mc_params_file} {temp_file} 2>/dev/null')
        elif mc_mode == 'fsl':
            print('DEBUG running mcflirt')
            os.system(f'mcflirt -in {temp_file} -dof 6 -reffile {rfi_file} -out {mc_file}')
        elif mc_mode == 'none':
            os.system(f'cp {temp_file} {mc_file}')
        
        end_time = time.time()
        print(f"Time motion correct: {end_time - start_time:.2f} seconds")
        
        # Convert to MNI space
        print('Converting to MNI')
        start_time = time.time()
        
        transformed_epi = proc_dir + '/img_mni_' + str(rep + 1).zfill(3) + '.nii.gz'
        
        # Apply warp transformation
        os.system(
            f"antsApplyTransforms -d 3 -i {mc_file} -r {mni_template} "
            f"-o {transformed_epi} -t {warp_file}"
        )
        
        end_time = time.time()
        print(f"Time MNI transform: {end_time - start_time:.2f} seconds")
        
        # Extract ROI data
        print('Extracting ROI data...')
        start_time = time.time()
        
        img = nib.load(transformed_epi)
        img_data = img.get_data()
        roi_data = map_voxels_to_roi(img_data, roi_voxels)
        
        end_time = time.time()
        print(f"Time ROI extraction: {end_time - start_time:.2f} seconds")
        
        print(f"DEBUG process_volume completed for rep: {rep}")
        return (roi_data, rep)
        
    except Exception as e:
        print(f"ERROR in process_volume for rep {rep}:")
        import traceback
        print(traceback.format_exc())
        return (None, rep)


def map_voxels_to_roi(img, roi_voxels):
    """
    Map voxels to ROI.
    
    Args:
        img: Image data
        roi_voxels: ROI voxel indices
    
    Returns:
        numpy.ndarray: ROI data
    """
    return img[roi_voxels[:, 0], roi_voxels[:, 1], roi_voxels[:, 2]]
