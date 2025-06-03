import random
from Benchmarks import FrColaBench
from Metrics import Accuracy, MatthewsCC
from Model import Model, make_claude_inference

bench = FrColaBench(used_split="test")
result = bench.evaluate(Model("random_0_1", lambda prompt: str(random.choice([0, 1]))))
print("Résultat modèle aléatoire:", result)

# Modèle Claude
claude_infer = make_claude_inference("claude-opus-4-20250514")
model = Model("claude-opus-4-20250514", claude_infer)

bench = FrColaBench(used_split="test")
dataset = bench.load_dataset()["test"]


sampled_tests = random.sample(list(dataset), 10)

gold_labels = []
predictions = []

print("\n--- Évaluation Claude sur 10 exemples aléatoires ---\n")
for idx, test in enumerate(sampled_tests):
    prompt = bench.build_prompt(test)
    prediction = model.infer(prompt)
    parsed_prediction = bench.parse_answer(prediction)
    gold_label = bench.get_gold_label(test)

    gold_labels.append(gold_label)
    predictions.append(parsed_prediction)

    print(f"Exemple {idx + 1}:")
    print(f"Phrase: {bench.gather_test_data(test)}")
    print(f"Prédiction: {parsed_prediction}")
    print(f"Gold Label: {gold_label}\n")

matthews = MatthewsCC()
mcc_score = matthews.compute(gold_labels, predictions)
print(f"✅ mcc_score sur les 10 exemples aléatoires : {mcc_score :.2f}%")
