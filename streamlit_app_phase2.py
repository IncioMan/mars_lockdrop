import streamlit as st
import pandas as pd
import altair as alt
from charts import ChartProvider
import requests
from PIL import Image
from data import DataProvider

st.set_page_config(page_title="Prism Forge - Analytics",\
        page_icon=Image.open(requests.get('https://raw.githubusercontent.com/IncioMan/prism_forge/master/images/xPRISM.png',stream=True).raw),\
        layout='wide')

###

@st.cache(ttl=10, show_spinner=False, allow_output_mutation=True)
def claim(claim_hash, cols_claim):
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

data_provider = DataProvider(claim)
data_provider.load_data_p2()
chart_provider = ChartProvider()

###
###

original_title = '<p style="font-size: 60px;">Prism Forge - Phase 2</p>'
col1, col2 = st.columns([2,12])
with col2:
    st.markdown(original_title, unsafe_allow_html=True)
with col1:
    st.markdown('<img src="https://raw.githubusercontent.com/IncioMan/prism_forge/master/images/prism_white_small.png" width=\"100px\">', unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns([5,50,50,50,50,50])
with col6:
    st.markdown('<div>Status: Idle <span class="idle"></span></div>',unsafe_allow_html=True)
st.text('')

col1, col2, col3 = st.columns([0.5,0.5,1])

with col1:
    st.text('')
    st.text('')
    st.text('')
    st.text('')
    st.metric(label="Total UST deposited",\
            value=f"${round((data_provider.tot_deposits/1000000.0),2)}M",\
            delta=f"{int((data_provider.tot_deposits-data_provider.next_last_ust)/1000)}k")
    st.metric(label="UST Withdrawn %", value=f"32.3%", delta=3,
    delta_color="off")
    st.metric(label="% Withdrawing Users", value=f"15.4%", delta=1.5, delta_color="off")

with col2:
    st.text('')
    st.text('')
    st.text('')
    st.text('')
    price = data_provider.tot_deposits/70000000
    price_delta = (data_provider.tot_deposits-data_provider.next_last_ust)/70000000
    st.metric(label="Current Price",  value=f"${round(price,2)}", delta=round(price_delta,2),delta_color="off")
    st.metric(label="Floor price", value=f"${round(price,2)}", delta=round(price_delta,2),delta_color="off")
    fdv = price*1000000000
    delta = (price_delta*70000000)/1000000000
    st.metric(label="Fully Diluted Value", value=f"${round(fdv/1000000,2)}M",\
            delta=round(delta/1000000,2),delta_color="off")

with col3:
    st.subheader('UST deposited over time')
    st.markdown("""This graph shows the cumulative net UST deposits into the Prism Forge.""")
    st.altair_chart(chart_provider.pie_ust_chart(data_provider.ust_df), use_container_width=True)

st.subheader('UST deposited over time')
st.markdown("""This graph shows the cumulative net UST deposits into the Prism Forge.""")
st.altair_chart(chart_provider.tot_ust_left_chart(data_provider.p2_hourly_df), use_container_width=True)

st.subheader('UST deposited over time')
st.markdown("""This graph shows the cumulative net UST deposits into the Prism Forge.""")
st.altair_chart(chart_provider.with_txs_hourly_chart(data_provider.p2_hourly_df), use_container_width=True)


col1, col2 = st.columns(2)
with col1:
    st.subheader('UST deposited over time')
    st.markdown("""This graph shows the cumulative net UST deposits into the Prism Forge.""")
    st.altair_chart(chart_provider.with_perc_buckets_chart(data_provider.with_perc_buckets), use_container_width=True)

with col2:
    st.subheader('UST deposited over time')
    st.markdown("""This graph shows the cumulative net UST deposits into the Prism Forge.""")
    st.altair_chart(chart_provider.with_users_hourly_chart(data_provider.p2_hourly_df), use_container_width=True)




st.subheader('UST deposited over time')
st.markdown("""This graph shows the cumulative net UST deposits into the Prism Forge. 70 million PRISM tokens are allocated to the Prism Forge and will be distributed to depositors based on their net UST contributed during this phase.""")
st.altair_chart(chart_provider.heatmap_withdrawing_chart(data_provider.heatmap_data_df), use_container_width=True)
###
st.markdown("""This dashboard was built with love for the 🌖 community by [IncioMan](https://twitter.com/IncioMan) and [sem1d5](https://twitter.com/sem1d5)""")
st.markdown("""
<style>
    @media (min-width:640px) {
        .block-container {
            padding-left: 5rem;
            padding-right: 5rem;
        }
    }
    @media (min-width:800px) {
        .block-container {
            padding-left: 15rem;
            padding-right: 15rem;
        }
    }
    .block-container
    {
        padding-bottom: 1rem;
        padding-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)
hide_streamlit_style = """
                        <style>
                        #MainMenu {visibility: hidden;}
                        footer {visibility: hidden;}
                        </style>
                        """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

col1, col2= st.columns([7,2])
with col1:
    st.text("In collaboration with:")
    st.markdown('[<img src="https://raw.githubusercontent.com/IncioMan/prism_forge/master/images/prismwhite.svg" style="margin-left:80px">](http://prismprotocol.app/)', unsafe_allow_html=True)
with col2:
    st.text("Sponsored by:")
    st.markdown('[<img src="https://raw.githubusercontent.com/IncioMan/prism_forge/master/images/flipsidewhite.png" width=\"160px\">](http://flipsidecrypto.xyz/)', unsafe_allow_html=True)
    st.markdown("""
    <style>
    .terminated {
        margin-left: 10px;
        width: 10px;
        height: 10px;
        display: inline-block;
        border: 1px solid red;
        background-color: red;
        border-radius: 100%;
        opacity: 0.8;
    }

    .idle {
        margin-left: 10px;
        width: 10px;
        height: 10px;
        display: inline-block;
        border: 1px solid grey;
        background-color: grey;
        border-radius: 100%;
        opacity: 0.8;
    }

    .blink_me {
        margin-left: 10px;
        animation: blinker 2s linear infinite;
        width: 10px;
        height: 10px;
        display: inline-block;
        border: 1px solid green;
        background-color: green;
        border-radius: 100%;
        }
        @keyframes blinker {
        50% {
            opacity: 0;
        }
    }
    </style>
    """, unsafe_allow_html=True)
