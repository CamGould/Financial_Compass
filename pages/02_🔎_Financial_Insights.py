import datetime as dt
from email import header
from operator import index
from re import sub
import streamlit as st
import pandas as pd
from PIL import Image
import time
from pathlib import Path
import urllib.request


# st.write('<style>div.Widget.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
st.set_page_config(page_title="Portfolio Builder", page_icon="🔎", initial_sidebar_state="collapsed", layout="wide")

urllib.request.urlretrieve("https://github.com/CamGould/Financial_Compass/blob/main/supplemental/Logo.png?raw=true", "logo.png")
urllib.request.urlretrieve("https://github.com/CamGould/Financial_Compass/blob/main/supplemental/Top_logo.png?raw=true", "header_logo.png")
urllib.request.urlretrieve("https://github.com/CamGould/Financial_Compass/blob/main/supplemental/Sidebar_Image.png?raw=true", "sidebar_logo.png")

header_logo = Image.open("header_logo.png")
sidebar_logo = Image.open("sidebar_logo.png")
logo = Image.open("logo.png")


title_1, title_2, title_3 = st.columns([0.5, 2, 0.5])
with title_2:
    st.image(header_logo)
st.markdown("<h2 style='text-align: center'>Welcome to the <em>Financial Insights<em> Tool</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center'>The <strong>Financial Insights</strong> tool was created as a way for individuals to help better understand their financial position, allowing them to <em>visualize their current standing and plan their desired future position</em>.</p>", unsafe_allow_html=True)





with st.form("Welcome to the Financial Insights Page! Please provide some insformation to get started:"):
    st.markdown("<h4 style='text-align: center'>Let's Personalize your Analysis</h4>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center'><em>Please begin by providing some information so we can personalize your insights:</em></h6>", unsafe_allow_html=True)
    
    form_col1, form_col2 = st.columns(2)
    with form_col1:
        st.text_input("What is your name?", "New User", 64, help="Your name will be used to customize some variables")
        st.number_input("What is your ideal net income per year?", 0, step=1000, help="Your ideal net income is the amount of additional money you woud like to have left over each year after all of your yearly expenses and spending." )
    
    with form_col2:
        st.selectbox("What province do you live in?", ["Alberta", "British Columbia", "Manitoba", "New Brunswick", "Newfoundland and Labrador", 
        "Northwest Territories", "Nova Scotia", "Nunavut", "Ontario", "Prince Edward Island", "Quebec", "Saskatchewan", "Yukon"], 
        help="Your provience is used to calculate applicable income taxes")
        st.selectbox("What is your current employment status", ["Employed", "Unemployed", "Student", "Other"], help= "This information is used for tax purposes and personalized recomendations")


    personal_information_form = st.form_submit_button('Confirm the above personal information?')
    if personal_information_form:
        st.success("Information added successfully!")

# Store tax variables - rough calculation due to progressive tax
tax_46226 = 0.2005
tax_50197 = 0.2415
tax_81411 = 0.2965
tax_92454 = 0.3148
tax_95906 = 0.3389
tax_100392 = 0.3791
tax_150000 = 0.4341
tax_155625 = 0.4497
tax_220000 = 0.4835
tax_221708 = 0.4991
tax_over_221708 = 0.5353

dividend_tax_46226 = 0.0924
dividend_tax_50197 = 0.1395
dividend_tax_81411 = 0.2028
dividend_tax_92454 = 0.2238
dividend_tax_95906 = 0.2516
dividend_tax_100392 = 0.2978
dividend_tax_150000 = 0.3610
dividend_tax_155625 = 0.3790
dividend_tax_220000 = 0.4179
dividend_tax_221708 = 0.4358
dividend_tax_over_221708 = 0.4774


ontario_tax_information = pd.DataFrame(
    [["Bracket 1", 46226, 0.2005, 0.0924],
    ["Bracket 2", 50197, 0.2415, 0.1395],
    ["Bracket 3", 81411, 0.2965, 0.2028],
    ["Bracket 4", 92454, 0.3148, 0.2238],
    ["Bracket 5", 95906, 0.3389, 0.2516],
    ["Bracket 6", 100392, 0.3791, 0.2978],
    ["Bracket 7", 150000, 0.4341, 0.3610],
    ["Bracket 8", 155625, 0.4497, 0.3790],
    ["Bracket 9", 220000, 0.4835, 0.4179],
    ["Bracket 10", 221708, 0.4991, 0.4358],
    ["Bracket 11", 1000000000, 0.5353, 0.4774]],
    columns=["Tax Bracket", "Max Income per Bracket_start", "Income Tax_start", "Dividend Tax_start"])

ontario_tax_information.set_index("Tax Bracket", inplace=True)
ontario_tax_information.loc[:, "Max Income per Bracket"] ='$'+ ontario_tax_information["Max Income per Bracket_start"].map('{:,.0f}'.format)
ontario_tax_information.loc[:, "Income Tax"] =ontario_tax_information["Income Tax_start"].map('{:.2%}'.format)
ontario_tax_information.loc[:, "Dividend Tax"] =ontario_tax_information["Dividend Tax_start"].map('{:.2%}'.format)
ontario_tax_information.drop("Max Income per Bracket_start", axis=1, inplace=True)
ontario_tax_information.drop("Income Tax_start", axis=1, inplace=True)
ontario_tax_information.drop("Dividend Tax_start", axis=1, inplace=True)

# Initiate the tax deduction incase no value is added

after_tax_yearly_income = 0
after_tax_yearly_dividend = 0
total_yearly_taxes = 0

col1, holder, col2 = st.columns([2, 0.1, 2])

with col1:
    st.markdown("<h3 style='text-align: center'>Income, Savings, & Taxation</h3>", unsafe_allow_html=True)
    with st.expander("Load in a portfolio from Portfolio Builder:", True):
        user_portfolio = st.file_uploader("Please upload your file from Portfolio Builder:", type={"csv", "text"})
        if user_portfolio is not None:
            user_portfolio_df = pd.read_csv(user_portfolio, parse_dates=["Date Purchased"])
            user_portfolio_df["Date Purchased"]  = user_portfolio_df["Date Purchased"].dt.strftime('%D')
            show_portfolio = st.selectbox("Porfolio Uploaded successfully!", ( "Hide your portfolio", "View your portfolio dataframe", "View portfolio summary"), index= 2)
            if show_portfolio == "View your portfolio dataframe":
                st.dataframe(user_portfolio_df)

            #Store some  variables from the portfolio
            total_holding_value = user_portfolio_df["Holding Value"].sum()
            total_holding_value_formatted = "{:,}".format(round(total_holding_value, 2))
            total_net_gain = user_portfolio_df["Net Gain"].sum()
            total_net_gain_formatted = "{:,}".format(round(total_net_gain, 2))
            total_yearly_dividends = user_portfolio_df["Yearly Dividend"].sum()
            total_yearly_dividends_formatted = "{:,}".format(round(total_yearly_dividends, 2))
            total_monthly_dividend = total_yearly_dividends/12
            total_daily_dividend = total_yearly_dividends/365

            if show_portfolio == "View portfolio summary":
                st.write(f"Your portfolio consists of **{len(user_portfolio_df)} holdings**:")
                with st.empty():
                    time.sleep(0.5)
                    st.write(f"It is worth a total value of **${total_holding_value_formatted}**")
                with st.empty():
                    time.sleep(0.5)
                    st.write(f"The total yearly dividend income is **${round(total_yearly_dividends, 2)}**")

        if user_portfolio is None:
            st.write(f"Check out the *Portfolio Builder* page to build an importable portfolio!") 
            total_holding_value = 0 
            total_net_gain = 0
            total_yearly_dividends = 0
            total_monthly_dividend = 0
            total_daily_dividend = 0
    
    with st.expander("Load in Finacial Information Manually", True):
        with st.form("Active Income Information", False):
            st.markdown("<h5 style='text-align: center'>Annual Income Information:</h5>", unsafe_allow_html=True)
            annual_salary = st.number_input("What is your average annual salary?", 0, value=0, step=1000)
            annual_additional = st.number_input("How much annual income do you earn from sources besides your salary?", 0, value=0, step=100)
            annual_passive = st.number_input("Excluding dividends, how much passive income do you earn annually?", 0, value=0, step=100)
            st.write("")

            st.markdown("<h5 style='text-align: center'>Additional Portfolio Information:</h5>", unsafe_allow_html=True)
            additional_holdings = st.slider("How many holdings make up this portfolio?", 1, 50, 0, 1)
            additional_total_holding_value = st.number_input("What is the total value of this portfolio?", value = 0, step=100)
            additional_net_gain = st.number_input("What is current net gain of this portfolio?", value = 0, step = 50)
            additional_yearly_dividend_income = st.number_input('What is yearly dividend income value from this portfolio?', value=0, step=25)
            additional_monthly_dividend_income = additional_yearly_dividend_income/12
            additional_daily_dividend_income = additional_yearly_dividend_income/365
            st.write("")

            st.markdown("<h5 style='text-align: center'>Bank Holding Information:</h5>", unsafe_allow_html=True)
            bank_account_balance = st.number_input("What is the net value of your bank accounts?", value = 0, step=250, help="This field is used to capture your net bank holdings. For example, if you have 20'000 in your savings and owe 5'000 towards your credit card you would enter 15'000 here.")

            additional_financials_form = st.form_submit_button('Add the above financial information?')
            if additional_financials_form:
                st.success("Information added successfully!")
    
    final_yearly_dividend = total_yearly_dividends + additional_yearly_dividend_income
    final_yearly_dividend_formatted = "{:,}".format(round(final_yearly_dividend, 2))
    total_tax_income = annual_salary + annual_passive + annual_additional
    total_tax_income_formatted = "{:,}".format(round(total_tax_income, 2))
    with st.expander("Determine your income tax", True):
        with st.form("This form will be used to calculate how much income tax you pay yearly", False):
            st.caption("Combined 2022 Federal and Provincial Tax Rates for Ontario:")
            st.table(ontario_tax_information)
            st.markdown("<h6 style='text-align: center'>Your Total Yearly Income is:</h6>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align: center'>${total_tax_income_formatted}</h4>", unsafe_allow_html=True)
            income_tax_bracket = st.selectbox("Which income tax bracket are you in?", ["Don't Calculate Taxes", "Bracket One", "Bracket Two", "Bracket Three", "Bracket Four", "Bracket Five", "Bracket Six", "Bracket Seven", "Bracket Eight", "Bracket Nine", "Bracket Ten", "Bracket Eleven"], help="Find the highest bracket your income fits into with out exceeding the bracket amount. For example, a yearly income of $100,000 would belong in Bracket 6.")
            
            st.markdown("<h6 style='text-align: center'>Your Total Yearly Dividend is:</h6>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align: center'>${final_yearly_dividend_formatted}</h4>", unsafe_allow_html=True)
            dividend_tax_bracket = st.selectbox("Which dividend income tax bracket are you in?", ["Don't Calculate Taxes", "Bracket One", "Bracket Two", "Bracket Three", "Bracket Four", "Bracket Five", "Bracket Six", "Bracket Seven", "Bracket Eight", "Bracket Nine", "Bracket Ten", "Bracket Eleven"], help="Find the highest bracket your dividend income fits into with out exceeding the bracket amount. For example, a yearly dividend income of $55,000 would belong in Bracket 3.")
            
            

            submit_tax_form = st.form_submit_button("Determine income tax amount")
            if submit_tax_form:
                st.success("Information added successfully!")

            if income_tax_bracket == "Don't Calculate Taxes":
                after_tax_yearly_income = total_tax_income

            elif income_tax_bracket == "Bracket One":
                after_tax_yearly_income = total_tax_income * (1 - tax_46226)
                
            elif income_tax_bracket == "Bracket Two":
                bracket_carryover = total_tax_income - 46226
                after_tax_yearly_income = (46226 * (1 - tax_46226) + bracket_carryover * (1 - tax_50197))
            
            elif income_tax_bracket == "Bracket Three":
                bracket_carryover = total_tax_income - 50197
                after_tax_yearly_income = ((46226 * (1 - tax_46226)) + (3971 * (1 - tax_50197)) + (bracket_carryover * (1 - tax_81411)))
            
            elif income_tax_bracket == "Bracket Four":
                bracket_carryover = total_tax_income - 81411
                after_tax_yearly_income = ((46226 * (1 - tax_46226)) + (3971 * (1 - tax_50197)) + (31214 * (1 - tax_81411) + (bracket_carryover * (1 - tax_92454))))
            
            elif income_tax_bracket == "Bracket Five":
                bracket_carryover = total_tax_income - 92454
                after_tax_yearly_income = ((46226 * (1 - tax_46226)) + (3971 * (1 - tax_50197)) + (31214 * (1 - tax_81411) + (11043 * (1 - tax_92454)) + (bracket_carryover * (1 - tax_92454))))
            
            elif income_tax_bracket == "Bracket Six":
                bracket_carryover = total_tax_income - 95906
                after_tax_yearly_income = ((46226 * (1 - tax_46226)) + (3971 * (1 - tax_50197)) + (31214 * (1 - tax_81411) + (11043 * (1 - tax_92454)) + (3452 * (1 - tax_95906)) + (bracket_carryover * (1 - tax_100392))))
                
            elif income_tax_bracket == "Bracket Seven":
                bracket_carryover = total_tax_income - 100392
                after_tax_yearly_income = ((46226 * (1 - tax_46226)) + (3971 * (1 - tax_50197)) + (31214 * (1 - tax_81411) + (11043 * (1 - tax_92454)) + (3452 * (1 - tax_95906)) + (4486 * (1 - tax_100392)) + (bracket_carryover * (1 - tax_150000))))
                
            elif income_tax_bracket == "Bracket Eight":
                bracket_carryover = total_tax_income - 150000
                after_tax_yearly_income = ((46226 * (1 - tax_46226)) + (3971 * (1 - tax_50197)) + (31214 * (1 - tax_81411) + (11043 * (1 - tax_92454)) + (3452 * (1 - tax_95906)) + (4486 * (1 - tax_100392)) + (49608 * (1 - tax_150000)) + (bracket_carryover * (1 - tax_155625))))
                
            elif income_tax_bracket == "Bracket Nine":
                bracket_carryover = total_tax_income - 155625
                after_tax_yearly_income = ((46226 * (1 - tax_46226)) + (3971 * (1 - tax_50197)) + (31214 * (1 - tax_81411) + (11043 * (1 - tax_92454)) + (3452 * (1 - tax_95906)) + (4486 * (1 - tax_100392)) + (49608 * (1 - tax_150000)) + (5625 * (1 - tax_155625)) + (bracket_carryover * (1 - tax_220000))))
                
            elif income_tax_bracket == "Bracket Ten":
                bracket_carryover = total_tax_income - 220000
                after_tax_yearly_income = ((46226 * (1 - tax_46226)) + (3971 * (1 - tax_50197)) + (31214 * (1 - tax_81411) + (11043 * (1 - tax_92454)) + (3452 * (1 - tax_95906)) + (4486 * (1 - tax_100392)) + (49608 * (1 - tax_150000)) + (5625 * (1 - tax_155625)) + (64375 * (1 - tax_220000)) + (bracket_carryover * (1 - tax_221708))))
                
            elif income_tax_bracket == "Bracket Eleven":
                bracket_carryover = total_tax_income - 221708
                after_tax_yearly_income = ((46226 * (1 - tax_46226)) + (3971 * (1 - tax_50197)) + (31214 * (1 - tax_81411) + (11043 * (1 - tax_92454)) + (3452 * (1 - tax_95906)) + (4486 * (1 - tax_100392)) + (49608 * (1 - tax_150000)) + (5625 * (1 - tax_155625)) + (64375 * (1 - tax_220000)) + (1708 * (1 - tax_221708)) + (bracket_carryover * (1 - tax_over_221708))))
            

            if dividend_tax_bracket == "Don't Calculate Taxes":
                after_tax_yearly_dividend = final_yearly_dividend

            elif dividend_tax_bracket == "Bracket One":
                after_tax_yearly_dividend = final_yearly_dividend * (1 - dividend_tax_46226)
                
            elif dividend_tax_bracket == "Bracket Two":
                bracket_carryover = final_yearly_dividend - 46226
                after_tax_yearly_dividend = (46226 * (1 - dividend_tax_46226) + bracket_carryover * (1 - dividend_tax_50197))
                
            elif dividend_tax_bracket == "Bracket Three":
                bracket_carryover = final_yearly_dividend - 50197
                after_tax_yearly_dividend = ((46226 * (1 - dividend_tax_46226)) + (3971 * (1 - dividend_tax_50197)) + (bracket_carryover * (1 - dividend_tax_81411)))
                
            elif dividend_tax_bracket == "Bracket Four":
                bracket_carryover = final_yearly_dividend - 81411
                after_tax_yearly_dividend = ((46226 * (1 - dividend_tax_46226)) + (3971 * (1 - dividend_tax_50197)) + (31214 * (1 - dividend_tax_81411) + (bracket_carryover * (1 - dividend_tax_92454))))
                
            elif dividend_tax_bracket == "Bracket Five":
                bracket_carryover = final_yearly_dividend - 92454
                after_tax_yearly_dividend = ((46226 * (1 - dividend_tax_46226)) + (3971 * (1 - dividend_tax_50197)) + (31214 * (1 - dividend_tax_81411) + (11043 * (1 - dividend_tax_92454)) + (bracket_carryover * (1 - dividend_tax_92454))))
                
            elif dividend_tax_bracket == "Bracket Six":
                bracket_carryover = final_yearly_dividend - 95906
                after_tax_yearly_dividend = ((46226 * (1 - dividend_tax_46226)) + (3971 * (1 - dividend_tax_50197)) + (31214 * (1 - dividend_tax_81411) + (11043 * (1 - dividend_tax_92454)) + (3452 * (1 - dividend_tax_95906)) + (bracket_carryover * (1 - dividend_tax_100392))))
                
            elif dividend_tax_bracket == "Bracket Seven":
                bracket_carryover = final_yearly_dividend - 100392
                after_tax_yearly_dividend = ((46226 * (1 - dividend_tax_46226)) + (3971 * (1 - dividend_tax_50197)) + (31214 * (1 - dividend_tax_81411) + (11043 * (1 - dividend_tax_92454)) + (3452 * (1 - dividend_tax_95906)) + (4486 * (1 - dividend_tax_100392)) + (bracket_carryover * (1 - dividend_tax_150000))))
                
            elif dividend_tax_bracket == "Bracket Eight":
                bracket_carryover = final_yearly_dividend - 150000
                after_tax_yearly_dividend = ((46226 * (1 - dividend_tax_46226)) + (3971 * (1 - dividend_tax_50197)) + (31214 * (1 - dividend_tax_81411) + (11043 * (1 - dividend_tax_92454)) + (3452 * (1 - dividend_tax_95906)) + (4486 * (1 - dividend_tax_100392)) + (49608 * (1 - dividend_tax_150000)) + (bracket_carryover * (1 - dividend_tax_155625))))
                
            elif dividend_tax_bracket == "Bracket Nine":
                bracket_carryover = final_yearly_dividend - 155625
                after_tax_yearly_dividend = ((46226 * (1 - dividend_tax_46226)) + (3971 * (1 - dividend_tax_50197)) + (31214 * (1 - dividend_tax_81411) + (11043 * (1 - dividend_tax_92454)) + (3452 * (1 - dividend_tax_95906)) + (4486 * (1 - dividend_tax_100392)) + (49608 * (1 - dividend_tax_150000)) + (5625 * (1 - dividend_tax_155625)) + (bracket_carryover * (1 - dividend_tax_220000))))
                
            elif dividend_tax_bracket == "Bracket Ten":
                bracket_carryover = final_yearly_dividend - 220000
                after_tax_yearly_dividend = ((46226 * (1 - dividend_tax_46226)) + (3971 * (1 - dividend_tax_50197)) + (31214 * (1 - dividend_tax_81411) + (11043 * (1 - dividend_tax_92454)) + (3452 * (1 - dividend_tax_95906)) + (4486 * (1 - dividend_tax_100392)) + (49608 * (1 - dividend_tax_150000)) + (5625 * (1 - dividend_tax_155625)) + (64375 * (1 - dividend_tax_220000)) + (bracket_carryover * (1 - dividend_tax_221708))))
                
            elif dividend_tax_bracket == "Bracket Eleven":
                bracket_carryover = final_yearly_dividend - 221708
                after_tax_yearly_dividend = ((46226 * (1 - dividend_tax_46226)) + (3971 * (1 - dividend_tax_50197)) + (31214 * (1 - dividend_tax_81411) + (11043 * (1 - dividend_tax_92454)) + (3452 * (1 - dividend_tax_95906)) + (4486 * (1 - dividend_tax_100392)) + (49608 * (1 - dividend_tax_150000)) + (5625 * (1 - dividend_tax_155625)) + (64375 * (1 - dividend_tax_220000)) + (1708 * (1 - dividend_tax_221708)) + (bracket_carryover * (1 - dividend_tax_over_221708))))
            
    
with col2:
    st.markdown("<h3 style='text-align: center'>Critical & Personal Spending</h3>", unsafe_allow_html=True)
    with st.expander("Load in information regarding Critical Spending:", True):
        with st.form("Critical Spending"):
            st.markdown("<h5 style='text-align: center'>Critcal Spending Information:</h5>", unsafe_allow_html=True)
            monthly_mortgage = st.number_input("How much do you spend a month on mortgage?", 0, value=0, step=100, help="Monthly mortgage is how much you pay the bank per month to pay off your house. If you currently rent, leave this feild at zero.")
            monthly_rent = st.number_input("How much rent do you pay per month in terms of housing?", 0, value=0, step=100)
            monthly_transportation = st.number_input("How much does your transportation cost you a month?", 0, value = 0, step = 25, help="This is a fairly general field that would encompass all monthly transportation spending. This could include car payments, car lease payments, gas budget, bus fair, uber rides, etc.")
            monthly_utilities = st.number_input("How much do you spend on utilities a month?", 0, value=0)
            monthly_insurance = st.number_input("How much do you spend on all combined insurances a month?", 0, value=0, help="This feild includes your monthly payment for all of your insurances. This could include life insurance, car insurance, home insurance, etc.")
            monthly_food = st.number_input("How much money do you spend on food a month", 0, value=0)
            average_monthly_additional_debt = st.number_input("How much do you pay per month towards credit cards or other debts?", 0,  value=0, help="This can include any reoccuring debts such as student loans, government loans, etc.")
            additional_family_monthly = st.number_input("How much per month do you spend regarding other necessities not included above?", 0, value = 0)
            critical_spending_submit = st.form_submit_button('Add the above financial information?')
            if critical_spending_submit:
                st.success("Information added successfully!")
    
    with st.expander("Load in information regarding Personal Spending:", True):
        with st.form("Personal Spending"):
            st.markdown("<h5 style='text-align: center'>Personal Ammenities Information:</h5>", unsafe_allow_html=True)
            monthly_phone_bill = st.number_input("How much do you spend on your phone bill per month?", 0, value=0)
            monthly_tv = st.number_input("How much do you spend on television a month?", 0, value=0)
            monthly_wifi = st.number_input("How much do you spend on wifi a month?", 0, value=0)
            monthly_subscriptions = st.number_input("How much do you spend on subscriptions a month?", 0, value=0)
            st.write("")
            
            st.markdown("<h5 style='text-align: center'>Personal Luxuries Information:</h5>", unsafe_allow_html=True)
            monthly_personal_food = st.number_input("How much do you spend on going out for food a month?", 0, value=0)
            monthly_entertainment = st.number_input("How much do you spend on entertainment a month", 0, value=0)
            monthly_shopping = st.number_input("How much do you spend on shopping a month?", 0, value=0)
            st.write("")

            st.markdown("<h5 style='text-align: center'>Additional Personal Information:</h5>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center'><em>Use these fields to add up to three other areas you may spend your money in. Use the average monthly cost when inputing these feilds</em></p>", unsafe_allow_html=True)
            additional_label_1 = st.text_input("First additional monthly spending category", value="i.e. Vacations")
            additional_spending_1 = st.number_input(f"How much do you spend on the first category per month?", 0, value=0)
            additional_label_2 = st.text_input("Second additional monthly spending category", value="i.e. Sports Betting")
            additional_spending_2 = st.number_input(f"How much do you spend on the second category per month?", 0, value=0)
            dditional_label_3 = st.text_input("Second additional monthly spending category", value="i.e. Cigerettes")
            additional_spending_3 = st.number_input(f"How much do you spend on the third category per month?", 0, value=0)

            personal_spending_submit = st.form_submit_button('Add the above financial information?')
            if personal_spending_submit:
                st.success("Information added successfully!")







# Total Wealth:
total_wealth = total_holding_value + additional_total_holding_value + bank_account_balance

# Total Income:
total_yearly_income = total_yearly_dividends + annual_salary + annual_additional + annual_passive

# Total month Critical Spending:
total_monthly_critical_spending = monthly_mortgage + monthly_rent + monthly_transportation + monthly_utilities + monthly_insurance + monthly_food + average_monthly_additional_debt + additional_family_monthly

# Total month Personal Ammenities:
total_monthly_personal_ammenities = monthly_phone_bill + monthly_tv + monthly_wifi + monthly_subscriptions

# Total month Personal Luxeries:
total_monthly_personal_luxuries = monthly_personal_food + monthly_entertainment + monthly_shopping

# Total month additional personal
total_monthly_additional_spending = additional_spending_1 + additional_spending_2 + additional_spending_3

# Total monthly personal spending
total_monthly_personal = total_monthly_additional_spending + total_monthly_personal_luxuries + total_monthly_personal_ammenities

# Total yearly taxes
total_yearly_income_tax = total_tax_income - after_tax_yearly_income
total_yearly_dividend_tax = final_yearly_dividend - after_tax_yearly_dividend
total_yearly_taxes = total_yearly_income_tax + total_yearly_dividend_tax

total_monthly_taxes = total_yearly_taxes / 12
total_monthly_income_tax = total_yearly_income_tax / 12
total_monthly_dividend_tax = total_yearly_dividend_tax / 12


# Month to year variables
total_yearly_critical_spending = total_monthly_critical_spending * 12 
total_yearly_personal_ammenities = total_monthly_personal_ammenities * 12
total_yearly_personal_luxuries = total_monthly_personal_luxuries * 12
total_yearly_additional_spending = total_monthly_additional_spending * 12
total_yearly_personal = total_monthly_personal * 12

yearly_mortgage = monthly_mortgage * 12
yearly_rent = monthly_rent * 12
yearly_transportation = monthly_transportation * 12
yearly_utilities = monthly_utilities * 12
yearly_insurance = monthly_insurance * 12
yearly_food = monthly_food * 12
average_yearly_additional_debt = average_monthly_additional_debt * 12
additional_family_yearly = additional_family_monthly * 12


total_yearly_personal = total_monthly_personal * 12 

total_monthly_income = total_yearly_income / 12
final_monthly_dividend = final_yearly_dividend / 12
monthly_salary = annual_salary / 12
monthly_additional = annual_additional / 12
monthly_passive = annual_passive / 12

total_yearly_spending = total_yearly_critical_spending + total_yearly_personal + total_yearly_taxes
net_income_gain = total_yearly_income - total_yearly_spending
net_wealth_in_year = total_wealth + net_income_gain
total_monthly_spending = total_yearly_spending / 12
monthly_net_income = total_monthly_income - total_monthly_spending
monthly_net_wealth = total_wealth + monthly_net_income





# Formatting
total_wealth_formatted = "{:,}".format(round(total_wealth, 2))
additional_total_holding_value_formatted = "{:,}".format(round(additional_total_holding_value, 2))
bank_account_balance_formatted = "{:,}".format(round(bank_account_balance, 2))
total_yearly_income_formatted = "{:,}".format(round(total_yearly_income, 2))
annual_salary_formatted = "{:,}".format(round(annual_salary, 2))
annual_additional_formatted = "{:,}".format(round(annual_additional, 2))
annual_passive_formatted = "{:,}".format(round(annual_passive, 2))
total_holding_value_formatted = "{:,}".format(round(total_holding_value, 2))


total_yearly_critical_spending_formatted = "{:,}".format(round(total_yearly_critical_spending, 2))
yearly_mortgage_formatted = "{:,}".format(round(yearly_mortgage, 2))
yearly_rent_formatted = "{:,}".format(round(yearly_rent, 2))
yearly_transportation_formatted = "{:,}".format(round(yearly_transportation, 2))
yearly_utilities_formatted = "{:,}".format(round(yearly_utilities, 2))
yearly_insurance_formatted = "{:,}".format(round(yearly_insurance, 2))
yearly_food_formatted = "{:,}".format(round(yearly_food, 2))
average_yearly_additional_debt_formatted = "{:,}".format(round(average_yearly_additional_debt, 2))
additional_family_yearly_formatted = "{:,}".format(round(additional_family_yearly, 2))

total_yearly_personal_formatted = "{:,}".format(round(total_yearly_personal, 2))
total_yearly_personal_ammenities_formatted = "{:,}".format(round(total_yearly_personal_ammenities, 2))
total_yearly_personal_luxuries_formatted = "{:,}".format(round(total_yearly_personal_luxuries, 2))
total_yearly_additional_spending_formatted = "{:,}".format(round(total_yearly_additional_spending, 2))

total_monthly_income_formatted = "{:,}".format(round(total_monthly_income, 2))
final_monthly_dividend_formatted = "{:,}".format(round(final_monthly_dividend, 2))
monthly_salary_formatted = "{:,}".format(round(total_monthly_income, 2))
monthly_additional_formatted = "{:,}".format(round(monthly_additional, 2))
monthly_passive_formatted = "{:,}".format(round(monthly_passive, 2))

total_monthly_critical_spending_formatted = "{:,}".format(round(total_monthly_critical_spending, 2))
monthly_mortgage_formatted = "{:,}".format(round(monthly_mortgage, 2))
monthly_rent_formatted = "{:,}".format(round(monthly_rent, 2))
monthly_transportation_formatted = "{:,}".format(round(monthly_transportation, 2))
monthly_utilities_formatted = "{:,}".format(round(monthly_utilities, 2))
monthly_insurance_formatted = "{:,}".format(round(monthly_insurance, 2))
monthly_food_formatted = "{:,}".format(round(monthly_food, 2))
average_monthly_additional_debt_formatted = "{:,}".format(round(average_monthly_additional_debt, 2))
additional_family_monthly_formatted = "{:,}".format(round(additional_family_monthly, 2))

total_yearly_taxes_formatted = "{:,}".format(round(total_yearly_taxes, 2))
total_yearly_income_tax_formatted = "{:,}".format(round(total_yearly_income_tax, 2))
total_yearly_dividend_tax_formatted = "{:,}".format(round(total_yearly_dividend_tax, 2))
after_tax_yearly_income_formatted = "{:,}".format(round(after_tax_yearly_income, 2))

total_monthly_personal_formatted = "{:,}".format(round(total_monthly_personal, 2))
total_monthly_personal_ammenities_formatted = "{:,}".format(round(total_monthly_personal_ammenities, 2))
total_monthly_personal_luxuries_formatted = "{:,}".format(round(total_monthly_personal_luxuries, 2))
total_monthly_additional_spending_formatted = "{:,}".format(round(total_monthly_additional_spending, 2))

total_monthly_taxes_formatted = "{:,}".format(round(total_monthly_taxes, 2))
total_monthly_income_tax_formatted = "{:,}".format(round(total_monthly_income_tax, 2))
total_monthly_dividend_tax_formatted = "{:,}".format(round(total_monthly_dividend_tax, 2))

net_wealth_in_year_formatted = "{:,}".format(round(net_wealth_in_year, 2))
net_income_gain_formatted = "{:,}".format(round(net_income_gain, 2))
total_yearly_spending_formatted = "{:,}".format(round(total_yearly_spending, 2))
monthly_net_income_formatted = "{:,}".format(round(monthly_net_income, 2))
total_monthly_spending_formatted = "{:,}".format(round(total_monthly_spending, 2))
monthly_net_wealth_formatted = "{:,}".format(round(monthly_net_wealth, 2))




with st.sidebar:
    st.markdown("<h3 style='text-align: center'>Income and Savings Overview</h3>", unsafe_allow_html=True)

yearly_tab, monthly_tab, net_financials = st.sidebar.tabs(["Yearly", "Monthly", "Net Financials"])

with yearly_tab:
    st.caption("Your **YEARLY** financial breakdown...")
    
    if total_wealth is not 0:
        st.markdown("<h4>Total Current Wealth:</h4>", unsafe_allow_html=True)
        with st.expander(f"$ {total_wealth_formatted}", True):
            if total_holding_value is not 0:
                st.markdown(f"<h6>|| <em>Initial Portfolio Holding Value</em> ||  $ {total_holding_value_formatted}</h6>", unsafe_allow_html= True)
            
            if additional_total_holding_value is not 0:    
                st.markdown(f"<h6>|| <em>Additional Portfolio Holding Value</em> ||  $ {additional_total_holding_value_formatted}</h6>", unsafe_allow_html= True)
            
            if bank_account_balance is not 0:
                st.markdown(f"<h6>|| <em>Bank Holding Value</em> ||  $ {bank_account_balance_formatted}</h6>", unsafe_allow_html= True)
    
    if total_yearly_income is not 0:
        st.markdown("<h4>Total Yearly Income:</h4>", unsafe_allow_html=True)
        with st.expander(f"$ {total_yearly_income_formatted}", True):
            if final_yearly_dividend is not 0:
                st.markdown(f"<h6>|| <em>Total Yearly Dividends</em> ||  $ {final_yearly_dividend_formatted}</h6>", unsafe_allow_html= True)
            
            if annual_salary is not 0:
                st.markdown(f"<h6>|| <em>Annual Salary</em> ||  $ {annual_salary_formatted}</h6>", unsafe_allow_html= True)
            
            if annual_additional is not 0:
                st.markdown(f"<h6>|| <em>Annual Additional Income</em> ||  $ {annual_additional_formatted}</h6>", unsafe_allow_html= True)
            
            if annual_passive is not 0:
                st.markdown(f"<h6>|| <em>Annual Passive Income</em> ||  $ {annual_passive_formatted}</h6>", unsafe_allow_html= True)
    
    if total_yearly_critical_spending is not 0:
        st.markdown("<h4>Total Yearly Critical Spending:</h4>", unsafe_allow_html=True)
        with st.expander(f"$ {total_yearly_critical_spending_formatted}", True):
            if yearly_mortgage is not 0:
                st.markdown(f"<h6>|| <em>Total Yearly Mortgage</em> ||  $ {yearly_mortgage_formatted}</h6>", unsafe_allow_html= True)
            
            if yearly_rent is not 0:
                st.markdown(f"<h6>|| <em>Total Yearly Rent</em> ||  $ {yearly_rent_formatted}</h6>", unsafe_allow_html= True)
            
            if yearly_transportation is not 0:
                st.markdown(f"<h6>|| <em>Total Yearly Transportation</em> ||  $ {yearly_transportation_formatted}</h6>", unsafe_allow_html= True)

            if yearly_utilities is not 0:
                st.markdown(f"<h6>|| <em>Total Yearly Utilities</em> ||  $ {yearly_utilities_formatted}</h6>", unsafe_allow_html= True)

            if yearly_insurance is not 0:
                st.markdown(f"<h6>|| <em>Total Yearly Insurance</em> ||  $ {yearly_insurance_formatted}</h6>", unsafe_allow_html= True)

            if yearly_food is not 0:
                st.markdown(f"<h6>|| <em>Total Yearly Food</em> ||  $ {yearly_food_formatted}</h6>", unsafe_allow_html= True)

            if average_yearly_additional_debt is not 0:
                st.markdown(f"<h6>|| <em>Total Yearly Additional Debt</em> ||  $ {average_yearly_additional_debt_formatted}</h6>", unsafe_allow_html= True)

            if additional_family_yearly is not 0:
                st.markdown(f"<h6>|| <em>Total Yearly Additional Family Costs</em> ||  $ {additional_family_yearly}</h6>", unsafe_allow_html= True)

    if total_yearly_personal is not 0:
        st.markdown("<h4>Total Yearly Personal Spending:</h4>", unsafe_allow_html=True)
        with st.expander(f"$ {total_yearly_personal_formatted}", True):
            if total_yearly_personal_ammenities is not 0:
                st.markdown(f"<h6>|| <em>Total Yearly Ammenities Spending</em> ||  $ {total_yearly_personal_ammenities_formatted}</h6>", unsafe_allow_html= True)

            if total_yearly_personal_luxuries is not 0:
                st.markdown(f"<h6>|| <em>Total Yearly Luxeries Spending</em> ||  $ {total_yearly_personal_luxuries_formatted}</h6>", unsafe_allow_html= True)

            if total_yearly_additional_spending is not 0:
                st.markdown(f"<h6>|| <em>Total Yearly Additional Spending</em> ||  $ {total_yearly_additional_spending_formatted}</h6>", unsafe_allow_html= True)

    if income_tax_bracket != "Don't Calculate Taxes":
        st.markdown("<h4>Total Yearly Taxes:</h4>", unsafe_allow_html=True)
        with st.expander(f"$ {total_yearly_taxes_formatted}", True):
            if total_yearly_income_tax is not 0:
                st.markdown(f"<h6>|| <em>Total Yearly Income Tax</em> ||  $ {total_yearly_income_tax_formatted}</h6>", unsafe_allow_html= True)

            if total_yearly_dividend_tax is not 0:
                st.markdown(f"<h6>|| <em>Total Yearly Dividend Tax</em> ||  $ {total_yearly_dividend_tax_formatted}</h6>", unsafe_allow_html= True)

with monthly_tab:
    st.caption("Your **MONTHLY** financial breakdown...")
    
    if total_wealth is not 0:
        st.markdown("<h4>Total Current Wealth:</h4>", unsafe_allow_html=True)
        with st.expander(f"$ {total_wealth_formatted}", True):
            if total_holding_value is not 0:
                st.markdown(f"<h6>|| <em>Initial Portfolio Holding Value</em> ||  $ {total_holding_value_formatted}</h6>", unsafe_allow_html= True)
            
            if additional_total_holding_value is not 0:    
                st.markdown(f"<h6>|| <em>Additional Portfolio Holding Value</em> ||  $ {additional_total_holding_value_formatted}</h6>", unsafe_allow_html= True)
            
            if bank_account_balance is not 0:
                st.markdown(f"<h6>|| <em>Bank Holding Value</em> ||  $ {bank_account_balance_formatted}</h6>", unsafe_allow_html= True)

    if total_monthly_income is not 0:
        st.markdown("<h4>Total Monthly Income:</h4>", unsafe_allow_html=True)
        with st.expander(f"$ {total_monthly_income_formatted}", True):
            if final_monthly_dividend is not 0:
                st.markdown(f"<h6>|| <em>Total Monthly Dividends</em> ||  $ {final_monthly_dividend_formatted}</h6>", unsafe_allow_html= True)
            
            if annual_salary is not 0:
                st.markdown(f"<h6>|| <em>Monthly Salary</em> ||  $ {monthly_salary_formatted}</h6>", unsafe_allow_html= True)
            
            if annual_additional is not 0:
                st.markdown(f"<h6>|| <em>Monthly Additional Income</em> ||  $ {monthly_additional_formatted}</h6>", unsafe_allow_html= True)
            
            if annual_passive is not 0:
                st.markdown(f"<h6>|| <em>Monthly Additional Passive Income</em> ||  $ {monthly_passive_formatted}</h6>", unsafe_allow_html= True)
            
    if total_monthly_critical_spending is not 0:
        st.markdown("<h4>Total Monthly Critical Spending:</h4>", unsafe_allow_html=True)
        with st.expander(f"$ {total_monthly_critical_spending}", True):
            if monthly_mortgage is not 0:
                st.markdown(f"<h6>|| <em>Total Monthly Mortgage</em> ||  $ {monthly_mortgage_formatted}</h6>", unsafe_allow_html= True)

            if monthly_rent is not 0:
                st.markdown(f"<h6>|| <em>Total Monthly Rent</em> ||  $ {monthly_rent_formatted}</h6>", unsafe_allow_html= True)
            
            if monthly_transportation is not 0:
                st.markdown(f"<h6>|| <em>Total Monthly Transportation</em> ||  $ {monthly_transportation_formatted}</h6>", unsafe_allow_html= True)
            
            if monthly_utilities is not 0: 
                st.markdown(f"<h6>|| <em>Total Monthly Utilities</em> ||  $ {monthly_utilities_formatted}</h6>", unsafe_allow_html= True)

            if monthly_insurance is not 0: 
                st.markdown(f"<h6>|| <em>Total Monthly Insurance</em> ||  $ {monthly_insurance_formatted}</h6>", unsafe_allow_html= True)

            if monthly_food is not 0:
                st.markdown(f"<h6>|| <em>Total Monthly Food</em> ||  $ {monthly_food_formatted}</h6>", unsafe_allow_html= True)
            
            if average_monthly_additional_debt is not 0:
                st.markdown(f"<h6>|| <em>Total Monthly Debt Payments</em> ||  $ {average_monthly_additional_debt_formatted}</h6>", unsafe_allow_html= True)

            if additional_family_monthly is not 0:
                st.markdown(f"<h6>|| <em>Total Monthly Additional Necessities</em> ||  $ {additional_family_monthly_formatted}</h6>", unsafe_allow_html= True)

    if total_yearly_personal is not 0:
        st.markdown("<h4>Total Monthly Personal Spending:</h4>", unsafe_allow_html=True)
        with st.expander(f"$ {total_monthly_personal_formatted}", True):
            if total_yearly_personal_ammenities is not 0:
                st.markdown(f"<h6>|| <em>Total Monthly Ammenities Spending</em> ||  $ {total_monthly_personal_ammenities}</h6>", unsafe_allow_html= True)

            if total_yearly_personal_luxuries is not 0:
                st.markdown(f"<h6>|| <em>Total Monthly Luxeries Spending</em> ||  $ {total_monthly_personal_luxuries_formatted}</h6>", unsafe_allow_html= True)

            if total_yearly_additional_spending is not 0:
                st.markdown(f"<h6>|| <em>Total Monthly Additional Spending</em> ||  $ {total_monthly_additional_spending_formatted}</h6>", unsafe_allow_html= True)

    if income_tax_bracket != "Don't Calculate Taxes":
        st.markdown("<h4>Total Monhtly Taxes:</h4>", unsafe_allow_html=True)
        with st.expander(f"$ {total_monthly_taxes_formatted}", True):
            if total_yearly_income_tax is not 0:
                st.markdown(f"<h6>|| <em>Total Monthly Income Tax</em> ||  $ {total_monthly_income_tax_formatted}</h6>", unsafe_allow_html= True)

            if total_yearly_dividend_tax is not 0:
                st.markdown(f"<h6>|| <em>Total Monthly Dividend Tax</em> ||  $ {total_monthly_dividend_tax_formatted}</h6>", unsafe_allow_html= True)

with net_financials:
    st.caption("Your **NET FINANCIAL** breakdown...")
    
    if total_wealth is not 0:
        st.markdown("<h4>Projected Wealth in a Year:</h4>", unsafe_allow_html=True)
        with st.expander(f"$ {net_wealth_in_year_formatted}", True):
            if total_wealth is not 0:
                st.markdown(f"<h6>|| <em>Wealth Created Yearly</em> ||  $ {net_income_gain_formatted}</h6>", unsafe_allow_html= True)
            
            st.markdown("<sub><sup>Your yearly net finacial gain is calculated from...</sub></sup>", unsafe_allow_html=True)

            if total_yearly_income is not 0:    
                st.markdown(f"<h6>|| <em>Yearly Income Before Taxes</em> ||  $ {total_yearly_income_formatted}</h6>", unsafe_allow_html= True)
            
            if total_yearly_spending is not 0:
                st.markdown(f"<h6>|| <em>Yearly Spending & Taxes</em> ||  $ {total_yearly_spending_formatted}</h6>", unsafe_allow_html= True)

    if total_wealth is not 0:
        st.markdown("<h4>Projected Wealth in a Month:</h4>", unsafe_allow_html=True)
        with st.expander(f"$ {monthly_net_wealth_formatted}", True):
            if total_wealth is not 0:
                st.markdown(f"<h6>|| <em>Wealth Created Monthly</em> ||  $ {monthly_net_income_formatted}</h6>", unsafe_allow_html= True)
            
            st.markdown("<sub><sup>Your monthly net finacial gain is calculated from...</sub></sup>", unsafe_allow_html=True)

            if total_yearly_income is not 0:    
                st.markdown(f"<h6>|| <em>Monthly Income Before Taxes</em> ||  $ {total_monthly_income_formatted}</h6>", unsafe_allow_html= True)
            
            if total_yearly_spending is not 0:
                st.markdown(f"<h6>|| <em>Monthly Spending & Taxes</em> ||  $ {total_monthly_spending_formatted}</h6>", unsafe_allow_html= True)            



with st.sidebar:
    st.image(sidebar_logo)
    st.markdown("<h4 style='text-align: center'><em>Financial Compass</em></h4>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center'><em>Tools for Navigating Your Financials</em></h5>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center'><em>Established in August 2022</em></h6>", unsafe_allow_html=True)

st.markdown("")
st.markdown("")
st.markdown("")

st.image(logo, width=150)
st.caption("*Design Rights Property of: Financial Compass*")
st.caption("*Results are financial insights, not advice*")
st.caption("*Contributor: [Cam Gould](https://www.linkedin.com/in/camrgould/)*")