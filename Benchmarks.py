import random

import Metrics
from Benchmark import Benchmark
from PromptBuilder import PromptBuilder


class FrColaBench(Benchmark):

    def build_prompt(self, test) ->str:
        prompt =  (PromptBuilder().
                add_premise("Juge si cette phrase est grammaticalement correcte :")
                .add_data(test["sentence"])
                .add_end("Réponds avec seulement 1 si la phrase est grammaticalement correcte, 0 sinon.").build())

        return prompt

    def get_gold_label(self, test):
        return test["label"]

    def parse_answer(self, answer):
        return answer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "frcola"

        self.prompt_instructions = "Answer with 1 if the sentence is correct, 0 otherwise "
        self.metrics = [Metrics.MatthewsCC()]


class AllocineBench(Benchmark):
    def build_prompt(self, test) -> str:
        prompt = (PromptBuilder()
                  .add_premise("Cette phrase possède-t-elle un sentiment positif ou négatif ?")
                  .add_data(test["review"])
                  .add_end(("Réponds "
             "uniquement par 1 si la phrase est positive,réponds par 0 sinon.")))
        return prompt


    def get_gold_label(self, test):
        return test["label"]

    def parse_answer(self, answer):
        return int(answer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "Allocine"
        self.prompt_instructions = \
            ("Dis-moi si la phrase précédente est positive, réponds "
             "uniquement par 1 si la phrase est positive, 0 sinon.")
        self.metrics = [Metrics.Accuracy()]



#TODO
class fquadBench(Benchmark):
    def build_prompt(self, test) -> str:
        print("FQUAD in developpement")
        prompt = (PromptBuilder()
                  .add_premise("")
                  .add_data()
                  .add_end(""))
        return prompt

    def gather_test_data(self, test):
        data = f""
        # TODO

    def get_gold_label(self, test):
        is_impossible = test["is_impossible"]
        return 1 if not is_impossible else 0

    def parse_answer(self, answer):
        return int(answer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "fquad"
        self.prompt_instructions = (
            "Réponds par 1 si tu peux répondre à la question uniquement à partir du contexte, 0 sinon.")

        self.metrics = [
            Metrics.MetricCollection([Metrics.Pearson(), Metrics.SpearmanR()]),
        ]
class frblimpBench(Benchmark):

    def build_prompt(self, test) -> str:
        if self.get_0_1_seeded(test) == 1:
            data = test["grammatical"]
        else:
            data = test["ungrammatical"]
        prompt = (PromptBuilder()
                  .add_premise("Cette phrase est-elle grammaticalement correcte ?")
                  .add_data(data)
                  .add_end("Réponds strictement par 1 si la phrase est correcte grammaticalement ; sinon, réponds 0."))
        return prompt

    def get_0_1_seeded(self, test):
        return (self.seed + test["id"] ^ 2 * 7) % 2

    def get_gold_label(self, test):
        return self.get_0_1_seeded(test)

    def parse_answer(self, answer):
        return int(answer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "fr_blimp"
        self.seed = random.randint(1, 10000)
        self.metrics=[Metrics.Accuracy()]


class gqnliBench(Benchmark):
    def build_prompt(self, test) -> str:
        prompt = (PromptBuilder()
                  .add_premise("Quelle est la relation de la deuxième phrase par rapport à la première ?")
                  .add_data(test["premise"]).add_data(test["hypothesis"])
                  .add_end("Réponds uniquement par :\n"
         "0 — si la deuxième phrase implique la première,\n"
         "1 — si la relation est neutre,\n"
         "2 — s'il y a contradiction.\n"
         "Réponds uniquement par 0, 1 ou 2."))
        return prompt

    def get_gold_label(self, test):
        return test["label"]

    def parse_answer(self, answer):
        return int(answer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "gqnli"

        self.prompt_instructions = ("Donne moi la relation entre la prémise et l'hypothèse,"
                                    "Réponds seulement 0 pour une implication, 1 pour une relation neutre"
                                    "et 2 pour une contradiction.Réponds seulement avec 0, 1 ou 2")
        self.metrics = [Metrics.Accuracy()]


class opus_parcusBench(Benchmark):
    def build_prompt(self, test) -> str:
        prompt = (PromptBuilder()
                  .add_premise("")
                  .add_data()
                  .add_end(""))
        return prompt
    def gather_test_data(self, test):
        sent1 = test["sent1"]
        sent2 = test["sent2"]
        return f"{sent1} {sent2}"

    def get_gold_label(self, test):
        return test["quality"]

    def parse_answer(self, answer):
        return int(answer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "opus_parcus"
        self.prompt_instructions = "TODO"
        self.metrics = [
            Metrics.MetricCollection([Metrics.Accuracy(), Metrics.F1()]),
        ]



class paws_xBench(Benchmark):
    def build_prompt(self, test) -> str:
        prompt = (PromptBuilder()
                  .add_premise("")
                  .add_data()
                  .add_end(""))
        return prompt
    def gather_test_data(self, test):
        sentence1 = test["sentence1"]
        sentence2 = test["sentence2"]
        return f"{sentence1} {sentence2}"

    def get_gold_label(self, test):
        return test["label"]

    def parse_answer(self, answer):
        return int(answer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "paws_x"
        self.prompt_instructions = ""
        self.metrics = [Metrics.Accuracy()]


class piafBench(Benchmark):
    def build_prompt(self, test) -> str:
        prompt = (PromptBuilder()
                  .add_premise("")
                  .add_data()
                  .add_end(""))
        return prompt
    def gather_test_data(self, test):
        context = test["context"]
        question = test["question"]
        return f"{context} {question}"

    def get_gold_label(self, test):
        return test["answer_start"][0]

    def parse_answer(self, answer):
        return int(answer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "piaf"
        self.prompt_instructions = ""
        self.metrics = [
            Metrics.MetricCollection([Metrics.Pearson(), Metrics.SpearmanR()]),
        ]


class sickfrBench(Benchmark):
    def build_prompt(self, test) -> str:
        prompt = (PromptBuilder()
                  .add_premise("")
                  .add_data()
                  .add_end(""))
        return prompt
    def gather_test_data(self, test):
        sentence_A = test["sentence_A"]
        sentence_B = test["sentence_B"]
        return f"{sentence_A} {sentence_B}"

    def get_gold_label(self, test):
        return test["relatedness_score"]

    def parse_answer(self, answer):
        return float(answer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "sickfr"
        self.prompt_instructions = ""
        self.metrics = [
            Metrics.MetricCollection([Metrics.Pearson(), Metrics.SpearmanR()]),
        ]


class XnliBench(Benchmark):
    def build_prompt(self, test) -> str:
        prompt = (PromptBuilder()
                  .add_premise("")
                  .add_data()
                  .add_end(""))
        return prompt
    def gather_test_data(self, test):
        premise = test["premise"]
        hypothesis = test["hypothesis"]
        return f"{premise} {hypothesis}"

    def get_gold_label(self, test):
        return test["label"]

    def parse_answer(self, answer):
        return int(answer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "Xnli"
        self.prompt_instructions = ""
        self.metrics = [Metrics.Accuracy()]
class sts22(Benchmark):
    def gather_test_data(self, test):
        sentence1 = test["sentence1"]
        sentence2 = test["sentence2"]
        return f"{sentence1} {sentence2}"

    def get_gold_label(self, test):
        return test["score"]

    def parse_answer(self, answer):
        return int(answer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "sts22_crosslingual"
        self.prompt_instructions = ""
        self.metrics = [
            Metrics.MetricCollection([Metrics.Pearson(), Metrics.SpearmanR()]),
        ]
