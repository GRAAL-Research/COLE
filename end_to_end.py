import random

from Benchmarks import FrColaBench
from Model import Model

bench = FrColaBench(used_split="train")
result = bench.evaluate(Model("random_0_1", lambda prompt : random.choice([0,1])))
print(result)