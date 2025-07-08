# How I got spp to work
Note: spp does not run on cli so `Rscript` command is used on cli to run an R script that contains spp.

## Start
1) Create R script

## Coverting sam to tagAlign
sam is the output format for bowtie2 and hisat2 aligners. tagAlign is the format accepted by spp. This is a 6 column bed like format.

1) Convert sam to sorted bams by running `samtools view -bS exp_output.sam | samtools sort -o exp_sorted.bam` and `samtools view -bS ctrl_output.sam | samtools sort -o ctrl_sorted.bam`.

- `view` is a subcommand of samtools that allows files to be read
- `-bS` the b tells view to output as .bam and S tells view that the input is in .sam

- `sort` sorts the .bam file by chromosome and position and outputs it
- `-o` indicates the name of sorted output file


2) Create indexes for sorted bam files by running `samtools index exp_sorted.bam` and `samtools index ctrl_sorted.bam`.

- `index` is a subcommand of samtools that produces and outputs an indexed file. Indexing is useful for quick accessing of specific chromosomes and reads


3) Create tagAlign files used by spp peakcaller by running `bedtools bamtobed -i exp_sorted.bam | awk 'BEGIN{OFS="\t"} {print $1, $2, $3, "N", "1000", $6}' > exp.tagAlign` and `bedtools bamtobed -i ctrl_sorted.bam | awk 'BEGIN{OFS="\t"} {print $1, $2, $3, "N", "1000", $6}' > ctrl.tagAlign`.

- `bamtobed` is a command that converts bam files to bed files
- `-i` indicates that the following argument is a sorted bam file. This sorted bam file must also have an index

- `awk` is a command that reads input and splits each line into fields
- `BEGIN{OFS="\t"}` is an intializer. `BEGIN` is translated as run this before processing. `OFS` stands for output field separator. `\t` indicates tab character. Overall, this initializer runs before processing and separates all fields with tabs
- `{print $1, $2, $3, "N", "1000", $6}` formats the output. The `$` corresponds the object or word that from the input ($1 first word or object). N and 1000 are just placeholders that do not have effect on running spp

## Writing R script that runs spp
Note: All commands run within an R script and using `Rscript` command on cli.

Run `library(spp)`
- loads in spp

Run `args <- commandArgs(trailingOnly = TRUE)`
- `trailingOnly` is an argument that makes `commandArgs` only consider cli arguments that follow the `--args` flag
- - setting to true makes `commandArgs` consider any cli arguments
- assigns output of `commandArgs` to `args` variable
- `commandArgs` assigns cli arguments as character vectors (list of specifically strings)

Not needed but `if (length(args) != 3) {stop("Usage: Rscript run_spp.R <exp.tagAlign> <ctrl.tagAlign> <output_file>")}` ensures the right number of arguments in cli command

Each element of `args` is assigned to their respective variables (3 different elements)
- Ex: `exp_file <- args[1]`

Run `exp.data <- read.tagalign.tags(exp_file)` and `exp.data <- exp.data$tags`
- runs spp function `read.tagalign.tags` on experiment file
- the second command ensure that only the tags are assigned to `exp.data` and gets rid of list of quality values

Run `ctrl.data <- read.tagalign.tags(ctrl_file)` and `ctrl.data <- ctrl.data$tags`
- these commands have the same function as the previous commands but do it for the control file

Run `results <- find.binding.positions(signal.data = exp.data, control.data = ctrl.data, fdr = .05)`
- this command saves the output of `find.binding.positions` into `results` variable
- `find.binding.positions` is the spp function that finds the peaks of an experiment
- `fdr` is set to 0.001 as it is the default of homer peakcaller

Run `write.table(results, file = output_file, sep = "\t", quote = FALSE, row.names = FALSE)`
- produces a tsv file of the results
- Note: empty if no peaks and can give error

Run `rscript ../spp.R exp.tagAlign ctrl.tagAlign 1pct_test.tsv` while in the desired output directory