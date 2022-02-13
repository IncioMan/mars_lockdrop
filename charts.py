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