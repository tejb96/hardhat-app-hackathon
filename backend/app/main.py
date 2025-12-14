from fastapi import FastAPI
from .routers import detect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(description="Hardhat App Hackathon Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(detect.router)

@app.get("/")
def root():
    return {"message": "Hello, World!"}