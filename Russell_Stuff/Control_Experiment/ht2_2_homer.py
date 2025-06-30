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

# creates log for pipeline
os.system(f'rm -f {wd}/log.txt')
os.system(f'touch {wd}/log.txt')
with open(f'{wd}/log.txt', 'w') as out:
    out.write(f'genome: {arg.genome}\n')
    out.write(f'experiment: {arg.exp}\n')
    out.write(f'control: {arg.ctrl}\n')

# cleans up file suffixes
def rm_suffix(string):
    if string.endswith('.fa.gz'):
        return string[:-6]
    elif string.endswith('.fa'):
        return string[:-3]
    return string

###############################
## initialization for hisat2 ##
###############################

os.system(f'rm -rf {wd}/index')
os.system(f'mkdir {wd}/index')
os.system(f'hisat2-build {arg.genome} {wd}/index/genome > {wd}/index/log.txt')

################################
### running hisat2 and homer ###
################################

i = 0 # used to track first run

for ctrl_file in os.listdir(arg.ctrl):
    ctrl_out = rm_suffix(ctrl_file)

    os.system(f'hisat2 -f -x {wd}/index/genome -U {arg.ctrl}/{ctrl_file} -S {wd}/{ctrl_out}_output.sam')
    os.system(f'samtools view -bS {wd}/{ctrl_out}_output.sam | samtools sort -o {wd}/{ctrl_out}_sorted.bam')
    os.system(f'makeTagDirectory {wd}/{ctrl_out}_tag_dir {wd}/{ctrl_out}_sorted.bam')

    for exp_file in os.listdir(arg.exp):
        exp_out = rm_suffix(exp_file)
        
        # ensures these files are only made once
        if i == 0:
            os.system(f'hisat2 -f -x {wd}/index/genome -U {arg.exp}/{ctrl_file} -S {wd}/{exp_out}_output.sam')
            os.system(f'samtools view -bS {wd}/{exp_out}_output.sam | samtools sort -o {wd}/{exp_out}_sorted.bam')
            os.system(f'makeTagDirectory {wd}/{exp_out}_tag_dir {wd}/{exp_out}_sorted.bam')
            
        os.system(f'findPeaks {wd}/{exp_out}_tag_dir -i {wd}/{ctrl_out}_tag_dir > {wd}/homer_{exp_out}_{ctrl_out}.txt')
        
    i += 1

#######################
### sorting outputs ###
#######################

os.system(f'rm -rf {wd}/outputs')
os.system(f'mkdir {wd}/outputs')
os.system(f'mv {wd}/homer* {wd}/outputs')

os.system(f'touch {wd}/output_summary.txt')
with open(f'{wd}/output_summary.txt', 'w') as out:

    for file in os.listdir(f'{wd}/outputs'):
        exp = ''
        ctrl = ''
        peaks = ''

        with open(f'{wd}/outputs/{file}', 'r') as fp:
            for line in fp:
                line = line.strip()
                if line.find('# tag ') != -1: exp = line[line.find('=')+2:]
                elif line.find('# total') != -1: peaks = line[2:]
                elif line.find('# input') != -1: ctrl = line[line.find('=')+2:]

                if exp != '' and ctrl != '' and peaks != '': break

            out.write(f'Experiment: {exp}\n')
            out.write(f'Control: {ctrl}\n')
            out.write(f'{peaks}\n\n')