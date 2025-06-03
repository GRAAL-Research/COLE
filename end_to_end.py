import pandas as pd
from Benchmarks import FrColaBench, AllocineBench, Sts22,Paws_xBench,XnliBench
from Model import Model, make_claude_inference

claude_model_names = [
    "claude-opus-4-20250514",
    "claude-sonnet-4-20250514",
    "claude-3-5-haiku-20241022",
    "claude-3-7-sonnet-20250219",
    "claude-3-opus-20240229",
]

results = []



def evaluate_benchmark(bench_class, benchmark_name):
    bench = bench_class(used_split="test")
    dataset = bench.load_dataset()["test"]
    first_ten = list(dataset)[:10]

    print(f"\n### Évaluation du benchmark {benchmark_name} ###\n")

    metric = bench.metrics[0]

    for model_name in claude_model_names:
        print(f"\n=== Évaluation pour le modèle {model_name} ===\n")
        infer_fn = make_claude_inference(model_name)
        model = Model(model_name, infer_fn)

        gold_labels = []
        predictions = []

        print("--- 10 premiers exemples ---\n")
        for idx, test in enumerate(first_ten):
            prompt = bench.build_prompt(test)
            raw_pred = model.infer(prompt)
            parsed_pred = bench.parse_answer(raw_pred)
            gold_label = bench.get_gold_label(test)

            gold_labels.append(gold_label)
            predictions.append(parsed_pred)

            print(f"Exemple {idx + 1}:")
            print(f"  Phrase       : {bench.gather_test_data(test)}")
            print(f"  Prédiction   : {parsed_pred}")
            print(f"  Gold Label   : {gold_label}\n")

        score = metric.compute(gold_labels, predictions)

        if isinstance(score, dict):
            score_strings = []
            for name, val in score.items():
                score_strings.append(f"{name}: {val:.2f}")
            joined = ", ".join(score_strings)
            print(f"✅ Scores (sur ces 10 exemples) : {joined}\n")
            score_for_df = joined
        else:
            print(f"✅ {metric.__class__.__name__} (sur ces 10 exemples) : {score:.2f}\n")
            score_for_df = f"{score:.2f}"

        results.append({
            "Benchmark": benchmark_name,
            "Modèle Claude": model_name,
            "Score (10 ex.)": score_for_df
        })

evaluate_benchmark(XnliBench, "Xnli")

evaluate_benchmark(Paws_xBench, "PAWS-X")

evaluate_benchmark(FrColaBench, "FrCola")

evaluate_benchmark(AllocineBench, "Allocine")

evaluate_benchmark(Sts22, "STS22")

df_results = pd.DataFrame(results)
print(df_results)
