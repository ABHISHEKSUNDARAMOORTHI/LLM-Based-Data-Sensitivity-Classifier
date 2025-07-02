# 🔐 LLM-Based Data Sensitivity Classifier

A sleek, efficient, and privacy-conscious Streamlit app that classifies data column sensitivity using **Google Gemini's Free API**.
---

## ✨ Goal & Vision

In today's data-driven world, understanding the **sensitivity of data** is essential for **compliance**, **security**, and **privacy**.  
This project provides a robust, user-friendly, production-grade solution to **automatically classify the sensitivity** of each data column.

By leveraging Google Gemini’s powerful LLM capabilities, the app infers labels like:
- `PII`
- `Finance-critical`
- `Internal`
- `Confidential`
- `Public`

...from just column names, types, and **sample values**—optimized to **minimize API usage**.

---

## 🧩 Architecture Overview

| Component              | Stack / Tool Used                     | Description                                                                 |
|------------------------|----------------------------------------|-----------------------------------------------------------------------------|
| 🧠 AI Intelligence      | Google Gemini API (Free Plan)          | Sends only minimal metadata (column name, type, 2 sample values)           |
| 💻 UI                  | Streamlit                              | Responsive layout, dark/light theme, sidebar controls                      |
| 🧰 IDE & Dev Tools      | VS Code, `.env`, `venv`, autopep8       | Dev environment, environment management                                    |
| 📦 Hosting             | Streamlit Sharing or Localhost         | Instant deployable with minimal setup                                      |
| 💾 Input Types         | CSV & JSON metadata                    | CSVs with headers or manually defined JSON schemas with sample values      |

---

## 🚀 Key Features

### 📥 Input Support

- Upload CSV files with headers or JSON schema
- Preview data and column structure
- Review/edit column sample values

### 🔍 Column Sensitivity Classifier

- **Sensitivity Level:** PII, Finance, Internal, etc.
- **Confidence Score:** 1–5
- **AI Explanation:** Brief reasoning from Gemini
- ✅ Optimized prompts for **low token usage**

### 🧠 AI Prompting Strategy

- Sends only: `column_name`, `data_type`, `1-2 sample_values`
- Uses `generation_config` (e.g., `temperature=0.2`) to get accurate results
- Built-in retry logic for Gemini API

### 🖼️ UI & UX

- Dark/light theme switch
- Sidebar with sticky actions
- Expanders for advanced options and explanations
- Quota usage warnings if token estimates are high

### 📤 Export Options

- Annotated CSV (adds sensitivity results to your original file)
- JSON report (complete results)
- Markdown summary

### 🧪 Test Mode

- Generate synthetic sensitive data (Email, Revenue, SSN, etc.)
- Great for demos and testing without real data

### 📚 Column History Log

- View past 5 classification results within your session

---

## 🏗️ Project Structure

```

llm-data-sensitivity-classifier/
│
├── app.py                    # Main Streamlit application
├── ai\_logic.py               # Gemini API interaction and prompt engineering
├── features.py               # File upload, input preview, and parsing
├── sensitivity\_labels.py     # Sensitivity categories and examples
├── additional\_features.py    # Test mode, exports, session history
├── styling.py                # Custom CSS and theme toggle logic
├── utils.py                  # Data cleaning, retry logic, logging, etc.
├── .env                      # API key (not tracked by Git)
├── requirements.txt          # All required packages
└── README.md                 # You’re reading it!

````

---

## 📦 `requirements.txt`

```text
streamlit
google-generativeai
pandas
python-dotenv
faker
plotly
numpy
scipy
````

---

## 🧠 Sample Prompt (from `ai_logic.py`)

```python
"""
Classify each column below with a sensitivity level from:
- Public, Internal, Confidential, PII, Finance-critical

For each column, return:
- sensitivity_level
- confidence (1–5)
- reasoning (briefly explain why)

Column Metadata:
[
  {"name": "user_email", "type": "string", "sample_values": ["john@example.com", "jane@corp.com"]},
  {"name": "revenue_q1", "type": "float", "sample_values": [12000.50, 15000.75]},
  {"name": "product_name", "type": "string", "sample_values": ["Laptop Pro", "Webcam HD"]}
]
"""
```

---

## 🛠️ Pro Development Practices

* ✅ Clean code with formatting tools (e.g., `black`, `autopep8`)
* 🔐 API key in `.env` (never hard-coded)
* ⏱️ Retry logic with exponential backoff for Gemini API
* 💬 All AI logic abstracted into `ai_logic.py` for maintainability
* 🧪 Token-efficient design: avoids full datasets, only samples
* ✨ Custom CSS for polished UI

---

## ▶️ Usage

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your Gemini API Key in .env
GEMINI_API_KEY="your_actual_key_here"

# Run the app
streamlit run app.py
```

---

## 📂 Sample Data

You can test using your own CSV or generate synthetic data via **Test Mode** in the sidebar.

---

## 🚀 Deployment (Optional)

1. Push to GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add `GEMINI_API_KEY` as a secret
4. Share the app URL publicly!

---
