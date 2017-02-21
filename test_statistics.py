import time
import threading
from test_config import statistics


class all(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        tmp = statistics()
        tmp.statistics_all()


class level(threading.Thread):

    def __init__(self, level):
        threading.Thread.__init__(self)
        self.level = level

    def run(self):
        tmp = statistics()
        tmp.statistics_level(level=self.level)


def main():
    tasks = []
    run_all = all()
    tasks.append(run_all)
    levels = [1, 2, 3, 4, 5, 6]
    for i in levels:
        run_level = level(level=i)
        tasks.append(run_level)
    for task in tasks:
        task.run()
    for task in tasks:
        task.join()

if __name__ == '__main__':
    while True:
        main()
        time.sleep(300)
