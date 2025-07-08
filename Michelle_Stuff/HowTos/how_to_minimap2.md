# How to use minimap2

## Conda environment creation
Start by creating a conda environment using `conda env create -f minimap2.yml`.

Activate using `conda activate minimap2`.

## Setup
Have your `genome.fa`, `ctrl.fa` and `exp.fa` files in the pwd.

## Running

`minimap2 -a genome.fa query.fa > alignment.sam`
  Run for both the control and exp.

minimap2 works with both FASTA and FASTQ files. They also don't need to be gunzipped.
