#!/usr/bin/env python
# coding: utf-8
# Author: zhangsiwen@grandomics.com, 20200317

import os
import argparse

def GetArgs():
    parser = argparse.ArgumentParser(description='Obtain mapping start and end position and draw a plot.')
    parser.add_argument('--bam', dest='bam', help='sample.bam', required=True) 
    parser.add_argument('--infection', dest='infection', help='infection_detector.py output file', required=True)
    parser.add_argument('--out', dest='out', help='output name', required=True)
    args = parser.parse_args()
    return args

def check_infection(bam, infection, out):
    result = open(infection)
    for line in result:
        if "#" not in line:
            print(out+"\t"+line.strip())
            stat = line.strip().split("\t")[-1]
            if stat=="True":
                os.system("ln -s "+bam+" ./outputs/"+out+".bam") 

def main():
    args = GetArgs()
    bam, infection, out = args.bam, args.infection, args.out
    check_infection(bam, infection, out)


if __name__=="__main__":
    main()

