import React from 'react';
import { COLORS, SENTIMENT_COLORS } from '../constants/colors';


const StatCard = ({ label, value, icon }) => (
<div className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow">
<div className="flex items-center justify-between mb-2">
<span className="text-gray-600 text-sm">{label}</span>
<div className="text-indigo-600">{icon}</div>
</div>
<p className="text-3xl font-bold text-gray-800">{value}</p>
</div>
);


export default StatCard;