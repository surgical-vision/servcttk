"""
Compute disparity error metrics across all experiments.

Compute error between ground truth and disparity estimations across all datasets
in different error metrics. Both absolute and signed errors get computed. The 
disparity_dir directory must include all disparity samples, named after their
corresponding reference e.g. 001.png. Additionally those file should be stored as 
16bit .pngs scaled by a factor of 256. To read and write disparity images in png
format, encapsulating decimal information, load_subpix_png and save_subpix_png
included in iotools can used respectively. This script will compute error
including metrics such as RMSE, Bad3 and EPE and export values per sample in .csv
format in a directory called error, under disparity_dir. A summary file will also
be created containing Mean Error for Mean, RMS and Median metrics. Per sample
errors can be found in noc and occ .csv files.
"""


import cv2
import numpy as np
import argparse
from pathlib import Path
import pandas as pd
from servcttk.iotools import load_subpix_png, parse_occlusion_image, agg_paths
from servcttk.analytics import describe_error_disparity


parser = argparse.ArgumentParser(description="Evaluate disparity")
parser.add_argument('dataset_dir', help="Path to dataset root directory")
parser.add_argument('disparity_dir', help='Path to the directory containing the estimated disparities')
parser.add_argument('--verbose','-v', help='Print result summary to the console', action='store_true')


if __name__ == "__main__":
    
    
    args = parser.parse_args()
    
    path_dict = agg_paths(args.dataset_dir)
    disparity_dir_p = Path(args.disparity_dir)
    out_dir_p = disparity_dir_p/'error'
    out_dir_p.mkdir(parents=True, exist_ok=True)
    
    disparity_error_df=pd.DataFrame()
    
    for occlusions in [True, False]:
        for gt_disparity_p, occ_p in zip (path_dict['disparity'], path_dict['occ']):
            #compute disparity error for each sample
            comp_disp_p = disparity_dir_p/gt_disparity_p.name
            
            ref = load_subpix_png(gt_disparity_p)
            comp = load_subpix_png(comp_disp_p)
            
            common_valid = parse_occlusion_image(occ_p, not occlusions)
            comp_valid = common_valid.copy()
            # pixels with disparity values of 0 or 255 are considered invalid
            # and do not affect the final score.
            comp_valid[comp == 255] = False
            comp_valid[comp == 0] = False

            disparity_diff = comp - ref
            valid_diff = disparity_diff[comp_valid == True].reshape(-1)

            metrics = {'Sample': Path(gt_disparity_p).stem}
            metrics.update(describe_error_disparity(valid_diff))
            metrics['Coverage'] = np.sum(comp_valid)/np.sum(common_valid)
            metrics['occ']=occlusions
            metrics['Experiment'] = gt_disparity_p.parents[2].name
            metrics['Modality']=gt_disparity_p.parents[1].name.split('_')[-1]
            disparity_error_df = disparity_error_df.append(metrics, ignore_index=True)
         
    #split results based on experiment, occlusions, modality and save them
    for experiment in list(set(disparity_error_df['Experiment'].to_list())):
        tmp_experiment_df = disparity_error_df[disparity_error_df['Experiment']==experiment]
        for modality in list(set(tmp_experiment_df['Modality'].to_list())):
            tmp_modality_df = tmp_experiment_df[tmp_experiment_df['Modality']==modality]
            for occlusions in [True, False]:
                tmp_df = tmp_modality_df[tmp_modality_df['occ']==occlusions]
                del tmp_df['occ']
                del tmp_df['Experiment']
                del tmp_df['Modality']
                save_dir = out_dir_p/experiment/modality
                save_dir.mkdir(parents=True, exist_ok=True)
                name = 'disparity_error_occ.csv' if occlusions else 'disparity_error_noc.csv'
                with open(save_dir/name , 'w') as f:
                    tmp_df.to_csv(f, index=False)
    
    #save and print results summary
    summary_df = disparity_error_df.groupby(['Experiment', 'Modality', 'occ']).mean()                
    if args.verbose:
        print(summary_df[['Bad3','RMS','EPE']] )
    with open(out_dir_p/'disparity_error_summary.csv' , 'w') as f:
        (summary_df[['Bad3','RMS','EPE']]).to_csv(f)
