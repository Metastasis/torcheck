from torcheck.settings import BLACKLIST_PATH
from torcheck.utils import is_valid_ipv4_address


class Blacklist:
    def __init__(self):
        self.data = {}
        self.ips = {}

    def load(self, pathname=None):
        path = pathname

        if not path:
            path = BLACKLIST_PATH

        with open(path, 'r') as f:
            self.update_list(f.read().splitlines())

    def save(self):
        if not len(self.data.keys()):
            raise ValueError("Config is empty. Nothing to save")
        lines = ""
        for url, ip_list in self.data.items():
            lines = lines + "{};{}\n".format(url, ','.join(ip_list))
        with open(BLACKLIST_PATH, 'w+') as f:
            f.write(lines)

    def update_list(self, blacklist):
        for line in blacklist:
            if not line:
                continue
            url, ip_list = self._parse(line)

            self.data[url] = ip_list
            for ip in ip_list:
                self.ips[ip] = True

    def _parse(self, line):
        url, all_ip = line.split(';')
        ip_list = all_ip.split(',')

        return url, ip_list

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        if is_valid_ipv4_address(key):
            return key in self.ips
        return key in self.data

    def has(self, key):
        return self.__contains__(key)
