import argparse
import os
import sys

parser = argparse.ArgumentParser(description='runs multiple coverages at once')
parser.add_argument('genome', help='genome')
parser.add_argument('exp', help='dir of diff exp coverages')
parser.add_argument('ctrl', help='dir of control fasta files')
parser.add_argument('--output', default='.', help='output destination')
parser.add_argument('--aligner', default='bt2', help='ht2 = hisat2, bt2 = bowtie2')
parser.add_argument('--peakcaller', default='homer', help='homer, spp')
parser.add_argument('-fdr', type=float, default=0.001, help='set fdr rate, default 0.001')
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
    out.write(f'aligner: {arg.aligner}\n')
    out.write(f'peakcaller: {arg.peakcaller}\n')

# cleans up file suffixes
def rm_suffix(string):
    if string.endswith('.fa.gz'):
        return string[:-6]
    elif string.endswith('.fa'):
        return string[:-3]
    return string

# creating directories
os.system(f'rm -rf {wd}/index')
os.system(f'mkdir {wd}/index')

#######################
### running bowtie2 ###
#######################

if arg.aligner == 'bt2':
    os.system(f'bowtie2-build {arg.genome} {wd}/index/genome > {wd}/index/log.txt')

    for ctrl_file in os.listdir(arg.ctrl):
        ctrl_out = rm_suffix(ctrl_file)
        ctrl_out = 'ctrl_' + ctrl_out
        os.system(f'bowtie2 -x {wd}/index/genome -f -U {arg.ctrl}/{ctrl_file} -S {wd}/{ctrl_out}_output.sam')

    for exp_file in os.listdir(arg.exp):
        exp_out = rm_suffix(exp_file)
        exp_out = 'exp_' + exp_out
        os.system(f'bowtie2 -x {wd}/index/genome -f -U {arg.exp}/{exp_file} -S {wd}/{exp_out}_output.sam')

######################
### running hisat2 ###
######################

elif arg.aligner == 'ht2':
    os.system(f'hisat2-build {arg.genome} {wd}/index/genome > {wd}/index/log.txt')

    for ctrl_file in os.listdir(arg.ctrl):
        ctrl_out = rm_suffix(ctrl_file)
        ctrl_out = 'ctrl_' + ctrl_out
        os.system(f'hisat2 -f -x {wd}/index/genome -U {arg.ctrl}/{ctrl_file} -S {wd}/{ctrl_out}_output.sam')

    for exp_file in os.listdir(arg.exp):
        exp_out = rm_suffix(exp_file)
        exp_out = 'exp_' + exp_out
        os.system(f'hisat2 -f -x {wd}/index/genome -U {arg.exp}/{ctrl_file} -S {wd}/{exp_out}_output.sam')

else: sys.exit('Error: not a valid aligner. Valid aligners "bt2" "ht2"')

########################
### running samtools ###
########################

for ctrl_file in os.listdir(arg.ctrl):
    ctrl_out = rm_suffix(ctrl_file)
    ctrl_out = 'ctrl_' + ctrl_out
    os.system(f'samtools view -bS {wd}/{ctrl_out}_output.sam | samtools sort -o {wd}/{ctrl_out}_sorted.bam')
    
    if arg.peakcaller == 'spp': os.system(f'samtools index {wd}/{ctrl_out}_sorted.bam')

for exp_file in os.listdir(arg.exp):
    exp_out = rm_suffix(exp_file)
    exp_out = 'exp_' + exp_out
    os.system(f'samtools view -bS {wd}/{exp_out}_output.sam | samtools sort -o {wd}/{exp_out}_sorted.bam')

    if arg.peakcaller == 'spp': os.system(f'samtools index {wd}/{exp_out}_sorted.bam')

########################
### running bedtools ###
########################
'''
Note: This runs only when using spp peakcaller.
Bam is converted to tagAlign using bedtools.
'''

if arg.peakcaller == 'spp':
    awk_command = """awk 'BEGIN{OFS="\\t"} {print $1, $2, $3, "N", "1000", $6}'"""

    for ctrl_file in os.listdir(arg.ctrl):
        ctrl_out = rm_suffix(ctrl_file)
        ctrl_out = 'ctrl_' + ctrl_out

        os.system(f"bedtools bamtobed -i {wd}/{ctrl_out}_sorted.bam | {awk_command} > {wd}/{ctrl_out}.tagAlign")

    for exp_file in os.listdir(arg.exp):
        exp_out = rm_suffix(exp_file)
        exp_out = 'exp_' + exp_out

        os.system(f"bedtools bamtobed -i {wd}/{exp_out}_sorted.bam | {awk_command} > {wd}/{exp_out}.tagAlign")


#####################
### running homer ###
#####################

if arg.peakcaller == 'homer':
    i = 0 # used to track first run

    for ctrl_file in os.listdir(arg.ctrl):
        ctrl_out = rm_suffix(ctrl_file)
        ctrl_out = 'ctrl_' + ctrl_out

        os.system(f'makeTagDirectory {wd}/{ctrl_out}_tag_dir {wd}/{ctrl_out}_sorted.bam')

        for exp_file in os.listdir(arg.exp):
            exp_out = rm_suffix(exp_file)
            exp_out = 'exp_' + exp_out
            
            # ensures these files are only made once
            if i == 0: os.system(f'makeTagDirectory {wd}/{exp_out}_tag_dir {wd}/{exp_out}_sorted.bam')
                
            os.system(f'findPeaks {wd}/{exp_out}_tag_dir -i {wd}/{ctrl_out}_tag_dir -fdr {arg.fdr} > {wd}/homer_{exp_out}_{ctrl_out}.txt')
            
        i += 1

    os.system(f'rm -rf {wd}/outputs')
    os.system(f'mkdir {wd}/outputs')
    os.system(f'mv {wd}/homer* {wd}/outputs')

###################
### running spp ###
###################
elif arg.peakcaller == 'spp':
    for ctrl_file in os.listdir(arg.ctrl):
        ctrl_out = rm_suffix(ctrl_file)
        ctrl_out = 'ctrl_' + ctrl_out

        for exp_file in os.listdir(arg.exp):
            exp_out = rm_suffix(exp_file)
            exp_out = 'exp_' + exp_out
            os.system(f'Rscript spp.R {wd}/{exp_out}.tagAlign {wd}/{ctrl_out}.tagAlign {arg.fdr} > {wd}/spp_{exp_out}_{ctrl_out}.txt')
    
    os.system(f'rm -rf {wd}/outputs')
    os.system(f'mkdir {wd}/outputs')
    os.system(f'mv {wd}/spp* {wd}/outputs')

else: sys.exit('Error: not a valid peakcaller. Valid peakcallers "homer" "spp"')

#######################
### sorting outputs ###
#######################

print('SORTING NOW')
os.system(f'touch {wd}/output_summary.txt')
with open(f'{wd}/output_summary.txt', 'w') as out:
    for file in os.listdir(f'{wd}/outputs'):
        exp = ''
        ctrl = ''
        peaks = ''

        with open(f'{wd}/outputs/{file}', 'r') as fp:
            if arg.peakcaller == 'homer':
                for line in fp:
                    line = line.strip()
                    if line.find('# tag ') != -1: exp = line[line.find('=')+2:]
                    elif line.find('# total') != -1: peaks = line[2:]
                    elif line.find('# input') != -1: ctrl = line[line.find('=')+2:]
                    if exp != '' and ctrl != '' and peaks != '': break

            results_section = False
            if arg.peakcaller == 'spp':
                for line in fp:
                    line = line.strip()
                    if line.find('exp') != -1:
                        line = line.split()
                        exp = line[1]
                        continue
                    if line.find('ctrl') != -1:
                        line = line.split()
                        ctrl = line[1]
                        continue
                    if line == '': continue
                    if line.find('results') == -1 and results_section == False: continue
                    results_section = True
                    line = line.split()
                    peaks = line[0]

            out.write(f'Experiment: {exp}\n')
            out.write(f'Control: {ctrl}\n')
            if peaks.find('peaks') != -1 or peaks.find('Peaks') != -1: out.write(f'{peaks}\n\n')
            else: out.write(f'Peaks: {peaks}\n\n')
