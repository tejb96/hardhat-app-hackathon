from fastapi import FastAPI
from .routers import detect

app = FastAPI(description="Hardhat App Hackathon Backend")

app.include_router(detect.router)

@app.get("/")
def root():
    return {"message": "Hello, World!"}