import pandas as pd
from constants import cols_dict

class DataProvider:
    
    def load_data(self):
        self.user_stats_df = self.claim(self.user_stats, self.cols_claim)
        self.deposit_balance_df = self.claim(self.deposit_balance, self.cols_claim)
        self.deposits_bucket_df = self.claim(self.deposits_bucket, self.cols_claim)
        self.wallet_age_df = self.claim(self.wallet_age, self.cols_claim)
        self.hourly_stats_df = self.claim(self.hourly_stats, self.cols_claim)
        self.prev_launches_df = self.claim(self.prev_launches, self.cols_claim)

        self.user_stats_df['DEPOSIT_NET'] = self.user_stats_df.DEPOSIT_AMOUNT - self.user_stats_df.WITHDRAWN_AMOUNT
        self.user_stats_df['N_TXS'] = self.user_stats_df.DEPOSIT_TXS + self.user_stats_df.WITHDRAW_TXS
        self.top_depositors = self.user_stats_df.sort_values(by='DEPOSIT_NET', ascending=False).head(5)[['SENDER','DEPOSIT_NET']]\
                    .set_index('SENDER').rename(columns=cols_dict)

        self.hourly_new_users_df = self.claim(self.hourly_new_users, self.cols_claim)
        self.hourly_new_users_df['cumsum_new_users'] = self.hourly_new_users_df.sort_values(by='TIME').NEW_USERS.cumsum()
        self.hourly_new_users_df['Hour'] = self.hourly_new_users_df['TIME']
        df = self.hourly_new_users_df.sort_values(by='TIME')
        index = df.index
        if(len(index)>1):
            i = -2
            self.next_last_users = df.loc[index[i]].cumsum_new_users
        else:
            self.next_last_users = 0
        self.hourly_new_users_df = self.hourly_new_users_df.rename(columns=cols_dict)


        self.wallet_age_df = self.wallet_age_df.rename(columns=cols_dict)

        self.hourly_stats_df['cumsum_ust'] = self.hourly_stats_df.sort_values(by='HR').NET_AMOUNT.cumsum()
        self.hourly_stats_df['cumsum_txs'] = self.hourly_stats_df.sort_values(by='HR').TOT_TXS.cumsum()
        self.hourly_stats_df['Hour'] = self.hourly_stats_df['HR']
        df = self.hourly_stats_df.sort_values(by='HR')
        index = df.index
        if(len(index)>1):
            i = -2
            self.next_last_ust = df.loc[index[i]].cumsum_ust
            self.next_last_txs = df.loc[index[i]].cumsum_txs
        else:
            i = 0
            self.next_last_ust = 0
            self.next_last_txs = 0
        self.hourly_stats_df = self.hourly_stats_df.rename(columns=cols_dict)



        self.n_txs = self.user_stats_df.DEPOSIT_TXS.sum() + self.user_stats_df.WITHDRAW_TXS.sum()
        self.n_users = self.user_stats_df.SENDER.nunique()
        self.tot_deposits = int(self.user_stats_df.DEPOSIT_AMOUNT.sum() - self.user_stats_df.WITHDRAWN_AMOUNT.sum())


        self.prev_launches_df = self.prev_launches_df.rename(columns=cols_dict)

        self.deposit_balance_df = self.deposit_balance_df.rename(columns=cols_dict)
        self.deposits_bucket_df['bucket_name']= self.deposits_bucket_df.BUCKET.map({0:'-$0',1:'$0-$10',2:'$10-$100',3:'$100-$1k',4:'$1k-$10k',
                                        5:'$10k-$100k',6:'$100k-$1m',7:'$1m-'})
        self.deposits_bucket_df.sort_values(by='BUCKET')

        self.dates_to_mark = pd.DataFrame([
            ['2021-03-04', '2021-03-11',15,'Anchor launch'],
            ['2021-09-24', '2021-10-01',15,'Columbus 5'],
            ['2021-12-12', '2021-12-19',15,'Astroport launch'], 
            ['2022-01-24', '2022-02-01',15,'Prism launch']], 
            columns=['text_date','date','height','text']
        )
    
    def load_data_phase2(self):
        self.p2_users_df = self.claim(self.p2_users, self.cols_claim)

    def __init__(self, claim):
        self.claim = claim

        self.user_stats = '499224b4-30a6-43d7-80b9-3a019cbb1d3d'
        self.deposits_bucket = 'b4953cda-a874-43fa-b78d-ceb0c1bfc3cf'
        self.deposit_balance = '9e2e9587-0850-466a-8a59-4dda2e8337f3'
        self.hourly_new_users = '65179a1e-fd70-43eb-a9e4-ce14b716c928'
        self.wallet_age = '5b7983de-8596-42de-a997-767754746b71'
        self.hourly_stats = '520fb3b6-a968-4742-bf0a-31cbb67b6b05'
        self.prev_launches = '4eac9ed8-be31-4cf4-9bbe-2a0776d224ad'
        ###
        self.p2_users = '07f87a6f-5bc6-49f3-a1bb-8e7d545ba95a'

        self.cols_claim = {
            self.user_stats : ['DEPOSIT_AMOUNT', 'DEPOSIT_TXS', 'SENDER', 'WITHDRAWN_AMOUNT',
            'WITHDRAW_TXS'],
            self.deposits_bucket : ['BUCKET', 'N_USERS'],
            self.prev_launches : ['PARTICIPANTS', 'PARTICIPATE_TYPE', 'TYPE'],
            self.hourly_stats : ['DEPOSIT_AMOUNT', 'DEPOSIT_TX', 'DEP_USERS', 'HR', 'NET_AMOUNT',
            'TOT_TXS', 'TOT_USERS', 'WITH_AMOUNT', 'WITH_TX', 'WITH_USERS'],
            self.wallet_age : ['ADDRESS_COUNT', 'MIN_DATE'],
            self.deposit_balance: ['AMOUNT', 'AVG_BALANCE_USD', 'MAX_BALANCE_USD', 'N_TXS', 'SENDER'],
            self.hourly_new_users: ['NEW_USERS', 'TIME'],
            self.p2_users: ["DEPOSIT_AMOUNT","HR","NET_DEPOSITED_AMOUNT","SENDER","WITHDRAWN_AMOUNT","WITHDRAWN_AMOUNT_PHASE2"]
        }
        self.load_data()