"""Build data/extra.json: chance references, Quebec-specific task class, quiz items (public train/validation splits only)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
models = json.loads((ROOT / "data/models.json").read_text())["models"]
rnd = next(m for m in models if m["id"] == "RandomBaselineModel")
NO_CHANCE = {
    "sickfr": "Pearson correlation: chance is a correlation near 0, not comparable with the baseline's class score",
    "sts22": "Pearson correlation: chance is a correlation near 0, not comparable with the baseline's class score",
}
GENERATION = {"fquad", "piaf", "wsd"}
chance = {}
for t, v in rnd["tasks"].items():
    if t in NO_CHANCE:
        chance[t] = {"value": None, "basis": "n/a", "note": NO_CHANCE[t]}
    else:
        chance[t] = {
            "value": v,
            "basis": "random-generation" if t in GENERATION else "random-baseline",
        }

quiz = [
    {
        "id": "multiblimp",
        "task": "multiblimp",
        "family": {
            "en": "Grammar: which sentence is correct?",
            "fr": "Grammaire : quelle phrase est correcte ?",
        },
        "split": "train",
        "file": "multiblimp/multiblimp_train.jsonl",
        "kind": "choice",
        "labels": [
            {"en": "Sentence 0", "fr": "Phrase 0"},
            {"en": "Sentence 1", "fr": "Phrase 1"},
        ],
        "options": [
            "Cette logique, poursuit-il, suis basée sur les résolutions que le Conseil de sécurité a adoptées depuis 2007 en vertu de lesquelles ce dernier a pris note de les deux propositions.",
            "Cette logique, poursuit-il, est basée sur les résolutions que le Conseil de sécurité a adoptées depuis 2007 en vertu de lesquelles ce dernier a pris note de les deux propositions.",
        ],
        "answer": 1,
        "why": {
            "en": "Sentence 0 uses « suis » where the subject « cette logique » needs « est ». The dataset label (1) marks sentence 1 as the grammatical one.",
            "fr": "La phrase 0 emploie « suis » alors que le sujet « cette logique » demande « est ». L’étiquette du jeu de données (1) désigne la phrase 1 comme correcte.",
        },
    },
    {
        "id": "qfrcola",
        "task": "qfrcola",
        "family": {
            "en": "Quebec acceptability: is the sentence correct?",
            "fr": "Acceptabilité québécoise : la phrase est-elle correcte ?",
        },
        "split": "train",
        "file": "qfrcola/frcola_train.jsonl",
        "kind": "choice",
        "labels": [
            {"en": "Not correct", "fr": "Incorrecte"},
            {"en": "Correct", "fr": "Correcte"},
        ],
        "prompt": "La journée était calme : point de vent, poing de bruit, point de mouvement.",
        "options": None,
        "answer": 0,
        "why": {
            "en": "Label 0 (not correct): « poing » (fist) is the wrong homophone, it should be « point ». The source is a language-advice page of the Office québécois de la langue française.",
            "fr": "Étiquette 0 (incorrecte) : « poing » est le mauvais homophone, il faut « point ». La source est une page de la Vitrine linguistique de l’Office québécois de la langue française.",
        },
    },
    {
        "id": "paws_x",
        "task": "paws_x",
        "family": {
            "en": "Meaning: same thing or not?",
            "fr": "Sens : même chose ou non ?",
        },
        "split": "validation",
        "file": "paws_x/paws_x_fr_validation.jsonl",
        "kind": "choice",
        "labels": [
            {"en": "Different meanings", "fr": "Sens différents"},
            {"en": "Same meaning", "fr": "Même sens"},
        ],
        "prompt": "1. Kathy et son mari Pete Beale (Peter Dean) sont financièrement stables.\n2. Kathy et son mari Peter Dean (Pete Beale) sont stables financièrement.",
        "options": None,
        "answer": 1,
        "why": {
            "en": "Label 1 (same meaning). The two sentences swap the two names between the brackets, which is a trap in this dataset, but the label says they mean the same.",
            "fr": "Étiquette 1 (même sens). Les deux phrases échangent les noms entre parenthèses, ce qui est un piège dans ce jeu de données, mais l’étiquette dit qu’elles ont le même sens.",
        },
    },
    {
        "id": "lingnli",
        "task": "lingnli",
        "family": {
            "en": "Reasoning: what is the relation?",
            "fr": "Raisonnement : quelle relation ?",
        },
        "split": "train",
        "file": "lingnli/lingnli_train.jsonl",
        "kind": "choice",
        "labels": [
            {"en": "Implication", "fr": "Implication"},
            {"en": "Neutral", "fr": "Neutre"},
            {"en": "Contradiction", "fr": "Contradiction"},
        ],
        "prompt": "1. Une grande partie de l’argent donné par la Slate 60 sert à financer de nouveaux bâtiments dans des universités déjà riches.\n2. Les universités riches reçoivent un financement de Slate 60.",
        "options": None,
        "answer": 0,
        "why": {
            "en": "Label 0 in the COLE prompt: implication. Sentence 2 follows from sentence 1.",
            "fr": "Étiquette 0 dans l’invite COLE : implication. La phrase 2 découle de la phrase 1.",
        },
    },
]
extra = {
    "chance": chance,
    "chance_note": "Chance reference = score of the project's own RandomBaselineModel on each task (one seeded run, from the snapshot). It matches 1/k for class tasks (about 50 for two classes, about 33 for three).",
    "quebec_tasks": [
        "qfrcore",
        "qfrcort",
    ],  # same two tests as categories.json "quebec"
    "dataset": {
        "repo": "graalul/COLE-public",
        "splits_checked": "README.md configs of the dataset repository, 2026-11-26",
    },
    "quiz": quiz,
}
(ROOT / "data/extra.json").write_text(json.dumps(extra, ensure_ascii=False, indent=1))
print("ok", len(quiz))
