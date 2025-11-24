
// ===========================
// File: src/components/AnalyticsPage.js
// ===========================

import React, { useEffect, useState } from 'react';
import { TrendingUp, Users, FileText, Zap, Target } from 'lucide-react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useAuth } from '../context/AuthContext';
// import { COLORS, SENTIMENT_COLORS } from '../constants/colors';

const API_BASE = 'http://localhost:8000';
const COLORS = { primary: '#6366f1' };
const SENTIMENT_COLORS = { positive: '#10b981', neutral: '#6366f1', negative: '#ef4444' };

const AnalyticsPage = ({ chatId, onNavigate }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const { token } = useAuth();

  useEffect(() => { fetchAnalytics(); }, [chatId]);

  const fetchAnalytics = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/analytics/${chatId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) setAnalytics(await res.json());
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600">Analyzing your chat...</p>
      </div>
    </div>
  );
}

if (!analytics) {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <p className="text-gray-600">No analytics data available</p>
    </div>
  );
}

  const sentimentData = analytics?.sentiments?.map(s => ({
    name: s._id,
    value: s.count
})) || [];

    const participantData = analytics?.participants?.map(p => ({
    name: p._id,
    messages: p.count
    })) || [];

  return (
    // original AnalyticsPage code unchanged
    <div className="min-h-screen bg-slate-50 p-6">
          <div className="max-w-7xl mx-auto">
            {/* Header */}
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-white mb-6 shadow-xl">
              <h1 className="text-3xl font-bold mb-2">Chat Analytics</h1>
              <p className="text-indigo-100">Comprehensive insights from your conversation</p>
            </div>
    
            {/* Productivity Score */}
            <div className="bg-white rounded-2xl p-8 shadow-lg mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-2">Productivity Score</h2>
                  <p className="text-gray-600">Based on sentiment and engagement analysis</p>
                </div>
                <div className="text-6xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  {analytics.productivity_score}
                </div>
              </div>
              <div className="mt-4 bg-gray-200 rounded-full h-4">
                <div
                  className="bg-gradient-to-r from-indigo-600 to-purple-600 h-4 rounded-full transition-all duration-1000"
                  style={{ width: `${analytics.productivity_score}%` }}
                ></div>
              </div>
            </div>
    
            {/* Charts Grid */}
            <div className="grid md:grid-cols-2 gap-6 mb-6">
              {/* Sentiment Chart */}
              <div className="bg-white rounded-2xl p-6 shadow-lg">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-indigo-600" />
                  Sentiment Distribution
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={sentimentData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {sentimentData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={SENTIMENT_COLORS[entry.name] || COLORS.primary} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
    
              {/* Participant Chart */}
              <div className="bg-white rounded-2xl p-6 shadow-lg">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <Users className="w-5 h-5 mr-2 text-indigo-600" />
                  Message Count by Participant
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={participantData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="messages" fill={COLORS.primary} radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
    
            {/* Summary and Keywords */}
            <div className="grid md:grid-cols-2 gap-6 mb-6">
              <div className="bg-white rounded-2xl p-6 shadow-lg">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-indigo-600" />
                  Summary
                </h3>
                <p className="text-gray-700 leading-relaxed">{analytics.summary}</p>
              </div>
    
              <div className="bg-white rounded-2xl p-6 shadow-lg">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <Zap className="w-5 h-5 mr-2 text-indigo-600" />
                  Top Keywords
                </h3>
                <div className="flex flex-wrap gap-2">
                  {analytics.keywords?.map((kw, idx) => (
                    <span
                      key={idx}
                      className="bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700 px-4 py-2 rounded-full text-sm font-semibold"
                    >
                      {kw.keyword}({kw.count})
                    </span>
                  ))}
                </div>
              </div>
            </div>
    
            {/* Action Items */}
            {analytics.action_items?.length > 0 && (
              <div className="bg-white rounded-2xl p-6 shadow-lg mb-6">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <Target className="w-5 h-5 mr-2 text-indigo-600" />
                  Action Items
                </h3>
                <div className="space-y-3">
                  {analytics.action_items.map((item, idx) => (
                    <div key={idx} className="flex items-start space-x-3 p-3 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors">
                      <div className="w-6 h-6 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
                        {idx + 1}
                      </div>
                      <p className="text-gray-700 flex-1">{item}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
    
            {/* Emotions */}
            {analytics.emotions && Object.keys(analytics.emotions).length > 0 && (
              <div className="bg-white rounded-2xl p-6 shadow-lg">
                <h3 className="text-xl font-bold text-gray-800 mb-4">Emotion Analysis</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(analytics.emotions).map(([emotion, count]) => (
                    <div key={emotion} className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl p-4 text-center">
                      <div className="text-3xl mb-2">
                        {emotion === 'joy' && '😊'}
                        {emotion === 'sadness' && '😢'}
                        {emotion === 'anger' && '😠'}
                        {emotion === 'fear' && '😰'}
                        {emotion === 'surprise' && '😲'}
                        {!['joy', 'sadness', 'anger', 'fear', 'surprise'].includes(emotion) && '😐'}
                      </div>
                      <p className="text-gray-600 text-sm capitalize">{emotion}</p>
                      <p className="text-2xl font-bold text-gray-800">{count}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          {/* Chat ID + Actions */}
<div className="bg-white rounded-2xl p-6 shadow-lg mt-8">

  {/* Chat ID Display */}
  <h3 className="text-xl font-bold text-gray-800 mb-3 flex items-center">
    <FileText className="w-5 h-5 mr-2 text-indigo-600" />
    Chat ID
  </h3>

  <div className="flex items-center">
    <input
      type="text"
      value={chatId}
      readOnly
      className="w-full px-4 py-2 border rounded-lg bg-slate-50 text-gray-700 font-mono"
    />
    <button
      onClick={() => navigator.clipboard.writeText(chatId)}
      className="ml-3 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
    >
      Copy
    </button>
  </div>

  {/* Action Buttons */}
  <div className="mt-6 flex space-x-4">

    {/* Generate Report */}
    <button
      onClick={() => onNavigate("reports")}
      className="px-5 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl shadow hover:opacity-90"
    >
      Generate Report
    </button>

    {/* Delete Chat */}
    <button
      onClick={async () => {
        if (!window.confirm("Are you sure you want to delete this chat?")) return;

        try {
          const res = await fetch(`${API_BASE}/api/chats/${chatId}`, {
            method: "DELETE",
            headers: { Authorization: `Bearer ${token}` }
          });

          const data = await res.json();

          if (res.ok) {
            alert("Chat deleted successfully.");
            window.location.href = "/dashboard";
          } else {
            alert(data.detail || "Failed to delete chat.");
          }
        } catch (err) {
          alert("Something went wrong.");
          console.error(err);
        }
      }}
      className="px-5 py-3 bg-red-600 text-white rounded-xl shadow hover:bg-red-700"
    >
      Delete Chat
    </button>
  </div>
</div>

</div> 
</div>         
  );
};

export default AnalyticsPage;
