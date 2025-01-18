from fastapi.middleware.cors import CORSMiddleware
from routes import router  # Assuming `router` is where your API routes are defined
import os
from fastapi import FastAPI
import uvicorn

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

app.include_router(router)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
if __name__ == "__main__":
    # Get the port from the environment variable or use 8000 for local testing
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)
