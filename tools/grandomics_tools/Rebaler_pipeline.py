import sys
import os
import time
import argparse
import multiprocessing
import tempfile
import shutil
import random
import subprocess
import pysam
import math
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

class MyHelpFormatter(argparse.HelpFormatter):

    def __init__(self, prog):
        terminal_width = shutil.get_terminal_size().columns
        os.environ['COLUMNS'] = str(terminal_width)
        max_help_position = min(max(24, terminal_width // 3), 40)
        super().__init__(prog, max_help_position=max_help_position)

    def _get_help_string(self, action):
        help_text = action.help
        if action.default != argparse.SUPPRESS and 'default' not in help_text.lower() and \
                action.default is not None:
            help_text += ' (default: ' + str(action.default) + ')'
        return help_text
        
def temp_dir(string):
    if os.path.isdir(string):
        return string
    else :
        try:
            os.makedirs(string)
            return string
        except:
            msg = "%r is invalid or don't have permission." % string
            raise argparse.ArgumentTypeError(msg)
            
def get_arguments():
    """
    Parse the command line arguments.
    """
    default_threads = min(multiprocessing.cpu_count(), 4)

    parser = argparse.ArgumentParser(description='Rebaler: reference-based long read assemblies '
                                                 'of bacterial genomes pipeline',
                                     formatter_class=MyHelpFormatter, add_help=False)
    #Positional arguments
    positional_args = parser.add_argument_group('Positional arguments')
    positional_args.add_argument('reference', type=str,
                                 help='FASTA file of reference assembly')
    positional_args.add_argument('reads', type=str,
                                 help='FASTA/FASTQ file of long reads')
    positional_args.add_argument('barcode', type=str,
                                 help='barcode file')
    
    
    #basics arguments
    basics_args = parser.add_argument_group('basics arguments')
    basics_args.add_argument('-t', '--threads', type=int, default=default_threads,
                               help='Number of threads to use ')
    basics_args.add_argument('-p', '--temp', type=temp_dir, default='tmp',
                               help='The temporary directory')
    basics_args.add_argument('-r', '--rm', action='store_true',default=False,
                             help='Delete intermediate file')
    #nanoplexer arguments
    nanoplexer_args = parser.add_argument_group('nanoplexer arguments')
    nanoplexer_args.add_argument('-L', type=int, default=70,
                               help='barcode lenght ')
    nanoplexer_args.add_argument('-M', type=str, default='fasta',
                               help='format')
    
    #sample arguments
    sample_args = parser.add_argument_group('sample arguments')
    sample_args.add_argument('-c','--cov', type=int,default=100,help='coverage')
    sample_args.add_argument('-T','--stime', type=int,default=10,help='sample time')
    
    #mosdepth arguments
    mosdepth_args = parser.add_argument_group('mosdepth arguments')
    mosdepth_args.add_argument('-b','--by',default=1,help='window-sizes')
    mosdepth_args.add_argument('--thresholds',default='1,2,3',help='Specify multiple integer values separated by ,')
    
    #output arguments
    output_args = parser.add_argument_group('output arguments')
    output_args.add_argument('-o','--output',type=str,default='result.asm.fasta',help='output file')
    output_args.add_argument('--prefix',type=str,default='COV-2019',help='prefix')
    
    if len(sys.argv) == 1:
        parser.print_help(file=sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    if not os.path.isfile(args.reference):
        sys.exit('Error: could not find ' + args.reference)
    if not os.path.isfile(args.reads):
        sys.exit('Error: could not find ' + args.reads)
    if not os.path.isfile(args.barcode):
        sys.exit('Error: could not find ' + args.barcode)

    return args


def cmd(command):
    subp = subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8")
    subp.wait()
    assert subp.poll() == 0 ,'<{0}> execution error {1} '.format(command,subp.poll())
    '''
    if subp.poll() != 0:
        print()
        sys.exit(0)
    '''

def run_nanoplexer(reads,barcode,threads,M,L,temp):
    #path=tempfile.TemporaryDirectory(dir=None)
    path=os.path.join(temp,'nanoplexer_out')
    temp_dir(path)
    command='nanoplexer -b {0} -p {1} -t {2} -L {3} {4} -M {5}'.format(barcode,path,threads,L,reads,M)
    #print(command)
    cmd(command)
    return path
 
def readfq(fp): # this is a generator function
    last = None # this is a buffer keeping the last unprocessed line
    while True: # mimic closure; is it a bad idea?
        if not last: # the first record or a record following a fastq
            for l in fp: # search for the start of the next record
                if l[0] in '>@': # fasta/q header line
                    last = l[:-1] # save this line
                    break
        if not last: break
        name, seqs, last = last[1:].partition(" ")[0], [], None
        for l in fp: # read the sequence
            if l[0] in '@+>':
                last = l[:-1]
                break
            seqs.append(l[:-1])
        if not last or last[0] != '+': # this is a fasta record
            yield name, ''.join(seqs), None # yield a fasta record
            if not last: break
        else: # this is a fastq record
            seq, leng, seqs = ''.join(seqs), 0, []
            for l in fp: # read the quality
                seqs.append(l[:-1])
                leng += len(l) - 1
                if leng >= len(seq): # have read enough quality
                    last = None
                    yield name, seq, ''.join(seqs); # yield a fastq record
                    break
            if last: # reach EOF before reading enough quality
                yield name, seq, None # yield a fasta record instead
                break
 


def run_sample(nanoplexer_path,cov,stime,temp):
    flist = list(filter(lambda x: x.startswith("nCoV"), os.listdir(nanoplexer_path)))
    path=os.path.join(temp,'sample_out')
    temp_dir(path)
    for n in range(1,stime+1):
        if n < 10:
            n='0'+str(n)
        primer_sample=os.path.join(path,'primer_sample{0}.fa'.format(n))
        
        fp = open(primer_sample, "w")
        for fn in flist:
            with open("%s/%s" % (nanoplexer_path, fn), "r") as fq:
                tmp = {}
                for name, seq, qual in readfq(fq):
                    if len(seq) > 200:
                        tmp[name] = seq
            names = tmp.keys() if len(tmp.keys()) <= cov else random.sample(tmp.keys(), cov)
            for name in names:  fp.write(">%s\n%s\n" % (name, tmp[name]))
        fp.close()
    return path



def run_rebaler(reference,sample_path,stime,threads):
    # rebaler $reference temp_outputs/primer_sample${i}.fa -t $threads> temp_outputs/primer_sample${i}.ref_base.fasta
    for n in range(1,stime+1):
        if n < 10:
            n='0'+str(n)
        command='rebaler {0} {1}/primer_sample{2}.fa -t {3} > {1}/primer_sample{2}.ref_base.fasta'\
                 .format(reference,sample_path,n,threads)
        cmd(command)
        
def run_map(reference,sample_path,stime,threads):
    # minimap2 -x map-ont --MD -Y -a -t $threads $reference temp_outputs/primer_sample${i}.ref_base.fasta | samtools \
    #view -S -b -h - |samtools sort -o temp_outputs/primer_sample${i}.ref_base.bam - && samtools index temp_outputs/primer_sample${i}.ref_base.bam
    for n in range(1,stime+1):
        if n < 10:
            n='0'+str(n)
        command='''minimap2 -x map-ont --MD -Y -a -t {0} {1} {2}/primer_sample{3}.ref_base.fasta |\
samtools view -S -b -h -|samtools sort -o {2}/primer_sample{3}.ref_base.bam - &&\
samtools index {2}/primer_sample{3}.ref_base.bam'''.format(threads,reference,sample_path,n) 
        cmd(command)


def run_mosdepth(by,thresholds,sample_path,stime,threads):
     #  mosdepth temp_outputs/primer_sample${i}.ref_base temp_outputs/primer_sample${i}.ref_base.bam -T 1,2,3 -b 1 -t 2
     for n in range(1,stime+1):
        if n < 10:
            n='0'+str(n)
        command='mosdepth {0}/primer_sample{1}.ref_base {0}/primer_sample{1}.ref_base.bam -T {2} -b {3} -t {4}'.format(sample_path,n,thresholds,by,threads)
        cmd(command)
        
def Rename(fasta,outprefix,output):
    record_list=[]
    for seq_record in SeqIO.parse(fasta, "fasta"):
        record_list.append(SeqRecord(seq_record.seq,id=outprefix,description='Reference-based assembly'))
    SeqIO.write(record_list, output, "fasta")
    
def ContigScore(num,base):
    return math.log(num,base)

def Calculate(bamfile,distfile):
    samfile=pysam.AlignmentFile(bamfile,'rb')
    NM_sum=0
    sup_align=0
    unmap=0
    cov_contig_num=0
    for record in samfile:
        if record.is_unmapped:
            unmap+=1
            continue
        NM_sum+=record.get_tag('NM')
        if record.is_supplementary or record.is_secondary:
            sup_align+=1
        else:
            cov_contig_num+=1
           
    X=open(distfile).readlines()[-2]
    cover_ratio=float(X.strip().split('\t')[-1])
    AL=math.sqrt(math.log((NM_sum+10*(sup_align+unmap)),10))
    CR=cover_ratio**2
    CT=(1+math.log(cov_contig_num,2))
    DS=AL*CT/CR
    return DS

def run_Draft(sample_path,outprefix,output):
    prefix_list=[os.path.splitext(i)[0] for i in filter(lambda x: x.endswith("bam"), os.listdir(sample_path))]
    min_score={}
    for prefix in prefix_list:
        bamfile=os.path.join(sample_path,prefix+'.bam')
        distfile=os.path.join(sample_path,prefix+'.mosdepth.global.dist.txt')
        sample=os.path.join(sample_path,prefix+'.fasta')
        DS=Calculate(bamfile,distfile)
        if not min_score:
            min_score['name']=sample
            min_score['score']=DS
        else:
            if DS < min_score['score']:
                min_score['name']=sample
                min_score['score']=DS
    Rename(min_score['name'],outprefix,output)   


def run():
    args=get_arguments()
    nanoplexer_path=run_nanoplexer(args.reads,args.barcode,args.threads,args.M,args.L,args.temp)
    sample_path=run_sample(nanoplexer_path,args.cov,args.stime,args.temp)
    run_rebaler(args.reference,sample_path,args.stime,args.threads)
    run_map(args.reference,sample_path,args.stime,args.threads)
    run_mosdepth(args.by,args.thresholds,sample_path,args.stime,args.threads)
    outprefix=os.path.splitext(os.path.split(args.prefix)[-1])[0]
    run_Draft(sample_path,outprefix,args.output)
    if args.rm:
        if os.path.exists(nanoplexer_path) :
            os.remove(nanoplexer_path)
        if os.path.exists(sample_path) :
            os.remove(sample_path)
        
def test():
    args=get_arguments()
    nanoplexer_path='tmp/nanoplexer_out'
    sample_path=run_sample(nanoplexer_path,args.cov,args.stime,args.temp)
    run_rebaler(args.reference,sample_path,args.stime,args.threads)
    run_map(args.reference,sample_path,args.stime,args.threads)
    run_mosdepth(args.by,args.thresholds,sample_path,args.stime,args.threads)
    outprefix=os.path.splitext(os.path.split(args.prefix)[-1])[0]
    run_Draft(sample_path,outprefix,args.output)
    if args.rm:
        if os.path.exists(nanoplexer_path) :
            os.remove(nanoplexer_path)
        if os.path.exists(sample_path) :
            os.remove(sample_path)


if __name__ == '__main__':
    run()
    #test()
    
