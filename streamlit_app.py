import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from constants import cols_dict
from charts import *
import requests
from data import tot_deposits,top_depositors,\
            n_users, n_txs,next_last_users, next_last_ust, next_last_txs
from PIL import Image

st.set_page_config(page_title="Prism Forge - Analytics",\
        page_icon=Image.open(requests.get('https://raw.githubusercontent.com/IncioMan/on-chain-data-analysis/prism_launch/prism_launch/images/xPRISM.png',stream=True).raw),\
        layout='wide')

###
user_stats = '499224b4-30a6-43d7-80b9-3a019cbb1d3d'
deposits_bucket = 'b4953cda-a874-43fa-b78d-ceb0c1bfc3cf'
deposit_balance = '9e2e9587-0850-466a-8a59-4dda2e8337f3'
hourly_new_users = '65179a1e-fd70-43eb-a9e4-ce14b716c928'
wallet_age = '5b7983de-8596-42de-a997-767754746b71'
hourly_stats = '520fb3b6-a968-4742-bf0a-31cbb67b6b05'
prev_launches = '4eac9ed8-be31-4cf4-9bbe-2a0776d224ad'
ciao = ''

cols_claim = {
    user_stats : ['DEPOSIT_AMOUNT', 'DEPOSIT_TXS', 'SENDER', 'WITHDRAWN_AMOUNT',
       'WITHDRAW_TXS'],
    deposits_bucket : ['BUCKET', 'N_USERS'],
    prev_launches : ['PARTICIPANTS', 'PARTICIPATE_TYPE', 'TYPE'],
    hourly_stats : ['DEPOSIT_AMOUNT', 'DEPOSIT_TX', 'DEP_USERS', 'HR', 'NET_AMOUNT',
       'TOT_TXS', 'TOT_USERS', 'WITH_AMOUNT', 'WITH_TX', 'WITH_USERS'],
    wallet_age : ['ADDRESS_COUNT', 'MIN_DATE'],
    deposit_balance: ['AMOUNT', 'AVG_BALANCE_USD', 'MAX_BALANCE_USD', 'N_TXS', 'SENDER'],
    hourly_new_users: ['NEW_USERS', 'TIME']
}

@st.cache(ttl=3000, show_spinner=False, allow_output_mutation=True)
def claim(claim_hash):
    try:
        df_claim = pd.read_json(
            f"https://api.flipsidecrypto.com/api/v2/queries/{claim_hash}/data/latest",
            convert_dates=["BLOCK_TIMESTAMP"],
        )
    except:
        return pd.DataFrame(columns = cols_claim[claim_hash])
    if(len(df_claim.columns)==0):
        return pd.DataFrame(columns = cols_claim[claim_hash])
    return df_claim


user_stats_df = claim(user_stats)
deposit_balance_df = claim(deposit_balance)
deposits_bucket_df = claim(deposits_bucket)
wallet_age_df = claim(wallet_age)
hourly_stats_df = claim(hourly_stats)
prev_launches_df = claim(prev_launches)

user_stats_df['DEPOSIT_NET'] = user_stats_df.DEPOSIT_AMOUNT - user_stats_df.WITHDRAWN_AMOUNT
top_depositors = user_stats_df.sort_values(by='DEPOSIT_NET', ascending=False).head(5)[['SENDER','DEPOSIT_NET']]\
             .set_index('SENDER').rename(columns=cols_dict)

hourly_new_users_df = claim(hourly_new_users)
hourly_new_users_df['cumsum_new_users'] = hourly_new_users_df.sort_values(by='TIME').NEW_USERS.cumsum()
df = hourly_new_users_df.sort_values(by='TIME')
index = df.index
if(len(index)>1):
    i = -2
    next_last_users = df.loc[index[i]].cumsum_new_users
else:
    next_last_users = 0
hourly_new_users_df = hourly_new_users_df.rename(columns=cols_dict)


wallet_age_df = wallet_age_df.rename(columns=cols_dict)


hourly_stats_df['cumsum_ust'] = hourly_stats_df.sort_values(by='HR').NET_AMOUNT.cumsum()
hourly_stats_df['cumsum_txs'] = hourly_stats_df.sort_values(by='HR').TOT_TXS.cumsum()
df = hourly_stats_df.sort_values(by='HR')
index = df.index
if(len(index)>1):
    i = -2
    next_last_ust = df.loc[index[i]].cumsum_ust
    next_last_txs = df.loc[index[i]].cumsum_txs
else:
    i = 0
    next_last_ust = 0
    next_last_txs = 0
hourly_stats_df = hourly_stats_df.rename(columns=cols_dict)


n_txs = user_stats_df.DEPOSIT_TXS.sum() + user_stats_df.WITHDRAW_TXS.sum()
n_users = user_stats_df.SENDER.nunique()
tot_deposits = int(user_stats_df.DEPOSIT_AMOUNT.sum() - user_stats_df.WITHDRAWN_AMOUNT.sum())


prev_launches_df = prev_launches_df.rename(columns=cols_dict)

deposit_balance_df = deposit_balance_df.rename(columns=cols_dict)
deposits_bucket_df['bucket_name']=deposits_bucket_df.BUCKET.map({0:'-$0',1:'$0-$10',2:'$10-$100',3:'$100-$1k',4:'$1k-$10k',
                                5:'$10k-$100k',6:'$100k-$1m',7:'$1m-'})
deposits_bucket_df.sort_values(by='BUCKET')

dates_to_mark = pd.DataFrame([
['2021-03-04', '2021-03-11',15,'Anchor launch'],
['2021-09-24', '2021-10-01',15,'Columbus 5'],
['2021-12-12', '2021-12-19',15,'Astroport launch'], 
['2022-01-17', '2022-01-24',15,'Prism launch']], 
columns=['text_date','date','height','text']
)
###


txs_over_time_chart = alt.Chart(hourly_stats_df).mark_bar().encode(
    x=alt.X(cols_dict['HR']+':T', \
            axis=alt.Axis(tickCount=10, labelAngle=0, tickBand = 'center'),\
            scale=alt.Scale(nice=3)),
    y=cols_dict['TOT_TXS']+":Q",
    tooltip=[cols_dict['HR']+':T',cols_dict['TOT_TXS']+":Q"]
).configure_mark(
    color='#ffde85'
).configure_view(strokeOpacity=0)
####
users_over_time_chart = alt.Chart(hourly_new_users_df).mark_bar().encode(
    x=alt.X(cols_dict['TIME']+':T',\
        axis=alt.Axis(tickCount=10, labelAngle=0, tickBand = 'center'),\
        scale=alt.Scale(nice=3)),
    y=cols_dict['cumsum_new_users']+":Q",
    tooltip=[cols_dict['TIME']+':T', cols_dict['cumsum_new_users']+":Q"]
).configure_mark(
    color='#fab0ba'
).configure_view(strokeOpacity=0)
####
users_dep_distr_chart = alt.Chart(deposits_bucket_df.rename(columns=cols_dict).sort_values(by='BUCKET')).mark_bar().encode(
    y=alt.X(cols_dict['bucket_name']+":N", sort=alt.EncodingSortField(order='ascending')),
    x=cols_dict['N_USERS']+":Q",
    tooltip=[cols_dict['bucket_name']+":N",cols_dict['N_USERS']+":Q"]
).configure_mark(
    color='#fab0ba'
).properties(height=300).configure_axisX(
    labelAngle=0
).configure_view(strokeOpacity=0)
####
cum_ust_chart = alt.Chart(hourly_stats_df.rename(columns=cols_dict)).mark_line(point=True).encode(
    x=alt.X(cols_dict['HR']+':T', sort=alt.EncodingSortField(order='ascending')),
    y=cols_dict['cumsum_ust']+":Q",
    tooltip=[cols_dict['HR']+':T',cols_dict['cumsum_ust']+":Q"]
).configure_mark(
    color='#fab0ba'
).properties(width=700).configure_axisX(
    labelAngle=0
).configure_view(strokeOpacity=0)
####
df = user_stats_df.rename(columns=cols_dict)[cols_dict['DEPOSIT_TXS']]\
    .value_counts().sort_index().reset_index().rename(columns={'index':cols_dict['DEPOSIT_TXS'],cols_dict['DEPOSIT_TXS']:'N° of users'})
n_tx_wallet_chart = alt.Chart(df).mark_line(point = True, color='#88D5D5').encode(
    y=alt.Y('N° of users:Q', sort="ascending"),
    x=cols_dict['DEPOSIT_TXS']+":O",
    tooltip=['N° of users:Q',cols_dict['DEPOSIT_TXS']+":Q"]
).properties(height=300).configure_view(strokeOpacity=0)
####
user_part_prev_launches_chart = alt.Chart(prev_launches_df).mark_bar().encode(
x=alt.X(cols_dict['TYPE']+":N", axis=alt.Axis(labelAngle=0, tickBand = 'center')),
y=cols_dict['PARTICIPANTS']+":Q",
color=alt.Color(cols_dict['PARTICIPATE_TYPE'],
    scale=alt.Scale(scheme='pastel1'),
    legend=alt.Legend(
    orient='none',
    padding=10,
    legendY=-10,
    direction='horizontal')),
tooltip=[cols_dict['TYPE']+":N",cols_dict['PARTICIPANTS']+":Q",cols_dict['PARTICIPATE_TYPE']]
).properties(height=400).configure_axisX(
labelAngle=-10
).configure_view(strokeOpacity=0)
####
if(len(deposit_balance_df)>5000):
    df = deposit_balance_df.sample(n=5000, random_state=1)
else:
    df = deposit_balance_df
dep_dist_balance_chart =alt.Chart(df).mark_point(opacity=1, filled=True).encode(
y=alt.Y(cols_dict['AMOUNT']+":Q",scale=alt.Scale(domain=(0, 100000))),
x=alt.X(cols_dict['AVG_BALANCE_USD']+":Q",scale=alt.Scale(domain=(0, 1000000))),
color=alt.Color(cols_dict['N_TXS'],
    scale=alt.Scale(scheme='yelloworangered')),
tooltip=[cols_dict['SENDER'], cols_dict['AMOUNT'],
    cols_dict['AVG_BALANCE_USD'],
    cols_dict['N_TXS']]
).configure_view(strokeOpacity=0).interactive()
###
wallet_age_df = wallet_age_df.rename(columns=cols_dict)
df2 = wallet_age_df.head()
c = alt.Chart(wallet_age_df).mark_bar(color='#ffde85').encode(
    x=alt.X(cols_dict['MIN_DATE']+":T", axis=alt.Axis(tickCount=10, labelAngle=0, title=cols_dict['MIN_DATE'])),
    y=cols_dict['ADDRESS_COUNT']+":Q",
    tooltip=[cols_dict['MIN_DATE']+":T",cols_dict['ADDRESS_COUNT']]
)

c2 = alt.Chart(dates_to_mark).mark_rule(color='#fab0ba').encode(
    x=alt.X('date'+':T',axis=alt.Axis(labels=False,title=''))
)

c3 = alt.Chart(dates_to_mark).mark_text(
    color='#fab0ba',
    angle=270
).encode(
    x=alt.X('text_date'+':T',axis=alt.Axis(labels=False,title='')),
    y='height',
    text='text'
)

wallet_age_chart = (c + c2 + c3).configure_view(strokeOpacity=0).properties(width=600)

###

alt.renderers.set_embed_options(theme='dark')
original_title = '<p style="font-size: 60px;">Prism Forge - Phase 1</p>'
col1, col2 = st.columns([1,12])
with col2:
    st.markdown(original_title, unsafe_allow_html=True)
with col1:
    st.image('https://raw.githubusercontent.com/IncioMan/on-chain-data-analysis/prism_launch/prism_launch/images/prism_white_small.png')
st.text('')
st.text('')
st.text('')

col1, col2, col3, col4, col5 = st.columns([1,2,2,2,2])

with col2:
    st.metric(label="Total UST deposited", value=f"${round((tot_deposits/1000000.0),2)}M", delta=f"${int((tot_deposits-next_last_ust)/1000)}k")

with col3:
    st.metric(label="Unique users", value=n_users, delta=int(n_users-next_last_users),
     delta_color="off")
    
with col4:
    st.metric(label="Transactions", value=n_txs, delta=int(n_txs-next_last_txs),
     delta_color="off")

with col5:
    st.metric(label="Estimated price", value=f"${round(tot_deposits/70000000,2)}", delta=round(((tot_deposits-next_last_ust))/70000000,2),delta_color="off")
####
st.subheader('UST deposited over time')
st.markdown("""This graph shows the cumulative net UST deposits into the Prism Forge. 70 million PRISM tokens are allocated to the Prism Forge and will be distributed to depositors based on their net UST contributed during this phase.""")
st.altair_chart(cum_ust_chart, use_container_width=True)
####
col1, col2 = st.columns(2)
with col1:
    st.subheader('Transactions over time')
    st.markdown("""This graph represents the number of deposits and withdrawals performed every hour in the Prism Forge.         """)
    st.altair_chart(txs_over_time_chart, use_container_width=True)
with col2:
    st.subheader('Users over time')
    st.markdown("""How does the total number of users who have interacted with the Prism Forge since launch look over time?""")
    st.altair_chart(users_over_time_chart, use_container_width=True)
####
col1, col2 = st.columns(2)
with col1:
    st.subheader('User deposits distribution')
    st.markdown("""How much UST are people depositing into the Forge each time? Well, this graph shows the distribution of deposits based on several ranges.""")
    st.altair_chart(users_dep_distr_chart, use_container_width=True)
with col2:
    st.subheader('Number of transactions per wallet')
    st.markdown("""Are people depositing once or multiple times on average? Here, we have the distribution of deposit transactions into the Forge.
    """)
    st.altair_chart(n_tx_wallet_chart, use_container_width=True)
####
st.subheader('Participants from previous bootstrapping or community farming events')
st.markdown("""For those who have participated in these previous launch events, how many of them have participated in the Prism Forge so far?""")
st.altair_chart(user_part_prev_launches_chart, use_container_width=True)
####
st.subheader('Participants\' wallet age')
st.markdown("""Are the participants mainly Terra OGs? This graph shows the number of wallets participating in the Prism Forge based on the date their wallets are created.""")
st.altair_chart(wallet_age_chart, use_container_width=True)
###
st.subheader('Top depositors')
st.markdown("""Let's now see the top 5 addresses which have deposited the most UST. If you are curious, you can 
look these addresses up on [ET Finder](https://finder.extraterrestrial.money/).""")
st.table(top_depositors)
####
st.subheader('Deposit distribution per balance')
st.markdown("""This graph depicts the distribution of UST deposited against the average balance of the respective wallets. Essentially we are asking the question - are wallets with high average balances depositing more UST or vice versa?
You can interact with the graph by zooming in and out to explore specific ranges. Zoom all the way out to see outliers.""")
st.altair_chart(dep_dist_balance_chart, use_container_width=True)
###
st.text('')
st.markdown("This dashboard was built with love for the 🌖 community by [IncioMan](https://twitter.com/IncioMan) and [sam](https://twitter.com/sem1d5) - with the support of [flipsidecrypto](https://flipsidecrypto.xyz/). You can participate in Prism Forge [here](https://forge.prismprotocol.app/).")
st.markdown("""
<style>
    .block-container
    {
        padding-left: 10rem;
        padding-right: 10rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)
hide_streamlit_style = """
                        <style>
                        footer {visibility: hidden;}
                        </style>
                        """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)