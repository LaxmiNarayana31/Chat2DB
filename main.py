import uvicorn
import warnings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.modules import ask_database_route

app = FastAPI(docs_url="/")

origins = ["*"]

warnings.filterwarnings("ignore")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def welcome():
    return "Welcome to Ask Database Service"

app.include_router(ask_database_route.router)

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=7000, log_level="info", reload=True)
    print("running")