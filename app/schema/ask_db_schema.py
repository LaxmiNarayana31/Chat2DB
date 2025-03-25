from typing import Optional
from pydantic import BaseModel

class DBConnectRequest(BaseModel):
    db_username: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str
    db_type: str

class DBQueryRequest(BaseModel):
    db_session_id : str
    user_query: Optional[str] = None

class DBSessionTermination(BaseModel):
    db_session_id : Optional[str] = None