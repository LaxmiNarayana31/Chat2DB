import traceback
from sqlalchemy.sql import text
from sqlalchemy.engine import create_engine
from urllib.parse import quote_plus
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from app.helper.llm_helper import LlmHelper


# Initialize database connection
def init_database_connection(user: str, password: str, host: str, port: str, database: str, db_type: str):
    try:
        encoded_password = quote_plus(password)
        database_conn_string = None

        if db_type.upper() == "MYSQL":
            database_conn_string = f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{database}"
        elif db_type.upper() == "POSTGRESQL":
            database_conn_string = f"postgresql+psycopg2://{user}:{encoded_password}@{host}:{port}/{database}"
        elif db_type.upper() == "MSSQL":
            database_conn_string = f"mssql+pymssql://{user}:{encoded_password}@{host}:{port}/{database}"
        elif db_type.upper() == "ORACLE":
            database_conn_string = f"oracle+cx_oracle://{user}:{encoded_password}@{host}:{port}/{database}"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        engine = create_engine(database_conn_string)
        sql_database = SQLDatabase.from_uri(database_conn_string)
        return sql_database, engine, database
    except Exception as e:
        # Get the traceback as a string
        traceback_str = traceback.format_exc()
        print(traceback_str)
        # Get the line number of the exception
        line_no = traceback.extract_tb(e.__traceback__)[-1][1]
        print(f"Exception occurred on line {line_no}")
        return str(e)


# Class to manage the database session
class SessionManager:
    def __init__(self):
        # Hold the database sessions
        self.sessions = {} 
        
    # Establish a database connection
    def establish_db_connection(self, db_session_id: str, user: str, password: str, host: str, port: str, database: str, db_type: str):
        if db_session_id in self.sessions:
            self.sessions[db_session_id]['db'] = None
            self.sessions[db_session_id]['engine'].dispose()
        try:
            db, engine, database_name = init_database_connection(user, password, host, port, database, db_type)
            db_schema = db.get_table_info()
            self.sessions[db_session_id] = {'db': db, 'engine': engine, 'database_name': database_name, 'schema': db_schema}
        except Exception as e:
            # Get the traceback as a string
            traceback_str = traceback.format_exc()
            print(traceback_str)
            # Get the line number of the exception
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)


    # Generate response on user query 
    def generate_response(self, db_session_id: str, user_query: str = None):
        try:
            if db_session_id not in self.sessions or self.sessions[db_session_id]['db'] is None:
                raise ValueError(f"Session for {db_session_id} is not established. Please call establish_session first.")
            
            database_name = self.sessions[db_session_id]['database_name']
            schema = self.sessions[db_session_id]['schema']
            chat_history = self.sessions[db_session_id].get('chat_history', [])

            # Add user query to chat history
            chat_history.append({"role": "user", "content": user_query})
            self.sessions[db_session_id]['chat_history'] = chat_history

            sql_chain = self.create_sql_chain(database_name, schema)

            # Generate the SQL query using the chain
            sql_query = sql_chain.invoke({
                "question": user_query,
                "chat_history": chat_history,
            }).strip().replace("\n", " ")
            
            sql_query = sql_query.replace("DATABASE()", f"'{database_name}'")

            # Execute the query
            engine = self.sessions[db_session_id]['engine']
            with engine.connect() as connection:
                result = connection.execute(text(sql_query))
                rows = result.fetchall()
                columns = result.keys()
                data = [dict(zip(columns, row)) for row in rows]

            return {
                "sql_query": sql_query,
                "data": data
            }
        except Exception as e:
            # Get the traceback as a string
            traceback_str = traceback.format_exc()
            print(traceback_str)
            # Get the line number of the exception
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)
        

    # Create a chain of operations to generate an SQL query from a user's natural language question.
    def create_sql_chain(self, schema: str, database_name: str):   
        template = """You are an SQL query expert and data analyst at a company. You are interacting with a user who is asking you questions 
        about the company's database. Based on the table schema below, write a **modern, executable SQL query** that would 
        answer the user's question. Ensure the query uses **current best practices** and avoids deprecated or non-standard syntax. 
        If there are multiple ways to achieve the same result, prefer the most widely supported and efficient approach.

        <SCHEMA>{schema}</SCHEMA>

        Conversation History: {chat_history}

        Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.

        **Guidelines:**
        1. Use modern date and time functions (e.g., prefer `CURDATE() - INTERVAL 1 DAY` over deprecated expressions like `DATE('now', '-1 day')`).
        2. Avoid using vendor-specific features unless explicitly required. Aim for compatibility across major database systems like MySQL, PostgreSQL, and SQL Server, unless specified otherwise.
        3. Ensure the query is clear, concise, and optimized for execution.
        4. Don't use unknown columns, always use columns from provided schema only.
        5. Limit the subquery to return a single row using LIMIT 1.
        6. Always use `'{database_name}'` explicitly in SQL queries instead of `DATABASE()`. Never use `DATABASE()`, even if it seems correct.
        7. When querying `information_schema`, always include a `WHERE` clause to filter by `table_schema = '{database_name}'` to ensure the query only targets the specified database.

        **Examples:**
        - Question: Which 3 artists have the most tracks?  
        SQL Query: SELECT ArtistId, COUNT(*) AS track_count FROM Track GROUP BY ArtistId ORDER BY track_count DESC LIMIT 3;

        - Question: Name 10 artists  
        SQL Query: SELECT Name FROM Artist LIMIT 10;

        Your turn:

        Question: {question}  
        SQL Query:
        """
        llm = LlmHelper.googleGeminiLlm()
        prompt = ChatPromptTemplate.from_template(template)

        return (
            RunnablePassthrough.assign(
                schema = lambda _: schema, 
                database_name = lambda _: database_name
            )
            | prompt
            | llm
            | StrOutputParser()
        )