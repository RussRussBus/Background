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