from __future__ import print_function
from __future__ import absolute_import

import sys
import dpkt

try:
    from collections import OrderedDict
except ImportError:
    # Python 2.6
    OrderedDict = dict

try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO

if sys.version_info < (3,):
    def iteritems(d, **kw):
        return d.iteritems(**kw)
else:
    def iteritems(d, **kw):
        return iter(d.items(**kw))

try:
    from collections import OrderedDict
except ImportError:
    # Python 2.6
    OrderedDict = dict


def parse_headers(f):
    """Return dict of headers parsed from a file object."""
    d = OrderedDict()
    while 1:
        # The following logic covers two kinds of loop exit criteria.
        # 1) If the header is valid, when we reached the end of the header,
        #    f.readline() would return with '\r\n', then after strip(),
        #    we can break the loop.
        # 2) If this is a weird header, which do not ends with '\r\n',
        #    f.readline() would return with '', then after strip(),
        #    we still get an empty string, also break the loop.
        line = f.readline().strip().decode("ascii", "ignore")
        if not line:
            break
        l = line.split(':', 1)
        if len(l[0].split()) != 1:
            raise dpkt.UnpackError('invalid header: %r' % line)
        k = l[0].lower()
        v = len(l) != 1 and l[1].lstrip() or ''
        if k in d:
            if not type(d[k]) is list:
                d[k] = [d[k]]
            d[k].append(v)
        else:
            d[k] = v
    return d


class Message(dpkt.Packet):
    """headers + params; based on HTTP.

    Attributes:
        __hdr__: Header fields.
    """

    __metaclass__ = type
    __hdr_defaults__ = {}
    headers = None

    def __init__(self, *args, **kwargs):
        if args:
            self.unpack(args[0])
        else:
            self.headers = OrderedDict()
            self.data = b''
            # NOTE: changing this to iteritems breaks py3 compatibility
            for k, v in self.__hdr_defaults__.items():
                setattr(self, k, v)
            for k, v in iteritems(kwargs):
                setattr(self, k, v)

    def unpack(self, buf):
        f = BytesIO(buf)
        # Parse headers
        self.headers = parse_headers(f)
        # Save the rest
        self.data = f.read()

    def pack_hdr(self):
        return ''.join(['%s: %s\r\n' % t for t in iteritems(self.headers)])

    def __len__(self):
        return len(str(self))

    def __str__(self):
        return '%s\r\n' % (self.pack_hdr())

    def __bytes__(self):
        # Not using byte interpolation to preserve Python 3.4 compatibility. The extra
        # \r\n doesn't get trimmed from the bytes, so it's necessary to omit the spacing
        # one when building the output if there's no body
        return self.pack_hdr().encode("ascii", "ignore")


class Request(Message):
    """Custom protocol based on HTTP.

    Attributes:
        __hdr__: Header fields of my protocol.
        TODO.
    """

    __hdr_defaults__ = {
        'method': None
    }
    __methods = dict.fromkeys((
        'TRACK', 'DUMMY'
    ))

    def unpack(self, buf):
        f = BytesIO(buf)
        line = f.readline().decode("ascii", "ignore")
        l = line.strip().split()
        if len(l) != 1:
            raise dpkt.UnpackError('invalid message: %r' % line)
        if l[0] not in self.__methods:
            raise dpkt.UnpackError('invalid protocol method: %r' % l[0])
        self.method = l[0]
        Message.unpack(self, f.read())

    def __str__(self):
        return '%s\r\n' % (self.method) + Message.__str__(self)

    def __bytes__(self):
        str_out = '%s\r\n' % (self.method)
        return str_out.encode("ascii", "ignore") + Message.__bytes__(self)


def test_parse_request():
    s = b"""TRACK\r\nFrom: 10.0.100.5\r\nTo: 10.0.100.19\r\nNext-Hop: 10.0.100.5\r\n\r\n"""
    r = Request(s)
    assert r.method == 'TRACK'
    assert r.headers['from'] == '10.0.100.5'
    assert r.headers['to'] == '10.0.100.19'
    assert r.headers['next-hop'] == '10.0.100.5'


if __name__ == '__main__':
    # Runs all the test associated with this class/file
    test_parse_request()
    print('Custom protocol: tests passed...')
