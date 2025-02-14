import streamlit as st
import pandas as pd
import os
# import matplotlib.pyplot as plt
# import plotly.express as px
import numpy as np
import altair as alt
# from scipy.stats import pearsonr

# 
main_path = os.path.abspath(os.getcwd())
data_path = os.path.join(main_path,'data')

st.set_page_config(page_title='QuantTrader',
                   initial_sidebar_state= 'collapsed')


def main():
    # menu = ['Forecast for Stocks', 'other strat', 'About'] 
    # choice = st.sidebar('Menu',menu)
    # df_pred = pd.read_excel(r'C:\Users\Admin\Documents\Repos_AlgoTrading\Strategy_Results\data\prediction_df.xlsx')
    # df_mape = pd.read_excel(r'C:\Users\Admin\Documents\Repos_AlgoTrading\Strategy_Results\data\errors_df.xlsx')
    df_pred = pd.read_excel('prediction_df.xlsx')
    df_mape = pd.read_excel('errors_df.xlsx')
    df_real = pd.read_excel('stock_real_data.xlsx')
    
    df_pred['fecha'] = pd.to_datetime(df_pred['fecha']).dt.date
    df_real['fecha'] = pd.to_datetime(df_real['fecha']).dt.date
    # df_pred = df_pred.set_index('fecha')
    # df_pred = pd.read_excel(os.path.join(data_path,'prediction_df.xlsx'))
    # df_mape = pd.read_excel(os.path.join(data_path,'errors_df.xlsx'))
    df_pred.columns = df_pred.columns.str.replace('.', '_', regex=False)
    df_mape.columns = df_mape.columns.str.replace('.', '_', regex=False)
    df_real.columns = df_real.columns.str.replace('.', '_', regex=False)
    stock_list = df_pred.columns.tolist()
    
    # st.write(df_real)

    # if choice == 'About':
    #     st.markdown('This streamlit app is intended to track all the strategies')

    # if choice == 'Forecast for Stocks':
    st.subheader('Forecast for Stocks 30 days ahead')
    stock = st.selectbox('Pick one stock',options= stock_list)

    # st.write(df_real)
    
    df_combined = df_pred[['fecha',stock]].copy()
    df_combined.columns = ['fecha','Predicted Price']
    df_real1 = df_real[['fecha',stock]].copy()
    df_real1.columns = ['fecha','Real Price']
    df_combined = df_combined.merge(df_real1,
                                     on = 'fecha',
                                     how="left")
    df_combined["Real Price"] = df_combined["Real Price"].astype(float)
    df_maped_oot = df_combined.copy()
    df_maped_oot = df_maped_oot.dropna()
    df_maped_oot['mape_oot'] = (df_maped_oot['Real Price'] - df_maped_oot['Predicted Price'])/df_maped_oot['Predicted Price']
    # st.write(df_combined)
    mean_oot = df_maped_oot['mape_oot'].mean()
    df_melted = df_combined.reset_index().melt(id_vars=["fecha"], var_name="Type", value_name="Price")
    df_melted = df_melted.dropna()
    df_melted = df_melted[df_melted['Type'] != 'index']
    # st.write(df_melted)
    # df_selected = df_melted[df_melted["Stock"] == stock]
    # print(df_selected)
    # st.write("Preview of selected stock data:", df_selected)
    num_real_points = df_melted[df_melted["Type"] == "Real Price"].dropna().shape[0]

    color_scale = alt.Scale(domain=["Predicted Price", "Real Price"], range=["#1f77b4", "orange"])

    chart = (
    alt.Chart(df_melted)
    .mark_line()
    .encode(
        x=alt.X("fecha:T", title = 'Date'), # Time data type
        y=alt.Y("Price:Q", title="Stock Price", scale=alt.Scale(zero=False)),
        color=alt.Color("Type:N", scale=color_scale, title="Price Type"),
        tooltip=["fecha", "Price",'Type'],  # Add tooltips
    )
    .properties(title=f"Stock Forecast: {stock}", width=700, height=400))

    point_chart = (
    alt.Chart(df_melted)
    .mark_point(size=80)  # Customize marker size
    .encode(
        x=alt.X("fecha:T", title = 'Date'),
        y="Price:Q",
        color=alt.Color("Type:N", scale=color_scale),  # Keep colors consistent
        tooltip=["fecha", "Price", "Type"]
    )
    .transform_filter(alt.datum.Type == "Real Price")) if num_real_points > 0 else None  # Show only if real data exists

# ###Display the chart in Streamlit
    final_chart = chart + (point_chart if point_chart else alt.Chart())  # Avoid None errors

    st.altair_chart(final_chart, use_container_width=True)
    st.write(f'Model percentual error for {stock} in test is {round(df_mape[stock].iloc[0]*100,2)}%')
    st.write(f'Model Out of time error for {stock} is {round(mean_oot*100,2)}%')
    
    # print(df_pred[stock])
    performances = []
    erros = []

    list_columns = df_pred.columns.tolist()[:-2]
    
    for symbol in list_columns:
        performance = (df_pred[f'{symbol}'].iloc[-1] - df_pred[f'{symbol}'].iloc[0])/df_pred[f'{symbol}'].iloc[0]
        performances.append(performance)
        error = df_mape[f'{symbol}'].iloc[0]
        erros.append(error)

    st.header(f'Expected Top and Buttom Performers')
    ln_val = st.slider('Select the number of stocks in the top and buttom',1,20,1)
    df_perf = pd.DataFrame(zip(list_columns,performances,erros),columns=['asset','expected_performance','error'])
    df_perf = df_perf.set_index('asset')
    df_perf = df_perf.sort_values('expected_performance',ascending=False)
    df_perf2 = df_perf.copy()
    df_perf2 = df_perf2[df_perf2['error'] <0.1]
    top_5 = df_perf2.head(ln_val)
    bottom_5 = df_perf2.tail(ln_val)

    col1_top, col2_top = st.columns(2)    
    
    with col1_top:
        st.subheader(f'Top {ln_val}')
        st.dataframe(top_5)
    with col2_top:
        st.subheader(f'Buttom {ln_val}')
        st.dataframe(bottom_5)
        

    
    st.write('Disclaimer: Invest in capital markets is a risky way to make money, Do not Invest money you need. I WILL BE NOT RESPONSIBLE FOR YOUR ACTIONS ON FINANCIAL MARKETS')

if __name__ == '__main__':
    main()

