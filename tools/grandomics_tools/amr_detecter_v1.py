#!/usr/bin/env python
# coding=utf-8
import sys,re,os,time,gzip,json,csv
import argparse
import subprocess as sb
from multiprocessing import Pool
import logging
logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
 

class ont_amr_detecter(object):
	'''
	
	'''
	def __init__(self):
		self.thread = 6
		self.gene_mapping_data_tab = ""
		self.bam = ""
		
	def get_opt(self):
		USAGE='''
		
		
		'''
		parser = argparse.ArgumentParser(description='nanopore reads analysis amr pipline', usage=USAGE)
		parser.add_argument('--ref',  metavar='ref', help='set the ref database of amr')
		parser.add_argument('--fastq', metavar='fastq', help='set the input fastq')
		parser.add_argument('--thread', metavar='thread', default = 6, help='set the threads for analysis[6]')
		parser.add_argument('--prefix', metavar='prefix', default = "out", help='set the prefix of output files[out]')
		parser.add_argument('--card', metavar='card',  help='path of card.json')
		parser.add_argument('--bam',   metavar='bam' , help='bam')
		# parser.add_argument('--bam',  metavar='bam' , help='set the bam with path')
		# parser.add_argument('--samtools',  metavar='samtools', default = "samtools" , help='set the samtools with path')
		opt = parser.parse_args()
		
		self.ref = opt.ref
		self.fastq = opt.fastq
		self.thread = opt.thread
		# self.bed = opt.bed
		self.card = opt.card
		self.prefix = opt.prefix
		if opt.bam:
			self.bam=opt.bam
		self.gene_mapping_data_tab = self.prefix+".txt"
		self.results = self.prefix+".amr.tsv"
		
	def make_bed(self):
		fo = open(self.prefix+".bed","w")
		for line in open(self.ref):
			line=line.strip()
			if line[0] == ">":
				name=line.split()[0].strip(">")
			else:
				l=len(line)
				fo.write(name+"\t0\t"+str(l)+"\n")
		fo.close()
		self.bed = self.prefix+".bed"
		
	def get_identity(self, seqs_info_txt):
		"""
		Parse tab-delimited file into dictionary for mapped reads
		"""
		dict_identity = {}
		dict_average_identity = {}
		dict_gene_len = {}
		dict_span_reads = {}
		
		for line in open(self.idxstats_summary,"r"):
			arr=line.strip().split("\t")
			gene_name = arr[0]
			gene_len = arr[1]
			dict_gene_len[gene_name] = gene_len
		
		for line in open(seqs_info_txt, 'r'):
			qname,flag,seq_name,start,mapq,cigar = line.strip().split("\t")
			# mapq = int(mapq)
			if seq_name == "*":
				continue
			
			match_length_list = re.findall('(\d+?)\D',cigar)
			if re.search('(^\d+?)S',cigar):
				left_softclip_len = match_length_list.pop(0)
			if re.search('(\d+?)S$',cigar):##删除头尾softclip的数值
				right_softclip_len = match_length_list.pop(-1)
			match_length = sum(list(map(int,match_length_list)))##将list中的元素全部装换为int格式
			
			match_base_list = re.findall('(\d+?)M',cigar)
			match_base = sum(list(map(int,match_base_list)))
			
			identity = 100*match_base/match_length
			
			if seq_name not in dict_identity:
				dict_identity[seq_name] = []
			dict_identity[seq_name].append(identity)
			
			##鉴定span reads
			del_length = sum(list(map(int,re.findall('(\d+?)D',cigar))))
			cov_len = del_length + match_base ##match上的碱基数+del的碱基数大概等于参考基因序列的长度
			gene_length = dict_gene_len[seq_name]
			
			if seq_name not in dict_span_reads:
				dict_span_reads[seq_name] = {"span":[], "complete":[]}
				
			if int(gene_length) - int(cov_len) < 50 and int(left_softclip_len) > 20 and int(right_softclip_len) > 20:##reads覆盖的长度与基因长度相差50bp，并且reads两端都有10bp以上的softclip就认为是span reads
				dict_span_reads[seq_name]["span"].append(qname)
			if int(left_softclip_len) <= 20 and int(right_softclip_len) <= 20:#两端的softclip都小于20bp认为是完全比对上的reads
				dict_span_reads[seq_name]["complete"].append(qname)
				
		for name,identity_list in dict_identity.items():
			dict_average_identity[name] = "%.2f" %(sum(identity_list)/len(identity_list))
		
		return dict_average_identity,dict_span_reads
			
	def pre_analysis(self):
		
		##minimap2 alignment
		cmd_map = "minimap2 -x map-ont --MD -Y -a -t {thread} {card_ref} {input_fq}| samtools view -S -b -h -F 4 -q 60 - |samtools sort -T temp -o {prefix}.bam - && samtools index {prefix}.bam".format(thread=self.thread,card_ref=self.ref,input_fq=self.fastq,prefix=self.prefix)
		if self.bam == "":
			status1,output1 = sb.getstatusoutput(cmd_map)
			
		##samtools idxstats 结果为四列，分别是：序列名字，序列长度，比对上的reads数，未比对上的reads数（此列主要针对NGS PE数据，ONT数据此列为0）
		cmd_stat = "samtools idxstats {prefix}.bam > {prefix}.idxstats".format(prefix=self.prefix)
		status2,output2 = sb.getstatusoutput(cmd_stat)
		
		##筛选出比对reads>0的序列
		cmd_filter = "awk '{if ($3>0){print $0}}' %s.idxstats > %s.idxstats.summary"%(self.prefix,self.prefix)
		status3,output3 = sb.getstatusoutput(cmd_filter)
		self.idxstats_summary = "%s.idxstats.summary" %(self.prefix)
		
		##获取bam文件前5列
		cmd_cigar = "samtools view {prefix}.bam | cut -f 1,2,3,4,5,6 | sort -k 3,3 > {prefix}.seqs.info.txt".format(prefix=self.prefix)
		status5,output5 = sb.getstatusoutput(cmd_cigar)
		#self.seqs_info_txt = "%s.seqs.info.txt" %(self.prefix)
		##返回比对到每条系列上reads的平均比对质量
		self.average_identity, self.span_reads = self.get_identity("%s.seqs.info.txt" %(self.prefix))
		
		##mosdepth bed文件格式：序列名称，1，序列长度
		self.make_bed()
		cmd_cov = "mosdepth --by {bed} -t {thread} -T 0,1,2,3,4,5,10,20,30,40,50,100,200,300,400,500,1000 {prefix} {prefix}.bam".format(bed=self.bed,thread=self.thread,prefix=self.prefix)
		status4,output4 = sb.getstatusoutput(cmd_cov)
		self.coverage = "%s.mosdepth.region.dist.txt" %(self.prefix)
		
	def get_alignments_gene(self):
		
		dict_amr_gene = {}
		for line in open(self.idxstats_summary):
			seq_name,seq_len,mapped_reads_num,unmapped_reads_num = line.strip().split("\t")
			if seq_name in dict_amr_gene:
				logger.info("Error! idxstats_summary %s appear twice" %seq_name)
			dict_amr_gene[seq_name] = [mapped_reads_num] ## 序列名称：比对到序列上的reads数
		
		for line in open(self.coverage):
			name,depth,cov_percent = line.strip().split("\t")
			if depth == "0":
				if name == "total":
					continue
				if name not in dict_amr_gene:
					logger.info("Error! mosdepth.region.dist.txt %s not in idxstats_summary" %name)
				dict_amr_gene[name].append(cov_percent) ## {序列名称：[比对到序列上的reads数,序列1X的覆盖度]}
		for line in gzip.open(self.prefix+".thresholds.bed.gz","r"):
			arr=line.decode().strip().split("\t")
			chrom = arr[0]
			length = arr[2]
			cov_len = arr[4]
			if chrom == "#chrom":
				continue
			if int(cov_len) > 0:
				dict_amr_gene[chrom].append(cov_len)
				dict_amr_gene[chrom].append(length)
			#{序列名称：[比对到序列上的reads数,序列1X的覆盖度,覆盖的长度，序列长度]}
			
		
		##check dict
		for key,value in dict_amr_gene.items():
			if len(value) != 4:
				logger.debug("Error! %s mapped num and cov info error"%key)
		
		self.cov_dict = dict_amr_gene
				
	def get_model_details(self, by_accession=False):
		"""
		Parse card.json to get each model details
		"""
		models = {}
		try:
			with open(self.card, 'r') as jfile:
				data = json.load(jfile)
		except Exception as e:
			logger.error("{}".format(e))
			exit()

		for i in data:
			if i.isdigit():
				categories = {}
				taxon = []

				if "model_sequences" in data[i]:
					for item in data[i]["model_sequences"]["sequence"]:
						taxa = " ".join(data[i]["model_sequences"]["sequence"][item]["NCBI_taxonomy"]["NCBI_taxonomy_name"].split()[:2])
						if taxa not in taxon:
							taxon.append(taxa)

				for c in data[i]["ARO_category"]:
					if data[i]["ARO_category"][c]["category_aro_class_name"] not in categories.keys():
						categories[data[i]["ARO_category"][c]["category_aro_class_name"]] = []
					if data[i]["ARO_category"][c]["category_aro_name"] not in categories[data[i]["ARO_category"][c]["category_aro_class_name"]]:
						categories[data[i]["ARO_category"][c]["category_aro_class_name"]].append(data[i]["ARO_category"][c]["category_aro_name"])
						
				if by_accession == False:
					models[data[i]["model_id"]] = {
						"model_id": data[i]["model_id"],
						"ARO_accession": data[i]["ARO_accession"],						
						"model_name": data[i]["model_name"],
						"model_type": data[i]["model_type"],
						"categories": categories,
						"taxon": taxon
					}
				else:
					models[data[i]["ARO_accession"]] = {
						"model_id": data[i]["model_id"],
						"ARO_accession": data[i]["ARO_accession"],
						"model_name": data[i]["model_name"],
						"model_type": data[i]["model_type"],
						"categories": categories,
						"taxon": taxon
					}
		return models	
			
	def get_model_id(self, models_by_accession, alignment_hit):
		model_id = ""
		if alignment_hit[0:22] == "Prevalence_Sequence_ID" or alignment_hit[0:4] == "ARO:":
			model_id = alignment_hit.split("|")[1].split(":")[1]
		else:
			accession = alignment_hit.split("|")[4].split(":")[1]
			try:
				model_id = models_by_accession[accession]["model_id"]
			except Exception as e:
				logger.warning("missing aro accession: {} for alignment {} -> {}".format(accession,alignment_hit,e))
		return model_id
		
	def summary(self, alignment_hit, models, variants, baits, models_by_accession):
		
		#self.cov_dict ##{序列名称：[比对到序列上的reads数,序列1X的覆盖度]}
		# for alignment_hit in self.cov_dict:
		model_id = self.get_model_id(models_by_accession, alignment_hit)##返回ARO:3001773|ID:104|Name:OXA-61|NCBI:AY587956 中的 104
		try:
			# mapq_average = self.average_mapq[alignment_hit]
			percent_identity = self.average_identity[alignment_hit]
			span_reads_num = len(self.span_reads[alignment_hit]["span"])
			complete_mapped_reads = len(self.span_reads[alignment_hit]["complete"])
			observed_in_genomes = "no data"
			observed_in_plasmids = "no data"
			prevalence_sequence_id = ""
			observed_data_types = []
			# Genus and species level only (only get first two words)
			observed_in_pathogens = []
			database = "CARD"
			reference_allele_source = "CARD curation"
			'''
			# if variants and "Resistomes & Variants" in database and "ARO:" not in alignment_hit:
			if "Prevalence_Sequence_ID" in alignment_hit:
				database = "Resistomes & Variants"
				# logger.debug("model_id: {}, alignment_hit: {}".format(model_id, alignment_hit))
				if model_id in variants.keys():
					_accession = ""
					for s in variants[model_id]:
						prevalence_sequence_id = alignment_hit.split("|")[0].split(":")[-1]
						observed_in_genomes = "NO"
						observed_in_plasmids = "NO"

						for accession in variants[model_id][prevalence_sequence_id]:
							_accession = accession
			
							if variants[model_id][prevalence_sequence_id][accession]["data_type"] not in observed_data_types:
								observed_data_types.append(variants[model_id][prevalence_sequence_id][accession]["data_type"])

							if variants[model_id][prevalence_sequence_id][accession]["species_name"] not in observed_in_pathogens:
								observed_in_pathogens.append(variants[model_id][prevalence_sequence_id][accession]["species_name"].replace('"', ""))
					
					if "Resistomes & Variants" in database:
						if "ncbi_chromosome" in observed_data_types:
							observed_in_genomes = "YES"
						if "ncbi_plasmid" in observed_data_types:
							observed_in_plasmids = "YES"
						
						# get prevalence_sequence_id Prevalence_Sequence_ID:10687|ID:2882|Name:tet(W/N/W)|ARO:3004442
						if "Prevalence_Sequence_ID" in alignment_hit:
							prevalence_sequence_id = alignment_hit.split("|")[0].split(":")[-1]
							try:
								reference_allele_source = "In silico {rgi_criteria} {percent_identity}% identity".format(
									rgi_criteria=variants[model_id][prevalence_sequence_id][_accession]["rgi_criteria"],
									percent_identity=variants[model_id][prevalence_sequence_id][_accession]["percent_identity"],
								)
								percent_identity = float(variants[model_id][prevalence_sequence_id][_accession]["percent_identity"])
							except Exception as e:
								reference_allele_source = ""
								# logger.debug(alignment_hit)
								# logger.debug(json.dumps(alignments, indent=2))
								# logger.debug(json.dumps(variants[model_id], indent=2))
								logger.warning("missing key with Prev_id: {}, Exception: {}, Database: {} for model_id: {}".format(prevalence_sequence_id, e, database, model_id))						


				else:
					# provide info from model
					observed_in_pathogens = models[model_id]["taxon"]
			
			else:
			'''
			observed_in_pathogens = models[model_id]["taxon"]##'taxon': ['Campylobacter jejuni']
			# assumption card canonical
			# percent_identity = 100.0

			# check all clases categories
			resistomes = models[model_id]["categories"]##'categories': {'AMR Gene Family': ['OXA beta-lactamase'], 'Drug Class': ['cephalosporin', 'penam'], 'Resistance Mechanism': ['antibiotic inactivation']}
			if "AMR Gene Family" not in resistomes.keys():
				resistomes["AMR Gene Family"] = []
			if "Drug Class" not in resistomes.keys():
				resistomes["Drug Class"] = []
			if "Resistance Mechanism" not in resistomes.keys():
				resistomes["Resistance Mechanism"] = []

			# stop = time.time()
			# elapsed = stop - start
			# logger.info("time lapsed: {} - {}".format(format(elapsed,'.3f'), alignment_hit))
			# self.async_print(alignment_hit, start, stop, elapsed)
			##number_of_mapped_baits, number_of_mapped_baits_with_reads, average_bait_coverage, bait_coverage_coefficient_of_variation = self.baits_reads_counts(models[model_id]["ARO_accession"])
			number_of_mapped_baits, number_of_mapped_baits_with_reads, average_bait_coverage, bait_coverage_coefficient_of_variation = 0,0,0,0
			# logger.debug(">>> {}".format(alignment_hit))
			return {
				"id": alignment_hit,
				"cvterm_name": models[model_id]["model_name"],
				"aro_accession": models[model_id]["ARO_accession"],
				"model_type": models[model_id]["model_type"],
				"database": database,
				"reference_allele_source": reference_allele_source,
				"observed_in_genomes": observed_in_genomes,
				"observed_in_plasmids": observed_in_plasmids,
				"observed_in_pathogens": observed_in_pathogens,
				"range_of_reference_allele_source": percent_identity,
				"reads": self.cov_dict[alignment_hit][0],
				# "alignments": alignments,
				# "mapq_average": mapq_average,
				"span_reads": span_reads_num,
				"complete_mapped": complete_mapped_reads,
				"flanking_reads": (int(self.cov_dict[alignment_hit][0])-span_reads_num-complete_mapped_reads),
				"number_of_mapped_baits": number_of_mapped_baits,
				"number_of_mapped_baits_with_reads": number_of_mapped_baits_with_reads,
				"average_bait_coverage": average_bait_coverage,
				"bait_coverage_coefficient_of_variation": bait_coverage_coefficient_of_variation,
				# "mate_pair": mate_pair,
				"percent_coverage": self.cov_dict[alignment_hit][1],
				"length_coverage": self.cov_dict[alignment_hit][2],
				"reference": self.cov_dict[alignment_hit][3],
				"mutation": "N/A",
				"resistomes": resistomes
				,"predicted_pathogen": "N/A"
				}
		except Exception as e:
			logger.warning("missing model with id : {}, Exception: {}".format(model_id,e))
				
	def jobs(self, job):
		return self.summary(job[0], job[1], job[2], job[3], job[4])
				
	def get_summary(self):
		
		summary = []
		variants = {}
		baits = {}
		models = {}
	
		logger.info("get_model_details ...")
		models = self.get_model_details()
		models_by_accession = self.get_model_details(True)
		'''
		if self.include_wildcard:
			logger.info("get_variant_details ...")
			variants = self.get_variant_details()

		if self.include_baits:
			logger.info("get_baits_details ...")
			baits = self.get_baits_details()
		'''
		# mapq_average = 0

		jobs = []
		for alignment_hit in self.cov_dict:
			jobs.append((alignment_hit, models, variants, baits, models_by_accession,))
		with Pool(processes=int(self.thread)) as p:
			results = p.map_async(self.jobs, jobs)
			summary = results.get()

		# wrtie tab-delimited gene_mapping_data
		mapping_summary = {}
		alleles_mapped = []
		index = "aro_accession"
		# range_of_reference_allele_source = []
		for r in summary:
			if r:
				alleles_mapped.append(r[index])##r[index],r["aro_accession"]=3001773
				if r[index] not in mapping_summary.keys():
					mapping_summary[r[index]] = {
						"id": [],
						"cvterm_name": [],
						"aro_accession": [],
						"model_type": [],
						"database": [],
						"alleles_mapped": [],
						"range_of_reference_allele_source": [],
						"observed_in_genomes": [],
						"observed_in_plasmids": [],
						"observed_in_pathogens": [],
						"span": [],
						"complete_mapped":[],
						"flanking": [],
						"all": [],
						"percent_coverage": [],
						# "confidence":[],
						"length_coverage": [],
						# "mapq_average": [],
						"number_of_mapped_baits": [],
						"number_of_mapped_baits_with_reads": [],
						"average_bait_coverage": [],
						"bait_coverage_coefficient_of_variation": [],
						"mate_pair": [],
						"reference_sequence_length": [],
						"AMR Gene Family": [],
						"Drug Class": [],
						"Resistance Mechanism": []
					}

					mapping_summary[r[index]]["id"].append(r["id"])
					mapping_summary[r[index]]["cvterm_name"].append(r["cvterm_name"])
					mapping_summary[r[index]]["aro_accession"].append(r["aro_accession"])
					mapping_summary[r[index]]["model_type"].append(r["model_type"])
					mapping_summary[r[index]]["database"].append(r["database"])
					mapping_summary[r[index]]["observed_in_genomes"].append(r["observed_in_genomes"])
					mapping_summary[r[index]]["observed_in_plasmids"].append(r["observed_in_plasmids"])	

					for p in r["observed_in_pathogens"]:
						mapping_summary[r[index]]["observed_in_pathogens"].append(p)

					mapping_summary[r[index]]["span"].append(r["span_reads"])
					mapping_summary[r[index]]["complete_mapped"].append(r["complete_mapped"])
					mapping_summary[r[index]]["range_of_reference_allele_source"].append(r["range_of_reference_allele_source"])
					mapping_summary[r[index]]["flanking"].append(r["flanking_reads"])
					mapping_summary[r[index]]["all"].append(r["reads"])
					mapping_summary[r[index]]["percent_coverage"].append(r["percent_coverage"])
					mapping_summary[r[index]]["length_coverage"].append(r["length_coverage"])
					# mapping_summary[r[index]]["mapq_average"].append(r["mapq_average"])
					mapping_summary[r[index]]["reference_sequence_length"].append(r["reference"])
					mapping_summary[r[index]]["number_of_mapped_baits"].append(r["number_of_mapped_baits"])
					mapping_summary[r[index]]["number_of_mapped_baits_with_reads"].append(r["number_of_mapped_baits_with_reads"])
					mapping_summary[r[index]]["average_bait_coverage"].append(r["average_bait_coverage"])
					mapping_summary[r[index]]["bait_coverage_coefficient_of_variation"].append(r["bait_coverage_coefficient_of_variation"])
					
					# for m in r["mate_pair"]:
						# if m not in ["*"]:
							# arr = m.split("|")
							# if len(arr) == 4:
								# mapping_summary[r[index]]["mate_pair"].append("{}".format(m.split("|")[2].split(":")[1]))
							# elif len(arr) == 7:
								# mapping_summary[r[index]]["mate_pair"].append("{}".format(m.split("|")[5]))

					for a in r["resistomes"]["AMR Gene Family"]:
						mapping_summary[r[index]]["AMR Gene Family"].append(a)

					for d in r["resistomes"]["Drug Class"]:
						mapping_summary[r[index]]["Drug Class"].append(d)

					for c in r["resistomes"]["Resistance Mechanism"]:
						mapping_summary[r[index]]["Resistance Mechanism"].append(c)

				else:
					if r["model_type"] not in mapping_summary[r[index]]["model_type"]:
						mapping_summary[r[index]]["model_type"].append(r["model_type"])
					if r["database"] not in mapping_summary[r[index]]["database"]:
						mapping_summary[r[index]]["database"].append(r["database"])
					if r["observed_in_genomes"] not in mapping_summary[r[index]]["observed_in_genomes"]:
						mapping_summary[r[index]]["observed_in_genomes"].append(r["observed_in_genomes"])
					if r["observed_in_plasmids"] not in mapping_summary[r[index]]["observed_in_plasmids"]:
						mapping_summary[r[index]]["observed_in_plasmids"].append(r["observed_in_plasmids"])	

					for p in r["observed_in_pathogens"]:
						if p not in mapping_summary[r[index]]["observed_in_pathogens"]:
							mapping_summary[r[index]]["observed_in_pathogens"].append(p)	

					mapping_summary[r[index]]["span"].append(r["span_reads"])
					mapping_summary[r[index]]["complete_mapped"].append(r["complete_mapped"])
					mapping_summary[r[index]]["range_of_reference_allele_source"].append(r["range_of_reference_allele_source"])
					mapping_summary[r[index]]["flanking"].append(r["flanking_reads"])
					mapping_summary[r[index]]["all"].append(r["reads"])
					mapping_summary[r[index]]["percent_coverage"].append(r["percent_coverage"])
					mapping_summary[r[index]]["length_coverage"].append(r["length_coverage"])
					# mapping_summary[r[index]]["mapq_average"].append(r["mapq_average"])
					mapping_summary[r[index]]["reference_sequence_length"].append(r["reference"])
					mapping_summary[r[index]]["number_of_mapped_baits"].append(r["number_of_mapped_baits"])
					mapping_summary[r[index]]["number_of_mapped_baits_with_reads"].append(r["number_of_mapped_baits_with_reads"])
					mapping_summary[r[index]]["average_bait_coverage"].append(r["average_bait_coverage"])
					mapping_summary[r[index]]["bait_coverage_coefficient_of_variation"].append(r["bait_coverage_coefficient_of_variation"])

					# for m in r["mate_pair"]:
						# if m not in ["*"]:
							# arr = m.split("|")
							# if len(arr) == 4:
								# mapping_summary[r[index]]["mate_pair"].append("{}".format(m.split("|")[2].split(":")[1]))
							# elif len(arr) == 7:
								# mapping_summary[r[index]]["mate_pair"].append("{}".format(m.split("|")[5]))

					for a in r["resistomes"]["AMR Gene Family"]:
						if a not in mapping_summary[r[index]]["AMR Gene Family"]:
							mapping_summary[r[index]]["AMR Gene Family"].append(a)

					for d in r["resistomes"]["Drug Class"]:
						if d not in mapping_summary[r[index]]["Drug Class"]:
							mapping_summary[r[index]]["Drug Class"].append(d)

					for c in r["resistomes"]["Resistance Mechanism"]:
						if c not in mapping_summary[r[index]]["Resistance Mechanism"]:
							mapping_summary[r[index]]["Resistance Mechanism"].append(c)

		with open(self.gene_mapping_data_tab, "w") as tab_out:
			writer = csv.writer(tab_out, delimiter='\t', dialect='excel')
			writer.writerow([
							"ARO Term",
							"ARO Accession",
							"Reference Model Type",
							"Reference DB",
							"Alleles with Mapped Reads",
							"Average identity(%)",
							"Resistomes & Variants: Observed in Genome(s)",
							"Resistomes & Variants: Observed in Plasmid(s)",
							"Resistomes & Variants: Observed Pathogen(s)",
							"Span Mapped Reads",
							"Completely Mapped Reads",
							"Mapped Reads with Flanking Sequence",
							"All Mapped Reads",
							"Average Percent Coverage",
							"Average Length Coverage (bp)",
							"Confidence",
							# "Average MAPQ (Completely Mapped Reads)",
							"Number of Mapped Baits",
							"Number of Mapped Baits with Reads",
							"Average Number of reads per Bait",
							"Number of reads per Bait Coefficient of Variation (%)",
							"Number of reads mapping to baits and mapping to complete gene",
							"Number of reads mapping to baits and mapping to complete gene (%)",
							# "Mate Pair Linkage (# reads)",
							"Reference Length",
							"AMR Gene Family",
							"Drug Class",
							"Resistance Mechanism"
							])
			am = { item:alleles_mapped.count(item) for item in alleles_mapped }##alleles_mapped.append(r[index]),r[index],r["aro_accession"]=3001773

			for i in mapping_summary:
				observed_in_genomes = "NO"
				observed_in_plasmids = "NO"

				if "YES" in mapping_summary[i]["observed_in_genomes"]:
					observed_in_genomes = "YES"
				elif "no data" in mapping_summary[i]["observed_in_genomes"]:
					observed_in_genomes = "no data"

				if "YES" in mapping_summary[i]["observed_in_plasmids"]:
					observed_in_plasmids = "YES"
				elif "no data" in mapping_summary[i]["observed_in_plasmids"]:
					observed_in_plasmids = "no data"

				average_percent_coverage = 0
				average_length_coverage = 0
				# average_mapq  = 0				
		
				if len(mapping_summary[i]["percent_coverage"]) > 0:
					average_percent_coverage = sum(map(float,mapping_summary[i]["percent_coverage"]))/len(mapping_summary[i]["percent_coverage"])

				if len(mapping_summary[i]["length_coverage"]) > 0:
					average_length_coverage = sum(map(float,mapping_summary[i]["length_coverage"]))/len(mapping_summary[i]["length_coverage"])

				# if len(mapping_summary[i]["mapq_average"]) > 0:
					# average_mapq = sum(map(float,mapping_summary[i]["mapq_average"]))/len(mapping_summary[i]["mapq_average"])

				# mate_pairs = []
				# mp = { item:mapping_summary[i]["mate_pair"].count(item) for item in mapping_summary[i]["mate_pair"]}
				# for k in mp:
					# if k != i.replace(" ", "_"):
						# if k not in mapping_summary[i]["cvterm_name"]:
							# mate_pairs.append("{} ({})".format(k,mp[k]))

				# identity range
				# min_identity = float(min(mapping_summary[i]["range_of_reference_allele_source"]))
				# max_identity = float(max(mapping_summary[i]["range_of_reference_allele_source"]))
				# identity_range = ""
				# logger.debug("percent identity range for {} : {} => ({} - {})".format("; ".join(mapping_summary[i]["cvterm_name"]), mapping_summary[i]["range_of_reference_allele_source"], min_identity, max_identity))

				# if min_identity == 0.0 and max_identity > 0.0:
					# identity_range = "{}".format(max_identity)
				# elif min_identity > 0.0 and max_identity > min_identity:
					# identity_range = "{} - {}".format(min_identity, max_identity)
				# elif min_identity == max_identity and min_identity > 0.0:
					# identity_range = "{}".format(max_identity)
				confidence = ""
				average_indentity = sum(map(float,mapping_summary[i]["range_of_reference_allele_source"]))
				confidence_reads = sum(map(float,mapping_summary[i]["span"])) + sum(map(float,mapping_summary[i]["complete_mapped"]))
				
				if average_indentity >= 87 and confidence_reads >= 3 and average_percent_coverage >= 0.9:
					confidence = "high"
				elif average_indentity <= 80 and confidence_reads == 0 and average_percent_coverage <= 0.8:
					confidence = "low"
				else:
					confidence = "middle"
				writer.writerow([
					"; ".join(mapping_summary[i]["cvterm_name"]),
					i,
					"; ".join(mapping_summary[i]["model_type"]),
					"; ".join(mapping_summary[i]["database"]),
					am[i],
					# identity_range,
					format(sum(map(float,mapping_summary[i]["range_of_reference_allele_source"])),'.2f'),##identity
					observed_in_genomes,
					observed_in_plasmids,
					"; ".join(mapping_summary[i]["observed_in_pathogens"]),
					format(sum(map(float,mapping_summary[i]["span"])),'.2f'),
					format(sum(map(float,mapping_summary[i]["complete_mapped"])),'.2f'),
					format(sum(map(float,mapping_summary[i]["flanking"])),'.2f'),
					format(sum(map(float,mapping_summary[i]["all"])),'.2f'),
					format(average_percent_coverage,'.2f'),
					format(average_length_coverage,'.2f'),
					confidence,
					# format(average_mapq,'.2f'),
					mapping_summary[i]["number_of_mapped_baits"][-1],
					mapping_summary[i]["number_of_mapped_baits_with_reads"][-1],
					mapping_summary[i]["average_bait_coverage"][-1],
					mapping_summary[i]["bait_coverage_coefficient_of_variation"][-1],
					"N/A",
					"N/A",
					# "; ".join(mate_pairs),
					"; ".join(mapping_summary[i]["reference_sequence_length"]),
					"; ".join(mapping_summary[i]["AMR Gene Family"]),
					"; ".join(mapping_summary[i]["Drug Class"]),
					"; ".join(mapping_summary[i]["Resistance Mechanism"])
				])
	
	def get_final_result(self):
		dict_drug={}
		for line in open(self.gene_mapping_data_tab):
			arr = line.strip().split("\t")
			if arr[0] == "ARO Term":
				continue
			ARO_Term = arr[0]
			species = arr[8]
			confidence = arr[15]
			drugs = arr[24]
			for drug in drugs.strip().split(";"):
				drug = drug.strip()
				if drug not in dict_drug:
					dict_drug[drug] = {"gene":{}, "species":{}, "confidence":{}}
				dict_drug[drug]["gene"][ARO_Term] = ""
				dict_drug[drug]["species"][species] = ""
				dict_drug[drug]["confidence"][confidence] = ""
		fo = open(self.results, "w")
		fo.write("Drugs\tConfidence\tSpecies\tARO Term\n")
		writer = csv.writer(fo, delimiter='\t', dialect='excel')
		for DRUG in dict_drug:
			confidence = ""
			confidence_list = dict_drug[DRUG]["confidence"].keys()
			if "high" in confidence_list:
				confidence = 'high'
			elif "middle" in confidence_list:
				confidence = "middle"
			elif "low" in confidence_list:
				confidence = "low"
			else:
				logger.info("confidence error...")
			writer.writerow([
							DRUG,
							confidence,
							(";").join(dict_drug[DRUG]["species"].keys()),
							(";").join(dict_drug[DRUG]["gene"].keys())
							])
		fo.close()
	
	def run(self):
		self.get_opt()
		self.pre_analysis()
		self.get_alignments_gene()
		self.get_summary()
		self.get_final_result()
		
if __name__ == '__main__':
	
	run_detecter = ont_amr_detecter()
	run_detecter.run()

		
