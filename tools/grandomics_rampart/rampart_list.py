import argparse, os, docker


class Docker(object):
    def __init__(self):
        self._client = docker.from_env()
        self._host_ip = os.getenv('GALAXY_IP')
        if not self._host_ip: raise Exception("can not find $GALAXY_IP in Environment variables")

    @property
    def client(self):
        return self._client

    @property
    def containers(self):
        return [c for c in self._client.containers.list() if c.name.startswith('rampart_')]

    def get_port(self, container):
        for name in container.ports.keys():
            port = int(name.split('/')[0])
            if port % 2 == 0: return port
        return None

    def write_htmls(self, outdir):
        if not os.path.isdir(outdir): os.makedirs(outdir)
        for container in self.containers:
            cell = container.name.replace('rampart_', '')
            port = self.get_port(container)
            fo = open(os.path.join(outdir, '%s.html' % cell), 'w')
            fo.write('<iframe src="http://%s:%d/" frameborder="0" width="%s" height="%s"></iframe>\n' % (
                self._host_ip, port, '100%', '100%'
            ))
            fo.close()


def main(args):
    docker = Docker()
    docker.write_htmls(args.outdir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Author: Ying Zhu (zhuy@grandomics.com) from GrandOmics'
    )
    parser.add_argument('-o', '--outdir', required=True, help='output dir')
    parser.set_defaults(function=main)
    args = parser.parse_args()
    args.function(args)
