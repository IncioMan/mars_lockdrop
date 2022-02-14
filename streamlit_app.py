import streamlit as st
import pandas as pd
import altair as alt
from charts import ChartProvider
import requests
from PIL import Image
from data import DataProvider
import base64

st.set_page_config(page_title="Mars Lockdrop - Analytics",\
        page_icon=Image.open(requests.get('https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master/images/mars_logo_hd.png',stream=True).raw),\
        layout='wide')

###

@st.cache(ttl=3000, show_spinner=False, allow_output_mutation=True)
def claim(claim_hash, cols_claim, data_claim):
    try:
        df_claim = pd.read_json(
            f"https://api.flipsidecrypto.com/api/v2/queries/{claim_hash}/data/latest",
            convert_dates=["BLOCK_TIMESTAMP"],
        )
    except:
        return pd.DataFrame(data_claim[claim_hash],columns=cols_claim[claim_hash])
    if(len(df_claim.columns)==0):
        return pd.DataFrame(data_claim[claim_hash],columns=cols_claim[claim_hash])
    return df_claim

@st.cache(ttl=3000, show_spinner=False, allow_output_mutation=True)
def get_url(url):
    return pd.read_csv(url, index_col=0)
    

data_provider = DataProvider(claim, get_url)
data_provider.load_data()
chart_provider = ChartProvider()

###
###
st.markdown("""
<div style=\"max-width: 50px;position: fixed;float: left;z-index: 1\">
    <a href="https://marsprotocol.io/">
        <img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master/images/mars_logo_hd.png" style=\"margin-left: 5px;\" width=\"100px\">
        <img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master/images/M.png" width=\"100px\">
        <img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master/images/A.png" width=\"100px\">
        <img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master/images/R.png" style=\"margin-left: 6px;\" width=\"100px\">
        <img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master/images/S.png" width=\"100px\">
    </a>
    <div style=\"width: 100px;margin-top: 5px;margin-bottom: 10px;\"><span class="blink_me"></span>Active</div>
    <div style=\"border-top: 3px solid #ffffff;width: 100px;margin-top: 15px;padding-bottom: 20px;\"></div>
    <div style=\"width: 100px; margin-left: 10px;\">
        <a href="https://flipsidecrypto.xyz"><img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master//images/fc.png" width=\"30px\"></a>
        <a href="https://twitter.com/IncioMan"><img src="https://raw.githubusercontent.com/IncioMan/mars_lockdrop/master//images/twitter.png" width=\"50px\"></a>
    </div>
</div>
""", unsafe_allow_html=True)

st.text("")
st.text("")
st.text("")
st.text("")
st.text("")
col1, col2,col3, col4,col5 = st.columns([2,6,0.5,1.5,1])
with col2:
    st.subheader('Percentage withdrawn')
    st.markdown("""How many users have withdrawn in a percentage range?""")
    st.altair_chart(chart_provider.ust_duration_chart(data_provider.last_duration_amount), use_container_width=True)
with col4:
    st.metric(label="Total UST deposited",\
            value=f"${round((15000000/1000000.0),2)}M")
    st.metric(label="UST Withdrawn %", value=f"{round(100,2)}%")
    st.metric(label="% Withdrawing Users", value=f"{round(145,2)}%")

col1, col2, col3 = st.columns([2,8,1])
with col2:
    st.subheader('Percentage withdrawn')
    st.markdown("""How many users have withdrawn in a percentage range?""")
    st.altair_chart(chart_provider.time_duration_chart(data_provider.time_duration_df), use_container_width=True)

col1, col2, col3, col4 = st.columns([2,4,4,1])
with col2:
    st.subheader('Percentage withdrawn')
    st.markdown("""How many users have withdrawn in a percentage range?""")
    st.altair_chart(chart_provider.txs_over_time_chart(data_provider.hourly_stats_df), use_container_width=True)
with col3:
    st.subheader('Percentage withdrawn')
    st.markdown("""How many users have withdrawn in a percentage range?""")
    st.altair_chart(chart_provider.users_over_time_chart(data_provider.hourly_new_users_df), use_container_width=True)
  

col1, col2, col3, col4 = st.columns([2,4,4,1])
with col2:
    st.subheader('Percentage withdrawn')
    st.markdown("""How many users have withdrawn in a percentage range?""")
    st.altair_chart(chart_provider.n_duration_wallet_chart(data_provider.count_durations_users), use_container_width=True)
with col3:
    st.subheader('Percentage withdrawn')
    st.markdown("""How many users have withdrawn in a percentage range?""")
    st.altair_chart(chart_provider.n_duration_wallet_chart(data_provider.count_durations_users), use_container_width=True)
    
col1, col2, col3 = st.columns([2,8,1])
with col2:
    st.subheader('Percentage withdrawn')
    st.markdown("""How many users have withdrawn in a percentage range?""")
    st.altair_chart(chart_provider.wallet_age_chart(data_provider.wallet_age_df,data_provider.dates_to_mark), use_container_width=True)

col1, col2, col3 = st.columns([2,8,1])
with col2:
    st.subheader('Percentage withdrawn')
    st.markdown("""How many users have withdrawn in a percentage range?""")
    st.altair_chart(chart_provider.wallet_balance(data_provider.users_balance_df), use_container_width=True)


###
#st.markdown("""This dashboard was built with love for the 🌖 community by [IncioMan](https://twitter.com/IncioMan) and [sem1d5](https://twitter.com/sem1d5)""")
st.markdown("""
<style>
    @media (min-width:640px) {
        .block-container {
            padding-left: 7rem;
            padding-right: 7rem;
        }
    }
    @media (min-width:800px) {
        .block-container {
            padding-left: 7rem;
            padding-right: 7rem;
        }
    }
    .block-container
    {
        padding-bottom: 1rem;
        padding-top: 5rem;
    }
</style>
""", unsafe_allow_html=True)
hide_streamlit_style = """
                        <style>
                        #MainMenu {visibility: hidden;}
                        #footer {visibility: hidden;}
                        </style>
                        """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.markdown("""
    <style>
    .terminated {
        margin-right: 10px;
        width: 10px;
        height: 10px;
        display: inline-block;
        border: 1px solid red;
        background-color: red;
        border-radius: 100%;
        opacity: 0.8;
    }

    .idle {
        margin-right: 10px;
        width: 10px;
        height: 10px;
        display: inline-block;
        border: 1px solid grey;
        background-color: grey;
        border-radius: 100%;
        opacity: 0.8;
    }

    .blink_me {
        margin-left: 15px;
        margin-right: 15px;
        animation: blinker 2s linear infinite;
        width: 10px;
        height: 10px;
        display: inline-block;
        border: 1px solid #FFFFFF;
        background-color: #FFFFFF;
        border-radius: 100%;
        }
        @keyframes blinker {
        50% {
            opacity: 0;
        }
    }

    @media (min-width:800px) {
        .css-yksnv9 {
            margin-top: 140px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
