from fastapi import FastAPI

from routers import extracted_job
from database.db_init import init_db


app = FastAPI()
app.include_router(extracted_job.router)


@app.get("")
@app.get("/")
def main():
    init_db()
    
    return "Hello World"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)  # file_name : FastAPI_object