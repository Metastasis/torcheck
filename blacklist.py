from config import BLACKLIST_PATH


class Blacklist:
    def __init__(self):
        self.data = {}
        pass

    def load(self, pathname=None):
        path = pathname

        if not path:
            path = BLACKLIST_PATH

        with open(path, 'r') as f:
            for line in f.read().splitlines():
                if not line:
                    continue

                url, ip_list = self._parse(line)

                self.data[url] = ip_list
                for ip in ip_list:
                    self.data[ip] = url

    def _parse(self, line):
        url, all_ip = line.split(';')
        ip_list = all_ip.split(',')

        return url, ip_list

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return key in self.data

    def has(self, key):
        return self.__contains__(key)


# if __name__ == '__main__':
#     blacklist = Blacklist()
#     blacklist.load()
#     print('parimatch-go2.com' in blacklist.data)
#     print('104.28.0.94' in blacklist.data)
#     print('parimatch-go2.com' in blacklist)
#     print('104.28.0.94' in blacklist)
#     print(blacklist.has('parimatch-go2.com'))
#     print(blacklist.has('104.28.0.94'))
#     print('parimatc.com' in blacklist.data)
#     print('parimatc.com' in blacklist)
#     print(blacklist.has('104.28.3.94'))
