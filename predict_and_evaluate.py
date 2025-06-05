import os
import json
import argparse
import pandas as pd

from datasets import load_dataset
from Model import make_claude_inference
from HuggingFaceModel import HFLLMModel

from BenchmarkSuite import BenchmarkSuite

from Benchmarks import AllocineBench , Paws_xBench


def make_model_instance(model_identifier: str):

    if model_identifier.lower().startswith("hf:"):
        hf_name = model_identifier.split("hf:", 1)[1]
        return HFLLMModel(hf_name)

    elif model_identifier.lower().startswith("claude:"):
        claude_name = model_identifier.split("claude:", 1)[1]
        inference_fn = make_claude_inference(claude_name)

        class InferenceModel:
            def __init__(self, fn, name):
                self._fn = fn
                self.model_name = name

            def infer(self, prompt: str) -> str:
                return self._fn(prompt)

            def unload_model(self):
                pass

        return InferenceModel(inference_fn, claude_name)

    else:
        return HFLLMModel(model_identifier)


def dump_hf_test_and_nolabel(repo_id: str,
                             data_dir: str,
                             out_dir: str):

    os.makedirs(out_dir, exist_ok=True)

    bench_name = os.path.basename(data_dir)

    try:
        ds = load_dataset(
            repo_id,
            data_dir=data_dir,
            split="test"
        )
    except Exception as e:
        print(f"[WARN] Impossible de charger '{repo_id}' / '{data_dir}' / split 'test' : {e}")
        return None, None

    path_lab     = os.path.join(out_dir, f"{bench_name}_test.jsonl")
    path_nolabel = os.path.join(out_dir, f"{bench_name}_test_nolabel.jsonl")

    with open(path_lab, "w", encoding="utf-8") as f_lab:
        for example in ds:
            f_lab.write(json.dumps(example, ensure_ascii=False) + "\n")

    df = pd.DataFrame(ds)
    if "label" in df.columns:
        df_nolabel = df.drop(columns=["label"])
    else:
        df_nolabel = df.copy()

    with open(path_nolabel, "w", encoding="utf-8") as f_nl:
        for _, row in df_nolabel.iterrows():
            f_nl.write(json.dumps(row.to_dict(), ensure_ascii=False) + "\n")

    print(f"[DUMP] '{bench_name}' →")
    print(f"   • labellisé   : {path_lab}  (n={len(df)})")
    print(f"   • no_label    : {path_nolabel}  (n={len(df_nolabel)})")

    return path_lab, path_nolabel


def main():
    parser = argparse.ArgumentParser(
        description="Évalue un modèle sur Allocine et PAWS-X en chargeant directement depuis HF."
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,

    )
    parser.add_argument(
        "--max_examples",
        type=int,
        default=10,
        help="Nombre d’exemples à traiter (par benchmark)."
    )
    args = parser.parse_args()
    model_identifier = args.model
    max_examples     = args.max_examples

    print(f"[INFO] Instanciation du modèle `{model_identifier}` …")
    model = make_model_instance(model_identifier)
    print(f"[INFO] Modèle chargé : {model.model_name}")

    hf_data_dir = "hf_data"

    allocine_lab, allocine_nolabel = dump_hf_test_and_nolabel(
        repo_id  = "COLLE-Graal/ColleGraal",
        data_dir = "data/Allocine",
        out_dir  = hf_data_dir
    )

    pawsx_lab, pawsx_nolabel = dump_hf_test_and_nolabel(
        repo_id  = "paws-x",
        data_dir = "fr",
        out_dir  = hf_data_dir
    )

    benchmarks = []

    if allocine_lab and allocine_nolabel:
        benchmarks.append(
            AllocineBench(
                data_path     = allocine_lab,
                no_label_path = allocine_nolabel
            )
        )
    else:
        print("[WARN] AllocineBench ignoré (pas de JSONL)")

    if pawsx_lab and pawsx_nolabel:
        benchmarks.append(
            Paws_xBench(
                data_path     = pawsx_lab,
                no_label_path = pawsx_nolabel
            )
        )
    else:
        print("[WARN] Paws_xBench ignoré (pas de JSONL)")

    print(f"[INFO] {len(benchmarks)} benchmarks configurés.")

    if not benchmarks:
        print("[ERROR] Aucun benchmark n’a pu être chargé → sortie.")
        return

    suite = BenchmarkSuite(
        suite_name = "EvaluationAutomatique",
        models     = [model],
        benchmarks = benchmarks
    )
    os.makedirs("results", exist_ok=True)

    print(f"[INFO] Lancement de l’évaluation labellisée pour `{model.model_name}` …")
    global_scores = suite.evaluate_model(model, max_targets=max_examples)

    for bench in benchmarks:
        bench_name  = bench.name
        scores_dict = global_scores.get(model.model_name, {}).get(bench_name, {})

        no_label_path = getattr(bench, "no_label_path", None)
        if not no_label_path or not os.path.isfile(no_label_path):
            print(f"[WARN] Pas de fichier no_label pour `{bench_name}` → skip.")
            continue

        df_no = pd.read_json(no_label_path, lines=True).head(max_examples)
        preds = []
        for _, row in df_no.iterrows():
            prompt     = bench.build_prompt(row)
            raw_answer = model.infer(prompt)
            pred       = bench.parse_answer(raw_answer)
            preds.append({
                "id":          row.get("id", None),
                "input_data":  bench.gather_test_data(row),
                "pred":        int(pred)
            })

        export_obj = {
            "predictions": preds,
            "metrics":     scores_dict
        }
        model_fname = model.model_name.replace("/", "_")
        output_path = f"results/{model_fname}_{bench_name}_preds_metrics.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_obj, f, ensure_ascii=False, indent=2)

        print(f"[SAVED] {bench_name} → {output_path}")

    summary = global_scores.get(model.model_name, {})
    summary_path = f"results/{model.model_name.replace('/', '_')}_scores_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"[SAVED] Résumé global → {summary_path}")

    if hasattr(model, "unload_model"):
        model.unload_model()

    print("[INFO] Terminé.")


if __name__ == "__main__":
    main()
