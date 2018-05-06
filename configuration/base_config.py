class BaseConfig:
    def __init__(self, filename):
        self.PATH_TO_CONFIG = filename
        self.data = []

    def load(self, filename=None):
        if filename is None:
            filename = self.PATH_TO_CONFIG
        with open(filename, 'r+') as f:
            for line in f.read().splitlines():
                if not line:
                    continue
                parsed_line = self._parse_line(line)
                self.data.append(parsed_line)

    def save(self):
        if not len(self.data):
            raise ValueError("Config is empty. Nothing to save")
        with open(self.PATH_TO_CONFIG, 'w+') as f:
            f.write('\n'.join(self.data) + '\n')

    def _parse_line(self, line):
        return line
