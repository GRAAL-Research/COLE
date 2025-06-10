import os
import shutil

from fastapi import FastAPI, UploadFile, Form, File
from starlette.middleware.cors import CORSMiddleware
import zipfile
import tempfile
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
async def submit_post(email : str = Form(...),labels : UploadFile = File(...)):
    print(email,labels)
    print(inspect(labels))
    return {"data received" : email}


@app.get("/submit")
async def submit_get():
    return {"data received" : "data"}

def inspect(zip_file : UploadFile):
    tempf = tempfile.NamedTemporaryFile(delete=False)
    shutil.copyfileobj(zip_file.file, tempf)

    tempf.close()

    with zipfile.ZipFile(tempf.name,"r") as zip:
        ret = zip.namelist()

    os.unlink(tempf.name)
    return ret