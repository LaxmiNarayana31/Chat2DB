from fastapi import APIRouter
from app.utils.message import msg
from app.schema.response_schema import ResponseSchema  
from app.schema.ask_db_schema import DBConnectRequest, DBQueryRequest, DBSessionTermination
from app.modules.ask_database_service import AskDBService

router = APIRouter(prefix="/api/v1/db", tags=["Chat DB"])

# Route for connect to the database
@router.post("/connect")
def connect_db(db_connection: DBConnectRequest):
    response = AskDBService.connect_db(db_connection = db_connection)

    if response is not None and type(response) == dict:
        return ResponseSchema(status = True, status_code = 200, response = msg['database_connected'], data = response)
    elif response == 1 and type(response) == int:
        return ResponseSchema(status = False, status_code = 400, response = msg['database_not_connected'], data = None)
    else:
        return ResponseSchema(status = False, status_code = 500, response = msg['something_went_wrong'], data = None)
   

# Route for ask question to the database
@router.post("/ask")
def ask_db(ask_question: DBQueryRequest):
    response = AskDBService.ask_db(ask_question = ask_question)

    if response is not None and type(response) == dict:
        return ResponseSchema(status = True, status_code = 200, response = msg['response_generated'], data = response)
    elif response == 1 and type(response) == int:
        return ResponseSchema(status = False, status_code = 400, response = msg['database_not_connected'], data = None)
    else:
        return ResponseSchema(status = False, status_code = 500, response = msg['something_went_wrong'], data = None)

@router.post("/ask_natural")
def ask_db_natural(ask_question: DBQueryRequest):
    # response = AskDBService.ask_db(ask_question=ask_question)
    response = AskDBService.ask_db_natural(ask_question = ask_question)

    if response is not None and type(response) == dict:
        return ResponseSchema(status=True, status_code=200, response=msg['response_generated'], data=response)
    elif response == 1 and type(response) == int:
        return ResponseSchema(status=False, status_code=400, response=msg['database_not_connected'], data=None)
    else:
        return ResponseSchema(status=False, status_code=500, response=msg['something_went_wrong'], data=None)


# Route for disconnect from the database
@router.delete("/disconnect")
def disconnect_db(session: DBSessionTermination):
    response = AskDBService.disconnect_db(session = session)

    if response == 1 and type(response) == int:
        return ResponseSchema(status = True, status_code = 200, response = msg['all_db_disconnected'], data = None)
    elif response == 2 and type(response) == int:
        return ResponseSchema(status = True, status_code = 200, response = msg['db_disconnected'], data = None)
    elif response == 3 and type(response) == int:
        return ResponseSchema(status = False, status_code = 404, response = msg['db_session_not_found'], data = None)
    else:
        return ResponseSchema(status = False, status_code = 500, response = msg['something_went_wrong'], data = None)