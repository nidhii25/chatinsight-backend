import React from 'react';
import { COLORS, SENTIMENT_COLORS } from '../constants/colors';


const FeatureCard = ({ icon, title, description, color }) => (
<div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-2 cursor-pointer">
<div className={`w-16 h-16 bg-gradient-to-r ${color} rounded-xl flex items-center justify-center text-white mb-4`}>
{icon}
</div>
<h3 className="text-xl font-bold text-gray-800 mb-2">{title}</h3>
<p className="text-gray-600">{description}</p>
</div>
);


export default FeatureCard;