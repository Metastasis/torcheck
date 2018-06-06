from settings import NODES_PATH
from urllib.request import urlopen
from utils import is_valid_ipv4_address


class TorNodes:
    def __init__(self):
        self.filepath = NODES_PATH
        self.node_list_url = 'https://torstatus.blutmagie.de/ip_list_all.php/Tor_ip_list_ALL.csv'
        self.list = []

    def update(self):
        with urlopen(self.node_list_url) as response:
            nodes_list = response.read().decode('utf-8').split('\n')
            self.list = list(filter(is_valid_ipv4_address, nodes_list))
        with open(self.filepath, 'w') as f:
            f.write('\n'.join(self.list))

    def load(self):
        with open(self.filepath, 'r') as f:
            self.list = f.read().splitlines()
            print(self.list)

    def __contains__(self, node):
        return node in self.list

    def has(self, node):
        return self.__contains__(node)
