import os
import sys # used for debugging
import argparse

parser = argparse.ArgumentParser(description='runs multiple coverages at once')
parser.add_argument('genome', help='genome')
parser.add_argument('exp', help='dir of diff exp coverages')
parser.add_argument('ctrl', help='dir of control fasta files')
parser.add_argument('--output', default='.', help='output destination')
arg = parser.parse_args()

# working directory (aka output directory)
wd = arg.output

# creating the chrom.sizes file 
genome_path = arg.genome.rstrip('.fa.gz')  
os.system(f'gunzip -k {arg.genome}') 
os.system(f'samtools faidx {genome_path}.fa')
os.system(f'cut -f 1,2 {genome_path}.fa.fai > {genome_path}.chrom.sizes')


################################
## initialization for bowtie2 ##
################################

os.system(f'rm -rf {wd}/index')
os.system(f'mkdir {wd}/index')
os.system(f'bowtie2-build {arg.genome} {wd}/index/genome > {wd}/index/log.txt')
os.system(f'mkdir {wd}/sam_bam_bed')

#################################
### running bowtie2 and sicer2 ###
#################################

i = 0 # used to track first run

for ctrl_file in os.listdir(arg.ctrl):
    ctrl_out = ctrl_file.strip('.fa')

    os.system(f'bowtie2 -x {wd}/index/genome -f -U {arg.ctrl}/{ctrl_file} -S {wd}/{ctrl_out}_output.sam')
    os.system(f'samtools view -bS {wd}/{ctrl_out}_output.sam | samtools sort -o {wd}/{ctrl_out}_sorted.bam')
    os.system(f'mv {wd}/{ctrl_out}_sorted.bam {wd}/sam_bam_bed')
    os.system(f'mv {wd}/{ctrl_out}_output.sam {wd}/sam_bam_bed')

    for exp_file in os.listdir(arg.exp):
        exp_out = exp_file.strip('.fa')
        
        # ensures these files are only made once
        if i == 0:
            os.system(f'bowtie2 -x {wd}/index/genome -f -U {arg.exp}/{exp_file} -S {wd}/{exp_out}_output.sam')
            os.system(f'samtools view -bS {wd}/{exp_out}_output.sam | samtools sort -o {wd}/{exp_out}_sorted.bam')
            os.system(f'mv {wd}/{exp_out}_sorted.bam {wd}/sam_bam_bed')
            os.system(f'mv {wd}/{exp_out}_output.sam {wd}/sam_bam_bed')
            
        os.system(f'epic2 --treatment {wd}/sam_bam_bed/{exp_out}_sorted.bam --control {wd}/sam_bam_bed/{ctrl_out}_sorted.bam --chromsizes {genome_path}.chrom.sizes --output epic2_{exp_out}_{ctrl_out}.bed')
    i += 1

os.system(f'rm -rf {wd}/results')
os.system(f'mkdir {wd}/results')
os.system(f'mv {wd}/epic2_{exp_out}_{ctrl_out}.bed {wd}/results')
