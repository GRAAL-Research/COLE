from random import randint

from archives.Models.Model import Model

from constants import BenchSuites


class ExampleModel(Model):

    def infer(self, prompt: str, conditions=None) -> str:
        answer = randint(0,1)
        print(f"now guessing for : {prompt[0:20]} ... {prompt[-20:]} , my answer is {answer}" )
        return f"{answer}"


Colle = BenchSuites.COLLE.value
results = Colle.evaluate_model(model = ExampleModel(model_name="mon_super_ultra_merveilleux_modele"),max_targets=5)

Colle.save_results(results)
