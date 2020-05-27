#!/usr/bin/env python
# coding: utf-8

import sys,re,os
import argparse
import subprocess as sb

def get_args():
	parser = argparse.ArgumentParser(description='filter SNVs from medaka vcf')
	parser.add_argument('--raw_vcf',  metavar='raw_vcf', help='set the input raw vcf ,must be the result of medaka snp')
	parser.add_argument('--ref_prob', metavar='ref_prob', default = 0.06, help='set the max ref_prob of variation[0.06]')
	parser.add_argument('--qual', metavar='qual', default = 17, help='set the  min qual of variation[17]')
	parser.add_argument('--min_depth', metavar='min_depth', default = 15, help='set the min depth[15]')
	parser.add_argument('--frequence', metavar='frequence', default = 0.6, help='set the min frequence[0.6]')
	parser.add_argument('--out_vcf',   metavar='out_vcf' , help='set the output vcf')
	parser.add_argument('--bam',  metavar='bam' , help='set the bam with path')
	parser.add_argument('--samtools',  metavar='samtools', default = "samtools" , help='set the samtools with path')
	opt = parser.parse_args()
	return opt

def count_base(seq):
	while len(seq) > 0:
		if seq[0] in ["+","-"]:
			num = int(seq[1])
			n = 2+num
		else:
			n = 1
		yield seq[0:n]
		seq = seq[n:]

		count_base(seq)

def filter(raw_vcf,out_vcf,ref_prob,qual,bam,samtools,min_depth,frequence):

	fo=open(out_vcf,"w")
	for line in open(raw_vcf):
		line = line.strip()
		if line[0:2] == "##":
			fo.write(line+"\n")
			continue
		if line[0:2] == "#C":
			# fo.write('##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">\n')
			# fo.write('##FORMAT=<ID=AD,Number=1,Type=Integer,Description="Alleles Depth">\n')
			fo.write(line+"\n")
			continue
			
		arr = line.split("\t")
		CHROM,POS,ID,REF,ALT,QUAL,FILTER,INFO,FORMAT,SAMPLE = arr
		RefProb=re.findall("ref_prob=(.+?);",INFO)[0]
		if float(RefProb) > float(ref_prob) or float(QUAL) < float(qual): ##filter 默认0.06、17
			continue
		#DP = os.popen("{samtools} depth -r {chrom}:{pos}-{pos} {bam}".format(samtools=samtools,chrom=CHROM,pos=POS,bam=bam)).read().split()[2]
		status,output = sb.getstatusoutput("{samtools} mpileup -Q 0 -d 10000000 -r {chrom}:{pos}-{pos} {bam}".format(samtools=samtools,chrom=CHROM,pos=POS,bam=bam))
		DP,math_info = output.split("\n")[-1].split()[3:5]
		
		if int(DP) < int(min_depth): ## filter low depth，默认15X
			continue
		
		dictbase = {}
		for base in count_base(math_info):## count bases mapped in POS
			BASE = base.upper()
			if BASE not in dictbase:
				dictbase[BASE] = 0
			dictbase[BASE] += 1
		
		if re.search(",",ALT): ## 跳过多alt位点
			continue
		AD = str(dictbase[ALT])
		AF = "%.4f"%(float(AD)/int(DP))
		if float(AF) < float(frequence): ##过滤低频位点，默认0.75
			continue
		'''
		AD_list = []
		for alt in ALT.split(","):
			AD_list.append(str(dictbase[alt]))
		AD = (",").join(AD_list)
		new_FORMAT = "GT:GQ:DP:AD"
		new_SAMPLE = SAMPLE+":"+str(DP)+":"+AD
		'''
		if int(DP) >= 30 and float(AF) >=0.8: #过滤条件一
			fo.write(("\t").join(arr[0:8])+"\t"+FORMAT+"\t"+SAMPLE+"\n")
			continue
		if float(RefProb) <= 0.01 and float(QUAL)>=28:#过滤条件二
			fo.write(("\t").join(arr[0:8])+"\t"+FORMAT+"\t"+SAMPLE+"\n")
			continue
	fo.close()
	
if __name__ == '__main__':
	
	opt=get_args()
	os.system("samtools index %s"%opt.bam)
	filter(opt.raw_vcf,opt.out_vcf,opt.ref_prob,opt.qual,opt.bam,opt.samtools,opt.min_depth,opt.frequence)
