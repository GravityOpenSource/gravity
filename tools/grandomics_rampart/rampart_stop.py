import argparse, os, docker
from jinja2 import Template


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

    def get_template(self, html):
        html = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rampart_list.html')
        fi = open(html)
        tpl = Template(fi.read())
        fi.close()
        return tpl

    def write_out(self, tpl, html):
        containers = list()
        for container in self.containers:
            containers.append({
                'name': container.name.replace('rampart_', ''),
                'port': self.get_port(container)
            })
        fo = open(html, 'w')
        fo.write(tpl.render(containers=containers, host=os.getenv('GALAXY_IP', '159.138.147.148')))
        fo.close()


def main(args):
    docker = Docker()
    container = docker.get_container(args.cell)
    if container: container.stop()
    tpl = docker.get_template(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rampart_list.html'))
    docker.write_out(tpl, args.out_html)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Author: Ying Zhu (zhuy@grandomics.com) from GrandOmics'
    )
    parser.add_argument('-c', '--cell', required=True, help='cell name')
    parser.add_argument('-o', '--out_html', required=True, help='output html')
    parser.set_defaults(function=main)
    args = parser.parse_args()
    args.function(args)
