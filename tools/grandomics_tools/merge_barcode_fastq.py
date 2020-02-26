import argparse, os, re


def get_name_fastq_dict(names, fastqs):
    data = dict()
    for i in range(len(names)):
        data.setdefault(names[i], list()).append(fastqs[i])
    return data


def merge(data):
    for name, fastqs in data.items():
        fo = open('%s.fastq' % name, 'w')
        for fastq in fastqs:
            fi = open(fastq)
            fo.write(fi.read())
            fi.close()
        fo.close()


def main(args):
    if len(args.names) != len(args.inputs):
        raise Exception("len(names) != len(inputs)")
    merge(get_name_fastq_dict(args.names, args.inputs))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Author: Ying Zhu (zhuy@grandomics.com) from GrandOmics'
    )
    parser.add_argument('-n', '--names', nargs='+', required=True, help='barcode names')
    parser.add_argument('-i', '--inputs', nargs='+', required=True, help='input fastq files')
    parser.set_defaults(function=main)
    args = parser.parse_args()
    args.function(args)
