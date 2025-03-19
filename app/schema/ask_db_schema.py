from typing import Optional
from pydantic import BaseModel

class DBConnectionRequest(BaseModel):
    user: str
    password: str
    host: str
    port: str
    database: str
    db_type: str

class QueryRequest(BaseModel):
    db_session_id : str
    user_query: Optional[str] = None

class TerminateDbSession(BaseModel):
    db_session_id : Optional[str] = None