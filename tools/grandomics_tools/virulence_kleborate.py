#!/usr/bin/env python
# coding=utf-8
import sys,re,os,time,gzip,json,csv
import argparse
import subprocess as sb
import logging
logging.basicConfig(level = logging.INFO,filename="virulence_kleborate.log",filemode="w",format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("virulence detction:")

def get_opt():
	USAGE='''
	输入组装结果
		单样本
		virulence_kleborate.py --data_type contig --assembly_fasta $assembly_fasta
		多样本
		virulence_kleborate.py --data_type contig --assembly_fasta $assembly_fasta_1,$assembly_fasta_2,$assembly_fasta_3
	输入测序reads
		二代数据
		virulence_kleborate.py --data_type read --sequencing_platform ngs --ngs_r1 $R1 --ngs_r2 $R2 --prefix $prefix
		virulence_kleborate.py --data_type read --sequencing_platform ngs --ngs_r1 $R1_1,$R1_2,$R1_3 --ngs_r2 $R2_1,$R2_2,$R2_3 --prefix $prefix_1,$prefix_2,$prefix_3
		ONT数据
		virulence_kleborate.py --data_type read --sequencing_platform ont --ont_fastq $fastq --prefix $prefix
		virulence_kleborate.py --data_type read --sequencing_platform ont --ont_fastq $fastq_1,$fastq_2,$fastq_3 --prefix $prefix_1,$prefix_2,$prefix_3
		ngs+ont混合数据
		virulence_kleborate.py --data_type read --sequencing_platform hybrid --ngs_r1 $R1 --ngs_r2 $R2 --ont_fastq $fastq --prefix $prefix
		virulence_kleborate.py --data_type read --sequencing_platform hybrid --ngs_r1 $R1_1,$R1_2,$R1_3 --ngs_r2 $R2_1,$R2_2,$R2_3 --ont_fastq $fastq_1,$fastq_2,$fastq_3 --prefix $prefix_1,$prefix_2,$prefix_3
	
	参数说明
		prefix为样本名称，最后展示在分析结果中
		组装的数据不需要prefix，测序数据必须输入prefix。
	'''
	parser = argparse.ArgumentParser(description='肺炎克雷伯杆菌耐药和毒力分析流程', usage=USAGE)
	parser.add_argument('--data_type', dest="data_type", type=str.lower, choices=['contig','read'], required=True,help='')
	parser.add_argument('--assembly_fasta', dest='assembly_fasta', required=False, help='')
	parser.add_argument('--sequencing_platform', dest="sequencing_platform", type=str.lower, choices=['ont','ngs','hybrid'], required=False,help='')
	parser.add_argument('--ont_fastq', dest='ont_fastq', required=False, help='')
	parser.add_argument('--ngs_r1', dest='ngs_r1', required=False, help='')
	parser.add_argument('--ngs_r2', dest='ngs_r2', required=False, help='')
	parser.add_argument('--prefix', dest='prefix', required=False, default = "out", help='')
	parser.add_argument('--outdir', dest='outdir', required=False, default = ".", help='')
	parser.add_argument('--thread', dest='thread', default = 6, help='set the threads for analysis[6]')
	opt = parser.parse_args()
	return opt
				
def ont_assembly(ont_fastq, prefix, outdir, thread):
	
	contig_list = []
	fq_list = ont_fastq.strip().split(",")
	prefix_list = prefix.strip().split(",")
	if len(fq_list) == len(prefix_list):
		logger.info("开始ONT数据组装")
	else:
		logger.error("输入的ONT数据和prefix数目不一致")
		
	for fq in fq_list:
		pfix = prefix_list[fq_list.index(fq)]
		od = outdir+"/"+pfix
		os.system("mkdir -p %s" %od)
		cmd_ont = "unicycler -l {fq} --min_fasta_length 300 -o {od} --keep 0 -t {thread} > {od}/run_unicycler.log".format(fq=fq,od=od,thread=thread)
		status,output = sb.getstatusoutput(cmd_ont)
		os.system("mv {od}/assembly.fasta {od}/{pfix}.fasta".format(od=od,pfix=pfix))
		contig_list.append("{od}/{pfix}.fasta".format(od=od,pfix=pfix))
		
	return contig_list
	
def ngs_assembly(ngs_r1, ngs_r2, prefix, outdir, thread):
	
	contig_list = []
	r1_list = ngs_r1.strip().split(",")
	r2_list = ngs_r2.strip().split(",")
	prefix_list = prefix.strip().split(",")
	if len(r1_list) == len(r2_list) == len(prefix_list):
		logger.info("开始ngs数据的组装")
	else:
		logger.error("输入的r1、r2和prefix数目不一致")
		
	for R1 in r1_list:
		index = r1_list.index(R1)
		R2 = r2_list[index]
		pfix = prefix_list[index]
		od = outdir+"/"+pfix
		os.system("mkdir -p %s" %od)
		cmd_ngs = "unicycler -1 {R1} -2 {R2} --min_fasta_length 300 -o {od} --keep 0 -t {thread} > {od}/run_unicycler.log".format(R1=R1,R2=R2,od=od,thread=thread)
		status,output = sb.getstatusoutput(cmd_ngs)
		os.system("mv {od}/assembly.fasta {od}/{pfix}.fasta".format(od=od,pfix=pfix))
		contig_list.append("{od}/{pfix}.fasta".format(od=od,pfix=pfix))
	
	return contig_list
	
def hybrid_assembly(ngs_r1, ngs_r2, ont_fastq, prefix, outdir, thread):
	
	contig_list = []
	r1_list = ngs_r1.strip().split(",")
	r2_list = ngs_r2.strip().split(",")
	fq_list = ont_fastq.strip().split(",")
	prefix_list = prefix.strip().split(",")
	if len(r1_list) == len(r2_list) == len(fq_list) == len(prefix_list):
		logger.info("开始ngs+ont数据的混合组装")
	else:
		logger.error("输入的r1、r2、ont fastq和prefix数目不一致")
		
	for R1 in r1_list:
		index = r1_list.index(R1)
		R2 = r2_list[index]
		fq = fq_list[index]
		pfix = prefix_list[index]
		od = outdir+"/"+pfix
		os.system("mkdir -p %s" %od)
		cmd_hybrid = "unicycler -1 {R1} -2 {R2} -l {fq} --min_fasta_length 300 -o {od} --keep 0 -t {thread} > {od}/run_unicycler.log".format(R1=R1,R2=R2,fq=fq,od=od,thread=thread)
		status,output = sb.getstatusoutput(cmd_hybrid)
		os.system("mv {od}/assembly.fasta {od}/{pfix}.fasta".format(od=od,pfix=pfix))
		contig_list.append("{od}/{pfix}.fasta".format(od=od,pfix=pfix))
		
	return contig_list
	
def run_kleborate(assembly_fasta, outdir):
	
	cmd_kleborate = "kleborate --all -o {outdir}/Kleborate_results.txt -a {assembly_fasta} > {outdir}/kleborate.log".format(assembly_fasta=assembly_fasta,outdir=outdir)
	status,output = sb.getstatusoutput(cmd_kleborate)
	
def check_ngs_suffix(r1,r2):
	if re.search("fastq|fq|fastq.gz|fq.gz$",r1) and re.search("fastq|fq|fastq.gz|fq.gz$",r2):
		R1 = r1
		R2 = r2
	else:
		if re.search(".gz$",r1):
			R1 = "./{basename}.fastq.gz".format(basename=os.path.basename(r1))
			os.system("cp %s %s" %(r1, R1))
		else:
			R1 = "./{basename}.fastq".format(basename=os.path.basename(r1))
			os.system("cp %s %s" %(r1, R1))
			
		if re.search(".gz$",r2):
			R2 = "./{basename}.fastq.gz".format(basename=os.path.basename(r2))
			os.system("cp %s %s" %(r2, R2))
		else:
			R2 = "./{basename}.fastq".format(basename=os.path.basename(r2))
			os.system("cp %s %s" %(r2, R2))
	return R1,R2
	
	
if __name__ == '__main__':
	
	opt = get_opt()
	os.system("mkdir -p %s" %(opt.outdir))
	prefix = opt.prefix.split(" ")[0].strip('"')
	
	if opt.data_type == "contig":
		logger.info("使用组装数据进行分析")
		run_kleborate(opt.assembly_fasta, opt.outdir)
	if opt.data_type == "read":
		# logger.info("使用测序数据进行分析")
		if opt.sequencing_platform == "ont":
			if not opt.ont_fastq:
				logger.error("请指定ont的fastq文件")
			logger.info("使用ont测序数据进行分析")
			contig_list = ont_assembly(opt.ont_fastq, prefix, opt.outdir, opt.thread)
			
		if opt.sequencing_platform == "ngs":
			logger.info("使用ngs测序数据进行分析")
			if not opt.ngs_r1:
				logger.error("请指定ngs的R1文件")
			if not opt.ngs_r2:
				logger.error("请指定ngs的R2	文件")
			R1,R2 = check_ngs_suffix(opt.ngs_r1, opt.ngs_r2)
			contig_list = ngs_assembly(R1, R2, prefix, opt.outdir, opt.thread)
			
		if opt.sequencing_platform == "hybrid":
			logger.info("使用ngs+ont测序数据进行分析")
			if not opt.ngs_r1:
				logger.error("请指定ngs的R1文件")
			if not opt.ngs_r2:
				logger.error("请指定ngs的R2	文件")
			if not opt.ont_fastq:
				logger.error("请指定ont的fastq文件")
			R1,R2 = check_ngs_suffix(opt.ngs_r1, opt.ngs_r2)
			contig_list = hybrid_assembly(R1, R2, opt.ont_fastq, prefix, opt.outdir, opt.thread)
			
		assembly_fasta = (",").join(contig_list)
		run_kleborate(assembly_fasta, opt.outdir)