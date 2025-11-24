
// ===========================
// File: src/components/DashboardPage.js
// ===========================

import React, { useState } from 'react';
import { MessageSquare, Upload, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { COLORS, SENTIMENT_COLORS } from '../constants/colors';
import FeatureCard from "../components/FeatureCard";
import StatCard from "../components/StatCard";

import { 
  Brain, 
  Target, 
  BarChart3, 
  FileText,
  TrendingUp
} from "lucide-react";

const API_BASE = 'http://localhost:8000';

const DashboardPage = ({ onNavigate }) => {
  const [uploading, setUploading] = useState(false);
  const { token, user, logout } = useAuth();

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE}/api/chats/upload`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        alert('Chat uploaded successfully!');
        onNavigate('analytics', data.chat_id);
      } else {
        alert('Upload failed');
      }
    } catch {
      alert('Error uploading file');
    } finally {
      setUploading(false);
    }
  };

  return (
    // original DashboardPage code unchanged
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
              <MessageSquare className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              ChatScope
            </h1>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-gray-600">Welcome back,</p>
              <p className="font-semibold text-gray-800">{user?.name || 'User'}</p>
            </div>
            <button
              onClick={logout}
              className="p-2 hover:bg-red-50 rounded-lg transition-colors"
              title="Logout"
            >
              <LogOut className="w-5 h-5 text-red-600" />
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-3xl p-12 text-white shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-10 rounded-full -mr-32 -mt-32"></div>
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-white opacity-10 rounded-full -ml-24 -mb-24"></div>
          
          <div className="relative z-10">
            <h2 className="text-4xl font-bold mb-4">Unlock Chat Insights</h2>
            <p className="text-xl text-indigo-100 mb-8 max-w-2xl">
              Transform your WhatsApp conversations into actionable intelligence with AI-powered analytics
            </p>

            <label className="inline-block cursor-pointer">
              <div className="bg-white text-indigo-600 px-8 py-4 rounded-xl font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all flex items-center space-x-3">
                <Upload className="w-5 h-5" />
                <span>{uploading ? 'Uploading...' : 'Upload Chat File'}</span>
              </div>
              <input
                type="file"
                onChange={handleFileUpload}
                accept=".txt"
                className="hidden"
                disabled={uploading}
              />
            </label>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-6 mt-12">
          <FeatureCard
            icon={<Brain className="w-8 h-8" />}
            title="AI-Powered Insights"
            description="Advanced NLP for sentiment analysis and emotion detection"
            color="from-blue-500 to-cyan-500"
          />
          <FeatureCard
            icon={<Target className="w-8 h-8" />}
            title="Action Items"
            description="Automatically extract tasks and to-dos from conversations"
            color="from-purple-500 to-pink-500"
          />
          <FeatureCard
            icon={<BarChart3 className="w-8 h-8" />}
            title="Visual Reports"
            description="Beautiful charts and downloadable PDF/CSV reports"
            color="from-orange-500 to-red-500"
          />
        </div>

        {/* Stats Section */}
        <div className="grid md:grid-cols-4 gap-6 mt-12">
          <StatCard label="Chats Analyzed" value="0" icon={<MessageSquare />} />
          <StatCard label="Messages Processed" value="0" icon={<FileText />} />
          <StatCard label="Action Items" value="0" icon={<Target />} />
          <StatCard label="Avg Productivity" value="0%" icon={<TrendingUp />} />
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
