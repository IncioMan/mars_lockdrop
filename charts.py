import pandas as pd
from constants import cols_dict
import altair as alt

class ChartProvider:

    def __init__(self):
        pass
    
    def time_duration_chart(self, time_duration_df):
        max_date = self.get_max_domain_date(time_duration_df,'hr',10)
        time_duration_chart = alt.Chart(time_duration_df.rename(columns={'hr':'Time'})).mark_line(point = True).encode(
            x=alt.X('Time:T',scale=alt.Scale(domain=(time_duration_df.hr.min(),max_date))),
            y=alt.X('UST deposited:Q',scale=alt.Scale(domain=(0,time_duration_df['UST deposited'].max()+30))),
            color=alt.Color('Lockup period:N', 
                        sort=['3 months','6 months',
                              '9 months','12 months',
                              '15 months','18 months'],
                        scale=alt.Scale(scheme='lightorange'),
                        legend=alt.Legend(
                                    orient='none',
                                    padding=5,
                                    legendY=0,
                                    direction='horizontal')),
            tooltip=[alt.Tooltip('Time:T', format='%Y-%m-%d %H:%M'),'UST deposited:Q','Lockup period:N']
        ).properties(height=400).configure_view(strokeOpacity=0)
        return time_duration_chart

    def n_duration_wallet_chart(self,count_durations_users):
        n_duration_wallet_chart = alt.Chart(count_durations_users).mark_bar().encode(
            y=alt.Y('Number of users:Q', sort="ascending"),
            x=alt.X("Number of lockup durations:O",scale=alt.Scale(domain=[1,2,3,4,5,6])),
            tooltip=['Number of users:Q',"Number of lockup durations:Q"],
            color=alt.Color('Number of lockup durations:O', 
                        sort=[1,2,3,4,5,6],
                        scale=alt.Scale(scheme='lightorange'),
                        legend=None),
        ).properties(height=300).configure_view(strokeOpacity=0)
        return n_duration_wallet_chart

    def txs_over_time_chart(self,hourly_stats_df):
        df = hourly_stats_df.rename(columns={'hr':'Time','tot_txs':'Number of transactions'})
        max_date = self.get_max_domain_date(df,'Time',10)
        txs_over_time_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('Time:T', \
                    axis=alt.Axis(tickCount=10, labelAngle=0, tickBand = 'center'),
                    scale=alt.Scale(domain=(df.Time.min(),max_date))),
            y="Number of transactions:Q",
            tooltip=[alt.Tooltip('Time:T', format='%Y-%m-%d %H:%M'),"Number of transactions:Q"]
        ).configure_mark(
            color='#fa9f75'
        ).configure_view(strokeOpacity=0)
        return txs_over_time_chart
    
    def get_max_domain_date(self, df, time_field, n_hours):
        if((pd.Timestamp(df[time_field].max()) - 
                    pd.Timestamp(df[time_field].min())).total_seconds()/3600 < n_hours):
            max_date = (pd.Timestamp(df[time_field].min()) + pd.to_timedelta(n_hours, unit='h')).strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            max_date = df[time_field].max()
        return max_date
    
    def users_over_time_chart(self, hourly_new_users_df):
        df = hourly_new_users_df.rename(columns={'time':'Time','cumsum_new_users':'Number of total users'})
        max_date = self.get_max_domain_date(df,'Time',10)
        users_over_time_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('Time:T',\
                axis=alt.Axis(tickCount=10, labelAngle=0, tickBand = 'center'),
                    scale=alt.Scale(domain=(hourly_new_users_df.time.min(), max_date))),
            y="Number of total users:Q",
            tooltip=[alt.Tooltip('Time:T', format='%Y-%m-%d %H:%M'), "Number of total users:Q"]
            ).configure_mark(
                color='#e1565b'
            ).configure_view(strokeOpacity=0)
        return users_over_time_chart
    
    def ust_duration_chart(self, last_duration_amount):
        ust_duration_chart = alt.Chart(last_duration_amount).mark_bar().encode(
                            y=alt.Y(field="UST deposited", type="quantitative"),
                            x=alt.X(field="Lockup period", type="nominal", axis=alt.Axis(labelAngle=0),
                                    sort=['3 months','6 months',
                                          '9 months','12 months',
                                          '15 months','18 months']),
                            color=alt.Color(field="Lockup period", type="nominal",
                                    sort=['3 months','6 months',
                                          '9 months','12 months',
                                          '15 months','18 months'],
                                    scale=alt.Scale(scheme='lightorange'),
                                    legend=None),
                                tooltip=["UST deposited","Lockup period"]
                            ).configure_view(strokeOpacity=0).properties(height=400)
        return ust_duration_chart

    def simulation_apr_chart(self, df):
        df = df.T.reset_index().rename(columns={'roi_perc':'ROI','index':'Lockup period',
                                                'roi_perc_label':'% ROI'})
        print(df)
        ust_duration_chart = alt.Chart(df).mark_bar().encode(
                            y=alt.Y(field="ROI", type="quantitative"),
                            x=alt.X(field="Lockup period", type="nominal", axis=alt.Axis(labelAngle=0),
                                    sort=['3 months','6 months',
                                          '9 months','12 months',
                                          '15 months','18 months']),
                            color=alt.Color(field="Lockup period", type="nominal",
                                    sort=['3 months','6 months',
                                          '9 months','12 months',
                                          '15 months','18 months'],
                                    scale=alt.Scale(scheme='lightorange'),
                                    legend=None),
                                tooltip=["% ROI","Lockup period"]
                            )
        text = ust_duration_chart.mark_text(
                align='center',
                baseline='middle',
                dy=-15,  # Nudges text to right so it doesn't appear on top of the bar
                fontSize=25
            ).encode(
                text='% ROI:N'
            )

        return (ust_duration_chart + text).properties(height=400).configure_view(strokeOpacity=0)
         

    def wallet_age_chart(self, wallet_age_df, dates_to_mark):
        dates_to_mark.height = max(30,int(wallet_age_df.address_count.max()/3*2))
        wallet_age_df = wallet_age_df.rename(columns={'min_date':'Date of wallet creation',
                                                     'address_count':'Number of wallets'})
        c = alt.Chart(wallet_age_df).mark_bar(color='#fab98d').encode(
            x=alt.X("Date of wallet creation:T", axis=alt.Axis(tickCount=10, labelAngle=0, title='Date of wallet creation')),
            y=alt.Y('Number of wallets:Q',scale=alt.Scale(domain=(0, max(50,int(wallet_age_df['Number of wallets'].max())))),axis=alt.Axis(labels=False,title='Number of wallets')),
            tooltip=["Date of wallet creation:T","Number of wallets:Q"]
        )

        c2 = alt.Chart(dates_to_mark).mark_rule(color='#e1565b').encode(
            x=alt.X('date'+':T',axis=alt.Axis(labels=False,title=''))
        )

        c3 = alt.Chart(dates_to_mark).mark_text(
            color='#e1565b',
            angle=270
        ).encode(
            x=alt.X('text_date'+':T',axis=alt.Axis(labels=False,title='')),
            y=alt.Y('height',axis=alt.Axis(labels=False,title='')),
            text='text'
        )

        wallet_age_chart = (c + c2 + c3).configure_view(strokeOpacity=0).properties(width=600)
        return wallet_age_chart

    def wallet_balance(self, users_balance_df):
        users_balance_df = users_balance_df.rename(columns={'amnt_sum':'Total UST deposited',
                                                            'balance':'Address balance ($)',
                                                            'weighted_avg_dur':'Weighted average lockup period',
                                                            'sender':'User address'})
        users_balance_df['url'] = 'https://finder.extraterrestrial.money/mainnet/address/'+users_balance_df['User address']
        if(len(users_balance_df)>5000):
            df = users_balance_df.sample(n=5000, random_state=1)
        else:
            df = users_balance_df
        dep_dist_balance_chart =alt.Chart(df).mark_point(opacity=1, filled=True).encode(
                                    y=alt.Y("Total UST deposited:Q",scale=alt.Scale(domain=(0, 100000))),
                                    x=alt.X("Address balance ($):Q",scale=alt.Scale(domain=(0, 100000))),
                                    href='url:N',
                                    color=alt.Color('Weighted average lockup period',
                                        scale=alt.Scale(scheme='lightorange'),
                                        legend=alt.Legend(
                                                    orient='none',
                                                    padding=5,
                                                    legendY=0,
                                                    direction='horizontal')),
                                    tooltip=['User address', 'Total UST deposited','Address balance ($)','Weighted average lockup period']
                                    ).configure_view(strokeOpacity=0).interactive()
        return dep_dist_balance_chart
    
    def boxplot_lockup(self,user_stats_df):
        chart = alt.Chart(user_stats_df.sort_values(by='duration')\
                        .rename(columns={'duration':'Lockup period (months)',
                                         'amount':'Amount UST deposited'}))\
                    .mark_boxplot(extent='min-max').encode(
                        x=alt.X(field="Lockup period (months)",
                                axis=alt.Axis(labelAngle=0)),
                        y='Amount UST deposited:Q',
                        color=alt.Color(field="Lockup period (months)", 
                                        type="nominal",
                                        scale=alt.Scale(scheme='lightorange'),
                                        legend=None),
                        tooltip=['Lockup period (months):N','Amount UST deposited']
                    ).configure_view(strokeOpacity=0)
        return chart