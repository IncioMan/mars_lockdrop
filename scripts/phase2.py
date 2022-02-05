import time
import pandas as pd

# import the Terra Python SDK modules
from terra_sdk.client.lcd import LCDClient

# list of deposit wallets
df_claim = pd.read_json(
            "https://api.flipsidecrypto.com/api/v2/queries/499224b4-30a6-43d7-80b9-3a019cbb1d3d/data/latest",
            convert_dates=["BLOCK_TIMESTAMP"],
        )

# create LCD
terra = LCDClient(url="https://lcd.terra.dev", chain_id="columbus-5")

deposit_info = []

print(len(df_claim))
# list of wallet addresses
i = 0
for _, item in df_claim['SENDER'].iteritems():

  msg = {"deposit_info": {"address": item}}

  results = terra.wasm.contract_query("terra1angxk38zehp0k09m0wqrrxf0r3ces6qjj432l8", msg)

  # turn on sleep here
  # time.sleep(2)

  #print(results)

  deposit_info.append({'sender': item, **results})
  i+=1
  if(i%500==0):
    print(i)

# list to df
df = pd.DataFrame(deposit_info)
df.deposit=df.deposit.apply(int)/1000000
df.total_deposit=df.total_deposit.apply(int)/1000000
df.withdrawable_amount=df.withdrawable_amount.apply(int)/1000000
df.tokens_to_claim=df.tokens_to_claim.apply(int)/1000000

# dump to csv
df.to_csv('data/with_phase1.csv')
# upload to your GitHub