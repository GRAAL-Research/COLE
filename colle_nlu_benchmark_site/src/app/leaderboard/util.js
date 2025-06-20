export const computeAverageScore = (entry) => {
  const values = Object.values(entry.results || {}).flatMap((scoreObj) =>
    Object.values(scoreObj).filter((v) => typeof v === "number")
  );

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
