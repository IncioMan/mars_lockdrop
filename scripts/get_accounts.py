import time
import pandas as pd

# import the Terra Python SDK modules
from terra_sdk.client.lcd import LCDClient

# create LCD
terra = LCDClient(url="https://lcd.terra.dev", chain_id="columbus-5")
# list of wallet addresses
msg = {"all_accounts": {}}

#terra1hzh9vpxhsk8253se0vv5jj6etdvxu3nv8z07zu aUST
#terra1kc87mu460fwkqte29rquh4hc20m54fxwtsx7gp bLuna
results = terra.wasm.contract_query("terra1kc87mu460fwkqte29rquh4hc20m54fxwtsx7gp", msg)
addresses = []
addresses=[*addresses,*results['accounts']]

last_address = addresses[-1:][0]
prev_last_address = ""

i=0
while(last_address != prev_last_address):
    prev_last_address = last_address
    msg = {"all_accounts": {"start_after":addresses[-1:][0],"limit":1000}}
    results = terra.wasm.contract_query("terra1kc87mu460fwkqte29rquh4hc20m54fxwtsx7gp", msg)
    addresses=[*addresses,*results['accounts']]
    last_address = addresses[-1:][0]
    i+=1
    if(i%100==0):
        print(len(set(addresses)))
        
pd.DataFrame(addresses).to_csv('./data/bLuna_addresses.csv')