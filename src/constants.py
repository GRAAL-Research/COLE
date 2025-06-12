from enum import Enum

from BenchmarkSuite import BenchmarkSuite
from Benchmarks import FrColaBench, Paws_xBench, SickfrBench, Opus_parcusBench, PiafBench, XnliBench, Sts22Bench
from Models.HuggingFaceModel import HFLLMModel
from src.Benchmarks import AllocineBench

DATASETS = ["Allocine", "paws_x", "fquad", "opus_parcus", "gqnli", "multiblimp", "piaf", "sickfr", "Xnli"]

COLLE_HUGGING_FACE = "COLLE-Graal/ColleGraal"

class BenchSuites(Enum):
    COLLE = BenchmarkSuite(suite_name="COLLE",
        benchmarks=[AllocineBench(),FrColaBench(),Paws_xBench(),SickfrBench(),Opus_parcusBench(),PiafBench(),XnliBench(),Sts22Bench()],
        models=[HFLLMModel("microsoft/DialoGPT-small")],
    )