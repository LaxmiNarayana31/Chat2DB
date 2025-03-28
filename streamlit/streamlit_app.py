import streamlit as st
import requests

# FastAPI Server URL
BASE_URL = "http://localhost:7000/api/v1/db"

st.set_page_config(page_title="Chat DB", layout="wide")

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "connect" 

# Initialize session state for storing query response
if "query_response" not in st.session_state:
    st.session_state.query_response = None  

# Function to connect to the database
def connect_to_database(db_connection):
    response = requests.post(f"{BASE_URL}/connect", json=db_connection)
    if response.status_code == 200 and response.json().get("status"):
        st.session_state.db_session_id = response.json()["data"]["db_session_id"]
        st.session_state.page = "chat" 
        st.success("Connected to database successfully!")
        st.rerun() 
    else:
        st.error("Failed to connect to database. Check your credentials.")

# Function to disconnect from the database
def disconnect_from_database():
    db_disconnect = {"db_session_id": st.session_state.db_session_id}
    response = requests.delete(f"{BASE_URL}/disconnect", json=db_disconnect)
    if response.status_code == 200 and response.json().get("status"):
        st.session_state.db_session_id = None
        st.session_state.page = "connect"  
        st.success("Database disconnected successfully!")
        st.rerun()  
    else:
        st.error("Failed to disconnect database.")

if st.session_state.page == "connect":
    col = st.columns([1, 2, 1])[1]  
    with col:
        st.title("Connect to Your Database")  
    
        with st.form("db_connection_form"):
            st.subheader("Enter Database Credentials")
            db_type = st.selectbox("DB Type", ["MYSQL", "POSTGRESQL", "MSSQL", "ORACLE"], key="db_type")
            host = st.text_input("Host", key="host", max_chars=50)
            user = st.text_input("User", key="user", max_chars=50)
            password = st.text_input("Password", type="password", key="password", max_chars=50)
            port = st.text_input("Port", key="port", max_chars=10)
            database = st.text_input("Database", key="database", max_chars=50)
            submitted = st.form_submit_button("Connect to Database")
            
            if submitted:
                db_connection = {
                    "db_username": user,
                    "db_password": password,
                    "db_host": host,
                    "db_port": port,
                    "db_name": database,
                    "db_type": db_type
                }
                connect_to_database(db_connection)


elif st.session_state.page == "chat":
    col = st.columns([1, 2, 1])[1]  
    with col:
        st.title("Chat with Your Database")  
        
        if st.button("Disconnect from Database"):
            disconnect_from_database()
        
        st.subheader("Chat with Database")
        user_query = st.text_area("Enter your query:")
    
        if st.button("Send Query"):
            if st.session_state.db_session_id:
                db_query = {
                    "db_session_id": st.session_state.db_session_id,
                    "user_query": user_query
                }
                response = requests.post(f"{BASE_URL}/ask_natural", json=db_query)
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    if response_data.get("status"):
                        # Store response in session state
                        st.session_state.query_response = {
                            "explanation": response_data["data"].get("natural_explanation", "No explanation generated."),
                            "sql_query": response_data["data"].get("sql_query", "No SQL query generated."),
                            "query_result": response_data["data"].get("data", "No data returned."),
                        }
                    else:
                        st.error(f"API returned failure: {response_data.get('response')}")
                else:
                    st.error("Failed to get response from database. API request failed.")

        # Display response
        if st.session_state.query_response:
            st.write("### Result:")
            st.write(st.session_state.query_response["explanation"])

            st.write("### SQL Query:")
            st.code(st.session_state.query_response["sql_query"], language="sql")  

            st.write("### Query Result:")
            st.write(st.session_state.query_response["query_result"])
