
export const normalizeBenchmarkName = (name) => {
  const parts = name.toLowerCase().split("|");
  if (parts.length >= 2) return parts[1].replace(/-/g, "_");
  return name.toLowerCase();
};

export const computeAverageScore = (entry) => {
  const allowedMetrics = [
    "acc",
    "accuracy",
    "f1",
    "exact_match",
    "fquad",
    "pearson",
    "pearsonr",
    "spearman",
  ];

  const perTaskAverages = [];

  Object.values(entry.results || {}).forEach((taskData) => {
    if (taskData && typeof taskData === "object") {
      Object.values(taskData).forEach((metricGroup) => {
        if (metricGroup && typeof metricGroup === "object") {
          const taskMetrics = Object.entries(metricGroup)
            .filter(([metric]) => allowedMetrics.includes(metric.toLowerCase()))
            .map(([, value]) =>
              typeof value === "number" ? value : null
            )
            .filter((v) => v !== null);

          if (taskMetrics.length > 0) {
            const normalized = taskMetrics.map((v) => v > 1 ? v / 100 : v);
            const taskAvg = normalized.reduce((a, b) => a + b, 0) / normalized.length;
            perTaskAverages.push(taskAvg);
          }
        }
      });
    }
  });

  if (perTaskAverages.length === 0) return null;

  return perTaskAverages.reduce((a, b) => a + b, 0) / perTaskAverages.length;
};


const BRAND_NAMES = {
  gpt: "GPT",
  chatgpt: "ChatGPT",
  claude: "Claude",
  opus: "Opus",
  sonnet: "Sonnet",
  haiku: "Haiku",
  fable: "Fable",
  gemini: "Gemini",
  gemma: "Gemma",
  llama: "Llama",
  mistral: "Mistral",
  mixtral: "Mixtral",
  qwen: "Qwen",
  deepseek: "DeepSeek",
  phi: "Phi",
  camembert: "CamemBERT",
  flaubert: "FlauBERT",
  bert: "BERT",
  roberta: "RoBERTa",
  command: "Command",
  aya: "Aya",
  expanse: "Expanse",
  plus: "Plus",
  instruct: "Instruct",
  chat: "Chat",
};

// Turn a raw submitted model name ("openai/gpt-4o", "claude-opus-4-5")
// into its usual display name ("GPT-4o", "Claude Opus 4.5").
export const prettifyModelName = (name) => {
  if (!name || typeof name !== "string") return name;
  const base = name.trim().split("/").pop();
  const tokens = base.split(/[-_\s]+/).filter(Boolean);
  const isClaude = tokens[0]?.toLowerCase() === "claude";

  const mapped = tokens.map(
    (tok) =>
      BRAND_NAMES[tok.toLowerCase()] ??
      (/^[a-z]$/.test(tok) ? tok.toUpperCase() : tok)
  );
  if (!isClaude) return mapped.join(mapped[0] === "GPT" ? "-" : " ");

  // Claude: "Claude 3 Opus", "Claude Opus 4.5" (consecutive digits -> "4.5").
  const out = [];
  mapped.forEach((tok) => {
    const prev = out[out.length - 1];
    if (/^\d{1,2}$/.test(tok) && /^\d+(\.\d+)?$/.test(prev ?? "")) {
      out[out.length - 1] = `${prev}.${tok}`;
    } else {
      out.push(tok);
    }
  });
  return out.join(" ");
};

// Short task name for column headers: "FQuAD - French Question ..." -> "FQuAD".
export const shortTaskName = (title) =>
  title.split(/\s+[-–]\s+|\s*:\s+/)[0].trim();
