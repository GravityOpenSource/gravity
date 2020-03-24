#!/usr/bin/env python

from optparse import OptionParser

VERSION = 0.1

def process(options):
  database = {}
  with open(options.pathogen, "r") as fp:
    header = fp.readline()
    for line in fp:
      stat = line.strip().split("\t")
      database[stat[0]] = database.get(stat[0], []) + stat[-1].split(";")
  for key,value in database.items():  database[key] = set(value)
  fout = open(options.output, "w")
  with open(options.centrifuge, "r") as fp:
    header = fp.readline().strip()
    fout.write("%s\tdisease\n" % header)
    for line in fp:
      stat = line.strip().split("\t")
      if stat[1] in database:
        fout.write("%s\t%s\n" % (line.strip(), "; ".join(list(database[stat[1]]))))
  fout.close()

def parse_command():
  usage = "Extract human pathogen from centrifuge result\n\npython detect_pathogen.py -r human_pathogen -i centrifuge_result -o output"
  parser = OptionParser(usage=usage, version=VERSION)
  parser.add_option("-r", dest="pathogen", help="input human pathogen file")
  parser.add_option("-i", dest="centrifuge", help="input centrifuge result file")
  parser.add_option("-o", dest="output", help="output file")
  return parser.parse_args()

def main():
  (options, args) = parse_command()
  process(options)

if __name__ == "__main__":
  main()
