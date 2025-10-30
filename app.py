import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os

DB_FILE = "samarth.db"

if not os.path.exists(DB_FILE):
    st.error(f"Error: Database file not found at {DB_FILE}")
    st.stop()

db = SQLDatabase.from_uri(f"duckdb:///{DB_FILE}")

llm = ChatGoogleGenerativeAI(
    model="models/gemini-flash-latest", 
    temperature=0, 
    google_api_key="" # PASTE YOUR KEY
)

# Get the database schema. We do this once.
db_schema = db.get_table_info()


sql_template = """
Based on the table schema below, write a SQL query that answers the user's question.
Only output the SQL query and nothing else.

Schema: {schema}
Question: {question}
SQL Query:
"""
sql_prompt = ChatPromptTemplate.from_template(sql_template)


answer_template = """
Given the user's question and the results from a SQL query,
write a natural language answer.
If the SQL results are empty, just say you couldn't find any data.

Question: {question}
SQL Results: {results}
Answer:
"""
answer_prompt = ChatPromptTemplate.from_template(answer_template)

# This function runs the SQL query
def run_sql_query(inputs):
    sql_query = inputs['sql_query']
    try:
        return db.run(sql_query)
    except Exception as e:
        return f"Error executing query: {e}"

# This is the full chain. It runs in two steps.
sql_chain = (
    RunnablePassthrough.assign(schema=lambda x: db_schema)
    | sql_prompt
    | llm
    | StrOutputParser()
)

full_chain = (
    RunnablePassthrough.assign(sql_query=sql_chain)
    .assign(results=run_sql_query)
    | answer_prompt
    | llm
    | StrOutputParser()
)


st.set_page_config(page_title="Project Samarth", page_icon="🌾")
st.title("Project Samarth: Agri-Climate Q&A")
st.caption("A Q&A system for `data.gov.in` data (Free Tier).")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Ask a question about agriculture and climate..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking... (Generating SQL and synthesizing answer)"):
            try:
               
                response = full_chain.invoke({"question": prompt})
                answer = response
            
            except Exception as e:
                answer = f"Sorry, I ran into an error: {e}"

            st.markdown(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})