import argparse, os
from multiprocessing import Pool


def find_files(cell_dir, pass_required):
    files = list()
    for root, _, filanames in os.walk(cell_dir):
        for filename in filanames:
            if not filename.endswith('fastq'): continue
            if pass_required and filename.find('_pass_') == -1: continue
            files.append(os.path.join(root, filename))
    if not files: raise Exception("can not find any fastq files")
    return sorted(files)


def make_symlink(files, outdir):
    for filo in files:
        target = os.path.join(outdir, os.path.basename(filo))
        if os.path.exists(target): continue
        os.symlink(filo, target)


def split_list(array, number):
    results = [list() for i in range(number)]
    for i in range(len(array)):
        j = i % number
        results[j].append(array[i])
    return results


def merge_files(files, target_file):
    fo = open(target_file, 'w')
    for filo in files:
        fi = open(filo)
        for line in fi:
            fo.write(line)
        fi.close()
    fo.close()


def main(args):
    basecalled_dir = os.getenv('BASECALLED_DIR')
    if not basecalled_dir: raise Exception("can not find $BASECALLED_DIR in Environment variables")
    cell_dir = os.path.join(basecalled_dir, args.cell)
    if not os.path.isdir(cell_dir): raise Exception("can not find cell %s in $BASECALLED_DIR" % cell_dir)
    if not os.path.isdir(args.outdir): os.makedirs(args.outdir)
    files = find_files(cell_dir, args.pass_required == 'true')
    if len(files) <= args.number:
        make_symlink(files, args.outdir)
    else:
        multi_files = split_list(files, args.number)
        pool = Pool(args.number if args.number < 8 else 8)
        for i in range(args.number):
            outfile = os.path.join(args.outdir, 'merge_%d.fastq' % i)
            pool.apply_async(merge_files, args=(multi_files[i], outfile))
        pool.close()
        pool.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Author: Ying Zhu (zhuy@grandomics.com) from GrandOmics'
    )
    parser.add_argument('-c', '--cell', required=True, help='cell name')
    parser.add_argument('-r', '--pass_required', default='pass', choices=('true', 'false'), help='pass fastq required')
    parser.add_argument('-n', '--number', default=10, type=int, help='merge number')
    parser.add_argument('-o', '--outdir', required=True, help='output dir')
    parser.set_defaults(function=main)
    args = parser.parse_args()
    args.function(args)
