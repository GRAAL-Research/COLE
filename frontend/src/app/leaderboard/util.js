export const normalizeBenchmarkName = (name) => {
  const parts = name.toLowerCase().split("|");
  if (parts.length >= 2) return parts[1].replace("-", "_");
  return name.toLowerCase();
};

export const computeAverageScore = (entry) => {
  const allowedMetrics = ["acc", "f1", "pearson", "spearman"];

  const values = Object.entries(entry.results || {})
    .flatMap(([name, scoreObj]) =>
      Object.entries(scoreObj)
        .filter(([metric]) => allowedMetrics.includes(metric.toLowerCase()))
        .map(([_, value]) => value)
    )
    .filter((v) => typeof v === "number");

  if (values.length === 0) return null;

  const sum = values.reduce((acc, v) => acc + v, 0);
  return sum / values.length;
};

export const computeRankedEntries = (data) => {
  return data
    .map((entry) => ({
      ...entry,
      score: computeAverageScore(entry),
    }))
    .sort((a, b) => (b.score ?? -Infinity) - (a.score ?? -Infinity))
    .map((entry, index) => ({
      ...entry,
      rank: index + 1,
    }));
};
