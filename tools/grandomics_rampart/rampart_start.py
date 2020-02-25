import argparse, os, random, string, shutil, json, docker


class Cell(object):
    def __init__(self, work_dir, basecalled_dir, name):
        self._work_dir = work_dir
        self._basecalled_dir = basecalled_dir
        self._name = name

    @property
    def work_cell_dir(self):
        random_str = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        path = os.path.join(self._work_dir, '%s-%s' % (self._name, random_str))
        if not os.path.isdir(path): os.makedirs(path)
        return path

    @property
    def protocol_dir(self):
        path = os.path.join(self.work_cell_dir, 'protocol')
        if not os.path.isdir(path): os.makedirs(path)
        return path

    @property
    def fastq_dir(self):
        cell_dir = os.path.join(self._basecalled_dir, self._name)
        if os.path.isdir(cell_dir):
            for root, dirnames, _ in os.walk(cell_dir):
                for dirname in dirnames:
                    if dirname == 'fastq_pass': return os.path.join(root, dirname)
        raise Exception('找不到该Cell目录或目录下没有fastq_pass目录: %s' % self._name)

    def create_script(self):
        source_script = os.path.join(os.path.dirname(os.path.abspath('__file__')), 'run.sh')
        target_script = os.path.join(self.work_cell_dir, 'run.sh')
        shutil.copyfile(source_script, target_script)

    def create_protocol(self, genome_file, references_file, primers_file):
        target_genome_file = os.path.join(self.protocol_dir, 'genome.json')
        target_references_file = os.path.join(self.protocol_dir, 'references.fasta')
        target_primers_file = os.path.join(self.protocol_dir, 'primers.json')
        if not os.path.isfile(target_genome_file): shutil.copyfile(genome_file, target_genome_file)
        if not os.path.isfile(target_references_file): shutil.copyfile(references_file, target_references_file)
        if not os.path.isfile(target_primers_file): shutil.copyfile(primers_file, target_primers_file)

    def create_config(self):
        data = {'title': self._name, 'basecalledPath': '../fastq', 'samples': []}
        for i in range(1, 25):
            data['samples'].append({
                'name': 'Sample{:0>2d}' % i,
                'description': '',
                'barcodes': ['NB{:0>2d}' % i]
            })
        config_json = os.path.join(self.work_cell_dir, 'run_configuration.json')
        fo = open(config_json, 'w')
        fo.write(json.dumps(data, indent=4) + '\n')
        fo.close()

    def get_volumes(self):
        _shell_dir = '%s/shell' % self.WORKDIR
        _fastq_dir = '%s/fastq_pass' % self.WORKDIR
        _annnotations_dir = '%s/annotations' % self.WORKDIR
        return {
            self.work_cell_dir: {'bind': '/home/rampart/work', 'mode': 'rw'},
            self.fastq_dir: {'bind': '/home/rampart/fastq', 'mode': 'rw'},
        }

    def create(self, docker_client, protocol_dir, shell_dir):
        docker_client.containers.run(
            image=self._image,
            command=self.command,
            ports=self.ports,
            environment=self.envs,
            name=self.container_name,
            volumes=self.get_volumes(protocol_dir, shell_dir),
            detach=True,
            remove=True
        )

class Docker(object):
    def __init__(self):
        self._client = docker.from_env()

    @property
    def client(self):
        return self._client

    @property
    def containers(self):
        return [c for c in self._client.containers.list() if c.name.startswith('rampart_')]

    def get_container(self, cell_name):
        for container in self.containers:
            if container.name == 'rampart_%s' % cell_name:
                return container
        return None

    def get_port(self, container):
        for name in container.ports.keys():
            port = int(name.split('/')[0])
            if port % 2 == 0: return port
        return None

    @property
    def port(self):
        ports = list()
        for container in self.containers:
            _port = self.get_port(container)
            if _port: ports.append(_port)
        for _port in range(3000, 65534, 2):
            if _port not in ports: return _port
        raise Exception('ERROR: there is no port avaliable between 3000 to 65532')


def main(args):
    cell = Cell(work_dir=args.workdir, basecalled_dir=args.basecalled, name=args.cell)
    cell.create_protocol(genome_file=args.genome, references_file=args.references, primers_file=args.primers)
    cell.create_config()
    cell.create_script()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Author: Ying Zhu (zhuy@grandomics.com) from GrandOmics'
    )
    parser.add_argument('-g', '--genome', required=True, help='genome json file')
    parser.add_argument('-r', '--references', required=True, help='references fastq file')
    parser.add_argument('-p', '--primers', required=True, help='primers json file')
    parser.add_argument('-c', '--cell', required=True, help='cell name')
    parser.add_argument('-w', '--workdir', required=True, help='work dir')
    parser.add_argument('-b', '--basecalled', default=os.getenv('BASECALLED_DIR', '/data/basecalled'),
                        help='basecalled path')
    parser.add_argument('-i', '--image', help='docker images')
    parser.set_defaults(function=main)
    args = parser.parse_args()
    args.function(args)
