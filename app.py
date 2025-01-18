from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router  # Assuming `router` is where your API routes are defined

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

app.include_router(router)