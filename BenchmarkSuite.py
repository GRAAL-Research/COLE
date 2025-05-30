from Benchmark import Benchmark
from Model import Model


class Benchmark_suite():
    def __init__(self, models: list[Model] = None, benchmarks: list[Benchmark] = None):
        self.models = models if models is not None else []
        self.benchmarks = benchmarks if benchmarks is not None else []

    def compute_all(self):
        global_results = {}
        for model in self.models:
            results_per_model = {}
            for benchmark in self.benchmarks:
                results_per_model[benchmark.name] = benchmark.evaluate(model)
            global_results[model.model_name] = results_per_model
        return global_results

    """Computes results by using a model for each benchmark, if you want to evaluate only 1 model for each benchmark, use evaluate_model instead"""

    def compute_1_model_per_bench_model(self):
        global_results = {}
        for idx, benchmark in enumerate(self.benchmarks):
            if self.models[idx] is not None:
                model = self.models[idx]
                global_results[benchmark.name] = benchmark.evaluate(model)
            else:
                global_results[benchmark.name] = "(no model)"
        return global_results

    """Evaluates a single model on all the tasks."""
    def evaluate_model(self, model: Model):
        global_results = {}
        for benchmark in self.benchmarks:
            global_results[benchmark.name] = benchmark.evaluate(model)
        return global_results
