import os
import shutil
import tempfile
import zipfile
import json
from dotenv import load_dotenv
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware

from src.Benchmarks import (
    AllocineBench, FrColaBench, Paws_xBench, XnliBench,
    PiafBench, SickfrBench, Opus_parcusBench, Sts22Bench
)

load_dotenv()

RESULTS_DIR = "src/Backend/results"
os.makedirs(RESULTS_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",  # Frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BENCHMARKS = {
    "allocine": AllocineBench(),
    "frcola": FrColaBench(),
    "paws_x": Paws_xBench(),
    "xnli": XnliBench(),
    "piaf": PiafBench(),
    "sickfr": SickfrBench(),
    "opus_parcus": Opus_parcusBench(),
    "sts22_crosslingual": Sts22Bench()
}


@app.post("/submit")
async def submit_post(email: str = Form(...), labels: UploadFile = File(...),display_name: str = Form(...),):
    print(" Requête reçue avec email :", email)
    print(" Nom du fichier ZIP soumis :", labels.filename)

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "submission.zip")

        with open(zip_path, "wb") as f:
            shutil.copyfileobj(labels.file, f)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        json_files = []
        for root, _, files in os.walk(tmpdir):
            for file in files:
                if file.endswith(".json") or file.endswith(".jsonl"):
                    json_files.append(os.path.join(root, file))

        print(" Fichiers extraits :", json_files)
        print(" Benchmarks disponibles :", list(BENCHMARKS.keys()))

        results_summary = {}
        errors = {}

        for json_file in json_files:
            bench_name = os.path.splitext(os.path.basename(json_file))[0].lower()
            print(" Benchmark détecté :", bench_name)
            benchmark = BENCHMARKS.get(bench_name)

            if not benchmark:
                print(f" Benchmark inconnu : {bench_name}")
                errors[json_file] = "Benchmark inconnu"
                continue

            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    predictions = [line.strip() for line in f if line.strip()]
                score = benchmark.compare_infered_results(predictions)
                results_summary[bench_name] = score
            except Exception as e:
                print(f" Erreur dans {json_file} :", e)
                errors[json_file] = str(e)

        submission_id = str(uuid4())
        filename = f"{submission_id}.json"
        result_path = os.path.join(RESULTS_DIR, filename)

        with open(result_path, "w", encoding="utf-8") as f:
            json.dump({
                "email": email,
                "display_name": display_name,
                "zip_filename": labels.filename,        # ✅ ajouté
                "results": results_summary,
                "errors": errors
            }, f, indent=2, ensure_ascii=False)

        print(f" Résultats sauvegardés dans {result_path}")

        return {
            "email": email,
            "results": results_summary,
            "errors": errors,
            "submission_id": submission_id,
            "file": filename
        }


@app.get("/results")
def get_latest_results():
    raise HTTPException(status_code=400, detail="Tu dois utiliser un identifiant de soumission pour voir les résultats.")


@app.get("/results/{filename}")
def get_result_file(filename: str):
    file_path = os.path.join(RESULTS_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "Fichier non trouvé"}
    return FileResponse(file_path, media_type="application/json", filename=filename)


@app.get("/leaderboard")
def get_leaderboard():
    summaries = []
    for file in os.listdir(RESULTS_DIR):
        if not file.endswith(".json"):
            continue
        path = os.path.join(RESULTS_DIR, file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                summaries.append({
                    "name": file,
                    "submission_id": data.get("submission_id"),
                    "display_name": data.get("display_name", ""),
                    "zip_filename": data.get("zip_filename"),
                    "email": data.get("email", "unknown"),
                    "results": data.get("results", {})
                })
        except Exception as e:
            print(f" Erreur lecture {file} : {e}")
    return summaries
