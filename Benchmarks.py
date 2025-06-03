import random
import re

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

    def gather_test_data(self, test):
        return test["sentence"]

    def get_gold_label(self, test):
        return test["label"]

    def parse_answer(self, answer):
        match = re.search(r'\b[01]\b', answer)
        if match:
            return int(match.group())

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
             "uniquement par 1 si la phrase est positive,réponds par 0 sinon."))
             .build())
        return prompt


    def get_gold_label(self, test):
        return test["label"]

    def gather_test_data(self, test):
        return test["review"]
    def parse_answer(self, answer):
        match = re.search(r"\b[01]\b", answer)
        if match:
            return int(match.group())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "Allocine"
        self.metrics = [Metrics.Accuracy()]



#TODO
class FquadBench(Benchmark):
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
class FrblimpBench(Benchmark):

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


class GqnliBench(Benchmark):
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

        self.metrics = [Metrics.Accuracy()]


class Opus_parcusBench(Benchmark):
    def build_prompt(self, test) -> str:
        sent1 = test["sent1"]
        sent2 = test["sent2"]
        prompt = (PromptBuilder()
                  .add_premise("Les deux phrases suivantes expriment-elles la même idée ou sont-elles différentes ?")
                  .add_data(sent1).add_data(sent2)
                  .add_end("Réponds seulement avec un chiffre de 0 à 5 où 5"
                           " signifie que les deux phrases veulent dire exactement la même chose."))
        return prompt


    def get_gold_label(self, test):
        return test["quality"] # Ou test["annot-score"]

    def parse_answer(self, answer):
        return int(answer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "opus_parcus"
        self.metrics = [
            Metrics.MetricCollection([Metrics.Accuracy(), Metrics.F1()]),
        ]




class Paws_xBench(Benchmark):
    def build_prompt(self, test) -> str:
        sentence1 = test["sentence1"]
        sentence2 = test["sentence2"]
        prompt = (PromptBuilder()
                  .add_premise("Les deux phrases suivantes veulent-elles dire la même chose, ou ont-elles des significations différentes ?")
                  .add_data(sentence1).add_data(sentence2)
                  .add_end("Réponds seulement 1 si les deux phrases ont la même signification, 0 sinon")
                  .build())
        return prompt

    def get_gold_label(self, test):
        return test["label"]

    def gather_test_data(self, test):
        return f"{test['sentence1']}  /  {test['sentence2']}"
    def parse_answer(self, answer):
        match = re.search(r"\b[01]\b", answer)
        if match:
            return int(match.group())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "paws_x"

        self.metrics = [Metrics.Accuracy()]


class PiafBench(Benchmark):
    def build_prompt(self, test) -> str:
        context = test["context"]
        question = test["question"]
        prompt = (PromptBuilder()
                  .add_premise(
            "Voici une question et un contexte. Où, dans le texte, commence la réponse à la question ?")
                  .add_data(f"Question : {question}")
                  .add_data(f"Contexte : {context}")
                  .add_end("Réponds seulement avec le **nombre de mots** qui précèdent la réponse à la question dans le contexte."))
        return prompt

    def get_gold_label(self, test):
        return test["answer_start"][0]

    def parse_answer(self, answer):
        return int(answer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "piaf"

        self.metrics = [
            Metrics.MetricCollection([Metrics.Pearson(), Metrics.SpearmanR()]),
        ]


class SickfrBench(Benchmark):
    def build_prompt(self, test) -> str:
        sentence_A = test["sentence_A"]
        sentence_B = test["sentence_B"]
        prompt = (PromptBuilder()
                  .add_premise("À quel point, de 0 à 5, les 2 phrases suivantes sont-elles similaires ?")
                  .add_data(sentence_A).add_data(sentence_B)
                  .add_end("Réponds avec seulement un nombre de 0 à 5, où 5 signifie une très grande similarité entre les phrases."))
        return prompt


    def get_gold_label(self, test):
        return test["relatedness_score"]

    def parse_answer(self, answer):
        return float(answer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "sickfr"

        self.metrics = [
            Metrics.MetricCollection([Metrics.Pearson(), Metrics.SpearmanR()]),
        ]


class XnliBench(Benchmark):
    def build_prompt(self, test) -> str:
        prompt = (PromptBuilder()
                  .add_premise("Quelle est la relation de la deuxième phrase par rapport à la première ?")
                  .add_data(test["premise"]).add_data(test["hypothesis"])
                  .add_end("Réponds uniquement par :\n"
         "0 — si la deuxième phrase implique la première,\n"
         "1 — si la relation est neutre,\n"
         "2 — s'il y a contradiction.\n"
         "Réponds uniquement par 0, 1 ou 2.")
        .build())
        return prompt

    def get_gold_label(self, test):
        return test["label"]
    def gather_test_data(self, test):
        return f"{test['premise']}  /  {test['hypothesis']}"
    def parse_answer(self, answer):
        match = re.search(r"\b[0-2]\b", answer)
        if match:
            return int(match.group())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "Xnli"
        self.metrics = [Metrics.Accuracy()]

class Sts22(Benchmark):
    def build_prompt(self, test) -> str:
        prompt = (PromptBuilder()
                  .add_premise("En scorant de 0 à 5, à quel point les phrases suivants sont-elles similaires ?")
                  .add_data(test["sentence1"])
                  .add_data(test["sentence2"])
                  .add_end("Réponds seulement avec un nombre de 0 à 5, où 5 signifie que les 2 phrases veulent dire exactement la même chose."))
        return prompt.build()

    def get_gold_label(self, test):
        return test["score"]
    def gather_test_data(self, test):
        return f"{test['sentence1']}  /  {test['sentence2']}"
    def parse_answer(self, answer):
        match = re.search(r"\b[0-5]\b", answer)
        if match:
            return int(match.group())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "sts22_crosslingual"
        self.metrics = [
            Metrics.MetricCollection([Metrics.Pearson(), Metrics.SpearmanR()]),
        ]
