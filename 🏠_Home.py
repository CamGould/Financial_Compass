# Contents of ~/my_app/streamlit_app.py
import streamlit as st
from PIL import Image
import urllib.request

st.set_page_config(page_title="Home Page", page_icon="🏠", initial_sidebar_state="collapsed")

urllib.request.urlretrieve("https://github.com/CamGould/Financial_Compass/blob/main/supplemental/Logo.png?raw=true", "logo.png")
urllib.request.urlretrieve("https://github.com/CamGould/Financial_Compass/blob/main/supplemental/Top_logo.png?raw=true", "header_logo.png")
urllib.request.urlretrieve("https://github.com/CamGould/Financial_Compass/blob/main/supplemental/Sidebar_Image.png?raw=true", "sidebar_logo.png")

# logo_path = Path("/users/cg/Documents/Personal/Projects/Capstone_Project/Supplemental/Logo.png")
# header_logo_path = Path("/users/cg/Documents/Personal/Projects/Capstone_Project/Supplemental/Top_logo.png")
# sidebar_logo_path = Path("/users/cg/Documents/Personal/Projects/Capstone_Project/Supplemental/Sidebar_Image.png")

header_logo = Image.open("header_logo.png")
sidebar_logo = Image.open("sidebar_logo.png")
logo = Image.open("logo.png")

st.image(header_logo)

st.markdown("")

st.markdown("<h3 style='text-align: center'>Welcome to Your <em>Financial Compass<em></h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center'><em>The <strong>Financial Compass</strong> is intended to be used as a tool to allow users to quickly and accurately gain insights into their current financial position and habits.</em></p>", unsafe_allow_html=True)


# Insert a line break
st.markdown("")
st.markdown("")
# Explain the usefulness of the app
st.markdown(f"Within this app users can:")
st.markdown(f"- **Build Their Portfolio** with *live time prices*")
st.markdown(f"- Gain **Financial Insights** into their *current financial position*")
st.markdown(f"- Conduct **Financial Research** on *perspective financial decisions*")

# Insert a line break
st.markdown("")
st.markdown("")

st.markdown("<h5 style='text-align: center'>Select a Page to Learn More</h5>", unsafe_allow_html=True)
page_learning = st.selectbox("Which page do you wish to learn about?", ["Portfolio Builder", "Financial Insights", "Financial Research"], help="Selct a page from the dropdown to learn more about it.")

if page_learning == "Portfolio Builder":
    with st.expander("Show/hide information about the Portfolio Builder page:", True):
        st.markdown("<h6 style='text-align: center'>All Things <strong>Portfolio Builder</strong></h6>", unsafe_allow_html=True)
        st.caption("The Portfolio Builder was created to eliminate the need to manually search for stock prices to update spreadsheets that contained information about one's portfolio.")
        st.markdown("With the portfolio builder you can:")
        st.markdown("- Choose the currency that you wish to build your portfolio in (both *Canadian & American* currencies are currently suported at this  time")
        st.markdown("- Choose from over *1000 tickers* for your portfolio using live price data from *[Yahoo Finance](https://ca.finance.yahoo.com)*")
        st.markdown("- Select a *ticker, quantity of shares, and date purchased* and allow the app to gather all the rest of the information for you")
        st.markdown("- View your portfolio and analyze all of the insights from the *provided data*")
        st.markdown("- *Download* your up to date portfolio to override your old one or import it into the **Financial Insights** page")

if page_learning == "Financial Insights":
    with st.expander("Show/hide information about the Financial Insights page:", True):
        st.markdown("<h6 style='text-align: center'>All Things <strong>Financial Insights</strong></h6>", unsafe_allow_html=True)
        st.caption("The Financial Insights tool was created as a way for individuals to help better understand their financial position, allowing them to visualize their current standing and plan their desired future position.")
        st.markdown("With the Financial Insights tool you can:")
        st.markdown("- Personalize the analysis for recommendations and tax purposes")
        st.markdown("- Upload your portfolio previously made using the *Portfolio Builder*")
        st.markdown("- Capture information about your *income, axes, and spending*")
        st.markdown("- View breakdowns of your financial position from a *yearly, monthly*, or *net* position")

st.markdown("")
st.markdown("")

st.markdown("<h5 style='text-align: center'>Financial Compass <em>Disclaimer</em></h5>", unsafe_allow_html=True)
with st.expander("View Financial Disclaimer:"):
    st.write("**The information avaliable in this app is not finacial advice**.")
    st.write("The information contained within this application and the resources availble are not intended as, and shall not be understood or constructed as, financial advice. Members of *Financial Compass* are not attorneys, accountants, or financial advisors, nor are we holding ourselves to be. The information in this application is not a substitute for financial advise from a professional who is aware of the facts and circumstances of your individual situation.")
    st.write("*Financial Compass* strives to ensure that the information provided on this application is accurate and valuable. Regardless, nothing avaliable on or through this application should be understood as a recomendation that you should not consult with a financial proffesional to address your particular situation. *Financial Compass expressly recommends that you seek advice from a professional of industry.*")

# Insert line breaks 
st.write("")

st.image(logo, width=150)
st.caption("*Design Rights Property of: Financial Compass*")
st.caption("*Results are financial insights, not advice*")
st.caption("*Contributor: [Cam Gould](https://www.linkedin.com/in/camrgould/)*")

with st.sidebar:
    st.markdown("<h2 style='text-align: center'>^ Navigate to Another Page ^</h2>", unsafe_allow_html=True)
    st.image(sidebar_logo)
    st.markdown("<h4 style='text-align: center'><em>Financial Compass</em></h4>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center'><em>Tools for Navigating Your Financials</em></h5>", unsafe_allow_html=True)
    st.markdown("<h6 style='text-align: center'><em>Established in August 2022</em></h6>", unsafe_allow_html=True)


# [theme]
# primaryColor="#f5bb0f"
# backgroundColor="#fbf4f4"
# secondaryBackgroundColor="#f9eaca"
# textColor="#3d3d3d"
# font="serif"
