#!/usr/bin/env python

import argparse
import sys

from string import Template


slurm_header = """#!/bin/bash
#
# add all other SBATCH directives here...
#
#SBATCH -p $cluster
#SBATCH -n 1 # Number of cores
#SBATCH -N 1 # Ensure that all cores are on one machine
#SBATCH --gres=gpu
#SBATCH --mem=24000
#SBATCH -t $time
#SBATCH --mail-type=ALL
#SBATCH --mail-user=lekschas@g.harvard.edu
#SBATCH -o /n/pfister_lab/lekschas/perceptual-similarity/logs/out-%j.txt
#SBATCH -e /n/pfister_lab/lekschas/perceptual-similarity/logs/err-%j.txt

# add additional commands needed for Lmod and module loads here
source new-modules.sh
module load Anaconda3/5.0.1-fasrc02 cuda/9.0-fasrc02 cudnn/7.0_cuda9.0-fasrc01
"""

slurm_body = Template(
    """
# add commands for analyses here
cd /n/pfister_lab/lekschas/perceptual-similarity/
source activate /n/pfister_lab/lekschas/envs/perceptual-similarity
python compute_dists_pair.py -d imgs/data/$dataset -o imgs/data/$dataset.txt --use_gpu

# end of program
exit 0;
"""
)


def jobs(
    dataset: str,
    cluster: str = 'holyseas'
):
    if dataset is None:
        sys.stderr.write(
            "Provide either a path to multiple datasets or to a single dataset\n"
        )
        sys.exit(2)

    if cluster == "cox":
        max_time = "7-12:00"
    elif cluster == "holyseas":
        cluster = "holyseasgpu"
        max_time = "7-00:00"
    elif cluster == "seasdgx1":
        cluster = "seas_dgx1"
        max_time = "3-00:00"
    else:
        sys.stderr.write("Unknown cluster: {}\n".format(cluster))
        sys.exit(2)

    new_slurm_body = slurm_body.substitute(dataset=dataset)
    slurm = (
        slurm_header
        .replace("$cluster", cluster)
        .replace("$time", max_time)
        + new_slurm_body
    )

    slurm_name = "compute-similarity-{}.slurm".format(dataset) if dataset is not None else "compute-similarity.slurm"

    with open(slurm_name, "w") as f:
        f.write(slurm)

    print(
        "Created slurm file for compute the similarity of the '{}' dataset".format(dataset)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Peax Job Creator")
    parser.add_argument(
        "-d", "--dataset", help="name of the dataset"
    )
    parser.add_argument(
        "-c", "--cluster", help="cluster", default="holyseas", choices=["cox", "holyseas", "seasdgx1"]
    )

    args = parser.parse_args()

    jobs(
        args.dataset,
        cluster=args.cluster
    )
