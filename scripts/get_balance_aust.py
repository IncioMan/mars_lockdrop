import queue, time, urllib.request
from threading import Thread
import pandas as pd
from terra_sdk.client.lcd import LCDClient

def perform_web_requests(contract_address, addresses, no_workers):
    class Worker(Thread):
        def __init__(self, request_queue, contract_address):
            Thread.__init__(self)
            self.queue = request_queue
            self.contract_address = contract_address
            self.results = []
            self.terra = LCDClient(url="https://lcd.terra.dev", chain_id="columbus-5")


        def run(self):
            while True:
                address = self.queue.get()
                if address == "":
                    break
                msg = {"balance": {"address":address}}
                request_not_succeded = True
                results = {'balance':0}
                while(request_not_succeded):
                    try:
                        results = self.terra.wasm.contract_query(self.contract_address, msg)
                        request_not_succeded = False
                    except:
                        print('Request failed, retrying...',address)
                        request_not_succeded = True
                        time.sleep(1)
                self.results.append((address,(results['balance'] if 'balance' in results else '0')))
                self.queue.task_done()

    # Create queue and add addresses
    q = queue.Queue()
    for address in addresses:
        q.put(address)

    # Workers keep working till they receive an empty string
    for _ in range(no_workers):
        q.put("")

    # Create workers and add tot the queue
    workers = []
    for _ in range(no_workers):
        time.sleep(1)
        worker = Worker(q, contract_address)
        worker.start()
        workers.append(worker)
    # Join workers to wait till they finished
    for worker in workers:
        worker.join()

    # Combine results from all workers
    r = []
    for worker in workers:
        r.extend(worker.results)
    return r

addresses = pd.read_csv('./data/aUST_addresses.csv')['0'].values
addresses = addresses[:int(len(addresses)/2)]
print('Working on first half...')
addr_balances = pd.read_csv('./data/balances/aUST.csv').address.values
addresses = set(addresses).difference(set(addr_balances))
while(len(addresses) > 0):
    print(f'Left to query: {len(addresses)} addresses')
    results = perform_web_requests('terra1hzh9vpxhsk8253se0vv5jj6etdvxu3nv8z07zu',list(addresses)[:100], 1)
    balances = pd.DataFrame(results, columns=['address','aUST_balance'])
    balances.to_csv('./data/balances/aUST.csv',mode='a',header=False)
    addr_balances = pd.read_csv('./data/balances/aUST.csv').address.values
    addresses = set(addresses).difference(set(addr_balances))
