from enum import Enum

from BenchmarkSuite import BenchmarkSuite
from Benchmarks import FrColaBench, Paws_xBench, SickfrBench, Opus_parcusBench, PiafBench, XnliBench, Sts22Bench
from colle.src.Models.HuggingFaceModel import HFLLMModel


COLLE_HUGGING_FACE = "COLLE-Graal/ColleGraal"

class BenchSuites(Enum):
    COLLE = BenchmarkSuite(suite_name="COLLE",
        benchmarks=[FrColaBench(),Paws_xBench(),SickfrBench(),Opus_parcusBench(),PiafBench(),XnliBench(),Sts22Bench()],
        models=[HFLLMModel("microsoft/DialoGPT-small")],
    )