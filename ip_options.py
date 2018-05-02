from dpkt import Packet
from dpkt.ip import IP


class IPOption(Packet):
    """Internet Protocol Options.

    Attributes:
        __hdr__: Option fields of IP.
    """

    __hdr__ = (
        ('type', 'B', 0),
        ('length', 'B', 0)  # make it optionals, cause not all options have this field
    )

    def __init__(self, *args, **kwargs):
        super(IPOption, self).__init__(*args, **kwargs)

    @property
    def copied(self):
        return self.type >> 7

    @copied.setter
    def copied(self, copied):
        self.type = ((copied & 128) << 7) | self.type

    @property
    def category(self):
        return (self.type & 96) >> 5

    @category.setter
    def category(self, category):
        self.type = ((category & 96) << 5) | self.type

    @property
    def number(self):
        return self.type & 31

    @number.setter
    def number(self, number):
        self.type = (number & 31) | self.type

    def __len__(self):
        if self.length:
            return self.length
        return self.__hdr_len__ + len(self.data)

    def __bytes__(self):
        return self.pack_hdr() + bytes(self.data)

    def unpack(self, buf):
        Packet.unpack(self, buf)
        self.data = buf[self.__hdr_len__:self.length + 1]


class IPOptions(IPOption):
    def unpack(self, buf):
        # TODO: create algorithm for options
        IPOption.unpack(self, buf)
        self.data = buf[self.__hdr_len__:self.length + 1]


def test_opt():
    s = b'\x4f\x00\x00\x3c\xae\x08\x00\x00\x40\x06\x18\x10\xc0\xa8\x0a\x26\xc0\xa8\x0a\x01\x87\x27\x08\x01\x02\x03\x04\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x05\x04\x03\x02\x01'
    ip = IP(s)
    opts = IPOption(ip.opts)
    assert (bytes(opts) == ip.opts)
    opts.length = 12
    assert (opts.length == 12)
    opts.copy = 1
    assert (opts.copy == 1)
    raw_opts = b'\x44\x0c\x05\x01\x00\x00\x00\x00\x00\x00\x00\x00'
    new_opts = IPOption(
        type=0x44,
        length=0x0c,
        data=b'\x05\x01\x00\x00\x00\x00\x00\x00\x00\x00'
    )
    assert (raw_opts == bytes(new_opts))


if __name__ == '__main__':
    test_opt()
    print('Tests Successful...')
