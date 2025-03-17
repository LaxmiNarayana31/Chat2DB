from sqlalchemy.sql import text
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from app.helper.llm_helper import LlmHelper
from app.prompts.sql_prompt_template import sql_template
from app.prompts.nl_prompt_template import nl_template
from app.helper.session_helper import session_manager
from app.utils.handle_exception import handle_exception

class ResponseGenerator:
    
    # Handles response generation and SQL query execution.
    def generate_response(db_session_id: str, user_query: str = None, existed_query: str = None):
        try:
            if db_session_id not in session_manager.sessions or session_manager.sessions[db_session_id]['db'] is None:
                return "DB session not found"
            
            engine = session_manager.sessions[db_session_id]['engine']
            if existed_query is not None:
                with engine.connect() as connection:
                    result = connection.execute(text(existed_query))
                    rows = result.fetchall()
                    columns = result.keys()
                    response = [dict(zip(columns, row)) for row in rows]
                    sql_query = existed_query
            else:
                db = session_manager.sessions[db_session_id]['db']
                chat_history = session_manager.sessions[db_session_id].get('chat_history', [])
                chat_history.append({"role": "user", "content": user_query})
                session_manager.sessions[db_session_id]['chat_history'] = chat_history
                
                sql_chain = ResponseGenerator.get_sql_chain(db)
                sql_query = sql_chain.invoke({"question": user_query, "chat_history": chat_history})
                
                with engine.connect() as connection:
                    result = connection.execute(text(sql_query))
                    rows = result.fetchall()
                    columns = result.keys()
                    response = [dict(zip(columns, row)) for row in rows]
                
                chat_history.append({"role": "assistant", "content": response})
                session_manager.sessions[db_session_id]['chat_history'] = chat_history
            
            return {"sql_query": sql_query.replace("\n", " "), "result": response, "columns": list(columns)}
        except Exception as e:
            handle_exception(e)
            

    @staticmethod
    def get_sql_chain(db):
        try:
            """
            Create a chain of operations to generate an SQL query from a user's natural language question.

            Args:
                db (SQLDatabase): The SQLDatabase object representing the connection.
            """
            llm = LlmHelper.googleGeminiLlm()
            prompt = ChatPromptTemplate.from_template(sql_template)
            def get_schema(_):
                return db.get_table_info()

            return (
                RunnablePassthrough.assign(schema = get_schema)
                | prompt
                | llm
                | StrOutputParser()
            )
        except Exception as e:
            handle_exception(e)
    

    @staticmethod
    def generate_natural_response(db_session_id: str, user_query: str):
        try:
            sql_result = ResponseGenerator.generate_response(db_session_id, user_query)
            if not sql_result or "result" not in sql_result:
                return {"response": "I couldn't fetch data from the database."}

            # Use the natural language prompt template
            prompt = ChatPromptTemplate.from_template(nl_template)
            formatted_prompt = prompt.format(
                user_query=user_query,
                sql_query=sql_result["sql_query"],
                result=sql_result["result"]
            )

            # Get response from LLM
            llm = LlmHelper.googleGeminiLlm()
            natural_response = llm.invoke(formatted_prompt).content.strip()

            return {
                "natural_response": natural_response,
            }
        except Exception as e:
            handle_exception(e)
