import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { FileText, Download } from "lucide-react";

const API_BASE = "http://localhost:8000";

const GenerateReportPage = () => {
  const { token } = useAuth();

  const [chatId, setChatId] = useState("");
  const [loading, setLoading] = useState(false);
  const [reportId, setReportId] = useState(null);
  const [summary, setSummary] = useState("");

  const generateReport = async () => {
    if (!chatId.trim()) return;

    setLoading(true);
    setReportId(null);
    setSummary("");

    try {
      const res = await fetch(`${API_BASE}/api/reports/${chatId}/generate`, {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` },
      });

      const data = await res.json();

      if (res.ok) {
        setReportId(data.report_id);
        setSummary(data.summary);
      } else {
        alert(data.detail || "Failed to generate report.");
      }
    } catch (err) {
      console.error(err);
      alert("Something went wrong.");
    }

    setLoading(false);
  };

  const downloadFile = async (format) => {
  try {
    const res = await fetch(`${API_BASE}/api/reports/${reportId}/download?format=${format}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) {
      alert("Failed to download. Unauthorized.");
      return;
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `chat_report_${reportId}.${format}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  } catch (err) {
    console.error(err);
  }
};

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-2xl mx-auto bg-white p-6 rounded-2xl shadow-lg">

        <h2 className="text-2xl font-bold mb-6 text-gray-800 flex items-center">
          <FileText className="w-6 h-6 mr-2 text-indigo-600" />
          Generate Report
        </h2>

        {/* Chat ID Input */}
        <div className="mb-4">
          <label className="block text-gray-700 font-semibold mb-2">
            Enter Chat ID:
          </label>

          <input
            type="text"
            placeholder="Enter Chat ID here..."
            value={chatId}
            onChange={(e) => setChatId(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        {/* Generate Button */}
        <button
          onClick={generateReport}
          disabled={loading}
          className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        >
          {loading ? "Generating..." : "Generate Report"}
        </button>

        {/* Report Output */}
        {reportId && (
          <div className="mt-6 p-4 bg-slate-100 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              Report Generated Successfully
            </h3>

            <p className="text-gray-600 mb-4">{summary}</p>

            <div className="flex space-x-3">
              <button
                onClick={() => downloadFile("pdf")}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center"
              >
                <Download className="w-4 h-4 mr-2" />
                Download PDF
              </button>

              <button
                onClick={() => downloadFile("csv")}
                className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800 flex items-center"
              >
                <Download className="w-4 h-4 mr-2" />
                Download CSV
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default GenerateReportPage;
