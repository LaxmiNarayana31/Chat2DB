# Chat2DB

## Overview

Chat2DB is an innovative application that bridges the gap between natural language and database queries. Using cutting-edge AI technology, it allows users to interact with their databases using plain English, eliminating the need for complex SQL knowledge.

## Features

- Connect to multiple database types (MySQL, PostgreSQL, MSSQL, Oracle)
- Generate SQL queries from natural language prompts
- Execute queries and return results
- Provide human-readable explanations using LLMs
- Web-based UI using Streamlit

## Tech Stack

- **Backend:** FastAPI, LangChain, SQLAlchemy
- **LLM Integration:** Google Gemini API
- **Frontend:** Streamlit
- **Database Support:** MySQL, PostgreSQL, MSSQL, Oracle

### Setup

- Clone the repository:
  ```bash
  git clone https://github.com/LaxmiNarayana31/Chat2DB.git
  ```
- Create a virtual environment using pipenv. If you don't have pipenv installed, you can install it by running `pip install pipenv` in your terminal.
  ```bash
  pipenv shell
  pipenv install
  ```
- Run the application:
  - Start the FastAPI Backend
    ```
    pipenv run main
    ```
  - Start the Streamlit Frontend
    ```
    Start the Streamlit Frontend
    ```
