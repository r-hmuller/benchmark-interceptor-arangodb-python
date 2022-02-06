import multiprocessing
import random
import sys
from datetime import datetime
import time

import requests
from requests.auth import HTTPBasicAuth


def test_post_request(url, auth, directory):
    while True:
        random_number = random.randint(0, 100000)
        random_logger_number = random.randint(0, 5)
        if random_logger_number == 3:
            second_executed = datetime.now()
            start_time = datetime.now()
            r = requests.post(f"{url}/_api/document/python?waitForSync=true", json={"number": str(random_number)}, auth=auth, verify=False)
            print(r.status_code)
            r.close()
            end_time = datetime.now()
            latency_time = end_time - start_time
            with open(f"{directory}/latencies.csv", 'a+') as latencyFile:
                latencyFile.write(
                    f"{second_executed.strftime('%m/%d/%Y %H:%M:%S')},{str(latency_time.total_seconds() * 1000)}\n")

        else:
            r = requests.post(f"{url}/_api/document/python?waitForSync=true", json={"number": str(random_number)}, auth=auth, verify=False)
            r.close()
        time.sleep(0.1)


def get_throughput_from_arango(url, auth, initial_requests, directory):
    start_time = time.time()
    while True:
        time.sleep(60.0 - ((time.time() - start_time) % 60.0))
        second_executed = datetime.now()
        r = requests.get(f"{url}/_admin/statistics", auth=auth, verify=False)
        r.close()
        data = r.json()
        minute_throughput = int(data['http']['requestsPost']) - initial_requests
        initial_requests = data['http']['requestsPost']
        with open(f"{directory}/throughput.csv", 'a+') as throughputFile:
            throughputFile.write(f"{second_executed.strftime('%m/%d/%Y %H:%M:%S')},{str(minute_throughput)}\n")


if __name__ == '__main__':
    threadNumber = int(sys.argv[1])
    secondsToRun = int(sys.argv[2])
    testingUrl = sys.argv[3]
    files_directory = sys.argv[4]

    basic = HTTPBasicAuth('root', '')

    r = requests.get(f"{testingUrl}/_admin/statistics", auth=basic, verify=False)
    first_data = r.json()

    initial_requests = int(first_data['http']['requestsPost'])

    processes = []
    for i in range(threadNumber):
        name = f"TestLatency-{str(i)}"
        latency_process = multiprocessing.Process(target=test_post_request, name=name, args=(testingUrl, basic, files_directory))
        processes.append(latency_process)
        latency_process.start()
        time.sleep(0.1)
    throughput_process = multiprocessing.Process(target=get_throughput_from_arango, name="Throughput",
                                                args=(testingUrl, basic, initial_requests, files_directory))

    throughput_process.start()

    time.sleep(secondsToRun)

    if throughput_process.is_alive():
        throughput_process.terminate()
    for process in processes:
        if process.is_alive():
            process.terminate()
