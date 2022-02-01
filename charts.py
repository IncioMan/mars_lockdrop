import pandas as pd
from constants import cols_dict
import altair as alt

class ChartProvider:

    def __init__(self):
        pass
    
    def txs_over_time_chart(self, hourly_stats_df):
        txs_over_time_chart = alt.Chart(hourly_stats_df).mark_bar().encode(
            x=alt.X(cols_dict['HR']+':T', \
                    axis=alt.Axis(tickCount=10, labelAngle=0, tickBand = 'center')),
            y=cols_dict['TOT_TXS']+":Q",
            tooltip=['Hour',cols_dict['TOT_TXS']+":Q"]
        ).configure_mark(
            color='#F3BD6A'
        ).configure_view(strokeOpacity=0)
        return txs_over_time_chart
####
    def users_over_time_chart(self, hourly_new_users_df):
        users_over_time_chart = alt.Chart(hourly_new_users_df).mark_bar().encode(
        x=alt.X(cols_dict['TIME']+':T',\
            axis=alt.Axis(tickCount=10, labelAngle=0, tickBand = 'center')),
        y=cols_dict['cumsum_new_users']+":Q",
        tooltip=['Hour', cols_dict['cumsum_new_users']+":Q"]
        ).configure_mark(
            color='#F1705F'
        ).configure_view(strokeOpacity=0)
        return users_over_time_chart
####
    def users_dep_distr_chart(self, deposits_bucket_df):
        users_dep_distr_chart = alt.Chart(deposits_bucket_df.rename(columns=cols_dict).sort_values(by='BUCKET')).mark_bar().encode(
            y=alt.X(cols_dict['bucket_name']+":N", sort=alt.EncodingSortField(order='ascending')),
            x=cols_dict['N_USERS']+":Q",
            tooltip=[cols_dict['bucket_name']+":N",cols_dict['N_USERS']+":Q"]
        ).configure_mark(
            color='#F1705F'
        ).properties(height=300).configure_axisX(
            labelAngle=0
        ).configure_view(strokeOpacity=0)
        return users_dep_distr_chart
####
    def cum_ust_chart(self, hourly_stats_df):
        cum_ust_chart = alt.Chart(hourly_stats_df.rename(columns=cols_dict)).mark_line(point=True).encode(
            x=alt.X(cols_dict['HR']+':T', sort=alt.EncodingSortField(order='ascending')),
            y=cols_dict['cumsum_ust']+":Q",
            tooltip=['Hour',cols_dict['cumsum_ust']+":Q"]
        ).configure_mark(
            color='#F1705F'
        ).properties(width=700).configure_axisX(
            labelAngle=0
        ).configure_view(strokeOpacity=0)
        return cum_ust_chart
####
    def n_tx_wallet_chart(self, user_stats_df):
        df = user_stats_df.rename(columns=cols_dict)[cols_dict['N_TXS']]\
            .value_counts().sort_index().reset_index().rename(columns={'index':cols_dict['N_TXS'],cols_dict['N_TXS']:'N° of users'})
        n_tx_wallet_chart = alt.Chart(df).mark_line(point = True, color='#7DDBD3').encode(
            y=alt.Y('N° of users:Q', sort="ascending"),
            x=cols_dict['N_TXS']+":O",
            tooltip=['N° of users:Q',cols_dict['DEPOSIT_TXS']+":Q"]
        ).properties(height=300).configure_view(strokeOpacity=0)
        return n_tx_wallet_chart
####
    def user_part_prev_launches_chart(self, prev_launches_df):
        user_part_prev_launches_chart = alt.Chart(prev_launches_df).mark_bar().encode(
        x=alt.X(cols_dict['TYPE']+":N", axis=alt.Axis(labelAngle=0, tickBand = 'center')),
        y=cols_dict['PARTICIPANTS']+":Q",
        color=alt.Color(cols_dict['PARTICIPATE_TYPE'],
            scale=alt.Scale(domain=list(prev_launches_df[cols_dict['PARTICIPATE_TYPE']].unique()),
                            range=['#F1705F','#F3BD6A']),
            legend=alt.Legend(
            orient='none',
            padding=10,
            legendY=-10,
            direction='horizontal')),
        tooltip=[cols_dict['TYPE']+":N",cols_dict['PARTICIPANTS']+":Q",cols_dict['PARTICIPATE_TYPE']]
        ).properties(height=400).configure_axisX(
        labelAngle=-10
        ).configure_view(strokeOpacity=0)
        return user_part_prev_launches_chart
####
    def dep_dist_balance_chart(self, deposit_balance_df):
        if(len(deposit_balance_df)>5000):
            df = deposit_balance_df.sample(n=5000, random_state=1)
        else:
            df = deposit_balance_df
        dep_dist_balance_chart =alt.Chart(df).mark_point(opacity=1, filled=True).encode(
        y=alt.Y(cols_dict['AMOUNT']+":Q",scale=alt.Scale(domain=(0, 100000))),
        x=alt.X(cols_dict['AVG_BALANCE_USD']+":Q",scale=alt.Scale(domain=(0, 1000000))),
        color=alt.Color(cols_dict['N_TXS'],
            scale=alt.Scale(scheme='reds')),
        tooltip=[cols_dict['SENDER'], cols_dict['AMOUNT'],
            cols_dict['AVG_BALANCE_USD'],
            cols_dict['N_TXS']]
        ).configure_view(strokeOpacity=0).interactive()
        return dep_dist_balance_chart
###
    def wallet_age_chart(self, wallet_age_df, dates_to_mark):
        wallet_age_df = wallet_age_df.rename(columns=cols_dict)
        df2 = wallet_age_df.head()
        c = alt.Chart(wallet_age_df).mark_bar(color='#F3BD6A').encode(
            x=alt.X(cols_dict['MIN_DATE']+":T", axis=alt.Axis(tickCount=10, labelAngle=0, title=cols_dict['MIN_DATE'])),
            y=cols_dict['ADDRESS_COUNT']+":Q",
            tooltip=[cols_dict['MIN_DATE']+":T",cols_dict['ADDRESS_COUNT']]
        )

        c2 = alt.Chart(dates_to_mark).mark_rule(color='#F1705F').encode(
            x=alt.X('date'+':T',axis=alt.Axis(labels=False,title=''))
        )

        c3 = alt.Chart(dates_to_mark).mark_text(
            color='#F1705F',
            angle=270
        ).encode(
            x=alt.X('text_date'+':T',axis=alt.Axis(labels=False,title='')),
            y='height',
            text='text'
        )

        wallet_age_chart = (c + c2 + c3).configure_view(strokeOpacity=0).properties(width=600)
        return wallet_age_chart