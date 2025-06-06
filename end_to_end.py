import os
import pandas as pd

from Benchmarks import FrColaBench, AllocineBench, Sts22Bench, Paws_xBench, XnliBench,PiafBench,SickfrBench,Opus_parcusBench,FrblimpBench,GqnliBench
from BenchmarkSuite import BenchmarkSuite
from Model import Model, make_claude_inference
from all_llms import create_models


claude_model_names = [
    "claude-opus-4-20250514",
    "claude-sonnet-4-20250514",
    "claude-3-5-haiku-20241022",
    "claude-3-7-sonnet-20250219",
    "claude-3-opus-20240229",

]
claude_models = []
for name in claude_model_names:
    infer_fn = make_claude_inference(name)
    claude_models.append(Model(name, infer_fn))

print("Création des instances HFLLMModel à partir de all_llms.py …")
hfllm_models = create_models()

all_models = claude_models + hfllm_models
print(f"→ Nombre total de modèles à évaluer : {len(all_models)}")
for m in all_models:
    print("   •", m.model_name)


benchmarks = [
    XnliBench(used_split="test"),
    Paws_xBench(used_split="test"),
    FrColaBench(used_split="test"),
    AllocineBench(used_split="test"),
    Sts22Bench(used_split="test"),
    GqnliBench(used_split="test"),
    PiafBench(used_split="test"),
    SickfrBench(used_split="test"),
    Opus_parcusBench(used_split="test"),
    FrblimpBench(used_split="test"),


]
bench_names = [b.name for b in benchmarks]
print("\n Benchmarks à évaluer :", bench_names)


suite = BenchmarkSuite(
    suite_name="Evaluation complète LLMs vs Claude",
    models=all_models,
    benchmarks=benchmarks
)


max_examples = 3

raw_results = suite.compute_all(max_targets=max_examples)


concise = suite.generate_concise_results(raw_results)


output_dir = "./results"
suite.save_results(raw_results, directory=output_dir)
print(f"\n Résultats complets enregistrés sous {os.path.abspath(output_dir)}")


rows = []
for model_name, bench_dict in concise.items():
    for bench_name, score in bench_dict.items():
        rows.append({
            "Benchmark": bench_name,
            "Modèle": model_name,
            "Score (10 ex.)": score
        })

df = pd.DataFrame(rows)
print("\n\n=== Récapitulatif final de tous les scores (10 ex.) ===\n")
print(df.to_string(index=False))
