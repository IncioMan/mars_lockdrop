import pandas as pd
from constants import cols_dict
import altair as alt

class ChartProvider:

    def __init__(self):
        pass
    
    def time_duration_chart(self, time_duration_df):
        time_duration_chart = alt.Chart(time_duration_df.rename(columns={'hr':'Time'})).mark_line(point = True).encode(
            x='Time:T',
            y='UST deposited:Q',
            color=alt.Color('Lockup period:N', 
                        sort=['3 months','6 months',
                              '9 months','12 months',
                              '15 months','18 months'],
                        scale=alt.Scale(scheme='pastel1')),
            tooltip=[alt.Tooltip('Time:T', format='%Y-%m-%d %H:%M'),'UST deposited:Q','Lockup period:N']
        ).properties(height=400)
        return time_duration_chart

    def n_duration_wallet_chart(self,count_durations_users):
        n_duration_wallet_chart = alt.Chart(count_durations_users).mark_line(point = True, color='#7DDBD3').encode(
            y=alt.Y('Number of users:Q', sort="ascending"),
            x="Number of lockup durations:O",
            tooltip=['Number of users:Q',"Number of lockup durations:Q"]
        ).properties(height=300).configure_view(strokeOpacity=0)
        return n_duration_wallet_chart

    def txs_over_time_chart(self,hourly_stats_df):
        df = hourly_stats_df.rename(columns={'hr':'Time','tot_txs':'Number of transactions'})
        txs_over_time_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('Time:T', \
                    axis=alt.Axis(tickCount=10, labelAngle=0, tickBand = 'center')),
            y="Number of transactions:Q",
            tooltip=[alt.Tooltip('Time:T', format='%Y-%m-%d %H:%M'),"Number of transactions:Q"]
        ).configure_mark(
            color='#ffde85'
        ).configure_view(strokeOpacity=0)
        return txs_over_time_chart
    
    def users_over_time_chart(self, hourly_new_users_df):
        df = hourly_new_users_df.rename(columns={'time':'Time','cumsum_new_users':'Number of total users'})
        users_over_time_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('Time:T',\
                axis=alt.Axis(tickCount=10, labelAngle=0, tickBand = 'center')),
            y="Number of total users:Q",
            tooltip=['Time', "Number of total users:Q"]
            ).configure_mark(
                color='#fab0ba'
            ).configure_view(strokeOpacity=0)
        return users_over_time_chart
    
    def pie_ust_chart(self, last_duration_amount):
        pie_ust_chart = alt.Chart(last_duration_amount).mark_arc(innerRadius=60).encode(
                            theta=alt.Theta(field="UST deposited", type="quantitative"),
                            color=alt.Color(field="Lockup period", type="nominal",
                                    sort=['3 months','6 months',
                                          '9 months','12 months',
                                          '15 months','18 months'],
                                    scale=alt.Scale(scheme='pastel1'),
                                    legend=alt.Legend(
                                    orient='none',
                                    padding=10,
                                    legendY=-20,
                                    direction='vertical')),
                                tooltip=["UST deposited","Lockup period"]
                            ).configure_view(strokeOpacity=0)
        return pie_ust_chart