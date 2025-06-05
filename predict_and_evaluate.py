import os
import json
import argparse
import pandas as pd

from Model import make_claude_inference
from HuggingFaceModel import  HFLLMModel


from BenchmarkSuite import BenchmarkSuite


from Benchmarks import FrColaBench, AllocineBench,Paws_xBench,XnliBench



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


def main():
    parser_arg = argparse.ArgumentParser(
        description="Évalue automatiquement un modèle sur une suite de benchmarks."
    )
    parser_arg.add_argument(
        "--model",
        type=str,
        required=True,
    )
    parser_arg.add_argument(
        "--max_examples",
        type=int,
        default=10,
        help="Nombre maximum d’exemples à traiter par benchmark (par défaut : 10)."
    )
    args = parser_arg.parse_args()

    model_identifier = args.model
    max_examples     = args.max_examples

    print(f"[INFO] Création du modèle `{model_identifier}` …")
    model = make_model_instance(model_identifier)
    print(f"[INFO] Modèle instancié : {model.model_name}")

    benchmarks = []

    benchmarks.append(
        AllocineBench(
            data_path      = "C:/Users/firam/Downloads/stage/Benchmarks/data/Allocine/allocine_test.jsonl",
            no_label_path  = "C:/Users/firam/Downloads/stage/no_label/allocine_nolabels_test.jsonl"
        )
    )
    benchmarks.append(
        Paws_xBench(
            data_path      = "C:/Users/firam/Downloads/stage/Benchmarks/data/paws_x/paws_x_fr_test.jsonl",
            no_label_path  = "C:/Users/firam/Downloads/stage/no_label/paws_x_fr_nolabels_test.jsonl"
        )
    )




    print(f"[INFO] {len(benchmarks)} benchmarks configurés.")

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
        scores_dict = global_scores[model.model_name].get(bench_name, {})

        no_label_path = getattr(bench, "no_label_path", None)
        if not no_label_path or not os.path.isfile(no_label_path):
            print(f"[WARN] Pas de fichier no_label pour `{bench_name}` ; on skip.")
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

        print(f"[SAVED] Prédictions+métriques pour `{bench_name}` → {output_path}")

    summary = global_scores[model.model_name]
    summary_path = f"results/{model.model_name.replace('/', '_')}_scores_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"[SAVED] Résumé global des scores → {summary_path}")

    if hasattr(model, "unload_model"):
        model.unload_model()

    print("[INFO] Terminé.")


if __name__ == "__main__":
    main()
