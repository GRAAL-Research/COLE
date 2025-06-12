import json
import os
from enum import Enum
from pathlib import Path
from unittest import case
from xxsubtype import bench

from sympy.strategies.core import switch

from src.Utils import create_directory


class Format(Enum):
    FULL=0
    CONCISE=1
    INFERENCE_ONLY = 2


class BenchmarkResult:
    DEFAULT_DIRECTORY = "./results"
    def __init__(self, golds, preds, bench, metrics,tested_model):
        self.golds : list = golds
        self.preds : list = preds
        self.bench : str = bench
        self.tested_model : str = tested_model
        self.metrics : dict = metrics
    def __str__(self):
        return self.format(Format.FULL)

    def format(self, format_type: Format):

        match format_type:
            case Format.FULL:
                return self.as_full()
            case Format.CONCISE:
                pass
            case Format.INFERENCE_ONLY:
                return self.as_inference_only()
    def as_inference_only(self):
        lines = []
        for idx,infered in enumerate(self.preds):
            line = {idx: infered}
            lines.append(line)
        return lines
    def as_full(self):
        return str(self.golds) + str(self.preds) + str(self.bench) + str(self.metrics)

    def add_pair(self,gold,pred):
        self.golds.append(gold)
        self.preds.append(pred)

    def save(self, format_type = Format.FULL, directory = DEFAULT_DIRECTORY):
        create_directory(directory)
        safe_model = self.tested_model.replace("/", "_")
        filepath = os.path.join(directory, safe_model)
        create_directory(filepath)
        benchmark_path = os.path.join(filepath, self.bench + ".jsonl")
        with open(benchmark_path, "w") as file:
            data = self.format(Format.INFERENCE_ONLY)
            print(data)
            file.writelines(json.dumps(r) + "\n" for r in data)
    @staticmethod
    def get_infered_from_inference_only(file):
        file_path = Path(file)
        filename_without_ext = file_path.stem  # 'file'
        parent_dir_name = file_path.parent.name  # 'your'
        return BenchmarkResult(bench=filename_without_ext,tested_model=parent_dir_name,metrics=None)