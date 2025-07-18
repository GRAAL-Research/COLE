//submitforum
 "use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import BigBlueButton from "./BigBlueButton";
import ErrorMessage from "./ErrorMessage";
import {BACKEND_ADDRESS} from "@/app/resources/ResourcesPaths";

export default function SubmitForm() {
  const router = useRouter();
  const [requiredVisible, setRequiredVisible] = useState(false);
  const [email, setEmail] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [file, setFile] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const submitResults = async () => {
    if (!email || !displayName || !file) {
      setRequiredVisible(true);
      return;
    }
    if (!file.name.toLowerCase().endsWith(".zip")) {
      alert("Please upload a ZIP (.zip) file.");
      return;
    }
    setRequiredVisible(false);
    setIsSubmitting(true);

    const formData = new FormData();
    formData.append("email", email);
    formData.append("display_name", displayName);
    formData.append("predictions_zip", file);

    try {
      const res = await fetch(`${BACKEND_ADDRESS}/submit`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => null);
        throw new Error(err?.detail || `HTTP ${res.status}`);
      }
      const json = await res.json();
      const submissionId = json.submission_id;

      localStorage.setItem("last_result_file", `${submissionId}.json`);
      localStorage.setItem("just_submitted", "true");
      router.push(`/results/${submissionId}`);
    } catch (err) {
      alert("Error while submitting: " + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 bg-white rounded-xl shadow-md p-6 w-full max-w-xl mx-auto border border-gray-200">
      <h2 className="text-2xl font-semibold text-gray-800 text-center">
        Submit Your Results
      </h2>

      <div className="space-y-2">
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          Your Email
        </label>
        <input
          id="email" type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border border-gray-300 p-3 rounded-md w-full focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="displayname" className="block text-sm font-medium text-gray-700">
          Display Name
        </label>
        <input
          id="displayname" type="text"
          placeholder="Leaderboard Name"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          className="border border-gray-300 p-3 rounded-md w-full focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="zipfile" className="block text-sm font-medium text-gray-700">
          Predictions ZIP
        </label>
        <input
          id="zipfile" type="file" accept=".zip"
          onChange={handleFileChange}
          className="border border-gray-300 p-2 rounded-md w-full focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <ErrorMessage condition={requiredVisible}>
        ⚠️ Email, display name & ZIP are required.
      </ErrorMessage>

      <BigBlueButton onClick={submitResults} disabled={isSubmitting}>
        {isSubmitting ? "Submitting..." : "Submit Your Results"}
      </BigBlueButton>
    </div>
  );
}
