#!/usr/bin/env bash
# Re-run fquad, piaf and wsd for API models, one model at a time (see docs/relance-fquad-piaf-wsd.md).
#
# Usage:
#   scripts/relance_fquad_piaf_wsd.sh [model_identifier ...]
#
# Environment (never printed):
#   MAX_EXAMPLES  optional; limits examples per task (smoke test: 20)
#   RUN_DIR       output directory (default: runs/relance-fquad-piaf-wsd)
#   TASKS_GROUP   task group of the CLI (default: cole)
#   API keys and WANDB_*/HF_TOKEN must already be exported or present in ./.env of the repo root.
#
# Resumable: a model whose metrics file already contains fquad, piaf and wsd is skipped.
# Delete its file in $RUN_DIR/results to force a re-run.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="${RUN_DIR:-$REPO_ROOT/runs/relance-fquad-piaf-wsd}"
TASKS_GROUP="${TASKS_GROUP:-cole}"
TASKS="fquad,piaf,wsd"

DEFAULT_MODELS=(
  "pixtral-large-latest"
  "mistral-large-latest"
  "claude-opus-4-20250514"
  "o3-2025-04-16"
  "o1-2024-12-17"
  "gpt-4.1-2025-04-14"
  "gpt-4o-2024-08-06"
  "grok-3-latest"
  "grok-3-fast-latest"
  "google/gemini-2.5-flash"
  "command-r7b-12-2024"
)
if [ "$#" -gt 0 ]; then
  MODELS=("$@")
else
  MODELS=("${DEFAULT_MODELS[@]}")
fi

mkdir -p "$RUN_DIR/logs" "$RUN_DIR/results"
# The pipeline loads ".env" from its working directory.
if [ -f "$REPO_ROOT/.env" ] && [ ! -e "$RUN_DIR/.env" ]; then
  ln -s "$REPO_ROOT/.env" "$RUN_DIR/.env"
fi
export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"

has_all_tasks() {
  grep -q '"fquad"' "$1" && grep -q '"piaf"' "$1" && grep -q '"wsd"' "$1"
}

failed=()
for model in "${MODELS[@]}"; do
  safe_name="${model//\//_}"
  metrics_file="$RUN_DIR/results/${safe_name}_metrics.json"
  log_file="$RUN_DIR/logs/${safe_name}.log"

  if [ -f "$metrics_file" ] && has_all_tasks "$metrics_file"; then
    echo "[skip] $model (metrics already present)"
    continue
  fi

  echo "[run ] $model (log: $log_file)"
  args=(--models_name "$model" --tasks_group "$TASKS_GROUP" --tasks "$TASKS")
  if [ -n "${MAX_EXAMPLES:-}" ]; then
    args+=(--max_examples "$MAX_EXAMPLES")
  fi
  if ! (cd "$RUN_DIR" && python -m cole.evaluation.evaluation_pipeline_private_llm "${args[@]}") \
    >>"$log_file" 2>&1; then
    echo "[fail] $model (see log)"
    failed+=("$model")
    continue
  fi
  # The pipeline catches per-model errors and exits 0, and the NA guard drops a task from the
  # metrics: detect both from the metrics file.
  if [ ! -f "$metrics_file" ] || ! has_all_tasks "$metrics_file"; then
    echo "[fail] $model (metrics missing or incomplete, see log)"
    failed+=("$model")
  fi
done

if [ "${#failed[@]}" -gt 0 ]; then
  echo "Failed models: ${failed[*]}"
  exit 1
fi
echo "Done. Metrics in $RUN_DIR/results"
