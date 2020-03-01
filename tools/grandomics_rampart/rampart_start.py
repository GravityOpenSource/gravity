import argparse, os, random, string, shutil, json, docker


class Cell(object):
    def __init__(self, name):
        self._name = name
        self._ramdom = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        self._rampart_dir = os.getenv('RAMPART_WORK_DIR')
        self._basecalled_dir = os.getenv('BASECALLED_DIR')
        self._rampart_image = os.getenv('RAMPART_IMAGE')
        self._host_ip = os.getenv('GALAXY_IP')
        if not self._rampart_dir: raise Exception("can not find $RAMPART_WORK_DIR in Environment variables")
        if not self._basecalled_dir: raise Exception("can not find $BASECALLED_DIR in Environment variables")
        if not self._rampart_image: raise Exception("can not find $RAMPART_IMAGE in Environment variables")
        if not self._host_ip: raise Exception("can not find $GALAXY_IP in Environment variables")

    @property
    def name(self):
        return '%s-%s' % (self._name, self._ramdom)

    @property
    def rampart_work_cell_dir(self):
        path = os.path.join(self._rampart_dir, self.name)
        if not os.path.isdir(path): os.makedirs(path)
        return path

    @property
    def protocol_dir(self):
        path = os.path.join(self.rampart_work_cell_dir, 'protocol')
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

    def get_docker_params(self, port):
        return {
            'image': self._rampart_image,
            'ports': {'%d/tcp' % port: port, '%d/tcp' % (port + 1): port + 1},
            'command': 'run-rampart %s' % self.name,
            'environment': {
                'GALAXY_RAMPART_WORK_DIR': self._rampart_dir,
                'GALAXY_RAMPART_PORT1': port,
                'GALAXY_RAMPART_PORT2': port + 1,
                'NODE_OPTIONS': '--max_old_space_size=%s' % (32 * 1024)
            },
            'name': 'rampart_%s' % self._name,
            'volumes_from': 'data-volumes',
            'detach': True,
            'remove': True
        }

    def create_protocol(self, genome_file, references_file, primers_file):
        target_genome_file = os.path.join(self.protocol_dir, 'genome.json')
        target_references_file = os.path.join(self.protocol_dir, 'references.fasta')
        target_primers_file = os.path.join(self.protocol_dir, 'primers.json')
        if not os.path.isfile(target_genome_file): shutil.copyfile(genome_file, target_genome_file)
        if not os.path.isfile(target_references_file): shutil.copyfile(references_file, target_references_file)
        if not os.path.isfile(target_primers_file): shutil.copyfile(primers_file, target_primers_file)

    def create_config(self):
        data = {'title': self._name, 'basecalledPath': self.fastq_dir, 'samples': []}
        for i in range(1, 25):
            data['samples'].append({
                'name': 'Sample{:0>2d}'.format(i),
                'description': '',
                'barcodes': ['NB{:0>2d}'.format(i)]
            })
        config_json = os.path.join(self.rampart_work_cell_dir, 'run_configuration.json')
        fo = open(config_json, 'w')
        fo.write(json.dumps(data, indent=4) + '\n')
        fo.close()

    def write_html(self, out_html, port):
        fo = open(out_html, 'w')
        fo.write('<iframe src="http://%s:%d/" frameborder="0" width="%s" height="%s"></iframe>\n' % (
            self._host_ip, port, '100%', '100%'
        ))
        fo.close()

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
        start_port = int(os.getenv('RAMPART_START_PORT', 10000))
        for _port in range(start_port, 65534, 2):
            if _port not in ports: return _port
        raise Exception('ERROR: there is no port avaliable between 3000 to 65532')

    def create(self, **kwargs):
        self._client.containers.run(**kwargs)





def main(args):
    docker = Docker()
    container = docker.get_container(cell_name=args.cell)
    if container: container.stop()
    cell = Cell(name=args.cell)
    cell.create_protocol(genome_file=args.genome, references_file=args.references, primers_file=args.primers)
    cell.create_config()
    port = docker.port
    docker_params = cell.get_docker_params(port=port)
    docker.create(**docker_params)
    cell.write_html(args.out_html, port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Author: Ying Zhu (zhuy@grandomics.com) from GrandOmics'
    )
    parser.add_argument('-g', '--genome', required=True, help='genome json file')
    parser.add_argument('-r', '--references', required=True, help='references fastq file')
    parser.add_argument('-p', '--primers', required=True, help='primers json file')
    parser.add_argument('-c', '--cell', required=True, help='cell name')
    parser.add_argument('-o', '--out_html', required=True, help='output html')
    parser.set_defaults(function=main)
    args = parser.parse_args()
    args.function(args)
