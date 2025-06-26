import os
import shutil

from fastapi import FastAPI, UploadFile, Form, File
from starlette.middleware.cors import CORSMiddleware
import zipfile
import tempfile

from archives.BenchmarkSuite import BenchmarkSuite

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
    results = BenchmarkSuite.evaluate_zip(open_zip(labels))
    return {"data" : results}


@app.get("/submit")
async def submit_get():
    return {"data received" : "data"}

def inspect(zip_file: UploadFile):
    with open_zip(zip_file) as zip:
        return zip.namelist()

def open_zip(zip_file: UploadFile):
    tempf = tempfile.NamedTemporaryFile(delete=False)
    try:
        shutil.copyfileobj(zip_file.file, tempf)
        tempf.close()
        return zipfile.ZipFile(tempf.name, "r")
    finally:
        os.unlink(tempf.name)