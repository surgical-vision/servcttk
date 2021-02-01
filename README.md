# servcttk

This repository contains python code to evaluate on the Stereo-Endoscopic
Reconstruction Validation dataset based on CT (SERV-CT).

## About SERV-CT

SERV-CT contains 16 stereo-endoscopic image pairs with reference anatomical
segmentation derived from CT. Two different ex vivo porcine samples were imaged
using the straight and 30° endoscopes from the original classic da Vinci™
Surgical System (Intuitive Inc., Sunnyvale, US).

The dataset provides reference in both disparity and depth (Z distance between 3D
point and camera center) domain as well as occlusion images.

To download the SERV-CT dataset, visit the the [project's homepage](https://www.ucl.ac.uk/interventional-surgical-sciences/serv-ct).

The arXiv version of our paper can be
found [SERV-CT: A disparity dataset from CT for validation of endoscopic 3D reconstruction](https://arxiv.org/abs/2012.11779)

![dataset generation flowchart](doc/Flowchart.png?raw=true "Title")

## Changelog

Because we currently do not collect email addresses when we provide a copy of the
SERV-CT dataset, we will keep a changelog here. If you wish to get updates about
the dataset or the evaluation code(changes/additions/fixes), press the watch
button for this repository. Any changes made will be logged here.

- 1/2/21 Release of Evaluation code for the SERV-CT dataset. Code includes
evaluation scripts for both disparities and depthmaps. Additionally we provide
code to read and write disparity and depthmap files in the format used by the dataset.
- 18/1/21 Replaced an outdated version of the SERV-CT dataset. Download the
latest from the [project's webpage](https://www.ucl.ac.uk/interventional-surgical-sciences/serv-ct)
- 22/12/20 The [SERV-CT paper preprint](https://arxiv.org/abs/2012.11779) is now available to download.

## How to use

### Anaconda environment setup

We used anaconda to manage dependencies for this project. To setup an anaconda
environment suitable to running this code, after installing anaconda, create a
new environment.

- cd to this project's directory
- create an anaconda enviroment using the requirements.txt file

```code
conda create -n servcttk --file requirements.txt -c conda-forge
```

- activate the environement

```code
conda activate servcttk
```

### Evaluate Depth and Disparity samples

The toolkit provide two scripts for evaluation, one for depthmaps and one for
disparities. The scripts assume that the the samples to evaluate are named after
the samples they correspond to. For each domain [disparity, depthmap] a single
folder containing all samples for evaluation should be created following the
file structure bellow.

```tree
.
├── Disparities
│   ├── 001.png
│   ├── 002.png
│   :
│   ├── 015.png
│   └── 016.png
└── Depthmaps
    ├── 001.png
    ├── 002.png
    :
    ├── 015.png
    └── 016.png
```

#### Disparity Evaluation

Disparity is measured as the horizontal displacement of corresponding pixels in
two views.

```code
python -m scripts.evaluate_disparity /path/to/dataset/root/directory \
                                    /path/to/directory/containing/disparity/samples/for/evaluation -v
```

#### Depthmap Evaluation

Depth error is measured in mm distance along the Z camera axis.

```code
python -m scripts.evaluate_depthmap /path/to/dataset/root/directory \
                                    /path/to/directory/containing/depthmap/samples/for/evaluation -v
```

Both scripts will create a folder named `error`, under the directory evaluation samples
are stored, and export results for each dataset/modality/occlusion in csv format
in many different metrics. Furthermore, a separate .csv will be generated
summarizing the performance across every experiment using only a subset of metrics.

Depth error is measured in mm distance and disparity in pixel displacement between
views in the horizontal dimension.

## Citation

Please cite the following publication whenever research making use of the SERV-CT
dataset or this repository's code is reported in any academic publication or
research report:

```bibtex
@article{edwards2020serv,
  title={SERV-CT: A disparity dataset from CT for validation of endoscopic 3D reconstruction},
  author={Edwards, PJ and Psychogyios, Dimitris and Speidel, Stefanie and Maier-Hein, Lena and Stoyanov, Danail},
  journal={arXiv preprint arXiv:2012.11779},
  year={2020}
}
```
