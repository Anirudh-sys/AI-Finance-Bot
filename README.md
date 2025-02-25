# AI-Powered Stock Comparison Tool

## Description
This is a Streamlit application that allows users to compare stocks using AI analysis, historical data visualization, and news aggregation. Users can input stock symbols and receive detailed insights, including price charts, fundamental metrics, and recent news.

## Installation
To run this application, you need to install the required dependencies. You can do this by running:

```bash
pip install -r requirements.txt
```

## Usage
1. Clone the repository or download the files.
2. Create a `.env` file in the root directory and add your API keys:
   ```
   FINNHUB_API_KEY=your_finnhub_api_key
   GOOGLE_API_KEY=your_google_api_key
   ```
3. Run the application using Streamlit:
   ```bash
   streamlit run Finance-App.py
   ```
4. Open your web browser and navigate to the provided local URL.

## Dependencies
- Streamlit
- yfinance
- pandas
- plotly
- finnhub
- google.generativeai
- python-dotenv

## Acknowledgments
- Powered by Google Gemini, Yahoo Finance, and Finnhub.
