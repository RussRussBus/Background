import os
# import sys # used for debugging
import argparse

parser = argparse.ArgumentParser(description='runs multiple coverages at once')
parser.add_argument('genome', help='genome')
parser.add_argument('exp', help='dir of diff exp coverages')
parser.add_argument('ctrl', help='dir of control fasta files')
parser.add_argument('--output', default='.', help='output destination')
arg = parser.parse_args()

# working directory (aka output directory)
wd = arg.output

################################
## initialization for bowtie2 ##
################################

os.system(f'rm -rf {wd}/index')
os.system(f'mkdir {wd}/index')
os.system(f'bowtie2-build {arg.genome} {wd}/index/genome > {wd}/index/log.txt')

#################################
### running bowtie2 and homer ###
#################################

i = 0 # used to track first run

for ctrl_file in os.listdir(arg.ctrl):
    ctrl_out = ctrl_file.strip('.fa')

    os.system(f'bowtie2 -x {wd}/index/genome -f -U {arg.ctrl}/{ctrl_file} -S {wd}/{ctrl_out}_output.sam')
    os.system(f'samtools view -bS {wd}/{ctrl_out}_output.sam | samtools sort -o {wd}/{ctrl_out}_sorted.bam')
    os.system(f'makeTagDirectory {wd}/{ctrl_out}_tag_dir {wd}/{ctrl_out}_sorted.bam')

    for exp_file in os.listdir(arg.exp):
        exp_out = exp_file.strip('.fa')
        
        # ensures these files are only made once
        if i == 0:
            os.system(f'bowtie2 -x {wd}/index/genome -f -U {arg.exp}/{exp_file} -S {wd}/{exp_out}_output.sam')
            os.system(f'samtools view -bS {wd}/{exp_out}_output.sam | samtools sort -o {wd}/{exp_out}_sorted.bam')
            os.system(f'makeTagDirectory {wd}/{exp_out}_tag_dir {wd}/{exp_out}_sorted.bam')
            
        os.system(f'findPeaks {wd}/{exp_out}_tag_dir -i {wd}/{ctrl_out}_tag_dir > {wd}/homer_{exp_out}_{ctrl_out}.txt')
    i += 1

os.system(f'rm -rf {wd}/outputs')
os.system(f'mkdir {wd}/outputs')
os.system(f'mv {wd}/homer* {wd}/outputs')