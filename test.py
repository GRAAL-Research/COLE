#!/usr/bin/env python3
# evaluate.py

import os
import json
import argparse
from sklearn.metrics import accuracy_score, f1_score, matthews_corrcoef
from scipy.stats import pearsonr, spearmanr





ACCURACY_ONLY    = {"allocine", "fquad", "gqnli", "xnli", "piaf", "multiblimp","fr_blimp"}
ACCURACY_F1      = {"paws_x", "opus_parcus"}
PEARSON_SPEARMAN = {"sickfr"}
MAATHIEWS = {"frcola"}

def load_preds(preds_dir, task, split):
    fn = os.path.join(preds_dir, f"{task}_{split}_preds.json")
    if not os.path.isfile(fn):
        raise FileNotFoundError(f"No pred file: {fn}")
    with open(fn, "r", encoding="utf-8") as f:
        data = json.load(f)
    # si c'est un dict index→pred
    if isinstance(data, dict):
        return [v for _, v in sorted(data.items(), key=lambda kv: int(kv[0]))]
    return data

def main():
    p = argparse.ArgumentParser(description="Eval on local Benchmarks/data JSONL")
    p.add_argument("-p", "--preds_dir", required=True,
                   help="Folder with <task>_<split>_preds.json")
    p.add_argument("-t", "--tasks", nargs="+", required=True,
                   help="Tasks to eval (must match sub‑folder names, lowercase)")
    p.add_argument("-s", "--splits", nargs="+", default=["validation","test"],
                   help="Splits to eval")
    p.add_argument("-o", "--output", help="Write metrics to JSON file")
    args = p.parse_args()

    results = {}
    base = os.path.join("Benchmarks", "data")

    for task in args.tasks:
        results[task] = {}
        task_dir = os.path.join(base, task)
        for split in args.splits:
            jsonl = os.path.join(task_dir, f"{task}_{split}.jsonl")
            if not os.path.isfile(jsonl):
                print(f"[SKIP] no data for {task}/{split}")
                continue

            golds = []
            with open(jsonl, encoding="utf-8") as fh:
                for line in fh:
                    obj = json.loads(line)
                    golds.append(obj.get("label", obj.get("hasAns")))

            try:
                preds = load_preds(args.preds_dir, task, split)
            except FileNotFoundError:
                print(f"[SKIP] no preds for {task}/{split}")
                continue

            if len(preds) != len(golds):
                print(f"[ERROR] length mismatch {task}/{split}")
                continue


            if task in ACCURACY_ONLY:
                m = {"accuracy": accuracy_score(golds, preds)}

            elif task in ACCURACY_F1:
                m = {
                    "accuracy": accuracy_score(golds, preds),
                    "f1_micro": f1_score(golds, preds, average="micro")
                }

            elif task in PEARSON_SPEARMAN:
                m = {
                    "pearson_r":  pearsonr(golds, preds)[0],
                    "spearman_r": spearmanr(golds, preds)[0]
                }
            elif task in MAATHIEWS:
                m = {
                    "matthews_correlation": matthews_corrcoef(golds, preds),

                }

            else:
                m = {
                    "accuracy":    accuracy_score(golds, preds),
                    "f1_micro":    f1_score(golds, preds, average="micro"),
                    "matthews_cc": matthews_corrcoef(golds, preds),
                    "pearson_r":   pearsonr(golds, preds)[0],
                    "spearman_r":  spearmanr(golds, preds)[0],
                }

            print(f">> {task}/{split} →", m)
            results[task][split] = m

    if args.output:
        with open(args.output, "w", encoding="utf-8") as out:
            json.dump(results, out, indent=2)
        print("Saved results to", args.output)

if __name__ == "__main__":
    main()
