import json
import os

from Benchmark import Benchmark
from Model import Model


class BenchmarkSuite:
    def __init__(self, suite_name, models: list[Model | str] = None, benchmarks: list[Benchmark] = None):
        self.suite_name = suite_name
        self.models = models if models is not None else []
        self.benchmarks = benchmarks if benchmarks is not None else []

    def compute_all(self, max_targets=None):
        global_results = {}
        for model in self.models:
            print("Benchmarking model : ", model.model_name)
            results_per_model = {}
            for benchmark in self.benchmarks:
                print(f"Testing benchmark {model.model_name} on dataset {benchmark.name}")
                try:
                    result = benchmark.evaluate(model, max_targets)
                except Exception as e:
                    print(f" Erreur lors de l'évaluation de {model.model_name} sur {benchmark.name} : {e}")
                    result = None
                results_per_model[benchmark.name] = result
            global_results[model.model_name] = results_per_model
            try:
                model.unload_model()
            except Exception:
                pass
        return global_results

    """Computes results by using a model for each benchmark, if you want to evaluate only 1 model for each benchmark, use evaluate_model instead"""

    def compute_1_model_per_bench_model(self, max_targets=None):
        global_results = {}
        for idx, benchmark in enumerate(self.benchmarks):
            if self.models[idx] is not None:
                model = self.models[idx]
                global_results[benchmark.name] = benchmark.evaluate(model, max_targets)
            else:
                global_results[benchmark.name] = "(no model)"
        return global_results

    """Evaluates a single model on all the tasks."""

    def evaluate_model(self, model: Model, max_targets=None):
        global_results = {}
        for benchmark in self.benchmarks:
            global_results[benchmark.name] = benchmark.evaluate(model, max_targets)
        return {model.model_name: global_results}

    def generate_concise_results(self, results: dict):
        concise_results = {}

        for model in results.keys():
            concise_results[model] = {}
            for benchmark in results[model]:
                concise_results[model][benchmark] = results[model][benchmark][0]
        return concise_results

    def save_results(self, results, directory="./results"):
        for model in results.keys():
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                print(f" Impossible de créer le répertoire {directory} : {e}")
            safe_model = model.replace("/", "_")
            filepath = os.path.join(directory, safe_model + ".json")
            try:
                with open(filepath, "w") as file:
                    json.dump(results[model], file)
            except Exception as e:
                print(f" Impossible de sauvegarder {filepath} : {e}")