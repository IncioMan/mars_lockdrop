import pandas as pd
from constants import cols_dict
import requests
import random

class DataProvider:
    
    def load_data(self):
        ##Users stats
        self.user_stats_df = self.claim(self.user_stats,self.cols_claim,self.data_claim)
        self.user_stats_df.columns = [c.lower() for c in self.user_stats_df.columns]
        
        self.count_durations_users = \
            self.user_stats_df.groupby('sender').duration.nunique().reset_index()\
                 .groupby('duration').sender.count().reset_index()\
                 .rename(columns={
                            'duration':'Number of lockup durations',
                            'sender':'Number of users'})
        ##Hourly new users
        self.hourly_new_users_df = self.claim(self.hourly_new_users,self.cols_claim,self.data_claim)
        self.hourly_new_users_df.columns = [c.lower() for c in self.hourly_new_users_df.columns]
        self.hourly_new_users_df=self.hourly_new_users_df.sort_values(by='time',ascending=True)
        self.hourly_new_users_df['cumsum_new_users'] = self.hourly_new_users_df.new_users.cumsum()

        ##Hourly stats
        self.hourly_stats_df = self.claim(self.hourly_stats,self.cols_claim,self.data_claim)
        self.hourly_stats_df.columns = [c.lower() for c in self.hourly_stats_df.columns]
        self.hourly_stats_df = self.hourly_stats_df.sort_values(by='hr',ascending=True)
        self.hourly_stats_df['net_deposit_3'] = (self.hourly_stats_df.dep_amount_3-self.hourly_stats_df.with_amount_3).cumsum()
        self.hourly_stats_df['net_deposit_6'] = (self.hourly_stats_df.dep_amount_6-self.hourly_stats_df.with_amount_6).cumsum()
        self.hourly_stats_df['net_deposit_9'] = (self.hourly_stats_df.dep_amount_9-self.hourly_stats_df.with_amount_9).cumsum()
        self.hourly_stats_df['net_deposit_12'] = (self.hourly_stats_df.dep_amount_12-self.hourly_stats_df.with_amount_12).cumsum()
        self.hourly_stats_df['net_deposit_15'] = (self.hourly_stats_df.dep_amount_15-self.hourly_stats_df.with_amount_15).cumsum()
        self.hourly_stats_df['net_deposit_18'] = (self.hourly_stats_df.dep_amount_18-self.hourly_stats_df.with_amount_18).cumsum()
        self.hourly_stats_df['tot_txs'] = self.hourly_stats_df.with_tx + self.hourly_stats_df.deposit_tx

        self.time_duration_df = self.hourly_stats_df[['hr','net_deposit_3','net_deposit_6','net_deposit_9','net_deposit_12','net_deposit_15','net_deposit_18']]
        self.time_duration_df = self.time_duration_df.rename(columns={
            'net_deposit_3':'3 months',
            'net_deposit_6':'6 months',
            'net_deposit_9':'9 months',
            'net_deposit_12':'12 months',
            'net_deposit_15':'15 months',
            'net_deposit_18':'18 months'
        })
        self.time_duration_df = self.time_duration_df.melt(id_vars=["hr"], 
                var_name="Lockup period", 
                value_name="UST deposited")

        self.last_duration_amount = self.hourly_stats_df[self.hourly_stats_df.hr==self.hourly_stats_df.hr.max()]
        self.last_duration_amount= self.last_duration_amount[['net_deposit_3','net_deposit_6','net_deposit_9',
                            'net_deposit_12','net_deposit_15','net_deposit_18']]
        self.last_duration_amount = self.last_duration_amount.rename(columns={
                    'net_deposit_3':'3 months',
                    'net_deposit_6':'6 months',
                    'net_deposit_9':'9 months',
                    'net_deposit_12':'12 months',
                    'net_deposit_15':'15 months',
                    'net_deposit_18':'18 months'
                })
        self.last_duration_amount = self.last_duration_amount.T.reset_index()
        self.last_duration_amount.columns = ['Lockup period','UST deposited']

        #Wallet age
        self.wallet_age_df = self.claim(self.wallet_age,self.cols_claim,self.data_claim)
        self.wallet_age_df.columns = [c.lower() for c in self.wallet_age_df.columns]
        self.dates_to_mark = pd.DataFrame([
            ['2021-03-04', '2021-03-08',80,'Anchor launch'],
            ['2021-09-24', '2021-09-28',80,'Columbus 5'],
            ['2021-12-12', '2021-12-16',80,'Astroport launch'], 
            ['2022-01-24', '2022-01-28',80,'Prism launch']], 
            columns=['text_date','date','height','text']
        )

        ##Balance
        self.users_balance_df = self.claim(self.users_balance,self.cols_claim,self.data_claim)
        self.users_balance_df.columns = [c.lower() for c in self.users_balance_df.columns]
        self.user_stats_df['dur_amount']=self.user_stats_df.duration * self.user_stats_df.amount
        df = self.user_stats_df.groupby('sender').agg(mean_duration=('duration', 'mean'),
                                              dur_sum=('dur_amount', 'sum'),
                                              amnt_sum=('amount', 'sum'))
        df['weighted_avg_dur'] = df.dur_sum/df.amnt_sum
        self.users_balance_df = df.reset_index().merge(self.users_balance_df, on='sender')


    def __init__(self, claim, get_url=None):
        self.claim = claim
        self.get_url = get_url


        self.user_stats = '1'
        self.hourly_new_users = '2'
        self.wallet_age = '3'
        self.hourly_stats = '4'
        self.users_balance = '5'
        ###
        self.cols_claim = {
            self.user_stats : ['SENDER', 'DURATION', 'AMOUNT'],
            self.hourly_stats : ['HR', 
                                'DEP_AMOUNT', 'DEPOSIT_TX', 'DEP_USERS',
                                'WITH_AMOUNT', 'WITH_TX', 'WITH_USERS',
                                'DEP_AMOUNT_3', 'DEP_AMOUNT_6', 'DEP_AMOUNT_9','DEP_AMOUNT_12', 'DEP_AMOUNT_15', 'DEP_AMOUNT_18',
                                'WITH_AMOUNT_3', 'WITH_AMOUNT_6', 'WITH_AMOUNT_9','WITH_AMOUNT_12', 'WITH_AMOUNT_15', 'WITH_AMOUNT_18',
            ],
            self.wallet_age : ['MIN_DATE','ADDRESS_COUNT'],
            self.hourly_new_users: ['TIME','NEW_USERS'],
            self.users_balance: ['SENDER','BALANCE'],
        }
        users_stats = [['user1_1',3,10],
                    ['user1_2',3,3],
                    ['user1_3',3,4],
                    ['user1_4',3,67],
                    ['user1_5',3,33],
                    ['user1',9,20],
                    ['user1',18,15],
                    ['user2',3,10],
                    ['user2',6,120],
                    ['user2',18,13],
                    ['user2',3,10],
                    ['user3',6,120],
                    ['user3',18,13]]
        for i in range(0,100):
             users_stats.append([f'user{i}',random.choice([3,6,9,12,15,18]),random.randint(0,100000)])
        users_balance = [['user1',100],
                            ['user1_2',20],
                            ['user1_3',50],
                            ['user1_4',70],
                            ['user1_5',80],
                            ['user2',70],
                            ['user3',80]]
        for i in range(0,100):
            users_balance.append([f'user{i}',random.randint(0,100000)])
        
        wallet_age = []
        for i in range(1,31):
            wallet_age.append([f'2021-09-{"{:02d}".format(i)}T09:00:00Z',random.randint(0,10)])
        for i in range(1,32):
            wallet_age.append([f'2021-10-{"{:02d}".format(i)}T09:00:00Z',random.randint(0,10)])
        for i in range(1,31):
            wallet_age.append([f'2021-11-{"{:02d}".format(i)}T09:00:00Z',random.randint(0,10)])
        for i in range(1,32):
            wallet_age.append([f'2021-12-{"{:02d}".format(i)}T09:00:00Z',random.randint(0,10)])
        for i in range(1,32):
            wallet_age.append([f'2022-01-{"{:02d}".format(i)}T09:00:00Z',random.randint(0,10)])

        print(wallet_age)
        self.data_claim = {
            self.user_stats : users_stats,
            self.hourly_stats : [['2021-09-21T07:00:00Z',1000,4,3,
                        100,1,1,
                        10,20,30,40,50,60,
                        0,0,10,0,0,0],
                    ['2021-09-21T08:00:00Z',1000,4,3,
                        200,1,1,
                        10,10,30,10,50,5,
                        0,0,0,0,7,0],
                    ['2021-09-21T09:00:00Z',1000,4,3,
                        200,1,1,
                        10,10,30,10,50,5,
                        0,0,0,0,7,0],['2021-09-21T10:00:00Z',1000,4,3,
                        100,1,1,
                        10,20,30,40,50,60,
                        0,0,10,0,0,0],
                    ['2021-09-21T11:00:00Z',1000,4,3,
                        200,1,1,
                        10,10,30,10,50,5,
                        0,0,0,0,7,0],
                    ['2021-09-21T12:00:00Z',1000,4,3,
                        200,1,1,
                        10,10,30,10,50,5,
                        0,0,0,0,7,0]],
            self.wallet_age : wallet_age,
            self.hourly_new_users: [['2021-09-21T07:00:00Z',1000],
                                    ['2021-09-21T08:00:00Z',600],
                                    ['2021-09-21T09:00:00Z',200],
                                    ['2021-09-21T10:00:00Z',1000],
                                    ['2021-09-21T11:00:00Z',100],
                                    ['2021-09-21T12:00:00Z',140]],                  
            self.users_balance: users_balance
    }