# AI Finance Bot  

## 🚀 Live Demo  
Try the AI Finance Bot here: **[Live Demo](https://your-streamlit-app-link.streamlit.app/)**

## 📌 Description  
The AI Finance Bot is an intelligent financial assistant that integrates AI capabilities with multiple financial APIs to provide real-time insights, answer queries, and assist users in making informed financial decisions. The bot is designed using **Retrieval-Augmented Generation (RAG)** to enhance responses with accurate and up-to-date financial data.  

## ⚙️ Working  
1. The user interacts with the bot via a **Streamlit**-powered UI.  
2. The bot processes queries related to **stock prices, investment insights, and financial news**.  
3. The **Google Gemini 2.0 Flash** model, enhanced with RAG, retrieves relevant financial data from APIs.  
4. The AI model processes and analyzes the data to generate intelligent responses.  
5. The bot provides real-time financial insights with **contextual accuracy**.  

## ✨ Features  
- 🔍 **Real-time Financial Insights** – Fetches live stock market data.  
- 📊 **Investment Analysis** – Provides AI-driven investment insights.  
- 💬 **Conversational AI** – Uses **LLMs and NLP** for natural interaction.  
- 📰 **Financial News Aggregation** – Fetches the latest financial reports.  
- 📡 **API Integration** – Connects with **Yahoo Finance, Alpha Vantage, Finnhub, etc.**  
- 🚀 **User-Friendly UI** – Built using **Streamlit** for a seamless experience.  

## 🛠️ Technologies Used  
- **Programming Language:** Python  
- **AI Model:** Google Gemini 2.0 Flash with Retrieval-Augmented Generation (RAG)  
- **APIs:** Google [Gemini], Yahoo Finance, Finnhub
- **Framework:** Streamlit for UI  

## 🏗️ Project Structure  
```
AI-Finance-Bot/
│── .env                     # Environment variables for API keys  
│── Finance-App.py            # Main Streamlit application  
│── requirements.txt          # Dependencies  
│── README.md                
```  

## 🧠 About the AI Model  
The AI Finance Bot utilizes **Google Gemini 2.0 Flash**, a large language model optimized for financial queries. The model integrates **Retrieval-Augmented Generation (RAG)** to fetch and process real-time financial data, ensuring accuracy and relevance.  

## 🚀 Getting Started  

### 🔧 Setup and Installation  
1. **Clone the repository:**  
   ```bash  
   git clone https://github.com/Anirudh-sys/AI-Finance-Bot.git  
   cd AI-Finance-Bot  
   ```  
2. **Install dependencies:**  
   ```bash  
   pip install -r requirements.txt  
   ```  
3. **Set up API keys** in a `.env` file:  
   ```
   GOOGLE_API_KEY=your_google_api_key
   FINNHUB_API_KEY=your_finnhub_api_key
   ```  
4. **Run the application using Streamlit:**  
   ```bash  
   streamlit run Finance-App.py  
   ```  
"# AI-Finance-Bot" 
