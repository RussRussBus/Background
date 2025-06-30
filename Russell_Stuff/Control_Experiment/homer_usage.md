# How I got Homer to work
Note: I used mamba instead of conda in all conda/mamba related commands

## Converting .sam to .bam
This conversion needs to happen because outputs of bowtie2 are in .sam formats and Homer uses .bam formats as input

Steps:
1) If `control_exp` environment is not set up, run command `conda env create -f control_environment.yml`.

2) Activate `control_exp` environment

3) Run `samtools view -bS exp_1_output.sam | samtools sort -o exp_1_sorted.bam` and `samtools view -bS ctrl_1_output.sam | samtools sort -o ctrl_1_sorted.bam`
- `view` is a subcommand of samtools that allows files to be read
- `-bS` the b tells view to output as .bam and S tells view that the input is in .sam
- `sort` sorts the .bam file by chromosome and position and outputs it
- `-o` indicates the name of sorted output file

4) Run `samtools index exp_1_sorted.bam` and `samtools index ctrl_1_sorted.bam`
- **Run only if needed**
- `index` is a subcommand of samtools that produces and outputs an indexed file. Indexing is useful for quick accessing of specific chromosomes and reads

## Getting homer to work
1) Create Tag directories with `makeTagDirectory exp_1_tag_dir exp_1_sorted.bam` and `makeTagDirectory ctrl_1_tag_dir ctrl_1_sorted.bam`

2) Run `findPeaks exp_1_tag_dir -i ctrl_1_sorted.bam > homer_exp1_ctrl1.txt`
`-i` indicates the control tag directory

## other options
`-fdr` this changes the threshold for what is a peak. Setting closer to 1 increases sensitivity but lowers specificity. Set closer to 0 to find peaks that less likely to be false positives.