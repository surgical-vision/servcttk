from pathlib import Path
import numpy as np
import cv2
import os
import errno
import json





def load_subpix_png(path, scale_factor=256.0):
    """load one channel images holding decimal information and stored as 16-bit
    pngs and normalize them by scale_factor.

    Args:
        path ([pathlib.Path, str]): path of the file to load
        scale_factor (float, optional): the factor used to divide the 16-bit uint 
        integers of the input file. The scaling factor is only used when the
        pngs are 16bit. Defaults value is 256.0.

    Raises:
        FileNotFoundError: when path points to a file that does not exists.

    Returns:
        nd.array: the loaded image in np.float32 format, normalized if applicable.
    """
    if not Path(path).is_file():
        raise FileNotFoundError(
            errno.ENOENT, os.strerror(errno.ENOENT), str(path))
    disparity = cv2.imread(str(path), -1)
    disparity_type = disparity.dtype
    disparity = disparity.astype(np.float32)
    if disparity_type == np.uint16:
        disparity = disparity / scale_factor
    return disparity


def save_subpix_png(path, img, scale_factor=256.0):
    """Save a float one channel image as .png, keeping decimal information.

    To keep decimal information while allowing easy preview of image data,
    instead of saving information as .tif image, unsuitable for preview or 8 bit
    pngs, discretizing the values the of the image, this function
    multiplies the image by scale_factor and stores it is as a 16bit png. The 
    resulting image can be loaded and subpixel information can be recovered by 
    deviding the uint16 values by the same scale_factor. This process is lossy,
    but allows dephtmaps and disparities to be stored as png images for easy
    preview.

    Args:
        path ([str, pathlib.Path]): path to store the image.
        img (np.array): the image to store.
        scale_factor (float, optional): the factor to divide the uint16 values.
        Defaults to 256.0.
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    img = img.astype(np.float32) * scale_factor
    if np.amax(img) > (2**16)-1:
        warnings.warn("image out of range(" + str(np.amax(img)/scale_factor) +
                      "), try with a smaller scale factor. loading this file " +
                      "will results in invalid values, file: "+str(path))
        img[img > (2**16)-1] = 0
    img = img.astype(np.uint16)
    cv2.imwrite(str(path), img)


def parse_occlusion_image(path, noc=False):
    """parse occlusion image and return valid mask containing either all
    pixels except pixel of which ground truth is not known or only non occluded
    pixels. 

    Args:
        path ([pathlib.Path, str]): path to occlusion image
        noc (bool, optional): include only pixels visible from both views.
        Defaults to False.

    Raises:
        FileNotFoundError: occlusion image not found

    Returns:
        nd.array: mask indicating valid pixels
    """
    occlusion_color = cv2.imread(str(path))
    if occlusion_color is None:
        raise FileNotFoundError(errno.ENOENT, os.strerror(
            errno.ENOENT), path)

    h, w, c = occlusion_color.shape
    # regions without ground truth information are blue
    mask = np.full((h, w), fill_value=True)
    mask[np.where(np.all(occlusion_color == (255, 0, 0), axis=-1))] = False

    if noc:
        # regions outside the other image's borders are in yellow
        mask[np.where(np.all(occlusion_color == (0, 255, 255), axis=-1))] = False
        # regions schene occluded in the right image are in red
        mask[np.where(np.all(occlusion_color == (0, 0, 255), axis=-1))] = False
        # regions schene occluded in the left image are in green
        mask[np.where(np.all(occlusion_color == (0, 255, 0), axis=-1))] = False
    return mask


def agg_paths(dataset_root_dir):
    """aggregates filepaths from the datasets and returns them in a dictionary
    format.

    Args:
        dataset_root_dir ([pathlib.Path, str]): path to datasets's root directory
    """
    root_dir_p = Path(dataset_root_dir)
    experiment_dirs = sorted([e for e in root_dir_p.iterdir()])
    
    left_paths=[]
    right_paths=[]
    occl_paths=[]
    disparity_paths=[]
    depth_paths=[] 
    calib_paths=[]
    sample_name=[]

    for experiment in experiment_dirs:
        modality_gt_dirs = sorted([gt_dir for gt_dir in experiment.iterdir() if 'Ground_truth' in gt_dir.name])
        for modality_gt_dir in modality_gt_dirs:
            occl_paths.extend(sorted([p.resolve()
                            for p in (modality_gt_dir/'OcclusionL').iterdir()]))
            disparity_paths.extend(sorted([p.resolve()
                                for p in (modality_gt_dir/'Disparity').iterdir()]))
            depth_paths.extend(sorted([p.resolve()
                            for p in (modality_gt_dir/'DepthL').iterdir()]))
            
            
            left_paths.extend(sorted([(experiment/'Left_rectified'/p.name).resolve()
                            for p in (modality_gt_dir/'OcclusionL').iterdir()]))
            right_paths.extend(sorted([(experiment/'Right_rectified'/p.name).resolve()
                            for p in (modality_gt_dir/'OcclusionL').iterdir()]))
            calib_paths.extend(sorted([(experiment/'Rectified_calibration'/(p.stem+'.json')).resolve()
                            for p in (modality_gt_dir/'OcclusionL').iterdir()]))
            sample_name.extend(sorted([(p.parents[2]).name+' - ' + (p.parents[1]).name.split('_')[-1]+ ' - '+p.stem for p in (modality_gt_dir/'Disparity').iterdir()])) 
    return {'left': left_paths,
            'right': right_paths,
            'occ': occl_paths,
            'disparity': disparity_paths,
            'depth': depth_paths,
            'calib': calib_paths,
            'name': sample_name}            
        