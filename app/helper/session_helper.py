from sqlalchemy.engine import create_engine
from urllib.parse import quote_plus
from langchain_community.utilities import SQLDatabase
from app.utils.handle_exception import handle_exception

class SessionManager:
    """
    Manages database sessions.
    """
    def __init__(self):
        self.sessions = {}
    
    # Initialize database connection
    @staticmethod
    def init_database(user: str, password: str, host: str, port: str, database: str, db_type: str):
        """
        Initialize the connection to the specified database type.
        """
        try:
            encoded_password = quote_plus(password)
            db_uri = None
            
            if db_type.upper() == "MYSQL":
                db_uri = f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{database}"
            elif db_type.upper() == "POSTGRESQL":
                db_uri = f"postgresql+psycopg2://{user}:{encoded_password}@{host}:{port}/{database}"
            elif db_type.upper() == "MSSQL":
                db_uri = f"mssql+pymssql://{user}:{encoded_password}@{host}:{port}/{database}"
            elif db_type.upper() == "ORACLE":
                db_uri = f"oracle+cx_oracle://{user}:{encoded_password}@{host}:{port}/{database}"
            else:
                raise ValueError(f"Unsupported database type: {db_type}")

            engine = create_engine(db_uri)
            sql_database = SQLDatabase.from_uri(db_uri)
            return sql_database, engine, database
        except Exception as e:
            handle_exception(e)
    
    def establish_session(self, db_session_id: str, user: str, password: str, host: str, port: str, database: str, db_type: str):
        try:
            if db_session_id in self.sessions:
                self.sessions[db_session_id]['db'] = None
                self.sessions[db_session_id]['engine'].dispose()

            db, engine, database_name = self.init_database(user, password, host, port, database, db_type)
            self.sessions[db_session_id] = {'db': db, 'engine': engine, 'db_name': database_name}
        except Exception as e:
            handle_exception(e)


# Create an instance of SessionManager
session_manager = SessionManager()
