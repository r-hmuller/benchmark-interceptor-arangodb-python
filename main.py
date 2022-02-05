import multiprocessing
import random
import sys
from datetime import datetime, timedelta

import requests
from requests.auth import HTTPBasicAuth

latencies = []
throughput = []


def test_post_request(url, auth):
    random_number = random.randint(0, 100000)
    random_logger_number = random.randint(0, 30)
    if random_logger_number == 22:
        second_executed = datetime.now().timestamp()
        start_time = datetime.now()
        r = requests.post(f"${url}/_api/document/python", data={"number": str(random_number)}, auth=auth)
        end_time = datetime.now()
        latency_time = end_time - start_time
        latencies.append({str(second_executed): str(latency_time)})
    else:
        r = requests.post(f"${url}/_api/document/python", data={"number": str(random_number)}, auth=auth)


def get_throughput_from_arango(url, auth):
    pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    secondsToRun = int(sys.argv[1])
    testingUrl = sys.argv[2]
    filesDirectory = sys.argv[3]

    basic = HTTPBasicAuth('root', '')

    latencyProcess = multiprocessing.Process(target=test_post_request(), name="TestLatency", args=(testingUrl,basic,))
    throughputProcess = multiprocessing.Process(target=get_throughput_from_arango, name="Throughput", args=(testingUrl,basic))

    latencyProcess.start()
    throughputProcess.start()
    now = datetime.now()
    stopAt = now + timedelta(seconds=secondsToRun)
    while True:
        if now >= stopAt:
            if latencyProcess.is_alive():
                latencyProcess.terminate()
            if throughputProcess.is_alive():
                throughputProcess.is_alive()
        break

    with open(f"${filesDirectory}/throughput.txt") as throughputFile:
        for t in throughput:
            throughputFile.write(t)

    with open(f"${filesDirectory}/latencies.txt") as latencyFile:
        for l in latencies:
            for i in l:
                latencyFile.write(f"${i},${l[i]}")
