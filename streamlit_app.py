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
<div class="banner" style=\"max-width: 50px;float: left;z-index: 1\">
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

col1, col2,col3 = st.columns([2,8,1])
with col2:
    st.subheader('Return on Investment')
    st.markdown("""50M $MARS tokens will be distributed among depositors. The longer you lock your deposit, [the higher the boost you obtain](https://mars-protocol.medium.com/mars-distribution-plan-the-mars-token-launch-lockdrop-and-more-9f6d2dc0995c).""")
    st.markdown("""Therefore, we can simulate the expected ROI on each UST locked in each bucket. You simply have to:
                    <ul> 
                        <li> Insert what you expect the MARS token price to be </li>
                        <li> Insert your deposit and lockup period (optional) </li>
                    </ul>
                """,unsafe_allow_html=True)
    #st.markdown("""Expected ROI on single deposited UST if you deposited [] UST for [] and MARS tokens price was []""")
    

col1, col2, col4,col5 = st.columns([2,6,2,1])
with col4:
    st.text("")
    st.text("")
    input_deposit = st.number_input('UST deposit', step=1, min_value=0, help='Simulate a deposit of UST to see how this changes the ROI on the different lockup periods')
    input_duration = st.selectbox('Lockup duration',('3 months', '6 months', '9 months', '12 months', '15 months','18 months'))
    input_mars_price = st.number_input('$MARS price', step=0.01, min_value=0.01, help='By inserting the expected price of the $MARS tokens we can simulate the ROI on each UST deposited in each lockup period')
    df, mars_roi_on_deposit = data_provider.get_mars_tokens_aprs(input_deposit, input_duration, input_mars_price)    
    st.text(f'Rewards: {round(mars_roi_on_deposit,0)} MARS')
    #df.loc['roi_perc_label'][input_duration]
with col2:
    st.altair_chart(chart_provider.simulation_apr_chart(df), use_container_width=True)


col1, col2,col3 = st.columns([2,8,1])
with col2:
    st.subheader('Lockdrop Metrics')
col1, col2,col3, col4,col5 = st.columns([2,2,2,2,1])
with col2:
    st.metric(label="Total UST locked",\
            value=f"${round((15000000/1000000.0),2)}M")
with col3:
    st.metric(label="Number of users", value=f"{round(100,2)}")
with col4:
    st.metric(label="Number of transactions", value=f"{round(145,2)}")

col1, col2,col3 = st.columns([2,8,1])
with col2:
    st.subheader('Amount of UST locked')
    st.markdown("""Distribution of UST locked for different durations.""")
    st.markdown("""Have users preferred shorter or longer durations? Has one duration the largest share?""")
    st.altair_chart(chart_provider.ust_duration_chart(data_provider.last_duration_amount), use_container_width=True)



col1, col2, col3 = st.columns([2,8,1])
with col2:
    st.subheader('Amount of UST locked over time')
    st.markdown("""The trend of UST locked for each duration over the course of the lockdrop event.""")
    st.markdown("""What is the fastest growing duration in terms of locked UST? Are there spikes or is the growth linear?""")
    st.altair_chart(chart_provider.time_duration_chart(data_provider.time_duration_df), use_container_width=True)

col1, col2, col3, col4 = st.columns([2,4,4,1])
with col2:
    st.subheader('Number of transactions over time')
    st.markdown("""The number of hourly transactions""")
    st.altair_chart(chart_provider.txs_over_time_chart(data_provider.hourly_stats_df), use_container_width=True)
with col3:
    st.subheader('Number of unique users over time')
    st.markdown("""The cumulative number of unique users locking UST""")
    st.altair_chart(chart_provider.users_over_time_chart(data_provider.hourly_new_users_df), use_container_width=True)
  

col1, col2, col3, col4 = st.columns([2,4,4,1])
with col2:
    st.subheader('User deposits over lockup periods')
    st.markdown("By plotting the distribution of the amount deposited by each user in each lockup period, we can identify outliers and isolate the behavior of whales from the ones of retails/majority of users.")
    st.markdown("""What is the median deposit for each lockup period?""")
    st.altair_chart(chart_provider.boxplot_lockup(data_provider.user_stats_df), use_container_width=True)
with col3:
    st.subheader('Users vs Number of lockup periods')
    st.markdown("By plotting the number of different lockup periods in which users have deposited, we can identify behavioral patterns. We can investigate if users have chosen multiple periods or a single one.")
    st.markdown("""How many different durations have users locked their UST for?""")
    st.altair_chart(chart_provider.n_duration_wallet_chart(data_provider.count_durations_users), use_container_width=True)
    
col1, col2, col3 = st.columns([2,8,1])
with col2:
    st.subheader('Participants\' wallet age')
    st.markdown("""This graph shows the number of wallets participating in the Mars Lockdrop based on the date their wallets are created.""")
    st.markdown("""Are the participants mainly Terra OGs?""")
    st.altair_chart(chart_provider.wallet_age_chart(data_provider.wallet_age_df,data_provider.dates_to_mark), use_container_width=True)

col1, col2, col3 = st.columns([2,8,1])
with col2:
    st.subheader('Deposit distribution per balance')
    st.markdown("""This graph depicts the distribution of UST deposited against the average balance of the respective wallets. Essentially we are asking the question - are wallets with high average balances depositing more UST or vice versa?""")
    st.markdown("""You can interact with the graph by zooming in and out to explore specific ranges. Zoom all the way out to see outliers or click on one of the dots to open its [ET Finder](https://finder.extraterrestrial.money/) page.""")
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
    .st-bx{
        background-color: transparent;
    }
    .st-bu{
        background-color: transparent;
    }
    .css-k7dvn8{
        background-color: transparent;
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
            margin-top: 30px;
        }
        [data-testid="metric-container"]{
            padding-bottom: 20px;
        }
        .banner {
            position: fixed;
        }
    }
    </style>
    """, unsafe_allow_html=True)
