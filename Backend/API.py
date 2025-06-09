from fastapi import FastAPI, Body, UploadFile, Form, File
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {"message": "Home"}

@app.post("/submit")
async def submit(email : str = Form(...),labels : UploadFile = File(...)):
    print(email,labels)
    return {"data received" : email}


@app.get("/submit")
async def submit():
    return {"data received" : "data"}