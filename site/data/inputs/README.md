# Inputs that cannot be derived automatically

## size_from_details.json

Model sizes (billions of parameters) for seven entries whose id is not a key of
`predictions/models_size.json`. The values were read by hand from
`predictions/llm_details.csv` (the table of the paper, sizes written as "8B", names in LaTeX
`\texttt{...}`) and matched to the leaderboard ids by model name. The matching is manual:
the CSV uses paper names, the leaderboard uses Hugging Face ids, and no key links them.
Add an entry here when a new model has a size in the CSV but not in `models_size.json`.

## Where the other inputs live

- `cole/backend/results/leaderboard.json`: scores (source of `data/leaderboard-snapshot.json`).
- `predictions/models_size.json`: sizes in parameters, read first.
- `../categories.json`: the skill categories and their tasks (hand-written, versioned here).
- `../article.json`: text of the paper summary shown on the site (hand-written).
