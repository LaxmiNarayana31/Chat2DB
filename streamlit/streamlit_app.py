import streamlit as st
import requests

# FastAPI Server URL
BASE_URL = "http://localhost:7000/api/v1" 

st.set_page_config(page_title="Chat with Database", layout="wide")

if "db_session_id" not in st.session_state:
    st.session_state.db_session_id = None

st.title("Chat with Your Database")

# Database Connection Form
with st.form("db_connection_form"):
    st.subheader("Enter Database Credentials")
    col1, col2 = st.columns(2)
    
    with col1:
        user = st.text_input("User")
        host = st.text_input("Host")
        database = st.text_input("Database")
        db_type = st.selectbox("DB Type", ["MYSQL", "POSTGRESQL", "MSSQL", "ORACLE"])
    
    with col2:
        password = st.text_input("Password", type="password")
        port = st.text_input("Port")
    
    submitted = st.form_submit_button("Connect to Database")
    
    if submitted:
        response = requests.post(f"{BASE_URL}/establish-session", json={
            "user": user,
            "password": password,
            "host": host,
            "port": port,
            "database": database,
            "db_type": db_type
        })
        
        if response.status_code == 200 and response.json().get("status"):
            st.session_state.db_session_id = response.json()["data"]["db_session_id"]
            st.success("Connected to database successfully!")
        else:
            st.error("Failed to connect to database. Check your credentials.")

# Chat Section
if st.session_state.db_session_id:
    st.subheader("Chat with Database")
    user_query = st.text_area("Enter your query:")
    
    if st.button("Send Query"):
        response = requests.post(f"{BASE_URL}/generate-natural-response", json={
            "db_session_id": st.session_state.db_session_id,
            "user_query": user_query
        })
        
        if response.status_code == 200 and response.json().get("status"):
            st.write("**Response:**")
            st.write(response.json()["data"]["natural_response"])
        else:
            st.error("Failed to get response from database.")
