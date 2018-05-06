from config import CLIENTLOG_PATH
from datetime import datetime


class ClientLog:
    def __init__(self, recent_clients=5):
        self.RECENT_CLIENTS = recent_clients
        self.FIVE_SECONDS = 5
        self.DATE_FORMAT = "%Y-%m-%d %H:%M:%S:%f"

    def arrived_near(self, date=datetime.now()):
        """
        :param date: recent clients arrivals times will be checked against this date
        :return: True if theres client that has been arrived recently
        """
        lines_read = 0
        arrivals = []
        # TODO: should somehow mark lines that has been used
        with open(CLIENTLOG_PATH, 'r') as f:
            last_n_lines = f.read().splitlines()[-self.RECENT_CLIENTS:]
            for line in last_n_lines:
                if not line:
                    continue
                lines_read = lines_read + 1
                if lines_read > self.RECENT_CLIENTS:
                    break
                time = self._parse(line)
                arrive_time = datetime.strptime(time, self.DATE_FORMAT)
                arrivals.append(arrive_time)
        for arrive in arrivals:
            diff = date - arrive
            diff = diff.total_seconds()
            if diff >= 0 and diff <= self.FIVE_SECONDS:
                return True
        return False

    def log(self, date=datetime.now()):
        with open(CLIENTLOG_PATH, 'a') as f:
            line = date.strftime(self.DATE_FORMAT) + "\n"
            f.write(line)
        return True

    def clean(self):
        with open(CLIENTLOG_PATH, 'r') as f:
            last_n_lines = f.read().splitlines()[-self.RECENT_CLIENTS:]
        with open(CLIENTLOG_PATH, 'w') as f:
            f.write('\n'.join(last_n_lines) + '\n')

    def _parse(self, line):
        return line
