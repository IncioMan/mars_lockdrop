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
            color='#ffde85'
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
            color='#fab0ba'
        ).configure_view(strokeOpacity=0)
        return users_over_time_chart
####
    def users_dep_distr_chart(self, deposits_bucket_df):
        users_dep_distr_chart = alt.Chart(deposits_bucket_df.rename(columns=cols_dict).sort_values(by='BUCKET')).mark_bar().encode(
            y=alt.X(cols_dict['bucket_name']+":N", sort=alt.EncodingSortField(order='ascending')),
            x=cols_dict['N_USERS']+":Q",
            tooltip=[cols_dict['bucket_name']+":N",cols_dict['N_USERS']+":Q"]
        ).configure_mark(
            color='#fab0ba'
        ).properties(height=300).configure_axisX(
            labelAngle=0
        ).configure_view(strokeOpacity=0)
        return users_dep_distr_chart
####
    def cum_ust_chart(self, hourly_stats_df, tot_deposit):
        df=hourly_stats_df
        cum_ust_chart = alt.Chart(df.rename(columns=cols_dict)).mark_line(point=True).encode(
            x=alt.X(cols_dict['HR']+':T', sort=alt.EncodingSortField(order='ascending')),
            y=cols_dict['cumsum_ust']+":Q",
            tooltip=['Hour',cols_dict['cumsum_ust']+":Q"]
        ).configure_mark(
            color='#fab0ba'
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
        return user_part_prev_launches_chart
####
    def dep_dist_balance_chart(self, deposit_balance_df):
        deposit_balance_df['url'] = 'https://finder.extraterrestrial.money/mainnet/address/'+deposit_balance_df[cols_dict['SENDER']]
        if(len(deposit_balance_df)>5000):
            df = deposit_balance_df.sample(n=5000, random_state=1)
        else:
            df = deposit_balance_df
        dep_dist_balance_chart =alt.Chart(df).mark_point(opacity=1, filled=True).encode(
        y=alt.Y(cols_dict['AMOUNT']+":Q",scale=alt.Scale(domain=(0, 100000))),
        x=alt.X(cols_dict['AVG_BALANCE_USD']+":Q",scale=alt.Scale(domain=(0, 1000000))),
        href='url:N',
        color=alt.Color(cols_dict['N_TXS'],
            scale=alt.Scale(scheme='redpurple')),
        tooltip=[cols_dict['SENDER'], cols_dict['AMOUNT'],
            cols_dict['AVG_BALANCE_USD'],
            cols_dict['N_TXS']]
        ).configure_view(strokeOpacity=0).interactive()
        return dep_dist_balance_chart
###
    def wallet_age_chart(self, wallet_age_df, dates_to_mark):
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
        return wallet_age_chart

    def heatmap_withdrawing_chart(self, heatmap_data_df):
        dep_cat_label_order = heatmap_data_df.sort_values(by='DEP_CAT').DEP_CAT_label.unique()
        perc_withdrawn_cat_label_order = heatmap_data_df.sort_values(by='perc_withdrawn_cat_label').DEP_CAT_label.unique()
        heatmap_data_df[cols_dict['N_USERS']]=heatmap_data_df.sender
        heatmap_withdrawing_chart = alt.Chart(heatmap_data_df.rename(columns=cols_dict)).mark_rect().encode(
            y=alt.Y(cols_dict['perc_withdrawn_cat_label']+':O', sort=perc_withdrawn_cat_label_order),
            x=alt.X(cols_dict['DEP_CAT_label']+':O', sort=dep_cat_label_order),
            color=alt.Color(cols_dict['N_USERS']+':Q',
                    scale=alt.Scale(scheme='greenblue'),
                    legend=alt.Legend(title='N° users')),
            tooltip=[cols_dict['DEP_CAT_label']+':N',cols_dict['perc_withdrawn_cat_label']+':N',cols_dict['N_USERS']+':Q']
        ).properties(height=350)
        return heatmap_withdrawing_chart

    def heatmap_withdrawing_perc_users_chart(self, heatmap_data_df):
        dep_cat_label_order = heatmap_data_df.sort_values(by='DEP_CAT').DEP_CAT_label.unique()
        perc_withdrawn_cat_label_order = heatmap_data_df.sort_values(by='perc_withdrawn_cat_label').DEP_CAT_label.unique()
        heatmap_withdrawing_chart = alt.Chart(heatmap_data_df.rename(columns=cols_dict)).mark_rect().encode(
            y=alt.Y(cols_dict['perc_withdrawn_cat_label']+':O', 
                        sort=perc_withdrawn_cat_label_order
                        ),
            x=alt.X(cols_dict['DEP_CAT_label']+':O', sort=dep_cat_label_order),
            color=alt.Color(cols_dict['perc_sender']+':Q',
                    scale=alt.Scale(scheme='blues'),
                    legend=alt.Legend(title='% users')),
            tooltip=[cols_dict['DEP_CAT_label']+':N',
            cols_dict['perc_withdrawn_cat_label']+':N',
            cols_dict['perc_sender']+':Q',
            cols_dict['N_USERS']+':Q']
        ).properties(height=350).interactive()
        return heatmap_withdrawing_chart

    def tot_ust_left_chart(self,p2_hourly_df):
        tot_ust_left_chart = alt.Chart(p2_hourly_df.rename(columns=cols_dict)).mark_line(point=True).encode(
            x=alt.X(cols_dict['HR']+':T', sort=alt.EncodingSortField(order='ascending')),
            y=cols_dict['ust_left']+":Q",
            tooltip=[alt.Tooltip(cols_dict['HR']+':T', format='%Y-%m-%d %H:%M'), alt.Tooltip(cols_dict['ust_left']+":Q")]
        ).configure_mark(
            color='#fab0ba'
        ).properties(width=700).configure_axisX(
        ).configure_view(strokeOpacity=0)
        return tot_ust_left_chart

    def with_perc_buckets_chart(self,with_perc_buckets):
        with_perc_buckets_chart = alt.Chart(with_perc_buckets.sort_values(by='PERC_WITHDRAWN').rename(columns=cols_dict)).mark_bar().encode(
            y=alt.X(cols_dict['PERC_WITHDRAWN']+":N", sort=alt.EncodingSortField(order='ascending')),
            x=cols_dict['TOT_USERS']+":Q",
            tooltip=[cols_dict['PERC_WITHDRAWN']+":N",cols_dict['TOT_USERS']+":Q"]
        ).configure_mark(
            color='#ffde85'
        ).properties(height=300).configure_axisX(
            labelAngle=0
        ).configure_view(strokeOpacity=0)
        return with_perc_buckets_chart

    def with_users_hourly_chart(self,p2_hourly_df):
        p2_hourly_df['HR'] = '2022/'+p2_hourly_df['HR']
        with_users_hourly_chart = alt.Chart(p2_hourly_df.rename(columns=cols_dict)).mark_bar().encode(
            x=alt.X(cols_dict['HR']+':T',
                axis=alt.Axis(tickCount=10, labelAngle=0, tickBand = 'center')),
            y=cols_dict['WITH_USERS']+":Q",
            tooltip=[alt.Tooltip(cols_dict['HR']+':T', format='%Y-%m-%d %H:%M'),alt.Tooltip(cols_dict['WITH_USERS']+":Q")]
        ).configure_mark(
            color='#fab0ba'
        ).properties(width=700).configure_axisX(
            labelAngle=30
        ).configure_view(strokeOpacity=0)
        return with_users_hourly_chart

    def with_amount_hourly_chart(self,p2_hourly_df):
        with_txs_hourly_chart = alt.Chart(p2_hourly_df.rename(columns=cols_dict)).mark_bar().encode(
            x=alt.X(cols_dict['HR']+':T',
                axis=alt.Axis(tickCount=10, labelAngle=0, tickBand = 'center')),
            y=cols_dict['WITH_AMOUNT']+":Q",
            tooltip=[alt.Tooltip(cols_dict['HR']+':T', format='%Y-%m-%d %H:%M'),alt.Tooltip(cols_dict['WITH_AMOUNT']+":Q")]
        ).configure_mark(
            color='#B8E9E4'
        ).properties(width=700).configure_axisX(
            labelAngle=30
        ).configure_view(strokeOpacity=0)
        return with_txs_hourly_chart

    def pie_ust_chart(self, ust_df):
        ust_df = ust_df.sort_values(by='Type')
        pie_ust_chart = alt.Chart(ust_df).mark_arc(innerRadius=60).encode(
            theta=alt.Theta(field="UST", type="quantitative"),
            color=alt.Color(field="Type", type="nominal",
                    sort=['Withdrawn','Still deposited'],
                    scale=alt.Scale(scheme='pastel1'),
                    legend=alt.Legend(
                    orient='none',
                    padding=10,
                    legendY=-10,
                    direction='vertical'))
        ).configure_view(strokeOpacity=0)
        return pie_ust_chart

    def with_perc_user_chart(self, with_users_df):
        with_users_df['perc_withdrawn_precise'] = round(with_users_df[with_users_df.has_withdrawn_p2]['WITHDRAWN_AMOUNT_PHASE2'],3)/with_users_df['deposited_p1']
        with_users_df['url'] = 'https://finder.extraterrestrial.money/mainnet/address/'+with_users_df['sender']
        with_perc_user_chart =alt.Chart(with_users_df.rename(columns=cols_dict)).mark_point(opacity=1, filled=True).encode(
                y=alt.Y(cols_dict['deposited_p1']+":Q",scale=alt.Scale(domain=(0, 5500))),
                x=alt.X(cols_dict['WITHDRAWN_AMOUNT_PHASE2']+":Q",scale=alt.Scale(domain=(0, 5000))),
                href='url:N',
                color=alt.Color(cols_dict['perc_withdrawn_precise']+':Q',
                    scale=alt.Scale(scheme='redpurple'),
                    legend=alt.Legend(title='% With')),
                tooltip=[cols_dict['sender']+':N',cols_dict['deposited_p1']+':N',
                        cols_dict['WITHDRAWN_AMOUNT_PHASE2']+':N',cols_dict['perc_withdrawn_precise']+':N']
                ).configure_view(strokeOpacity=0).interactive()
        return with_perc_user_chart