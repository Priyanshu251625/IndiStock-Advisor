# 📈 IndiStock Advisor

An AI-powered conversational stock recommendation system built using **Groq LLM**, **Case-Based Reasoning (CBR)**, and **Streamlit**. The assistant understands natural language investment queries, asks follow-up questions when needed, and recommends stocks based on historical market patterns and user preferences.

---

## 🚀 Features

- 🤖 Conversational AI interface powered by Groq LLM
- 💬 Multi-turn conversations with follow-up questions
- 📊 Company and sector-based stock recommendations
- 🧠 Case-Based Reasoning (CBR) for investment decisions
- 📈 Technical indicator-based stock analysis
- 🎯 Personalized recommendations based on:
  - Risk tolerance
  - Target return
- 📋 View supported companies and sectors
- ⚡ Interactive Streamlit chat interface

---

## 🛠️ Tech Stack

- Python
- Streamlit
- Groq LLM API
- Case-Based Reasoning (Custom Implementation)
- Pandas
- NumPy
- Scikit-learn
- yfinance
- TA (Technical Analysis Library)

---

## 🌐 Live Demo

**Try the application here:**

https://indistock-advisor-itqxouputfo6fcpwx3lsqg.streamlit.app/



## 📂 Project Structure

```
Stock-ai-agent/
│
├── engine/
│   ├── conversation.py
│   ├── data_loader.py
│   ├── feature_engineering.py
│   ├── llm.py
│   ├── reasoning_engine.py
│   ├── ticker_resolver.py
│   └── ...
│
├── streamlit_app.py
├── requirements.txt
├── README.md
└── .env
```

---

## ⚙️ Installation

### Clone the repository

```bash
git clone <https://github.com/Priyanshu251625/IndiStock-Advisor>
cd Stock-ai-agent
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key
```

---

## ▶️ Running the Application

Start the Streamlit app:

```bash
streamlit run streamlit_app.py
```

The application will open in your browser.

---

## 💡 Example Queries

### Company Analysis

- Recommend Infosys
- Analyze HDFC Bank
- Should I buy SBI stock?
- Tell me about Sun Pharma

### Sector Recommendations

- Suggest banking stocks
- Recommend telecom stocks
- Suggest IT stocks

### Utility Commands

- Show supported companies
- Show supported sectors

---

## 🔄 How It Works

1. User submits a natural language investment query.
2. Groq LLM extracts:
   - Company or sector
   - Risk tolerance
   - Target return
3. If required information is missing, the assistant asks follow-up questions.
4. Historical stock data is downloaded using Yahoo Finance.
5. Technical indicators are calculated.
6. The Case-Based Reasoning engine compares the current stock with historical cases.
7. The system generates:
   - Recommendation
   - Confidence score
   - AI-generated explanation

---

## 📊 Recommendation Categories

- Buy
- Hold
- Avoid

Each recommendation includes:

- Confidence score
- Reasoning
- Similar historical cases

---

## 📌 Supported Companies

- Bharti Airtel
- HDFC Bank
- ICICI Bank
- Infosys
- ITC
- Larsen & Toubro
- Reliance Industries
- State Bank of India
- Sun Pharma
- Tata Consultancy Services

---

## 📌 Supported Sectors

- Banking
- Energy
- FMCG
- IT
- Infrastructure
- Pharma
- Telecom

---

## ⚠️ Disclaimer

This application is intended for educational and demonstration purposes only.

The recommendations are generated using historical market data and Case-Based Reasoning and should **not** be considered financial advice. Always conduct your own research before making investment decisions.

---

## 👨‍💻 Author

**Priyanshu Rajhans**

Built as part of the **Forward Deployed Engineer Intern Assignment**.
