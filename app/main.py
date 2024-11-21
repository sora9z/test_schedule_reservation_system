from fastapi import FastAPI

app = FastAPI(title="Test Schedule Resesrvation System")


@app.get("/")
def read_root():
    return {"message": "Hello World"}
