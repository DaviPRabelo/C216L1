from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API Prática 1 C216"}