from fastapi import FastAPI, Body

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Home"}

@app.post("/submit")
async def submit(data: dict = Body(...)):
    return {"data received" : data}

@app.get("/submit")
async def submit():
    return {"data received" : "data"}