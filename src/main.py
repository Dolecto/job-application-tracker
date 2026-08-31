from fastapi import FastAPI


app = FastAPI()


@app.get("")
@app.get("/")
def main():
    return "Hello World"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)  # file_name : FastAPI_object