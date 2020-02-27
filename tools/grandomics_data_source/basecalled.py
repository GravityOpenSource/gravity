import argparse, os, re

BASECALLED_DIR = '/data/basecalled'

def main(args):
    indir = os.path.join(BASECALLED_DIR, args.cell_name)
    files = list()
    for root, _, filanames in os.walk(indir):
        for filename in filanames:
            if not filename.endswith(args.format): continue
            path = os.path.join(root, filename)
            typo = os.path.basename(os.path.dirname(path))
            if args.type != 'all' and typo.find(args.type) == -1: continue
            files.append(path)
    for f in files: os.symlink(f, os.path.basename(f))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Author: Ying Zhu (zhuy@grandomics.com) from GrandOmics'
    )
    parser.add_argument('-n', '--cell_name', required=True, help='cell name')
    parser.add_argument('-f', '--format', default='fastq', choices=('fastq', 'fast5'), help='data fortmat')
    parser.add_argument('-t', '--type', default='all', choices=('all', 'pass', 'fail'), help='type')
    parser.set_defaults(function=main)
    args = parser.parse_args()
    args.function(args)
