# 🌾 Project Samarth

An intelligent Q&A system for India's agricultural and climate data, built on `data.gov.in` datasets.

---

## 🎯 The Problem

Government portals like `data.gov.in` are repositories for thousands of valuable, high-granularity datasets. However, this data is often siloed, existing in varied formats and inconsistent structures across different ministries.

This makes it extremely difficult for policymakers and researchers to derive the cross-domain insights needed for effective decision-making (e.g., *"How does annual rainfall in a state affect its total crop production?"*).

## 💡 The Solution

**Project Samarth** is a functional, end-to-end prototype that solves this problem. It's an intelligent Q&A system that allows users to ask complex, natural language questions.

The system sources its information directly from cleaned government data to provide a single, coherent, and data-backed answer.

## 🛠️ Technical Architecture

The system is built in two phases: a one-time data integration pipeline and a real-time Q&A application.

### 1. Data Integration (ETL)

* **Extract:** Raw CSVs for district-level crop production and meteorological rainfall are sourced from `data.gov.in` (via Kaggle mirrors).
* **Transform:** A Python **Pandas** script (`build_database.py`) cleans the data, standardizes column names, and maps inconsistent meteorological "Subdivisions" (e.g., `GANGETIC WEST BENGAL`) to standard state names (e.g., `West Bengal`).
* **Load:** The cleaned, unified data is loaded into a single, serverless **DuckDB** database file (`samarth.db`). This ensures the data is private, fast, and secure, as it runs entirely locally.

### 2. Intelligent Q&A System

* **Frontend:** A simple web interface built with **Streamlit** (`app.py`).
* **Backend (Text-to-SQL Chain):** A **LangChain** chain using the **Google Gemini API** (specifically `gemini-flash-latest`) powers the logic.
* **Workflow:**
    1.  A user asks a question in the Streamlit app.
    2.  The LangChain chain feeds the user's question and the DuckDB schema to the Gemini API, which generates a single, precise SQL query.
    3.  The query is executed locally on the `samarth.db` file.
    4.  The raw data results are sent *back* to the Gemini API, which synthesizes a final, natural language answer.

This "Text-to-SQL Chain" (instead of a "chatty" agent) is a key design choice, as it makes only two API calls per question, allowing it to run perfectly on the **Google AI free tier** without hitting rate limits.

---

## 🚀 How to Run Locally

**1. Prerequisites:**
* Python 3.8+
* A Google Gemini API Key

**2. Setup:**
```bash
# Clone the repository (or just add the files)

# Install required libraries
pip install pandas duckdb streamlit langchain langchain-community langchain-google-genai

**3. Build the Database:**

  * Download the raw CSVs (`crop_production.csv` and `rainfall_in_india_1901_2015.csv`) into your project folder.
  * Run the ETL script one time:

<!-- end list -->

```bash
python build_database.py
```

  * This will create the `samarth.db` file in your folder.

**4. Run the App:**

  * Paste your Google Gemini API key into the `app.py` file.
  * Run the Streamlit application:

<!-- end list -->

```bash
streamlit run app.py
```

  * Your browser will automatically open with the chat interface.

-----

## ❓ Sample Questions

You can ask the system complex, cross-domain questions like:

  * `Compare the average annual rainfall in Punjab and West Bengal for the last 3 available years. In parallel, list the total Rice production in each of those states during the same period, citing all data sources.`
  * `Identify the district in Punjab with the highest production of Wheat in the most recent year available.`
  * `What was the total production of Rice in Uttar Pradesh in 2010?`

-----

## 🖥️ Demo Output
<img width="1017" height="924" alt="Screenshot 2025-10-30 125646" src="https://github.com/user-attachments/assets/e0b5d322-87a1-495e-a9e2-761a056281cd" />



