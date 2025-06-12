import os
import shutil
import tempfile
import zipfile
import json
from dotenv import load_dotenv
from datetime import datetime

from fastapi import FastAPI, UploadFile, Form, File
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
    allow_origins=["http://localhost:3000"],
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
async def submit_post(email: str = Form(...), labels: UploadFile = File(...)):
    print(" Requête reçue avec email :", email)
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

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results_{email.replace('@', '_at_')}_{timestamp}.json"
        result_path = os.path.join(RESULTS_DIR, filename)

        with open(result_path, "w", encoding="utf-8") as f:
            json.dump({
                "email": email,
                "results": results_summary,
                "errors": errors
            }, f, indent=2, ensure_ascii=False)

        print(f" Résultats sauvegardés dans {result_path}")

        return {
            "email": email,
            "results": results_summary,
            "errors": errors,
            "file": filename
        }


@app.get("/results")
def get_latest_results():
    if not os.path.exists(RESULTS_DIR):
        return {"error": "Aucun dossier de résultats"}

    json_files = [
        f for f in os.listdir(RESULTS_DIR)
        if f.endswith(".json") or f.endswith(".jsonl")
    ]
    if not json_files:
        return {"error": "Aucun résultat disponible"}

    latest = max(
        json_files,
        key=lambda name: os.path.getmtime(os.path.join(RESULTS_DIR, name))
    )
    latest_path = os.path.join(RESULTS_DIR, latest)

    print(" Lecture du dernier résultat :", latest_path)

    try:
        with open(latest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["file"] = latest
            return data
    except Exception as e:
        print(" Erreur lors de la lecture du fichier :", e)
        return {"error": "Échec de la lecture du fichier de résultats."}
@app.get("/results/{filename}")
def get_result_file(filename: str):
    file_path = os.path.join(RESULTS_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "Fichier non trouvé"}
    return FileResponse(file_path, media_type="application/json", filename=filename)