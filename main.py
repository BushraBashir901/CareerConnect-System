# from fastapi import FastAPI
# from app.api.v1.router import router as api_router
# from dotenv import load_dotenv
# app = FastAPI()

# app.include_router(api_router)
# load_dotenv()
from dotenv import load_dotenv
import os
from app.api.v1.router import router as api_router
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()   # ✅ FIRST load env

print("CLIENT ID:", os.getenv("GOOGLE_CLIENT_ID"))
print("FRONTEND URL:", os.getenv("FRONTEND_URL"))

from fastapi import FastAPI

app = FastAPI()

app.include_router(api_router) 


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # backend-only, allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)