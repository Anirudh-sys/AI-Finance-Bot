import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import finnhub
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Finnhub client
finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))

# Configure Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "stock1_data" not in st.session_state:
    st.session_state.stock1_data = None
if "stock2_data" not in st.session_state:
    st.session_state.stock2_data = None
if "stock1_symbol" not in st.session_state:
    st.session_state.stock1_symbol = ""
if "stock2_symbol" not in st.session_state:
    st.session_state.stock2_symbol = ""

# Helper Functions
import time
import requests

import time
import requests

def get_stock_data(symbol):
    """Fetch stock data using Finnhub instead of yfinance."""
    try:
        stock_quote = finnhub_client.quote(symbol)
        company_profile = finnhub_client.company_profile2(symbol=symbol)

        if not stock_quote or stock_quote == {}:
            raise ValueError(f"Error fetching stock price for {symbol}. API may be down or symbol may be incorrect.")

        if not company_profile or company_profile == {}:
            raise ValueError(f"Error fetching company profile for {symbol}. API may be down or symbol may be incorrect.")

        stock_info = {
            "symbol": symbol,
            "current_price": stock_quote.get("c", "N/A"),
            "high_price": stock_quote.get("h", "N/A"),
            "low_price": stock_quote.get("l", "N/A"),
            "open_price": stock_quote.get("o", "N/A"),
            "previous_close": stock_quote.get("pc", "N/A"),
            "market_cap": company_profile.get("marketCapitalization", "N/A"),
            "sector": company_profile.get("finnhubIndustry", "N/A"),
            "company_name": company_profile.get("name", "N/A"),
            "exchange": company_profile.get("exchange", "N/A"),
            "country": company_profile.get("country", "N/A"),
            "website": company_profile.get("weburl", "N/A"),
        }

        return stock_info

    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}. Please ensure the symbol is correct and try again.")
        return None



def get_stock_news(symbol):
    """Fetch recent news for a stock using Finnhub."""
    try:
        news = finnhub_client.company_news(
            symbol,
            _from=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            to=datetime.now().strftime("%Y-%m-%d"),
        )
        return news[:5]
    except Exception as e:
        st.error(f"Error fetching news for {symbol}: {str(e)}")
        return []

def create_price_chart(stock_data, stock_symbol):
    """Create a valid candlestick chart using stock data from Finnhub."""
    try:
        # Ensure stock_data contains valid price values
        open_price = stock_data.get("open_price")
        high_price = stock_data.get("high_price")
        low_price = stock_data.get("low_price")
        close_price = stock_data.get("current_price")

        if None in [open_price, high_price, low_price, close_price]:
            raise ValueError("Missing stock price values.")

        fig = go.Figure(data=[
            go.Candlestick(
                x=["Open", "High", "Low", "Close"],
                open=[open_price, open_price, open_price, open_price],
                high=[high_price, high_price, high_price, high_price],
                low=[low_price, low_price, low_price, low_price],
                close=[close_price, close_price, close_price, close_price]
            )
        ])

        fig.update_layout(
            title=f"{stock_symbol} Stock Price",
            xaxis_title="Stock Metrics",
            yaxis_title="Price",
        )
        return fig  # ✅ Returns a valid Plotly figure

    except Exception as e:
        st.error(f"Error creating chart for {stock_symbol}: {str(e)}")
        return go.Figure()  # ✅ Returns an empty figure if an error occurs
def format_number(value):
    if isinstance(value, (int, float)):
        return f"${value:,.0f}"
    return value  # Return "N/A" or any string as-is

def get_ai_analysis(stock1_data, stock2_data, stock1_symbol, stock2_symbol):
    """Generate AI analysis for two stocks."""
    try:
        stock1_info = {
            "symbol": stock1_symbol,
            "market_cap": stock1_data.get("marketCap", "N/A"),
            "pe_ratio": stock1_data.get("trailingPE", "N/A"),
            "price": stock1_data.get("currentPrice", "N/A"),
            "52w_high": stock1_data.get("fiftyTwoWeekHigh", "N/A"),
            "52w_low": stock1_data.get("fiftyTwoWeekLow", "N/A"),
            "forward_pe": stock1_data.get("forwardPE", "N/A"),
            "dividend_yield": stock1_data.get("dividendYield", 0) * 100,
            "sector": stock1_data.get("sector", "N/A"),
            "beta": stock1_data.get("beta", "N/A"),
        }

        stock2_info = {
            "symbol": stock2_symbol,
            "market_cap": stock2_data.get("marketCap", "N/A"),
            "pe_ratio": stock2_data.get("trailingPE", "N/A"),
            "price": stock2_data.get("currentPrice", "N/A"),
            "52w_high": stock2_data.get("fiftyTwoWeekHigh", "N/A"),
            "52w_low": stock2_data.get("fiftyTwoWeekLow", "N/A"),
            "forward_pe": stock2_data.get("forwardPE", "N/A"),
            "dividend_yield": stock2_data.get("dividendYield", 0) * 100,
            "sector": stock2_data.get("sector", "N/A"),
            "beta": stock2_data.get("beta", "N/A"),
        }

        prompt = f"""
        As a professional financial analyst, analyze these two stocks:

        {stock1_info['symbol']}:
        - Sector: {stock1_info['sector']}
        - Market Cap: ${stock1_info['market_cap']:,}
        - P/E: {stock1_info['pe_ratio']} | Forward P/E: {stock1_info['forward_pe']}
        - Price: ${stock1_info['price']} (52W: {stock1_info['52w_low']}-{stock1_info['52w_high']})
        - Beta: {stock1_info['beta']} | Dividend Yield: {stock1_info['dividend_yield']:.2f}%

        {stock2_info['symbol']}:
        - Sector: {stock2_info['sector']}
        - Market Cap: ${stock2_info['market_cap']:,}
        - P/E: {stock2_info['pe_ratio']} | Forward P/E: {stock2_info['forward_pe']}
        - Price: ${stock2_info['price']} (52W: {stock2_info['52w_low']}-{stock2_info['52w_high']})
        - Beta: {stock2_info['beta']} | Dividend Yield: {stock2_info['dividend_yield']:.2f}%

        Provide detailed analysis covering:
        1. Valuation comparison
        2. Growth potential
        3. Risk assessment
        4. Sector outlook
        5. Investment recommendation

        Use professional tone with clear section headers.
        """

        response = model.generate_content(prompt)
        return response.text if response else "No analysis available"
    except Exception as e:
        return f"Analysis error: {str(e)}"


def generate_chat_response(prompt):
    """Generate AI response for chat conversations."""
    try:
        stock1 = st.session_state.stock1_data
        stock2 = st.session_state.stock2_data
        
        # Handle market cap formatting
        def format_market_cap(value):
            if isinstance(value, (int, float)):
                return f"${value:,.0f}"  # Format as currency with commas, no decimals
            return f"${value}"  # Just add $ if it's not a number (like 'N/A')
        
        # Format all values separately before string interpolation
        market_cap1 = format_market_cap(stock1.get('market_cap', 'N/A'))  
        market_cap2 = format_market_cap(stock2.get('market_cap', 'N/A'))  
        
        # Use pre-formatted values in the f-string
        context = f"""
            Analyzing {st.session_state.stock1_symbol} ({stock1.get('shortName', '')}) 
            vs {st.session_state.stock2_symbol} ({stock2.get('shortName', '')}).

            Key Metrics:
            - {st.session_state.stock1_symbol}: 
              P/E {stock1.get('trailingPE', 'N/A')}, 
              Market Cap {market_cap1}, 
              Beta {stock1.get('beta', 'N/A')}

            - {st.session_state.stock2_symbol}: 
              P/E {stock2.get('trailingPE', 'N/A')}, 
              Market Cap {market_cap2}, 
              Beta {stock2.get('beta', 'N/A')}
            """

        full_prompt = f"""
            {context}

            As a financial expert, answer this question: 
            {prompt}

            Guidelines:
            - Be specific to these companies
            - Compare key metrics
            - Highlight risks and opportunities
            - Maintain professional tone
            - Use bullet points when appropriate
            """

        response = model.generate_content(full_prompt)
        return response.text if response else "Couldn't generate response"
    except Exception as e:
        return f"Chat error: {str(e)}"

# Streamlit UI
st.set_page_config(page_title="AI Stock Analyst", layout="wide")
st.title("🤖 AI-Powered Stock Comparison Tool")

# Stock Input Section
col1, col2 = st.columns(2)
with col1:
    stock1 = st.text_input("First Stock Symbol:", "AAPL").upper()
with col2:
    stock2 = st.text_input("Second Stock Symbol:", "MSFT").upper()

if st.button("Analyze Stocks", type="primary"):
    if stock1 and stock2:
        st.session_state.stock1_data = get_stock_data(stock1)
        st.session_state.stock2_data = get_stock_data(stock2)
        st.session_state.stock1_symbol = stock1
        st.session_state.stock2_symbol = stock2
        st.session_state.chat_history = []
    else:
        st.warning("Please enter both stock symbols")

# Main Display Section
if st.session_state.stock1_data and st.session_state.stock2_data:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 AI Analysis", 
        "📈 Charts", 
        "💼 Fundamentals", 
        "📰 News", 
        "💬 AI Chat"
    ])

    with tab1:
        analysis = get_ai_analysis(
            st.session_state.stock1_data,
            st.session_state.stock2_data,
            st.session_state.stock1_symbol,
            st.session_state.stock2_symbol
        )
        st.markdown(analysis)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            fig = create_price_chart(st.session_state.stock1_data, st.session_state.stock1_symbol)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = create_price_chart(st.session_state.stock2_data, st.session_state.stock2_symbol)
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)

        metrics = [
        ('current_price', 'Price', '${:.2f}'),
        ('market_cap', 'Market Cap', '${:,.0f}B'),
        ('open_price', 'Opening Price', '${:.2f}'),
        ('high_price', 'High Price', '${:.2f}'),
        ('low_price', 'Low Price', '${:.2f}'),
        ('sector', 'Sector', '{}'),
        ]

    for metric in metrics:
        with col1:
            val = st.session_state.stock1_data.get(metric[0], "N/A")
            st.metric(
                label=f"{st.session_state.stock1_symbol} {metric[1]}",
                value=metric[2].format(val) if val != "N/A" else "N/A"
            )
        with col2:
            val = st.session_state.stock2_data.get(metric[0], "N/A")
            st.metric(
                label=f"{st.session_state.stock2_symbol} {metric[1]}",
                value=metric[2].format(val) if val != "N/A" else "N/A"
            )


    with tab4:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"{st.session_state.stock1_symbol} News")
            for article in get_stock_news(st.session_state.stock1_symbol):
                st.markdown(f"**{article['headline']}**")
                st.caption(f"{article['source']} - {datetime.fromtimestamp(article['datetime']).strftime('%b %d')}")
                st.write(article['summary'])
                st.divider()
        with col2:
            st.subheader(f"{st.session_state.stock2_symbol} News")
            for article in get_stock_news(st.session_state.stock2_symbol):
                st.markdown(f"**{article['headline']}**")
                st.caption(f"{article['source']} - {datetime.fromtimestamp(article['datetime']).strftime('%b %d')}")
                st.write(article['summary'])
                st.divider()

    with tab5:
        st.subheader("Chat with Financial AI")
        
        # Chat history
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.chat_message("human").write(msg["content"])
            else:
                st.chat_message("ai").write(msg["content"])
        
        # Chat input
        if prompt := st.chat_input(f"Ask about {stock1} vs {stock2}"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            with st.spinner("Analyzing..."):
                response = generate_chat_response(prompt)
                st.session_state.chat_history.append({"role": "ai", "content": response})
            
            st.rerun()

# Conversation Starters
if st.session_state.stock1_data:
    st.sidebar.header("Quick Analysis Prompts")
    questions = [
        "Compare growth potential",
        "Which has better valuation?",
        "Analyze risk factors",
        "Compare dividend policies",
        "Technical analysis outlook"
    ]
    
    for q in questions:
        if st.sidebar.button(q):
            st.session_state.chat_history.append({"role": "user", "content": q})
            with st.spinner("Analyzing..."):
                response = generate_chat_response(q)
                st.session_state.chat_history.append({"role": "ai", "content": response})
            st.rerun()

# Footer
st.markdown("---")
st.caption("Powered by Google Gemini, Yahoo Finance, and Finnhub | Created with Streamlit")
