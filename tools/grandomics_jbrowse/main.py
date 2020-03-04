import argparse, os, random, string
from jbrowse import run_jbrowse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_CODE_DIR = os.path.join(BASE_DIR, 'source_code', 'jbrowse')


class Jbrowse(object):
    def __init__(self):
        self._ramdom = ''
        self._jbrowse_html_dir = os.getenv('JBROWSE_HTML_DIR')
        self._host_ip = os.getenv('GALAXY_IP')
        self._port = int(os.getenv('JBROWSE_POTR', 8081))
        if not self._jbrowse_html_dir: raise Exception("can not find $JBROWSE_HTML_DIR in Environment variables")
        if not self._host_ip: raise Exception("can not find $GALAXY_IP in Environment variables")

    @property
    def outdir(self):
        if not self._ramdom:
            while True:
                ramdom = ''.join(random.sample(string.ascii_letters + string.digits, 32))
                path = os.path.join(self._jbrowse_html_dir, ramdom)
                if not os.path.isdir(path):
                    os.makedirs(path)
                    self._ramdom = ramdom
                    break
        return os.path.join(self._jbrowse_html_dir, self._ramdom)

    def write_track_xml(self, track_xml_handle):
        fo = open(os.path.join(self.outdir, 'galaxy.xml'), 'w')
        fo.write(track_xml_handle.read())
        fo.close()

    def write_html(self, out_html):
        link = 'http://%s:%d/%s/index.html' % (self._host_ip, self._port, self._ramdom)
        fo = open(out_html, 'w')
        fo.write('<iframe src="%s" frameborder="0" width="%s" height="%s"></iframe>\n' % (link, '100%', '100%'))
        fo.close()


def main(args):
    jb = Jbrowse()
    jb.write_track_xml(args.track_xml)
    run_jbrowse(args.track_xml.name, SOURCE_CODE_DIR, jb.outdir, args.standalone)
    jb.write_html(args.out_html)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="", epilog="")
    parser.add_argument('--track_xml', type=argparse.FileType('r'), help='Track Configuration')
    parser.add_argument('--standalone', help='Standalone mode includes a copy of JBrowse', action='store_true')
    parser.add_argument('--out_html', help='Output HTML')
    parser.add_argument('--version', '-V', action='version', version="%(prog)s 0.8.0")
    args = parser.parse_args()
    main(args)
