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
    # df_pred['Date'] = pd.to_datetime(df_pred['Date'])
    # df_pred = df_pred.set_index('fecha')
    # df_pred = pd.read_excel(os.path.join(data_path,'prediction_df.xlsx'))
    # df_mape = pd.read_excel(os.path.join(data_path,'errors_df.xlsx'))
    df_pred.columns = df_pred.columns.str.replace('.', '_', regex=False)
    df_mape.columns = df_mape.columns.str.replace('.', '_', regex=False)
    stock_list = df_pred.columns.tolist()
    df_melted = df_pred.reset_index().melt(id_vars=["fecha"], var_name="Stock", value_name="Price")

    # if choice == 'About':
    #     st.markdown('This streamlit app is intended to track all the strategies')

    # if choice == 'Forecast for Stocks':
    st.subheader('Forecast for Stocks 30 days ahead')
    stock = st.selectbox('Pick one stock',options= stock_list)
    df_selected = df_melted[df_melted["Stock"] == stock]
    # print(df_selected)
    # st.write("Preview of selected stock data:", df_selected)
    chart = (
    alt.Chart(df_selected)
    .mark_line()
    .encode(
        x="fecha:T",  # Time data type
        y=alt.Y("Price:Q", title="Stock Price", scale=alt.Scale(zero=False)),
        tooltip=["fecha", "Price"],  # Add tooltips
    )
    .properties(title=f"Stock Forecast: {stock}", width=700, height=400)
)

# Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)
    st.subheader(f'Model MAPE for {stock} in test is {round(df_mape[stock].iloc[0]*100,3)}%')
    
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

