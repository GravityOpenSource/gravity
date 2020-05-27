"""
Coverage datatypes
 
"""
 
import logging
import math
 
from galaxy.datatypes import metadata
from galaxy.datatypes.sniff import (
    build_sniff_from_prefix,
    get_headers,
    iter_headers,
)
from galaxy.datatypes.metadata import MetadataElement
from galaxy.datatypes.tabular import Tabular
 
log = logging.getLogger(__name__)
 
class DepthCoverage(Tabular):
 
    file_ext = "coverage"
 
    MetadataElement(name="chromCol", default=1, desc="Chrom column", param=metadata.ColumnParameter)
    MetadataElement(name="depth", default=2, desc="depth:1000X-0X", param=metadata.ColumnParameter)
    MetadataElement(name="coverage_percentage", default=3, desc="coverage percentage:0-1", param=metadata.ColumnParameter)
 
    def __init__(self, **kwd):
        """Initialize DepthCoverage datatype"""
        Tabular.__init__(self, **kwd)
 
    def sniff(self, filename):
        headers = get_headers(filename, '\t')
        try:
            if len(headers) < 3:
                return False
            headers[0] == "MN994467.1"
        except:
            return False
        # If we haven't yet returned False, then...
        return True

