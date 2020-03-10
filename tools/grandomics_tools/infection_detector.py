#!/usr/bin/env python

"""

Infection Detector Base on Genome Coverage Rate With Fixed Depth Using Amplicon Sequencing

Author: Xin Wu

GrandOmics Copyright 2020

Usage: 
    infection_detector.py  [-x depth] [-c coverage] [-t thresholds]  GENOME_BED BAM_FILE OUT_FILE

Infector Detector is a script for detecting infection or not based on genome coverage under fixed depth with amplicon sequencing data.

Arguments:
    GENOME_BED        input genome range file in BED format
    BAM_FILE          input mapping file in BAM format
    OUT_FILE          output file in TSV format

Options:
    -h --help                      Print help
    -x --depth=depth               Criteria of depth for positive detection [default: 100]
    -c --coverage=coverage         Criteria of coverage rate for positive detection (if real coverage is equal or above) [default: 0.6] 
    -t --thresholds=thresholds     Thresholds of depth should be reported, seperated by comma [default: 1,10,50,100,200,500,1000]
    -v --version                   Version

"""

from docopt import docopt
import pandas as pd
import subprocess
import os, logging

def main(depth: int, coverage: float, thresholds: list, genome_bed: str, bam_file: str, out_file: str):
    #print(depth, coverage, thresholds, genome_bed, bam_file, out_file) 
    basename = os.path.basename(os.path.splitext(bam_file)[0]) 
    thre = ','.join([str(i) for i in thresholds])

    # first index bam
    cmd = 'samtools index {bam}'.format(bam=bam_file)
    logger.info(cmd)
    process = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    logger.info(process.stdout)

    # then call mosdepth
    cmd = 'mosdepth -x --by {bed} --thresholds {thre} {base} {bam}'.format(bed=genome_bed, 
                                                                           thre=thre,
                                                                           base=basename,
                                                                           bam=bam_file)
    logger.info(cmd)
    process = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    logger.info(process.stdout)
    # mosdepth will generate <basename>.thresholds.bed.gz under the current working directory
    bed_file = '.'.join([basename,'thresholds.bed.gz'])
    df = pd.read_csv(bed_file, compression='gzip', sep='\t')
    # suppose we have only one row of whole genome line
    # in genome row, end is the size of the genome as below
    # #chrom  start   end     region  100X
    # MN994467.1      1       29882   whole_genome    17682 
    genome_size = int(df['end'][0])
    logger.info('genome size: {size}'.format(size=str(genome_size)))
    
    # header of depth should be like: 100X in which 100 is the depth and X means depth
    depth_header = str(depth) + 'X'     
    #real_coverage_size = df[depth_header][0]
    # keep 4 decimals like 0.1234 which is 12.34%
    #real_coverage = round(float(real_coverage_size/genome_size),4)

    # default postive is False
    positive = False

    #if real_coverage >= coverage:
    #    positive = True 

    # modify the data frame for output
    for thre in thresholds:
        # header shold be like 10X, etc
        cov_size = df[str(thre)+'X'][0]
        # replace it with ratio
        ratio = round(float(cov_size/genome_size),4)
        df.loc[0,str(thre)+'X'] = ratio 
        # check the depth set by user
        if thre == depth and df[str(thre)+'X'][0] >= coverage:
             positive = True

    # add asterisk * to the end of the header name of depth set by user, like 100X -> 100X*
    df = df.rename(columns = {depth_header: depth_header + '*'})
    # add positive column to data frame
    df['positive'] = [positive]

    # output df
    logger.info(df)
    df.to_csv(out_file, index=None, sep='\t')

    

if __name__ == '__main__':
    args = docopt(__doc__, version='infection_detector version 0.1')
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('detector')
    logger.info(args)
   
    genome_bed = args['GENOME_BED']
    bam_file = args['BAM_FILE']
    out_file = args['OUT_FILE']
    depth= int(args['--depth'])
    coverage= float(args['--coverage'])
    # a set of int, split arg by ',' and strip
    thresholds= set([int(i.strip()) for i in args['--thresholds'].split(',')])
    # add depth to the thresholds set
    thresholds.add(depth)
    # convert set to list
    thresholds = list(thresholds)
    thresholds.sort()
    main(depth, coverage, thresholds, genome_bed, bam_file, out_file)
    
