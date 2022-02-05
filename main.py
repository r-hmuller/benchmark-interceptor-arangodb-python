import multiprocessing
import random
import sys
from datetime import datetime, timedelta
import time

import requests
from requests.auth import HTTPBasicAuth

latencies = []
throughput = []
initial_requests = 0


def test_post_request(url, auth):
    random_number = random.randint(0, 100000)
    random_logger_number = random.randint(0, 30)
    if random_logger_number == 22:
        second_executed = datetime.now().timestamp()
        start_time = datetime.now()
        requests.post(f"{url}/_api/document/python", data={"number": str(random_number)}, auth=auth, verify=False)
        end_time = datetime.now()
        latency_time = end_time - start_time
        latencies.append({str(second_executed): str(latency_time)})
    else:
        requests.post(f"{url}/_api/document/python", data={"number": str(random_number)}, auth=auth, verify=False)


def get_throughput_from_arango(url, auth):
    global initial_requests
    start_time = time.time()
    while True:
        r = requests.get(f"{url}/_admin/statistics", auth=auth, verify=False)
        data = r.json()
        minute_throughput = int(data['http']['requestsPost']) - initial_requests
        throughput.append(minute_throughput)
        initial_requests = minute_throughput
        time.sleep(60.0 - ((time.time() - start_time) % 60.0))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #Argumentos: 300 https://137.184.12.131:32384 E:\Projetos
    secondsToRun = int(sys.argv[1])
    testingUrl = sys.argv[2]
    filesDirectory = sys.argv[3]

    basic = HTTPBasicAuth('root', '')

    r = requests.get(f"{testingUrl}/_admin/statistics", auth=basic, verify=False)
    first_data = r.json()

    initial_requests = int(first_data['http']['requestsPost'])

    #latencyProcess = multiprocessing.Process(target=test_post_request(), name="TestLatency", args=(testingUrl, basic,))
    throughputProcess = multiprocessing.Process(target=get_throughput_from_arango, name="Throughput",
                                                args=(testingUrl, basic))

    #latencyProcess.start()
    throughputProcess.start()
    now = datetime.now()
    stopAt = now + timedelta(seconds=secondsToRun)
    while True:
        if now >= stopAt:
            #if latencyProcess.is_alive():
            #    latencyProcess.terminate()
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
