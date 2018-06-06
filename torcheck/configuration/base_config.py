class BaseConfig:
    # TODO: add files in data folder to .gitignore
    def __init__(self):
        self.data = []

    def load(self, filename):
        with open(filename, 'r') as f:
            for line in f.read().splitlines():
                if not line:
                    continue
                parsed_line = self._parse_line(line)
                self.data.append(parsed_line)

    def save(self, filename):
        if not len(self.data):
            raise ValueError("Config is empty. Nothing to save")
        with open(filename, 'w+') as f:
            f.write('\n'.join(self.data) + '\n')

    def _parse_line(self, line):
        return line
