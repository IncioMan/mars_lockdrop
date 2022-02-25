import pandas as pd
from constants import tot_ust_rewards, tot_mars_rewards, cols_dict, mars_tokens, aust_price,bluna_price
import requests
import random

class DataProvider:
    
    def load_data_lba(self):
        ### Users stats
        user_stats_df = self.claim(self.user_stats,self.cols_claim,self.data_claim)
        user_stats_df.columns = [c.lower() for c in user_stats_df.columns]
        
        ##Airdrops
        airdrop_claims_df = self.claim(self.airdrop_claims,self.cols_claim,self.data_claim)
        airdrop_claims_df.columns = [c.lower() for c in airdrop_claims_df.columns]
        
        ### LBA Deposits
        lba_deposits_df = self.claim(self.lba_deposits,self.cols_claim,self.data_claim)
        lba_deposits_df.columns = [c.lower() for c in lba_deposits_df.columns]
        lba_deposits_df['time'] = pd.to_datetime(lba_deposits_df.time)
        lba_deposits_df['amount'] = lba_deposits_df.apply(lambda row: -row.amount if row.action=='withdraw' else row.amount, axis=1)
        
        ## Hourly Airdrops
        lba_deposits_df['hour'] = lba_deposits_df.time.dt.strftime("%Y-%m-%d %H:00")
        mars = lba_deposits_df[lba_deposits_df.denom=='MARS']
        ust = lba_deposits_df[lba_deposits_df.denom=='UST']
        df_mars = mars.groupby(['denom','hour']).amount.sum().reset_index().sort_values(by='hour')
        df_mars['cumsum'] = df_mars.amount.cumsum()
        df_ust = ust.groupby(['denom','hour']).amount.sum().reset_index().sort_values(by='hour')
        df_ust['cumsum'] = df_ust.amount.cumsum()
        lba_deposits_hourly_df = df_ust.append(df_mars)
        self.lba_deposits_hourly_df=lba_deposits_hourly_df

        ## Users Partecipation
        aidrop_users = airdrop_claims_df.sender.unique()
        aidrop_users_df = pd.DataFrame(aidrop_users, columns=['sender'])
        aidrop_users_df['type'] = 'Airdrop'
        p1_users = user_stats_df.sender.unique()
        p1_users_df = pd.DataFrame(p1_users, columns=['sender'])
        p1_users_df['type'] = 'Phase1'
        users_type = aidrop_users_df.append(p1_users_df)
        users_type = users_type.merge(users_type.groupby('sender').type.count().rename('n_types').reset_index(), on=['sender'], how='left')
        users_type['new_type'] = users_type.apply(lambda row: row.type if row.n_types==1 else 'Airdrop/Phase1', axis=1)
        users_type = users_type[["sender","new_type"]].drop_duplicates()

        ## LBA Mars origin
        mars_source = users_type.merge(lba_deposits_df[lba_deposits_df.denom=='MARS'], on='sender').groupby('new_type').amount.sum()
        mars_source = mars_source.reset_index()
        self.mars_source=mars_source

        ## Metrics
        users_aidrop_eligible = 66103
        perc_airdrop_eligible = len(airdrop_claims_df.sender.unique())/users_aidrop_eligible
        perc_airdrop_eligible
        #Phase 1 + airdrop
        mars_total = 60000000
        mars = lba_deposits_hourly_df[lba_deposits_hourly_df.denom=='MARS']
        self.act_mars_lba = mars[mars.hour == mars.hour.max()]["cumsum"].values[0]
        self.perc_mars_in_lba = self.act_mars_lba/mars_total
        #
        usts = lba_deposits_hourly_df[lba_deposits_hourly_df.denom=='UST']
        self.act_usts_lba = usts[usts.hour == mars.hour.max()]["cumsum"].values[0]
        self.act_price = self.act_mars_lba/self.act_usts_lba
        #
        users_p1 = len(user_stats_df.sender.unique())
        users_p1_lba = len(set(user_stats_df.sender.unique()).intersection(set(lba_deposits_df.sender.unique())))
        self.perc_p1_lba = users_p1_lba/users_p1
        ## P1 MARS rewards
        boost = pd.DataFrame([1,2.8,5.2,8,11.2,14.7],columns=['boost'],index=[3,6,9,12,15,18])
        boost = user_stats_df.groupby('duration').sum().join(boost)
        boost['amount_boosted'] = boost.amount * boost.boost    
        boost['amount_boosted_mars'] = (boost['amount_boosted']/boost['amount_boosted'].sum())*50000000
        boost['amount_per_ust'] = boost['amount_boosted_mars']/boost.amount
        boost

        ## % il LBA from P1 for each user
        user_stats_df = user_stats_df.merge(boost.reset_index()[['duration','amount_per_ust']], on=['duration'])
        user_stats_df['mars'] = user_stats_df.amount * user_stats_df.amount_per_ust
        user_p1_mars = user_stats_df.groupby('sender').mars.sum()
        user_p1_perc_mars = lba_deposits_df[lba_deposits_df.denom=='MARS'].groupby('sender').sum().join(user_p1_mars).fillna(0)
        user_p1_perc_mars['perc_p1_mars_lba'] = user_p1_perc_mars.apply(lambda row: 0 if ((row.mars == 0) or (row.amount==0)) else row.amount / row.mars,axis=1)
        self.user_p1_perc_mars = user_p1_perc_mars

        ## APR P2
        x,y, self.roi_phase_2 = self.get_lba_rewards(0,0,1)

        ## What have users deposited
        df = lba_deposits_df.groupby(['sender','denom']).amount.sum().reset_index() 
        df2 = df[df.amount>0].groupby('sender').denom.count().rename('n_denom')
        df3 = df.merge(df2.reset_index(), on='sender')
        df3['dep_type'] = df3.apply(lambda row: row.denom if row.n_denom==1 else 'MARS & UST', axis=1)
        user_dep_type = df3.groupby(['dep_type']).sender.count().reset_index()
        self.user_dep_type = user_dep_type

        ### MARS ROI Phase 1
        mars_roi_df = self.claim(self.mars_roi_p1,self.cols_claim,self.data_claim)
        mars_roi_df.columns = [c.lower() for c in mars_roi_df.columns]
        mars_roi_df.index = ['UST deposited','n_months','boost']
        self.mars_roi_p1 = mars_roi_df
        self.p1_roi_curr_price,_ = self.get_mars_tokens_aprs(0,'3 months',self.act_price)

    def load_data(self):
        self.aust_balance = self.get_url('https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master/data/balances/aUST.csv', index_col=1).drop(columns=['Unnamed: 0'])
        self.bluna_balance = self.get_url('https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master/data/balances/bLuna.csv', index_col=1).drop(columns=['Unnamed: 0'])
        
        self.aust_balance =  self.aust_balance /1000000 * aust_price
        self.bluna_balance =  self.bluna_balance /1000000 * bluna_price
        ##Users stats
        self.user_stats_df = self.claim(self.user_stats,self.cols_claim,self.data_claim)
        self.user_stats_df.columns = [c.lower() for c in self.user_stats_df.columns]
        
        self.count_durations_users = \
            self.user_stats_df.groupby('sender').duration.nunique().reset_index()\
                 .groupby('duration').sender.count().reset_index()\
                 .rename(columns={
                            'duration':'Number of lockup durations',
                            'sender':'Number of users'})
        self.top_depositors = self.user_stats_df.sort_values(by='amount', ascending=False).head(5)[['sender','amount','duration']]\
                                                .set_index('sender').rename(columns={'amount':'Amount locked (UST)','duration':'Lockup duration'})
        ##Hourly new users
        self.hourly_new_users_df = self.claim(self.hourly_new_users,self.cols_claim,self.data_claim)
        self.hourly_new_users_df.columns = [c.lower() for c in self.hourly_new_users_df.columns]
        self.hourly_new_users_df=self.hourly_new_users_df.sort_values(by='time',ascending=True)
        self.hourly_new_users_df['cumsum_new_users'] = self.hourly_new_users_df.new_users.cumsum()
        self.n_users = self.hourly_new_users_df.cumsum_new_users.max()
        ##Hourly stats
        hourly_stats_df = self.claim(self.hourly_stats,self.cols_claim,self.data_claim)
        hourly_stats_df.columns = [c.lower() for c in hourly_stats_df.columns]
        self.last_udpate = pd.to_datetime(hourly_stats_df.hr).max().strftime("%d-%m-%Y %H:%M")
        ###
        dep_amount = hourly_stats_df[hourly_stats_df.type_action=='deposit'].groupby('hr').amount.sum().rename('DEP_AMOUNT')
        dep_txs = hourly_stats_df[hourly_stats_df.type_action=='deposit'].groupby('hr').n_txs.sum().rename('DEPOSIT_TX')
        dep_users = hourly_stats_df[hourly_stats_df.type_action=='deposit'].groupby('hr').n_users.sum().rename('DEP_USERS')

        with_amount = hourly_stats_df[hourly_stats_df.type_action=='withdraw'].groupby('hr').amount.sum().rename('WITH_AMOUNT')
        with_txs = hourly_stats_df[hourly_stats_df.type_action=='withdraw'].groupby('hr').n_txs.sum().rename('WITH_TX')
        with_users = hourly_stats_df[hourly_stats_df.type_action=='withdraw'].groupby('hr').n_users.sum().rename('WITH_USERS')

        dep_amount_3 = hourly_stats_df[(hourly_stats_df.type_action=='deposit')&(hourly_stats_df.duration==3)].groupby('hr').amount.sum().rename('DEP_AMOUNT_3')
        dep_amount_6 = hourly_stats_df[(hourly_stats_df.type_action=='deposit')&(hourly_stats_df.duration==6)].groupby('hr').amount.sum().rename('DEP_AMOUNT_6')
        dep_amount_9 = hourly_stats_df[(hourly_stats_df.type_action=='deposit')&(hourly_stats_df.duration==9)].groupby('hr').amount.sum().rename('DEP_AMOUNT_9')
        dep_amount_12 = hourly_stats_df[(hourly_stats_df.type_action=='deposit')&(hourly_stats_df.duration==12)].groupby('hr').amount.sum().rename('DEP_AMOUNT_12')
        dep_amount_15 = hourly_stats_df[(hourly_stats_df.type_action=='deposit')&(hourly_stats_df.duration==15)].groupby('hr').amount.sum().rename('DEP_AMOUNT_15')
        dep_amount_18 = hourly_stats_df[(hourly_stats_df.type_action=='deposit')&(hourly_stats_df.duration==18)].groupby('hr').amount.sum().rename('DEP_AMOUNT_18')

        with_amount_3 = hourly_stats_df[(hourly_stats_df.type_action=='withdraw')&(hourly_stats_df.duration==3)].groupby('hr').amount.sum().rename('WITH_AMOUNT_3')
        with_amount_6 = hourly_stats_df[(hourly_stats_df.type_action=='withdraw')&(hourly_stats_df.duration==6)].groupby('hr').amount.sum().rename('WITH_AMOUNT_6')
        with_amount_9 = hourly_stats_df[(hourly_stats_df.type_action=='withdraw')&(hourly_stats_df.duration==9)].groupby('hr').amount.sum().rename('WITH_AMOUNT_9')
        with_amount_12 = hourly_stats_df[(hourly_stats_df.type_action=='withdraw')&(hourly_stats_df.duration==12)].groupby('hr').amount.sum().rename('WITH_AMOUNT_12')
        with_amount_15 = hourly_stats_df[(hourly_stats_df.type_action=='withdraw')&(hourly_stats_df.duration==15)].groupby('hr').amount.sum().rename('WITH_AMOUNT_15')
        with_amount_18 = hourly_stats_df[(hourly_stats_df.type_action=='withdraw')&(hourly_stats_df.duration==18)].groupby('hr').amount.sum().rename('WITH_AMOUNT_18')

        df = pd.DataFrame([dep_amount, dep_txs, dep_users, with_amount, with_txs, with_users,
                    dep_amount_3,dep_amount_6,dep_amount_9,dep_amount_12,dep_amount_15,dep_amount_18,
                    with_amount_3,with_amount_6,with_amount_9,with_amount_12,with_amount_15,with_amount_18]).fillna(0).T
        ###
        self.hourly_stats_df = df.reset_index().rename(columns={'index':'HR'})
        self.hourly_stats_df.columns = [c.lower() for c in self.hourly_stats_df.columns]
        self.hourly_stats_df = self.hourly_stats_df.sort_values(by='hr',ascending=True)
        self.hourly_stats_df['net_deposit_3'] = (self.hourly_stats_df.dep_amount_3-self.hourly_stats_df.with_amount_3).cumsum()
        self.hourly_stats_df['net_deposit_6'] = (self.hourly_stats_df.dep_amount_6-self.hourly_stats_df.with_amount_6).cumsum()
        self.hourly_stats_df['net_deposit_9'] = (self.hourly_stats_df.dep_amount_9-self.hourly_stats_df.with_amount_9).cumsum()
        self.hourly_stats_df['net_deposit_12'] = (self.hourly_stats_df.dep_amount_12-self.hourly_stats_df.with_amount_12).cumsum()
        self.hourly_stats_df['net_deposit_15'] = (self.hourly_stats_df.dep_amount_15-self.hourly_stats_df.with_amount_15).cumsum()
        self.hourly_stats_df['net_deposit_18'] = (self.hourly_stats_df.dep_amount_18-self.hourly_stats_df.with_amount_18).cumsum()
        self.hourly_stats_df['tot_txs'] = self.hourly_stats_df.with_tx + self.hourly_stats_df.deposit_tx
        self.tot_ust = self.hourly_stats_df.net_deposit_3.max() + \
                       self.hourly_stats_df.net_deposit_6.max() + \
                       self.hourly_stats_df.net_deposit_9.max() + \
                       self.hourly_stats_df.net_deposit_12.max() + \
                       self.hourly_stats_df.net_deposit_15.max() + \
                       self.hourly_stats_df.net_deposit_18.max()
        self.n_txs = self.hourly_stats_df.deposit_tx.sum() + self.hourly_stats_df.with_tx.sum()
        ###
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

        self.users_balance_df = self.users_balance_df\
                            .join(self.bluna_balance, on='sender', how='left')\
                            .join(self.aust_balance, on='sender', how='left').fillna(0)
        self.users_balance_df.balance = self.users_balance_df.balance + \
                                                self.users_balance_df.bLuna_balance + \
                                                self.users_balance_df.aUST_balance

        self.user_stats_df['dur_amount']=self.user_stats_df.duration * self.user_stats_df.amount
        df = self.user_stats_df.groupby('sender').agg(mean_duration=('duration', 'mean'),
                                              dur_sum=('dur_amount', 'sum'),
                                              amnt_sum=('amount', 'sum'))
        df['weighted_avg_dur'] = df.dur_sum/df.amnt_sum
        self.users_balance_df = df.reset_index().merge(self.users_balance_df, on='sender')

        #MARS ROI
        df_value = self.last_duration_amount.set_index('Lockup period').T
        df_value=df_value.append(pd.DataFrame([3,6,9,12,15,18],columns=['n_months'],index=['3 months','6 months','9 months','12 months','15 months','18 months']).T)
        df_value=df_value.append(pd.DataFrame([1,2.8,
                                            5.2,8,11.2,14.7],columns=['boost'],index=['3 months','6 months','9 months','12 months','15 months','18 months']).T)
        self.mars_roi_df = df_value


    def __init__(self, claim, get_url=None):
        self.claim = claim
        self.get_url = get_url


        self.user_stats = '334d8aa0-f9a3-4a9f-a138-3e35583f9477'
        self.hourly_new_users = 'bb19634c-10e2-4498-8427-76a7b6e401ac'
        self.wallet_age = 'f297f742-95a1-442e-84fb-babc5b1bb6e4'
        self.hourly_stats = '06d2ec31-cc77-4dd8-a781-91858c188b00'
        self.users_balance = '1d097568-a090-4cd8-b2db-495c9878f059'
        self.airdrop_claims = '2'
        self.lba_deposits = '3'
        self.mars_roi_p1 = '4'
        ###
        self.cols_claim = {
            self.mars_roi_p1 : ['3 months','6 months','9 months','12 months','15 months','18 months'],
            self.user_stats : ['SENDER', 'DURATION', 'AMOUNT'],
            self.hourly_stats : ['HR', 'DURATION','TYPE_ACTION','AMOUNT','N_USERS','N_TXS'],
            self.wallet_age : ['MIN_DATE','ADDRESS_COUNT'],
            self.hourly_new_users: ['TIME','NEW_USERS'],
            self.users_balance: ['SENDER','BALANCE'],
            self.airdrop_claims : ['SENDER','AMOUNT','TIME'],
            self.lba_deposits : ['SENDER','AMOUNT','DENOM','ACTION','TIME']
        }
        mars_roi_p1 = [
          [1.695441e+07, 1.329435e+07,  4.737131e+06,  3.118435e+06,  1.032555e+06,  4.229810e+07],
          [3.000000e+00,  6.000000e+00,  9.000000e+00,  1.200000e+01,  1.500000e+01,  1.800000e+01],
          [1.000000e+00,  2.800000e+00,  5.200000e+00,  8.000000e+00, 1.120000e+01,  1.470000e+01]
        ]
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

        self.data_claim = {
            self.mars_roi_p1 : mars_roi_p1,
            self.user_stats : [['user1_1',3,10],
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
                 ['user3',18,13]],
            self.airdrop_claims :
                [
                    ['user1',300,'2021-09-21T07:00:00Z'],
                    ['user2',70,'2021-09-21T07:00:00Z'],
                    ['user3',34,'2021-09-21T07:00:00Z'],
                    ['user1_1',132,'2021-09-21T07:00:00Z'],
                    ['user4',132,'2021-09-21T07:00:00Z']
                ],
            self.lba_deposits : [['user1_1',20,'MARS','deposit','2021-09-21T08:00:00Z'],
                            ['user1_1',50,'UST','deposit','2021-09-21T08:00:00Z'],
                            ['user2',70,'MARS','deposit','2021-09-21T08:00:00Z'],
                            ['user2',80,'UST','deposit','2021-09-21T08:00:00Z'],
                            ['user2',10,'UST','withdraw','2021-09-21T09:00:00Z'],
                            ['user1',70,'MARS','deposit','2021-09-21T08:00:00Z'],
                            ['user4',132,'MARS','deposit','2021-09-21T09:00:00Z'],
                            ['user1_5',132,'MARS','deposit','2021-09-21T09:00:00Z']],
            self.hourly_stats : [
                    ['2021-09-21T07:00:00Z',3,'deposit',3000,11,30],
                    ['2021-09-21T07:00:00Z',3,'withdraw',323,11,30],
                    ['2021-09-21T07:00:00Z',6,'deposit',2000,11,30],
                    ['2021-09-21T07:00:00Z',9,'deposit',200000,11,30],
                    ['2021-09-21T07:00:00Z',12,'deposit',500,11,30],
                    ['2021-09-21T07:00:00Z',15,'deposit',506,11,30],
                    ['2021-09-21T07:00:00Z',18,'deposit',12,11,30],
                    ['2021-09-21T08:00:00Z',3,'deposit',3000000,11,30],
                    ['2021-09-21T08:00:00Z',3,'withdraw',1001,11,30],
                    ['2021-09-21T08:00:00Z',6,'deposit',2000,11,30],
                    ['2021-09-21T08:00:00Z',9,'deposit',200,11,30],
                    ['2021-09-21T08:00:00Z',12,'deposit',5000,11,30],
                    ['2021-09-21T08:00:00Z',12,'withdraw',1001,11,30],
                    ['2021-09-21T08:00:00Z',15,'deposit',50006,11,30],
                    ['2021-09-21T08:00:00Z',18,'deposit',12,11,30],
                    ['2021-09-21T09:00:00Z',3,'deposit',3000,11,30],
                    ['2021-09-21T09:00:00Z',3,'withdraw',323,11,30],
                    ['2021-09-21T09:00:00Z',6,'deposit',2000,11,30],
                    ['2021-09-21T09:00:00Z',9,'deposit',200000,11,30],
                    ['2021-09-21T09:00:00Z',12,'deposit',500,11,30],
                    ['2021-09-21T09:00:00Z',15,'deposit',506,11,30],
                    ['2021-09-21T09:00:00Z',18,'deposit',12,11,30],
                    ['2021-09-21T10:00:00Z',3,'deposit',3000000,11,30],
                    ['2021-09-21T10:00:00Z',3,'withdraw',1001,11,30],
                    ['2021-09-21T10:00:00Z',6,'deposit',2000,11,30],
                    ['2021-09-21T10:00:00Z',9,'deposit',200,11,30],
                    ['2021-09-21T10:00:00Z',12,'deposit',5000,11,30],
                    ['2021-09-21T10:00:00Z',12,'withdraw',1001,11,30],
                    ['2021-09-21T10:00:00Z',15,'deposit',50006,11,30],
                    ['2021-09-21T10:00:00Z',18,'deposit',12,11,30]
            ],
            self.wallet_age : wallet_age,
            self.hourly_new_users: [['2021-09-21T07:00:00Z',1000],
                                    ['2021-09-21T08:00:00Z',600],
                                    ['2021-09-21T09:00:00Z',200],
                                    ['2021-09-21T10:00:00Z',1000],
                                    ['2021-09-21T11:00:00Z',100],
                                    ['2021-09-21T12:00:00Z',140]],                  
            self.users_balance: users_balance
    }

    def get_mars_tokens_aprs(self, amount, lockup, mars_price):
        df_value = self.mars_roi_df
        df_value[lockup]['UST deposited'] += amount
        df_value = df_value.append((df_value.T['UST deposited']*df_value.T.boost).rename('weighted_deposit'))
        df_value = df_value.append((df_value.T['weighted_deposit']/df_value.T['weighted_deposit'].sum()*mars_tokens).rename('mars_tokens'))
        df_value = df_value.append((df_value.T['mars_tokens']/df_value.T['UST deposited']).rename('mars_tokens_per_ust'))
        df_value = df_value.append((df_value.T['mars_tokens_per_ust']*mars_price).rename('roi_ust_per_ust'))
        df_value = df_value.append((df_value.T['roi_ust_per_ust']*100)\
                                             .apply(lambda x: round(x,2))\
                                             .rename('roi_perc'))
        df_value = df_value.append((df_value.T['roi_perc'])\
                                        .apply(lambda x: str(x)+'%')\
                                        .rename('roi_perc_label'))
        #return rois updated and the n of mars tokens obtained by the deposit
        return df_value, df_value.loc['mars_tokens_per_ust'][lockup]*amount

    def get_lba_rewards(self, amount_ust, amount_mars, price):
        ust_rewards_input = tot_ust_rewards/(self.act_usts_lba+amount_ust)*amount_ust
        mars_rewards_input = tot_mars_rewards/(self.act_mars_lba+amount_mars)*amount_mars
        ust_apr = tot_ust_rewards*price/self.act_usts_lba
        ust_apr 
        mars_apr = tot_mars_rewards/self.act_mars_lba
        mars_apr
        df = pd.DataFrame([[mars_apr,ust_apr],['MARS','UST']]).T
        df.columns = ['ROI','Token']
        return ust_rewards_input, mars_rewards_input, df
        