---
title: COLE !
emoji: 🐳
colorFrom: purple
colorTo: gray
sdk: docker
app_port: 7860
---

# COLE: Comprehensive Benchmark for Quebec French Language Understanding Evaluation

[![Website](https://img.shields.io/badge/Website-colebenchmark.org-blue)](https://colebenchmark.org/)
[![Paper](https://img.shields.io/badge/Paper-arXiv%3A2510.05046-b31b1b)](https://arxiv.org/abs/2510.05046)
[![Dataset](https://img.shields.io/badge/Dataset-HuggingFace-ffd21e)](https://huggingface.co/datasets/graalul/COLE-public)
[![Coverage](https://raw.githubusercontent.com/GRAAL-Research/COLE/badges/coverage-badge.svg)](https://github.com/GRAAL-Research/COLE/actions)

**COLE** is a comprehensive benchmark for evaluating Quebec French Natural Language Understanding (NLU). It includes 23 diverse tasks covering sentiment analysis, paraphrase detection, natural language inference, question answering, grammatical judgment, word sense disambiguation, and more — with a particular focus on linguistic phenomena relevant to the French language.

We benchmark 94 large language models (LLMs), providing an extensive analysis of the current state of Quebec French NLU. Our results highlight a significant performance gap between closed- and open-weight models and identify key challenging frontiers such as zero-shot extractive question answering, fine-grained word sense disambiguation, and understanding of regional language variations.

## Links

- **Leaderboard**: [colebenchmark.org](https://colebenchmark.org/)
- **Paper**: [COLE: a Comprehensive Benchmark for Quebec French Language Understanding Evaluation (arXiv:2510.05046)](https://arxiv.org/abs/2510.05046)
- **Dataset**: [HuggingFace — graalul/COLE-public](https://huggingface.co/datasets/graalul/COLE-public)

## Tasks

COLE consists of 23 tasks grouped by NLU capability:

### Sentiment Analysis
| Task | Description | Test size |
|------|-------------|-----------|
| **Allocine** | Sentiment classification of French movie reviews (positive/negative) | 20,000 |
| **MMS-fr** | Sentiment analysis with 3 classes (positive, neutral, negative) | 63,190 |

### Natural Language Inference (NLI)
| Task | Description | Test size |
|------|-------------|-----------|
| **DACCORD** | Semantic plausibility / contradiction detection of French sentences (binary) | 1,034 |
| **FraCaS** | NLI involving quantifiers, plurality, anaphora, and ellipsis | 346 |
| **GQNLI-fr** | NLI with quantifier logic (e.g., most, at least, more than half) | 30 |
| **LingNLI** | NLI corpus constructed with a linguist in the loop | 4,893 |
| **MNLI-nineeleven-Fr-MT** | French machine-translated MNLI using 9/11 context | 2,000 |
| **RTE3-Fr** | French version of RTE3 for textual entailment | 3,121 |
| **SICK-fr** | Sentence pair relatedness and entailment | 4,906 |
| **XNLI-fr** | Cross-lingual NLI in French | 5,010 |

### Question Answering
| Task | Description | Test size |
|------|-------------|-----------|
| **FQuAD** | Extractive QA on high-quality French Wikipedia articles | 400 |
| **Fr-BoolQ** | Boolean question answering in French | 178 |
| **PIAF** | French extractive QA pairs | 384 |

### Paraphrase Detection
| Task | Description | Test size |
|------|-------------|-----------|
| **PAWS-X** | Paraphrase identification from sentence pairs | 2,000 |
| **QFrBLiMP** | Semantic equivalence detection between sentence pairs | 2,290 |

### Grammatical Judgment
| Task | Description | Test size |
|------|-------------|-----------|
| **MultiBLiMP-Fr** | Grammatical correctness from minimal pairs | 77 |
| **QFrCoLA** | Sentence acceptability in French (grammar, syntax) | 7,546 |

### Semantic Similarity
| Task | Description | Test size |
|------|-------------|-----------|
| **STS22** | Document-level similarity of multilingual news articles | 72 |

### Word Sense Disambiguation
| Task | Description | Test size |
|------|-------------|-----------|
| **WSD-Fr** | Disambiguating verb meanings in context | 3,121 |

### Quebec French
| Task | Description | Test size |
|------|-------------|-----------|
| **QFrCoRE** | Matching Quebec French expressions to standard definitions | 4,633 |
| **QFrCoRT** | Matching Quebec French terms to standard definitions | 201 |

### Coreference / Pronoun Resolution
| Task | Description | Test size |
|------|-------------|-----------|
| **Wino-X-LM** | Pronoun resolution with ambiguous referents | 2,793 |
| **Wino-X-MT** | Translation-based pronoun resolution with gendered pronouns | 2,988 |

## Language

All data in COLE is in **French**.

## Evaluating mixed-type question files

Some corpora (e.g. the Netquiz/COLE corpus) store several question types in a single
JSONL file, each row keeping its type in a `question_type` field. Since the right
metric differs from one question to the next, `cole.metrics.mixed_questions` selects
the metric per row and aggregates the results:

```bash
# Predictions embedded in each row's "prediction" field
python -m cole.metrics.mixed_questions gold.jsonl

# Predictions in a separate file aligned line by line, JSON report written out
python -m cole.metrics.mixed_questions gold.jsonl --predictions preds.jsonl --output report.json
```

It reuses COLE's metric primitives and reports a per-type score plus two composite
scores: an unweighted mean of the per-type scores (GLUE-style) and a mean weighted by
the number of instances of each type. Supported types: `single_choice`, `true_false`,
`multiple_choice`, `short_answer`, `association`, `categorization`, `ordering`.
Mathematical `short_answer` rows (flagged via their `subjects`) are scored with
SymPy-based equivalence so answers like `2^5` and `32` or `1/2` and `0.5` match.

## Citation

If you use COLE in your research, please cite our paper:

```bibtex
@article{beauchemin2025cole,
  title={COLE: a Comprehensive Benchmark for Quebec French Language Understanding Evaluation},
  author={Beauchemin, David and Tremblay, Yan and Youssef, Mohamed Amine and Khoury, Richard},
  journal={arXiv preprint arXiv:2510.05046},
  year={2025},
  url={https://arxiv.org/abs/2510.05046}
}
```
