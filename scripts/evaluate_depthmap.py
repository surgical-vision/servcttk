"""
Compute depth error metrics across all experiments.

Compute error between ground truth and depthmap estimations across all datasets
in different error metrics. Both absolute and signed errors get computed. The 
disparity_dir directory must include all depthmap samples, named after their
corresponding reference e.g. 001.png. Additionally those file should be stored as 
16bit .pngs scaled by a factor of 256 or directly as .tif. To read and write
depthmap images in png format encapsulating decimal information, load_subpix_png
and save_subpix_png included in iotools can used respectively. This script will 
compute error including metrics such as RMSE, Median and Mean ablsolute error
and export values per sample in .csv format in a directory called error, under
depthmap_dir. A summary file will also be created containing Mean Error for Mean,
RMS and Median metrics. Per sample errors can be found in noc and occ .csv files.
"""

import cv2
import numpy as np
import argparse
from pathlib import Path
import pandas as pd
from servcttk.iotools import load_subpix_png, parse_occlusion_image, agg_paths
from servcttk.analytics import describe_error_depth


parser = argparse.ArgumentParser(description="Evaluate depthmap error")
parser.add_argument('dataset_dir', help="Path to dataset root directory")
parser.add_argument('depthmap_dir', help='Path to the directory containing the estimated depthmaps')
parser.add_argument('--verbose','-v', help='Print result summary to the console', action='store_true')

if __name__ == "__main__":
    args = parser.parse_args()

    path_dict = agg_paths(args.dataset_dir)
    depthmap_dir_p = Path(args.depthmap_dir)


    out_dir_p = depthmap_dir_p/'error'
    out_dir_p.mkdir(parents=True, exist_ok=True)

    depth_error_df = pd.DataFrame()

    for occlusions in [True, False]:
        for gt_depth_p, occ_p in zip(path_dict['depth'], path_dict['occ']):
            # compute depthmap error for each sample
            comp_depth_lst_p = [p for p in depthmap_dir_p.iterdir() if p.stem == gt_depth_p.stem]
            if comp_depth_lst_p:
                comp_depth_p = comp_depth_lst_p[0]
            else:
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(errno.ENOENT), str(depthmap_dir_p/(gt_depth_p.stem+'.*')))

            ref = load_subpix_png(gt_depth_p)
            comp = load_subpix_png(comp_depth_p)

            common_valid = parse_occlusion_image(occ_p, not occlusions)
            comp_valid = common_valid.copy()
            
            # pixels with depth values of 0 or inf are considered invalid
            # and do not affect the final score.            
            comp_valid[comp == -np.inf] = False
            comp_valid[comp == np.inf] = False
            comp_valid[comp == 0] = False

            deptmap_diff = comp - ref
            valid_diff = deptmap_diff[comp_valid == True].reshape(-1)

            metrics = {'Sample': Path(gt_depth_p).stem}
            metrics.update(describe_error_depth(valid_diff))
            metrics['Coverage'] = np.sum(comp_valid)/np.sum(common_valid)
            metrics['occ'] = occlusions
            metrics['Experiment'] = gt_depth_p.parents[2].name
            metrics['Modality'] = gt_depth_p.parents[1].name.split('_')[-1]
            depth_error_df = depth_error_df.append(metrics, ignore_index=True)

    # split results based on experiment, occlusions, modality and save them
    for experiment in list(set(depth_error_df['Experiment'].to_list())):
        tmp_experiment_df = depth_error_df[depth_error_df['Experiment'] == experiment]
        for modality in list(set(tmp_experiment_df['Modality'].to_list())):
            tmp_modality_df = tmp_experiment_df[tmp_experiment_df['Modality'] == modality]
            for occlusions in [True, False]:
                tmp_df = tmp_modality_df[tmp_modality_df['occ'] == occlusions]
                del tmp_df['occ']
                del tmp_df['Experiment']
                del tmp_df['Modality']
                save_dir = out_dir_p/experiment/modality
                save_dir.mkdir(parents=True, exist_ok=True)
                name = 'depthmap_error_occ.csv' if occlusions else 'depthmap_error_noc.csv'
                with open(save_dir/name, 'w') as f:
                    tmp_df.to_csv(f, index=False)

    # save and print results summary
    summary_df = depth_error_df.groupby(
        ['Experiment', 'Modality', 'occ']).mean()
    if args.verbose:
        print(
            summary_df[['RMS', 'Median (Absolute)', 'Mean (Absolute)']])
    with open(out_dir_p/'depthmap_error_summary.csv', 'w') as f:
        (summary_df[['RMS', 'Median (Absolute)', 'Mean (Absolute)']]).to_csv(
            f)
