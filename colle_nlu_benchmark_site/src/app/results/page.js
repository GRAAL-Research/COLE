"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function ResultsDefaultPage() {
  const router = useRouter();

  useEffect(() => {
    const savedFile = localStorage.getItem("last_result_file");
    if (savedFile) {
      const id = savedFile.replace(".json", "");
      router.push(`/results/${id}`);
    }
  }, [router]);

  return (
    <main className="max-w-2xl mx-auto px-6 py-12 text-center">
      <h1 className="text-3xl font-bold text-blue-700 mb-4">No Results Yet</h1>
      <p className="text-gray-700">
        Please submit a ZIP file to generate benchmark results.
      </p>
    </main>
  );
}
