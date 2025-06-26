import os
import shutil
import tempfile
import zipfile
import json
from dotenv import load_dotenv
from uuid import uuid4

from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware

from archives.Benchmarks import (
    AllocineBench, FrColaBench, Paws_xBench, XnliBench,
    PiafBench, SickfrBench, Opus_parcusBench, Sts22Bench
)

load_dotenv()

RESULTS_DIR = "src/Backend/results"
os.makedirs(RESULTS_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
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
async def submit_post(email: str = Form(...), labels: UploadFile = File(...), display_name: str = Form(...)):
    print(" Requête reçue avec email :", email)
    print(" Nom du fichier ZIP :", labels.filename)

    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "submission.zip")

        with open(zip_path, "wb") as f:
            shutil.copyfileobj(labels.file, f)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)

        json_files = [
            os.path.join(root, file)
            for root, _, files in os.walk(tmpdir)
            for file in files
            if file.endswith(".json")
        ]

        if not json_files:
            raise HTTPException(status_code=400, detail=" Aucun fichier JSON trouvé dans l'archive.")

        results_summary = {}
        errors = {}

        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)

                candidate_results = data.get("results") or data

                if not isinstance(candidate_results, dict):
                    raise ValueError("Format inattendu : les résultats ne sont pas un dictionnaire")

                for raw_name, predictions in candidate_results.items():
                    parts = raw_name.lower().split("|")
                    bench_key = parts[1] if len(parts) >= 2 else raw_name.lower()
                    bench_key = bench_key.replace("-", "_").strip()

                    benchmark = BENCHMARKS.get(bench_key)

                    if benchmark:
                        if isinstance(predictions, dict) and "acc" in predictions:
                            results_summary[raw_name] = predictions
                            print(f" Résultat pré-calculé accepté pour : {raw_name}")
                        else:
                            try:
                                score = benchmark.compare_infered_results(predictions)
                                results_summary[raw_name] = score
                            except Exception as e:
                                print(f" Erreur benchmark connu {raw_name} :", e)
                                errors[raw_name] = str(e)
                    else:
                        results_summary[raw_name] = predictions
                        print(f"️ Résultat brut ajouté pour : {raw_name}")

            except Exception as e:
                print(f" Erreur dans {json_file} :", e)
                errors[os.path.basename(json_file)] = str(e)

        submission_id = str(uuid4())
        filename = f"{submission_id}.json"
        result_path = os.path.join(RESULTS_DIR, filename)

        with open(result_path, "w", encoding="utf-8") as f:
            json.dump({
                "email": email,
                "display_name": display_name,
                "zip_filename": labels.filename,
                "results": results_summary,
                "errors": errors,
                "submission_id": submission_id
            }, f, indent=2, ensure_ascii=False)

        print(f" Résultats sauvegardés dans : {result_path}")

        return {
            "email": email,
            "results": results_summary,
            "errors": errors,
            "submission_id": submission_id,
            "file": filename
        }


@app.get("/results")
def get_latest_results():
    raise HTTPException(status_code=400, detail="️ Tu dois utiliser un identifiant de soumission pour voir les résultats.")


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
