from fastapi import APIRouter
from app.schema.ask_db_schema import *
from app.schema.response_schema import ResponseSchema
from app.utils.message import msg
from app.modules.ask_db_service import AskDBService

router = APIRouter(prefix="/api/v1", tags=["Chat DB"])

# Establish connection with database
@router.post("/establish-session")
def establish_db_connection(db_connection: DBConnectionRequest):
    response = AskDBService.establish_db_connection(db_connection = db_connection)

    if response is not None and type(response) == dict:
        return ResponseSchema(status=True, response=msg["db_conncted"], data=response)
    else:
        return ResponseSchema(status=False, response=msg["db_conncted_error"], data=None)

# Generate response on user query 
@router.post("/generate-response")
def generate_response(db_query: QueryRequest):
    response = AskDBService.generate_response(db_query = db_query)

    if response is not None and type(response) == dict:
        return ResponseSchema(status=True, response=msg["response_generated"], data=response)
    else:
        return ResponseSchema(status=False, response=msg["response_not_generated"], data=None)

# Generate response in natural langauge
@router.post("/generate-natural-response")
def generate_natural_response(db_query: QueryRequest):
    response = AskDBService.generate_natural_response(db_query = db_query)

    if response is not None and type(response) == dict:
        return ResponseSchema(status=True, response="Natural language response generated", data=response)
    else:
        return ResponseSchema(status=False, response="Failed to generate response", data=None)

# Delete the database session
@router.delete("/terminate_sessions")
def terminate_session(session_id: TerminateDbSession):
    response = AskDBService.terminate_session(session_id = session_id)

    if response is not None and type(response) == dict:
        return ResponseSchema(status=True, response=msg["session_deleted"], data=None)
    else:
        return ResponseSchema(status=True, response=msg["session_delete_error"], data=None)



    
