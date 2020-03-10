#!/usr/bin/python3
# coding: utf-8

"""
基于mosdepth结果的数据整合及展示
"""

__author__ = 'Jin hongshuai'
__email__ = 'jinhongshuai@grandomics.com'
__version__ = '0.0.1'
__status__ = 'Dev'

import sys,os,re,time,gzip,json
import argparse
import collections
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import subprocess as sb

#plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class DepthCoverageStat(object):
	
	def __init__(self):
		#self.thread = 4
		self.thresholds = (",").join([str(n) for n in range(1001)]) ##0,1,2,3...999,1000
		
	def get_args(self):

		parser = argparse.ArgumentParser(description='Depth and coverage stat of bam')
		parser.add_argument('-i', '--input_bam', metavar="input_bam", help='bam file')
		parser.add_argument('-b', '--bed', metavar="bed", help='bed file with primer pos.')
		parser.add_argument('-t', '--thread', metavar="thread", default=4, help='path of mosdepth output dir.')
		parser.add_argument('-T', '--thresholds', metavar="thresholds", help="for each interval in --bed, write number of bases covered by at least threshold bases. Specify multiple integer values separated by ','.")
		parser.add_argument('-p', '--prefix', metavar="prefix", default="output", help='prefix of output file, general sample name')
		parser.add_argument('-c', '--coverage_png', metavar="coverage_png",default="coverage", help='output coverage_png')
		parser.add_argument('-d', '--depth_png', metavar="depth_png", default="depth",help='output depth_png')
		opt = parser.parse_args()
		
		self.input_bam = opt.input_bam
		self.bed = opt.bed
		self.thread = opt.thread
		self.prefix = opt.prefix
		if opt.thresholds:
			self.thresholds = opt.thresholds  
		self.coverage_png = opt.coverage_png
		self.depth_png = opt.depth_png
		
	def run_mosdepth(self):
		status,output = sb.getstatusoutput ("mosdepth --by {bed} -t {thread} -T {thresholds} {prefix} {bam}".format(bed=self.bed,thread=self.thread,thresholds=self.thresholds,prefix=self.prefix,bam=self.input_bam))
		
	def process_data(self):
		per_base = self.prefix+".per-base.bed.gz"
		regions_depth = self.prefix+".regions.bed.gz"
		thresholds_cov = self.prefix+".thresholds.bed.gz"
		coverage_genome = self.prefix+".mosdepth.global.dist.txt"
		coverage_bed = self.prefix+".mosdepth.region.dist.txt"
		
		df = pd.read_table(thresholds_cov, sep="\t", compression='gzip')
		bed_length = df["end"]-df["start"] ##每个区间长度的二维数据框
		#title = np.array(df[1:2]).tolist()[0] ##二维数据框将第2行转为list
		title = list(df) ##将header转为list #chrom  start   end     region  0X ...
		series_list=[]
		for coverage_thresholds in title[4:]:
			series = df[coverage_thresholds]/bed_length
			series_list.append(series)
			
		df_percent = pd.concat(series_list,axis=1)
		df_percent.columns = title[4:]
		
		df_genome = pd.read_table(coverage_genome, sep="\t", header=None)
		df_genome_plot = df_genome[(df_genome[0] == "total") & (df_genome[1] <= 1000)]
		
		df_bed = pd.read_table(coverage_genome, sep="\t", header=None)
		df_bed_plot = df_bed[(df_bed[0] == "total") & (df_bed[1] <= 1000)]
		
		df_pre_base = pd.read_table(per_base,sep="\t",header=None,compression="gzip")
		#df_pre_base_plot = df_pre_base_plot.loc[df_pre_base_plot[3]>1000,3] = 1000 ##深度大于1000的位点取1000
	
		self.df_percent = df_percent
		self.df_genome_plot = df_genome_plot
		self.df_bed_plot = df_bed_plot
		self.df_pre_base_plot = df_pre_base
		
	def plot(self):
		##coverage
		plt.figure(figsize=(16,8))
		dict_cov = dict(collections.OrderedDict(zip(self.df_genome_plot.iloc[:,1],self.df_genome_plot.iloc[:,2])))
		for n in range(int(self.thresholds.split(",")[-1])+1):
			if n not in dict_cov:
				dict_cov[n]=dict_cov[n-1]

		plt.bar(sorted(dict_cov,key=int),[dict_cov[n] for n in sorted(dict_cov,key=int)],color="grey")
		plt.ylabel("Coverage (%)")
		plt.yticks([(n)/10.0 for n in range(0,11,2)],[(n)*10 for n in range(0,11,2)],fontsize=10)
		plt.xlabel("Depth (X)")
		#plt.savefig("/opt/galaxy/tools/grandomics_tools/tt.coverage.pdf",dpi=100)
		plt.savefig(self.coverage_png, format="png", dpi=80)
		##depth
		plt.figure(figsize=(20,6))
		self.df_pre_base_plot.loc[self.df_pre_base_plot[3]>1000,3] = 1000 ##深度大于1000的位点取1000
		plt.bar(self.df_pre_base_plot[2],self.df_pre_base_plot[3],color="blue")
		plt.ylabel("Depth",fontsize=16)
		old_ticks = [n for n in range(0,1001,100)]
		new_ticks = [str(n)+"X" for n in range(0,1000,100)]
		new_ticks.append(">1000X")
		plt.yticks(old_ticks,new_ticks,fontsize=14)
		plt.xlabel("Coordinate",fontsize=16)
		#plt.savefig("/opt/galaxy/tools/grandomics_tools/tt.depth.pdf",dpi=100)
		plt.savefig(self.depth_png, format="png", dpi=80)
		
	def run(self):
		self.get_args()
		self.run_mosdepth()
		self.process_data()
		self.plot()
		
if __name__ == '__main__':
	runStat = DepthCoverageStat()
	runStat.run()
