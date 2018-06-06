from config import CLIENTLOG_PATH
from datetime import datetime, timedelta
import pickle


class ClientLog:
    def __init__(self):
        self.ONE_MINUTE = timedelta(minutes=1)

    def find_first_arrived(self, data):
        copy = data.copy()
        copy.reverse()
        first_marked = next((k for k, v in enumerate(copy) if v[1] == 1), None)
        if first_marked is None and len(data):
            return len(data) - 1
        if not len(data):
            return None
        search_from = len(data) - first_marked
        rest_unmarked = data[search_from:]
        first_arrived_idx = next((k for k, v in enumerate(rest_unmarked) if v[1] == 0), None)
        return search_from + first_arrived_idx

    def arrived_near(self, date):
        with open(CLIENTLOG_PATH, 'rb') as input:
            data = pickle.load(input)
            time = date - self.ONE_MINUTE
            last_arrived = [v for v in data if v[0] >= time]
            if not len(last_arrived):
                return False
            arrived_idx = self.find_first_arrived(last_arrived)
            if arrived_idx is None:
                return False
            [date, flag] = last_arrived[arrived_idx]
            last_arrived[arrived_idx] = [date, 1]
            with open(CLIENTLOG_PATH, 'wb') as output:
                pickle.dump(last_arrived, output)
            return True

    def log(self, date=datetime.now()):
        with open(CLIENTLOG_PATH, 'rb') as input:
            data = pickle.load(input)
            data.append([date, 0])
            with open(CLIENTLOG_PATH, 'wb') as output:
                pickle.dump(data, output)

    def clean(self):
        with open(CLIENTLOG_PATH, 'wb'):
            pass
