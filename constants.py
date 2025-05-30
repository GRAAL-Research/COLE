from enum import Enum

from Model import Model


COLLE_HUGGING_FACE = "COLLE-Graal/ColleGraal"

class Models(Enum):
    GPT_o1 = Model("Gpt-o1",lambda prompt : "1")

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
