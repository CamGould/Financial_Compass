# Welcome to the Porfolio_Creator page

# NOTE : yahoo finance by defult is pulling prices in USD
    # Use st.radio button to allow the user which currency they are  using (CAD or US)

# NOTE : add in some 'help' functions:
    # https://docs.streamlit.io/library/api-reference/widgets/st.radio

# Import the libraries I need 
# from asyncio.constants import SENDFILE_FALLBACK_READBUFFER_SIZE
from cProfile import run
import csv
from tracemalloc import start
from st_aggrid import AgGrid
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import pandas_datareader as pdr
from datetime import date
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path
import altair as alt

st.set_page_config(page_title="Portfolio Builder", page_icon="📈", initial_sidebar_state="collapsed", layout="centered")

logo_path = Path("/users/cg/Documents/Personal/Projects/Capstone_Project/Supplemental/Logo.png")
header_logo_path = Path("/users/cg/Documents/Personal/Projects/Capstone_Project/Supplemental/Top_logo.png")
sidebar_logo_path = Path("/users/cg/Documents/Personal/Projects/Capstone_Project/Supplemental/Sidebar_Image.png")

header_logo = Image.open(header_logo_path)
sidebar_logo = Image.open(sidebar_logo_path)
logo = Image.open(logo_path)

st.image(header_logo)

st.markdown("")

st.markdown("<h2 style='text-align: center'>Welcome to the <em>Portfolio Builder<em></h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center'><em>The <strong>Portfolio Builder</strong> is a tool that allows user to quickly build their current portfolio using the most up to date stock prices pulled from Yahoo Finance.</em></p>", unsafe_allow_html=True)


# Get the user's name
user_name = st.text_input('What is your name?', 'New User', help="We capture this information to personalize your experience. This field is optional.")

# Create the session state variable that will hold the users datframe 
if "user_portfolio" not in st.session_state:
    st.session_state.user_portfolio = pd.DataFrame(columns=['Currency', 'Ticker','Name', 'Market Currency','Date Purchased','Quantity Owned','Purchase Price','Market Price','Holding Value', 'Net Gain', 'Dividend Yield','Dividend Per Share','Yearly Dividend','Quarterly Dividend'])

# Import the data set from NASDAQ that holds the company information
        # To obtain this .csv file head to https://www.nasdaq.com/market-activity/stocks/screener 
Path = "/users/cg/Documents/Personal/Projects/Capstone_Project/Supplemental/nasdaq_screener_1659152283521.csv"
nasdaq_data = pd.read_csv(Path)

# View a warning 
st.warning("Make sure you have selected your desired currency before building your portfolio!")


# Call in the library for currency converter
from currency_converter import CurrencyConverter

# Create a shortcut for calling in the currency converter
c = CurrencyConverter()

# Create the USD to CAD rate
usd_to_cad_rate = c.convert(1, "USD", "CAD")

# Store the CAD to USD rate
cad_to_usd_rate = c.convert(1, "CAD", "USD")

# Create the button for the user to select their currency
user_currency_selection = st.radio("Which currency do you want to build your porfolio in?", ("Canadian", "American"))
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

if user_currency_selection == "Canadian":
    st.write(f"1.00 CAD is currently worth {round(cad_to_usd_rate, 2)} USD")

if user_currency_selection == "American":
    st.write(f"1.00 USD is currently worth {round(usd_to_cad_rate, 2)} CAD")

# Create a list of all company names
all_stock_names = nasdaq_data.Name.values.tolist()

# Create a list of all available stocks the user can pull from 
all_tickers = nasdaq_data.Symbol.values.tolist()

# Call in and store variable for the row to be added:

# Allow the user to select the ticker they want to add 
ticker_selection = st.selectbox(
    "What is the Ticker of the company you are adding to your portfolio?",
    all_tickers,)

# Allow the user to input the number of shares they bought
amount_of_ticker_shares = st.number_input(f"How many shares of {ticker_selection} did you purchase?", min_value=0.1, value=1.0, step=0.1)
amount_of_shares = round(amount_of_ticker_shares, 2)

# Allow the user to select when they purchased the stock
stock_purchase_date = st.date_input(f"When did you purchase {ticker_selection}?")

# Touch of cheeky formatting
col1, col2, col3 = st.columns([0.18, 1, 0.18])
with col1:
    pass
with col3:
    pass
with col2:
# Create a button to call in the dividend info to increase the speed 
    pull_stock_info = st.button(f'Press here to add {amount_of_shares} shares of {ticker_selection} using {user_currency_selection} currency values')

if pull_stock_info:
    
    # Call in the info about the stock
    yf_stock = yf.Ticker(ticker_selection)

    # Here I will call in what currency it is 
    stock_currency = yf_stock.info['financialCurrency']

    # Use yFinance to get the price of the stock when the user purchased 
    start = stock_purchase_date
    price_df = yf.download(ticker_selection,start)
    user_purchase_price = round(price_df.iat[0,4], 2)
    # Convert the currency if necessary
    if user_currency_selection == "Canadian":
        user_purchase_price = user_purchase_price * usd_to_cad_rate

    # Use yFinance to get the last close price of the stock
    start = date.today()
    last_close = yf.download(ticker_selection,start)
    stock_current_close = round(last_close.iat[0,4], 2)
    # Convert the currency if necessary
    if user_currency_selection == "Canadian":
        stock_current_close = stock_current_close * usd_to_cad_rate

    # Here I will store the holding value
    holding_value = stock_current_close * amount_of_shares

    # Here I will store the net gain
    net_gain = holding_value - (user_purchase_price * amount_of_shares)
    
    # Here I will get the dividend yeild - A
    yearly_dividend = yf_stock.info['dividendRate']
    if yearly_dividend is None:
        yearly_dividend = 0
    # Convert the currency if necessary
    if user_currency_selection == "Canadian":
        yearly_dividend = yearly_dividend * usd_to_cad_rate
    
    # Here I will get the dividend income per share - Quarterly dividend yeild per share
    dividend_yield = yf_stock.info['dividendYield']
    if dividend_yield is None:
        dividend_yield = 0
    dividend_yield_percent = round(dividend_yield*100, 2)

    # Here I will store what exchange it is on
    stock_exchange = yf_stock.info['exchange']

    # Here I will get the company name
    stock_name = yf_stock.info['longName']

    # Here I will get the company image url
    stock_logo = yf_stock.info['logo_url']

    # Here I will capture the Quarterly dividend holding payout
    quarterly_dividend_payout = (yearly_dividend/4) * amount_of_shares

    # Here I will store the yearly dividend holding payout 
    yearly_dividend_payout = quarterly_dividend_payout * 4

    with st.expander("Show/Hide the Review Information", True):
        st.write(f'Please review the information for **{stock_name}** that has been added to your portfolio')
        st.write(f'|| *Ticker* : **{ticker_selection}** ||')
        st.write(f'|| *Company Name* : **{stock_name}** ||')
        st.write(f'|| *Stock Exchange* : **{stock_exchange}** ||')
        st.write(f'|| *Market Currency* : **{stock_currency}** ||')
        st.write(f'|| *Date Purchased* : **{stock_purchase_date}** ||')
        st.write(f'|| *Quantity Owned* : **{amount_of_shares}** ||')
        st.write(f'|| *Purchase Price* : **$ {round(user_purchase_price, 2)}** ||')
        st.write(f'|| *Market Price* : **$ {round(stock_current_close, 2)}** ||')
        st.write(f'|| *Current Holding Value* : **$ {round(holding_value, 2)}** ||')
        st.write(f'|| *Current Net Gain* : **$ {round(net_gain, 2)}** ||')
        st.write(f'|| *Dividend Yield* : **{dividend_yield_percent}%** ||')
        st.write(f'|| *Dividend Income per Share* : **$ {round(yearly_dividend, 2)}** ||')
        st.write(f'|| *Yearly Dividend* : **$ {round(yearly_dividend_payout, 2)}** ||')
        st.write(f'|| *Quarterly Dividend* : **$ {round(quarterly_dividend_payout, 2)}** ||')
        st.markdown(f"![]({stock_logo})")

    # Define the dataframe parameters 
    user_portfolio_df = pd.DataFrame(
        {'Currency': user_currency_selection,
        'Ticker': ticker_selection,
        'Name': stock_name,
        'Market Currency': stock_currency,
        'Date Purchased': stock_purchase_date, 
        'Quantity Owned': amount_of_shares, 
        'Purchase Price': user_purchase_price,
        'Market Price': stock_current_close,
        'Holding Value': holding_value,
        'Net Gain': net_gain,
        'Dividend Yield': dividend_yield_percent,
        'Dividend Per Share': yearly_dividend,
        'Yearly Dividend': yearly_dividend_payout,
        'Quarterly Dividend': quarterly_dividend_payout},
        index=[ticker_selection])

    # Add the new row of the portfolio with the old row 
    st.session_state.user_portfolio = pd.concat([st.session_state.user_portfolio, user_portfolio_df])

# Complete if statement for button
if not pull_stock_info:
    st.write()

# Allow the user to delete the last row 
with st.expander("Press here to delete a row:", False):
    col1, col2, col3 , col4, col5 = st.columns([0.5, 0.5, 1, 0.2, 0.2])
    with col1:
        pass
    with col2:
        pass
    with col4:
        pass
    with col5:
        pass
    with col3 :
        delete_holding = st.button('Delete Last Row')

# Add button to delete last add
if delete_holding:
    st.session_state.user_portfolio = st.session_state.user_portfolio[:-1]

# title for the df
st.header(f"{user_name}'s Current Portfolio")
# Display the users portfolio 
AgGrid(st.session_state.user_portfolio, )

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

complete_portfolio = st.button(f"Press here to complete {user_name}'s portfolio")
if complete_portfolio:
    final_portfolio = st.session_state.user_portfolio

    csv = convert_df(final_portfolio)

    total_value = round(final_portfolio["Holding Value"].sum(), 2)
    total_gain = round(final_portfolio["Net Gain"].sum(), 2)
    total_yearly_dividend = round(final_portfolio["Yearly Dividend"].sum(), 2)
    total_monthly_dividend = round(final_portfolio['Quarterly Dividend'].sum(), 2)

    
if len(st.session_state.user_portfolio) is not 0:
    total_portfolio_value = st.session_state.user_portfolio["Holding Value"].sum()
    total_portfolio_value_formatted = "{:,}".format(round(total_portfolio_value, 2))
    number_of_holdings = len(st.session_state.user_portfolio)
    portfolio_net_gain = st.session_state.user_portfolio["Net Gain"].sum()
    portfolio_net_gain_formatted = "{:,}".format(round(portfolio_net_gain, 2))
    total_yearly_dividend_income = st.session_state.user_portfolio["Yearly Dividend"].sum()
    total_yearly_dividend_income_formatted = "{:,}".format(round(total_yearly_dividend_income, 2))
    total_quarterly_dividend_income = st.session_state.user_portfolio["Quarterly Dividend"].sum()
    total_quarterly_dividend_income_formatted = "{:,}".format(round(total_quarterly_dividend_income, 2))
    total_number_of_shares = st.session_state.user_portfolio["Quantity Owned"].sum()
    average_purchase_price = st.session_state.user_portfolio["Purchase Price"].mean()
    average_purchase_price_formatted = "{:,}".format(round(average_purchase_price, 2))
    average_market_price = st.session_state.user_portfolio["Market Price"].mean()
    average_market_price_formatted = "{:,}".format(round(average_market_price, 2))

    yearly_dividend_income_per_share = total_yearly_dividend_income / total_number_of_shares
    yearly_dividend_income_per_share_formatted = "{:,}".format(round(yearly_dividend_income_per_share, 2))
    quarterly_dividend_per_share = total_quarterly_dividend_income / total_number_of_shares
    quarterly_dividend_per_share_formatted = "{:,}".format(round(quarterly_dividend_per_share, 2))


with st.sidebar:
    st.markdown("<h2 style='text-align: center'>Company Information Library</h2>", unsafe_allow_html=True)
    with st.expander("Find Info using Company Name", True):
        stock_name_lookup = st.selectbox("Who do you want the ticker for?", all_stock_names)
        stock_ticker_lookup = nasdaq_data.loc[nasdaq_data['Name'] == stock_name_lookup, 'Symbol'].values[0]
        st.markdown(f"<h3 style='text-align: center'>|| {stock_ticker_lookup} ||</h3>", unsafe_allow_html=True)
        show_more = st.button(f"Additional {stock_ticker_lookup} Information")
        if show_more:
            stock_search = yf.Ticker(stock_ticker_lookup)
            info = []
            info = stock_search.info 
            sb_last_price = stock_search.info['currentPrice']
            sb_fiftytwo_low  = stock_search.info['fiftyTwoWeekLow']
            sb_fiftytwo_high = stock_search.info['fiftyTwoWeekHigh']
            sb_dividendyeild = stock_search.info["dividendYield"]

            sb_last_price_formatted = "{:,}".format(round(sb_last_price, 2))
            st.markdown(f"<h6>|| <em>Current Price of {stock_ticker_lookup}</em> ||  ${sb_last_price_formatted}</h6>", unsafe_allow_html= True)
            sb_fiftytwo_high_formatted = "{:,}".format(round(sb_fiftytwo_high, 2))
            st.markdown(f"<h6>|| <em>52 Week High of {stock_ticker_lookup}</em> ||  ${sb_fiftytwo_high_formatted}</h6>", unsafe_allow_html= True)
            sb_fiftytwo_low_formatted = "{:,}".format(round(sb_fiftytwo_low, 2))
            st.markdown(f"<h6>|| <em>52 Week Low of {stock_ticker_lookup}</em> ||  ${sb_fiftytwo_low_formatted}</h6>", unsafe_allow_html= True)
            sb_dividendyeild_percent = "{:.2%}".format(sb_dividendyeild)
            st.markdown(f"<h6>|| <em>52 Dividend Yeild of {stock_ticker_lookup}</em> ||  {sb_dividendyeild_percent}</h6>", unsafe_allow_html= True)

if len(st.session_state.user_portfolio) is not 0:
    with st.sidebar:
        st.markdown("<h2 style='text-align: center'>Your Porfolio Breakdown</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Total Portfolio Value:</h4>", unsafe_allow_html=True)
        with st.expander(f"Your portfolio is worth: ${total_portfolio_value_formatted}", True):
            st.markdown(f"<h6>|| <em>Total Net Gain of Portfolio</em> ||  {portfolio_net_gain_formatted}</h6>", unsafe_allow_html= True)
            st.markdown(f"<h6>|| <em>Number of Holdings</em> ||  {number_of_holdings}</h6>", unsafe_allow_html= True)
            st.markdown(f"<h6>|| <em>Number of Shares</em> ||  {total_number_of_shares}</h6>", unsafe_allow_html= True)
            st.markdown(f"<h6>|| <em>Average Purchase Price</em> ||  ${average_purchase_price_formatted}</h6>", unsafe_allow_html= True)
            st.markdown(f"<h6>|| <em>Average Market Price</em> ||  ${average_market_price_formatted}</h6>", unsafe_allow_html= True)
        
        st.markdown("<h4>Total Dividend Income:</h4>", unsafe_allow_html=True)
        with st.expander(f"Yearly dividend income: ${total_yearly_dividend_income_formatted}", True):
            st.markdown(f"<h6>|| <em>Quarterly Dividend Income</em> ||  ${total_quarterly_dividend_income_formatted}</h6>", unsafe_allow_html= True)
            st.markdown(f"<h6>|| <em>Yearly Dividend per Share</em> ||  ${yearly_dividend_income_per_share_formatted}</h6>", unsafe_allow_html= True)
            
        
with st.sidebar:
    st.image(sidebar_logo)
    st.markdown("<h4 style='text-align: center'><em>Financial Compass</em></h4>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center'><em>Tools for Navigating Your Financials</em></h5>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center'><em>Established in August 2022</em></h6>", unsafe_allow_html=True)
    

if complete_portfolio:
    download_portfolio = st.download_button(f"Press here to download {user_name}'s portfolio!", csv,file_name=f'{user_name}s_portfolio.csv', mime='text/csv')

st.markdown("")
st.markdown("")
st.markdown("")

st.image(logo, width=150)
st.caption("*Design Rights Property of: Financial Compass*")
st.caption("*Results are financial insights, not advice*")
st.caption("*Contributor: [Cam Gould](https://www.linkedin.com/in/camrgould/)*")


