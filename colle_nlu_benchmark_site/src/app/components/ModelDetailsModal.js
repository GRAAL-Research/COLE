"use client";
import Modal from "./Modal";

export default function ModelDetailsModal({ entry, onClose }) {
  const modelName = entry.display_name || entry.name?.replace(".json", "") || "Unknown Model";

  return (
    <Modal onClose={onClose}>
      <div className="space-y-4 max-w-2xl mx-auto">
        {/* En-tête avec nom du modèle */}
        <div className="text-center sticky top-0 bg-white z-10 pb-2">
          <h3 className="text-2xl font-bold text-blue-700">{modelName}</h3>
          <p className="text-sm text-gray-500">Model Details</p>
        </div>

        {/* Contenu des benchmarks */}
        <div className="space-y-4">
          {Object.entries(entry.results || {}).map(([benchmark, metrics]) => (
            <div key={benchmark} className="p-4 border rounded-md bg-white shadow-md">
              <h4 className="text-lg font-medium text-blue-600 mb-2">📊 {benchmark}</h4>
              <ul className="ml-4 text-sm text-gray-700 list-disc">
                {Object.entries(metrics).map(([metric, value]) => (
                  <li key={metric}>
                    <strong>{metric}</strong>: {typeof value === "number" ? value.toFixed(4) : value}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </Modal>
  );
}
