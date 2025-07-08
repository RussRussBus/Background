#!/usr/bin/env Rscript

# runs spp

library(spp) # loads in spp

args <- commandArgs(trailingOnly = TRUE) # assignes cli arugments as a character vector
if (length(args) != 3) {
    stop("Usage: Rscript run_spp.R <exp.tagAlign> <ctrl.tagAlign> <output_file>")
}

exp_file <- args[1]
ctrl_file <- args[2]
fdr_input <- args[3]

exp.data <- read.tagalign.tags(exp_file)
exp.data <- exp.data$tags
ctrl.data <- read.tagalign.tags(ctrl_file)
ctrl.data <- ctrl.data$tags

results <- find.binding.positions(signal.data = exp.data, control.data = ctrl.data, fdr = fdr_input)

cat('results\n')
print(results$npl)
