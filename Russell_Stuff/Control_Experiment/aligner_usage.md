# How I got bowtie2 to work

## Conda environment creation
Start by creating a conda environment using `conda env create -f control_environment.yml`.

Activate using `conda activate control_exp`.

## Set up
Make sure `exp_1.fa`, `ctrl_1.fa`, and `random_genome_1.fa.gz` is in pwd.

Use `mkdir index` to create directory to store bowtie2 index.

Run `bowtie2-build random_genome_1.fa.gz index/rg_1` to create an index inside of `index` directory.

## Running bowtie2
Run command `bowtie2 -x index/rg_1 -f -U exp_1.fa -S exp_1_output.sam` and `bowtie2 -x index/rg_1 -f -U ctrl_1.fa -S ctrl_1_output.sam`

`-x` flag indicates which index to use.

`-f` tells bowtie2 that the query is in fasta format and `-U` indicates to the query.

`-S` indicates name for output file (in SAM format).

---

# Hisat2 usage

## Building index
Make index dir with `mkdir index`.

A index was build using the command `hisat2-build 1pct.fa 1pct_celegans`.

## Running hisat2
Ran hisat2 with this command `hisat2 -f -x index/1pct_celegans -U exp.fa -S exp.sam`.

> `-f` specifies that the input file is i fasta format
> `-x` specifies the index
> `-U` specifies the input file
> `-S` specifies the name of output file in sam format