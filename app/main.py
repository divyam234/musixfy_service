from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers import index
import uvicorn
import os
import sys
# Load Env Variables


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Functions
app.include_router(index.router, prefix="/api")


@app.middleware("http")
async def after_request(request: Request, call_next):
    response = await call_next(request)
    response.headers["Accept-Ranges"] = 'bytes'
    return response


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)