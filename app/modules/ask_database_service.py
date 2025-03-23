import traceback
import uuid
from app.helper.llm_helper import LlmHelper
from app.helper.session_helper import SessionManager
from app.schema.ask_db_schema import DBConnectRequest, DBQueryRequest, DBSessionTermination

# initialize session manager
session_manager = SessionManager()

class AskDBService:
    # Establish database connection
    def connect_db(db_connection: DBConnectRequest):
        try:
            db_session_id = str(uuid.uuid4()).replace("-", "_")
            session_manager.establish_db_connection(
                db_session_id = db_session_id,
                user = db_connection.db_username,
                password = db_connection.db_password,
                host = db_connection.db_host,
                port = db_connection.db_port,
                database = db_connection.db_name,
                db_type = db_connection.db_type,
            )
            if db_session_id not in session_manager.sessions or session_manager.sessions[db_session_id]['db'] is None:
                return 1
            return {"db_session_id": db_session_id}
        except Exception as e:
            # Get the traceback as a string
            traceback_str = traceback.format_exc()
            print(traceback_str)
            # Get the line number of the exception
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)
    

    # Ask questions to the database
    def ask_db(ask_question: DBQueryRequest):
        try:
            # Check if session for the db_session_id is established
            if ask_question.db_session_id not in session_manager.sessions or session_manager.sessions[ask_question.db_session_id]['db'] is None:
                return 1
            response = session_manager.generate_response(
                db_session_id = ask_question.db_session_id,
                user_query = ask_question.user_query
            )

            if "data" not in response:
                return {"error": "Failed to execute query"}
        
            return response
        except Exception as e:
            # Get the traceback as a string
            traceback_str = traceback.format_exc()
            print(traceback_str)
            # Get the line number of the exception
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)


    def ask_db_natural(ask_question):
        try:
            # Generate SQL query and execute it
            response = AskDBService.ask_db(ask_question)

            if response is None or not isinstance(response, dict):
                return {"error": "Something went wrong!"}

            if response is None:
                return 1

            query_result = response.get("data", [])

            if not query_result:
                natural_response = "No relevant data found."
            else:
                # Generate natural language response using LLM
                llm = LlmHelper.googleGeminiLlm()
                prompt = f"""
                You are a helpful AI assistant. Convert the following database query result into a human-friendly response. 
                Query Result: `{query_result}`
                Please format the response in clear, professional, and easy-to-understand language.
                """
                natural_response = llm.invoke(prompt).content.strip()


            response["natural_explanation"] = natural_response  
            return response

        except Exception as e:
            # Get the traceback as a string
            traceback_str = traceback.format_exc()
            print(traceback_str)
            # Get the line number of the exception
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)


    # Disconnect from the database
    def disconnect_db(session: DBSessionTermination):
        try:
            if not session.db_session_id:
                for session_id, session in session_manager.sessions.items():
                    session['engine'].dispose()
                session_manager.sessions.clear()
                return 1
            else:
                if session.db_session_id in session_manager.sessions:
                    session = session_manager.sessions.pop(session.db_session_id)
                    session['engine'].dispose()
                    return 2
                else:
                    return 3
        except Exception as e:
            # Get the traceback as a string
            traceback_str = traceback.format_exc()
            print(traceback_str)
            # Get the line number of the exception
            line_no = traceback.extract_tb(e.__traceback__)[-1][1]
            print(f"Exception occurred on line {line_no}")
            return str(e)
    