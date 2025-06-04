from enum import Enum

from BenchmarkSuite import BenchmarkSuite
from Benchmarks import FrColaBench, Paws_xBench, SickfrBench, Opus_parcusBench, PiafBench, XnliBench, Sts22Bench
from HuggingFaceModel import HFLLMModel
from Model import Model
import Benchmarks

COLLE_HUGGING_FACE = "COLLE-Graal/ColleGraal"

class BenchSuites(Enum):
    COLLE = BenchmarkSuite(suite_name="COLLE",
        benchmarks=[FrColaBench(),Paws_xBench(),SickfrBench(),Opus_parcusBench(),PiafBench(),XnliBench(),Sts22Bench()],
        models=[HFLLMModel("microsoft/DialoGPT-small")],
    )
#TODO
class Benchmarks(Enum):
    FrCola = None
    FrBlimp = None

#TODO
class Metrics(Enum):
    ACCURACY = None
    F1 = None
    MATTHEWS_COEFF = None
    PEARSON = None


#Colle = BenchSuites.COLLE.value
#Results = Colle.compute_all(5)
#print("Concise Results:")
#print(Colle.generate_concise_results(Results))
