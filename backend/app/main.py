from fastapi import FastAPI

app = FastAPI()


# cd to \app first lmao
# uvicorn app\main:app --reload

@app.get("/")
async def root():
    return {"message": "Hello World"}


# @app.get("/health")
# async def health():
#     return {"status": "ok"}
