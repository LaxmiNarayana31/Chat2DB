from uuid import uuid4
from app.schema.ask_db_schema import *
from app.helper.ai_helper import ResponseGenerator
from app.utils.handle_exception import handle_exception
from app.helper.session_helper import session_manager

class AskDBService:
    def establish_db_connection(db_connection: DBConnectionRequest):
        try:
            db_user = db_connection.user
            db_password = db_connection.password
            db_host = db_connection.host
            db_port = db_connection.port
            db_name = db_connection.database
            db_type = db_connection.db_type

            db_session_id = str(uuid4())
            session_manager.establish_session(
                db_session_id = db_session_id,
                user = db_user,
                password = db_password,
                host = db_host,
                port = db_port,
                database = db_name,
                db_type = db_type
            )

            if db_session_id not in session_manager.sessions or session_manager.sessions[db_session_id]['db'] is None:
                return None

            return {"db_session_id": db_session_id}

        except Exception as e:
            handle_exception(e)
            

    def generate_response(db_query: QueryRequest):
        try:
            db_session_id = db_query.db_session_id
            user_query = db_query.user_query
            response = ResponseGenerator.generate_response(db_session_id = db_session_id, user_query = user_query)
            return response
        except Exception as e:
            handle_exception(e)
    
    
    def generate_natural_response(db_query: QueryRequest):
        try:
            db_session_id = db_query.db_session_id
            user_query = db_query.user_query
            response = ResponseGenerator.generate_natural_response(db_session_id = db_session_id, user_query = user_query)
            return response
        except Exception as e:
            handle_exception(e)
            return None


    def terminate_session(session_id: TerminateDbSession):
        try:
            db_session_id = session_id.db_session_id
            if db_session_id in session_manager.sessions:
                session_manager.sessions[db_session_id]['engine'].dispose()
                del session_manager.sessions[db_session_id]
            return None
        except Exception as e:
            handle_exception(e)

