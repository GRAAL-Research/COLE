const benchmarks = [
  "Allocine",
  "Xnli",
  "fquad",
  "fr_blimp",
  "frcola",
  "gqnli",
  "opus_parcus",
  "paws_x",
  "piaf"
];

export default function LeaderboardPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-3">
      <h2 className="text-3xl font-bold text-center text-blue-700 border-b pb-4 mb-10">
        Leaderboard
      </h2>
      <table className="table-fixed border-4 border-blue-500 shadow-lg">
        <thead>
          <tr>
            <th className="border-2 border-blue-500 px-4 py-2 bg-blue-100 text-blue-800"></th>
            {benchmarks.map((name, i) => (
              <th
                key={i}
                className="border-2 border-blue-500 px-4 py-2 text-sm bg-blue-100 text-blue-800"
              >
                {name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {[...Array(10)].map((_, rowIndex) => (
            <tr key={rowIndex}>
              <td className="border-2 border-blue-400 px-4 py-2 text-center font-semibold bg-gray-50">

              </td>
              {[...Array(9)].map((_, colIndex) => (
                <td
                  key={colIndex}
                  className="border-2 border-blue-400 px-4 py-2 text-center"
                >

                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}