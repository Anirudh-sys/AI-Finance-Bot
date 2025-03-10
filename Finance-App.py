import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import finnhub
import google.generativeai as genai
import os
import requests
import time

st.set_page_config(page_title="AI Stock Analyst", layout="wide")

# Read API keys securely
finnhub_api_key = st.secrets["FINNHUB_API_KEY"]
google_api_key = st.secrets["GOOGLE_API_KEY"]

# Initialize Finnhub client
finnhub_client = finnhub.Client(api_key=finnhub_api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

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
def get_stock_data(symbol):
    """Fetch stock data using Finnhub."""
    try:
        # Get company profile
        profile = finnhub_client.company_profile2(symbol=symbol)
        if not profile:
            raise ValueError(f"No company profile data found for symbol: {symbol}")
            
        # Get quote
        quote = finnhub_client.quote(symbol)
        if not quote:
            raise ValueError(f"No quote data found for symbol: {symbol}")
            
        # Get basic financials
        financials = finnhub_client.company_basic_financials(symbol, 'all')
        if not financials:
            raise ValueError(f"No financial data found for symbol: {symbol}")
            
        # Get historical candle data for charts
        end_date = int(datetime.now().timestamp())
        start_date = int((datetime.now() - timedelta(days=365)).timestamp())
        candles = finnhub_client.stock_candles(symbol, 'D', start_date, end_date)
        
        # Create a consolidated data object
        stock_data = {
            'info': {
                'symbol': symbol,
                'shortName': profile.get('name', 'N/A'),
                'marketCap': profile.get('marketCapitalization', 'N/A') * 1000000 if profile.get('marketCapitalization') else 'N/A',
                'currentPrice': quote.get('c', 'N/A'),
                'trailingPE': financials.get('metric', {}).get('peBasicExclExtraTTM', 'N/A'),
                'forwardPE': financials.get('metric', {}).get('peNormalizedAnnual', 'N/A'),
                'fiftyTwoWeekHigh': quote.get('h', 'N/A'),
                'fiftyTwoWeekLow': quote.get('l', 'N/A'),
                'dividendYield': financials.get('metric', {}).get('dividendYieldIndicatedAnnual', 0) / 100 if financials.get('metric', {}).get('dividendYieldIndicatedAnnual') else 0,
                'sector': profile.get('finnhubIndustry', 'N/A'),
                'beta': financials.get('metric', {}).get('beta', 'N/A'),
            },
            'candles': candles
        }
        
        # Add additional method to mimic yfinance's history() function
        def history(period=None):
            if candles and candles.get('s') == 'ok':
                df = pd.DataFrame({
                    'Open': candles['o'],
                    'High': candles['h'],
                    'Low': candles['l'],
                    'Close': candles['c'],
                    'Volume': candles['v']
                })
                df.index = pd.to_datetime(candles['t'], unit='s')
                return df
            return pd.DataFrame()
        
        # Add the history method to our stock_data object
        stock_data['history'] = history
        
        return type('StockData', (), stock_data)  # Create a class dynamically
        
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

def get_stock_news(symbol):
    """Fetch recent news for a stock using Finnhub."""
    try:
        # Add delay to avoid rate limiting
        time.sleep(0.5)
        
        news = finnhub_client.company_news(
            symbol,
            _from=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            to=datetime.now().strftime("%Y-%m-%d"),
        )
        return news[:5]
    except Exception as e:
        st.error(f"Error fetching news for {symbol}: {str(e)}")
        return []

def create_price_chart(stock_data, symbol):
    """Create a candlestick chart for the stock."""
    try:
        hist = stock_data.history(period="1y")
        if hist.empty:
            st.warning(f"No historical data available for {symbol}")
            return None
            
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=hist.index,
                    open=hist["Open"],
                    high=hist["High"],
                    low=hist["Low"],
                    close=hist["Close"],
                )
            ]
        )
        fig.update_layout(
            title=f"{symbol} Stock Price - Last Year",
            xaxis_title="Date",
            yaxis_title="Price",
        )
        return fig
    except Exception as e:
        st.error(f"Error creating chart for {symbol}: {str(e)}")
        return None

def get_ai_analysis(stock1_data, stock2_data, stock1_symbol, stock2_symbol):
    """Generate AI analysis for two stocks."""
    try:
        stock1_info = {
            "symbol": stock1_symbol,
            "market_cap": stock1_data.info.get("marketCap", "N/A"),
            "pe_ratio": stock1_data.info.get("trailingPE", "N/A"),
            "price": stock1_data.info.get("currentPrice", "N/A"),
            "52w_high": stock1_data.info.get("fiftyTwoWeekHigh", "N/A"),
            "52w_low": stock1_data.info.get("fiftyTwoWeekLow", "N/A"),
            "forward_pe": stock1_data.info.get("forwardPE", "N/A"),
            "dividend_yield": stock1_data.info.get("dividendYield", 0) * 100,
            "sector": stock1_data.info.get("sector", "N/A"),
            "beta": stock1_data.info.get("beta", "N/A"),
        }

        stock2_info = {
            "symbol": stock2_symbol,
            "market_cap": stock2_data.info.get("marketCap", "N/A"),
            "pe_ratio": stock2_data.info.get("trailingPE", "N/A"),
            "price": stock2_data.info.get("currentPrice", "N/A"),
            "52w_high": stock2_data.info.get("fiftyTwoWeekHigh", "N/A"),
            "52w_low": stock2_data.info.get("fiftyTwoWeekLow", "N/A"),
            "forward_pe": stock2_data.info.get("forwardPE", "N/A"),
            "dividend_yield": stock2_data.info.get("dividendYield", 0) * 100,
            "sector": stock2_data.info.get("sector", "N/A"),
            "beta": stock2_data.info.get("beta", "N/A"),
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
        stock1 = st.session_state.stock1_data.info
        stock2 = st.session_state.stock2_data.info
        
        context = f"""
        Analyzing {st.session_state.stock1_symbol} ({stock1.get('shortName', '')}) 
        vs {st.session_state.stock2_symbol} ({stock2.get('shortName', '')}).
        
        Key Metrics:
        - {st.session_state.stock1_symbol}: 
          P/E {stock1.get('trailingPE', 'N/A')}, 
          Market Cap ${stock1.get('marketCap', 'N/A'):,}, 
          Beta {stock1.get('beta', 'N/A')}
          
        - {st.session_state.stock2_symbol}: 
          P/E {stock2.get('trailingPE', 'N/A')}, 
          Market Cap ${stock2.get('marketCap', 'N/A'):,}, 
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
st.title("🤖 AI-Powered Stock Comparison Tool")

# Stock Input Section
col1, col2 = st.columns(2)
with col1:
    stock1 = st.text_input("First Stock Symbol:", "NVDA").upper()
with col2:
    stock2 = st.text_input("Second Stock Symbol:", "MSFT").upper()

if st.button("Analyze Stocks", type="primary"):
    if stock1 and stock2:
        with st.spinner(f"Fetching data for {stock1}..."):
            st.session_state.stock1_data = get_stock_data(stock1)
            # Add delay to avoid rate limiting
            time.sleep(1)
        
        with st.spinner(f"Fetching data for {stock2}..."):
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
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = create_price_chart(st.session_state.stock2_data, st.session_state.stock2_symbol)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

    with tab3:
        col1, col2 = st.columns(2)
        metrics = [
            ('currentPrice', 'Price', '${:.2f}'),
            ('marketCap', 'Market Cap', '${:,.0f}'),
            ('trailingPE', 'P/E Ratio', '{:.2f}'),
            ('forwardPE', 'Forward P/E', '{:.2f}'),
            ('beta', 'Beta', '{:.2f}'),
            ('dividendYield', 'Dividend Yield', '{:.2%}'),
            ('fiftyTwoWeekHigh', '52W High', '${:.2f}'),
            ('fiftyTwoWeekLow', '52W Low', '${:.2f}'),
        ]
        for metric in metrics:
            with col1:
                val = st.session_state.stock1_data.info.get(metric[0])
                st.metric(
                    label=f"{st.session_state.stock1_symbol} {metric[1]}",
                    value=metric[2].format(val) if val and val != 'N/A' else 'N/A'
                )
            with col2:
                val = st.session_state.stock2_data.info.get(metric[0])
                st.metric(
                    label=f"{st.session_state.stock2_symbol} {metric[1]}",
                    value=metric[2].format(val) if val and val != 'N/A' else 'N/A'
                )

    with tab4:  # News Tab 
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"{st.session_state.stock1_symbol} News")
            news1 = get_stock_news(st.session_state.stock1_symbol)
            if news1: # Check if news were retrieved
                for article in news1:
                    st.markdown(f"**{article.get('headline', 'No headline')}**")
                    st.caption(f"{article.get('source', 'Unknown source')} - {datetime.fromtimestamp(article.get('datetime', 0)).strftime('%b %d')}")
                    st.write(article.get('summary', 'No summary available'))
                    st.divider()
            else:
                st.write(f"No news found for {st.session_state.stock1_symbol}")

        with col2:
            st.subheader(f"{st.session_state.stock2_symbol} News")
            news2 = get_stock_news(st.session_state.stock2_symbol)
            if news2: # Check if news were retrieved
                for article in news2:
                    st.markdown(f"**{article.get('headline', 'No headline')}**")
                    st.caption(f"{article.get('source', 'Unknown source')} - {datetime.fromtimestamp(article.get('datetime', 0)).strftime('%b %d')}")
                    st.write(article.get('summary', 'No summary available'))
                    st.divider()
            else:
                st.write(f"No news found for {st.session_state.stock2_symbol}")

    with tab5:
        st.subheader("Chat with AI")
        
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