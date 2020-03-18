import argparse, os, re


def get_name_fastq_dict(names, files):
    data = dict()
    for i in range(len(names)):
        data.setdefault(names[i], files[i])
    return data


def link_soft(data_txt,data_bam):
    for txt_name, txt_file in data_txt.items():
        bam_file = data_bam[txt_name]
        for line in open(txt_file):
            line=line.strip()
            if line[0] == "#":
                continue
            positive = line.split("\t")[-1]
            if positive == "True":
                os.system("cp %s %s.bam"%(bam_file,txt_name))

def main(args):
    if len(set([len(args.txt_names), len(args.input_txts), len(args.input_bams), len(args.bam_names)])) != 1:
        raise Exception("number error!")
   
    link_soft(get_name_fastq_dict(args.txt_names, args.input_txts), get_name_fastq_dict(args.bam_names, args.input_bams))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Author: Ying Zhu (zhuy@grandomics.com) from GrandOmics'
    )
    parser.add_argument('--txt_names' , nargs='+', required=True, help='barcode names of input txt files')
    parser.add_argument('--input_txts', nargs='+', required=True, help='input txt files')
    parser.add_argument('--input_bams', nargs='+', required=True, help='input bam files')
    parser.add_argument('--bam_names' , nargs='+', required=True, help='barcode names of input bam files')
    parser.set_defaults(function=main)
    args = parser.parse_args()
    #print(args.txt_names)
    args.function(args)
