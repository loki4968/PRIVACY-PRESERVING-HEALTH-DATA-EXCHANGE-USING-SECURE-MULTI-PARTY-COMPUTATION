"use client";

import React, { useState, useEffect } from 'react';
import { LineChart, BarChart2, PieChart, TrendingUp, Filter, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';
import { CustomButton } from './ui/custom-button';
import { analyticsService } from '../services/analyticsService';

const AnalyticsDashboard = ({ data }) => {
  const [timeRange, setTimeRange] = useState('month');
  const [metrics, setMetrics] = useState({
    totalUploads: 0,
    successRate: 0,
    trendingMetrics: [],
    dataTypes: {}
  });
  const [phq9Input, setPhq9Input] = useState('');
  const [phq9Result, setPhq9Result] = useState(null);
  const [cmpInput, setCmpInput] = useState('{"sodium_mmol_l":140, "potassium_mmol_l":4.2, "creatinine_mg_dl":1.0, "glucose_mg_dl":95}');
  const [cmpResult, setCmpResult] = useState(null);
  const [bmiHeight, setBmiHeight] = useState('172');
  const [bmiWeight, setBmiWeight] = useState('72');
  const [bmiResult, setBmiResult] = useState(null);
  const [gad7Input, setGad7Input] = useState('');
  const [gad7Result, setGad7Result] = useState(null);
  const [markersInput, setMarkersInput] = useState('{"crp_mg_l":5.2, "esr_mm_hr":15, "procalcitonin_ng_ml":0.8}');
  const [markersResult, setMarkersResult] = useState(null);
  const [sirsInput, setSirsInput] = useState('{"temperature_c":38.5, "heart_rate_bpm":95, "respiratory_rate":22, "wbc_count":12000}');
  const [sirsResult, setSirsResult] = useState(null);

  useEffect(() => {
    if (!data) return;

    // Calculate analytics from data
    const calculateMetrics = () => {
      const total = data.length;
      const successful = data.filter(item => item.status === 'completed').length;
      const successRate = total ? (successful / total) * 100 : 0;

      // Count data types
      const types = data.reduce((acc, item) => {
        const type = item.type || 'unknown';
        acc[type] = (acc[type] || 0) + 1;
        return acc;
      }, {});

      // Get trending metrics
      const trending = Object.entries(types)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);

      setMetrics({
        totalUploads: total,
        successRate,
        trendingMetrics: trending,
        dataTypes: types
      });
    };

    calculateMetrics();
  }, [data, timeRange]);

  const timeRangeOptions = [
    { id: 'week', label: 'Last Week' },
    { id: 'month', label: 'Last Month' },
    { id: 'quarter', label: 'Last Quarter' },
    { id: 'year', label: 'Last Year' }
  ];

  return (
    <div className="space-y-6">

      {/* Time Range Filter */}
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <Calendar className="w-5 h-5 text-gray-500" />
          <div className="flex space-x-2">
            {timeRangeOptions.map(option => (
              <button
                key={option.id}
                onClick={() => setTimeRange(option.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  timeRange === option.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Analytics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Total Uploads */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Total Uploads</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{metrics.totalUploads}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <BarChart2 className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4">
            <div className="h-2 bg-gray-100 rounded-full">
              <div
                className="h-full bg-blue-500 rounded-full transition-all duration-500"
                style={{ width: '100%' }}
              />
            </div>
          </div>
        </motion.div>

        {/* Success Rate */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Success Rate</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">{metrics.successRate.toFixed(1)}%</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4">
            <div className="h-2 bg-gray-100 rounded-full">
              <div
                className="h-full bg-green-500 rounded-full transition-all duration-500"
                style={{ width: `${metrics.successRate}%` }}
              />
            </div>
          </div>
        </motion.div>

        {/* Trending Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl shadow-sm p-6 border border-gray-200"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm font-medium text-gray-500">Trending Metrics</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <PieChart className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <div className="space-y-3">
            {metrics.trendingMetrics.map((metric, index) => (
              <div key={metric.name} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 capitalize">{metric.name}</span>
                <span className="text-sm font-medium text-gray-900">{metric.count}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Data Type Distribution */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Type Distribution</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(metrics.dataTypes).map(([type, count]) => (
            <div
              key={type}
              className="bg-gray-50 rounded-lg p-4"
            >
              <p className="text-sm text-gray-500 capitalize">{type}</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{count}</p>
              <div className="mt-2 h-1 bg-gray-200 rounded-full">
                <div
                  className="h-full bg-blue-500 rounded-full"
                  style={{
                    width: `${(count / metrics.totalUploads) * 100}%`
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* On-demand Clinical Analytics */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">On-demand Clinical Analytics</h3>

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {/* PHQ-9 */}
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h4 className="font-medium text-gray-800 mb-2">PHQ-9 (Depression)</h4>
            <p className="text-xs text-gray-500 mb-2">Enter 9 values between 0-3, comma-separated (e.g., 2,1,2,1,2,2,1,2,1)</p>
            <input
              className="w-full p-2 border border-gray-300 rounded mb-2 text-sm"
              placeholder="2,1,2,1,2,2,1,2,1"
              value={phq9Input}
              onChange={(e) => setPhq9Input(e.target.value)}
            />
            <button
              className="px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              onClick={async () => {
                try {
                  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
                  const responses = phq9Input.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n));
                  const res = await analyticsService.phq9(responses, token);
                  setPhq9Result(res);
                } catch (e) {
                  setPhq9Result({ error: e?.message || 'Failed to score PHQ-9' });
                }
              }}
            >
              Analyze
            </button>
            {phq9Result && (
              <pre className="mt-2 bg-white border text-xs p-2 rounded overflow-auto max-h-48">{JSON.stringify(phq9Result, null, 2)}</pre>
            )}
          </div>

          {/* CMP */}
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h4 className="font-medium text-gray-800 mb-2">CMP (Metabolic Panel)</h4>
            <p className="text-xs text-gray-500 mb-2">Provide CMP JSON (keys match backend ranges). Example provided.</p>
            <textarea
              className="w-full p-2 border border-gray-300 rounded mb-2 text-xs h-24"
              value={cmpInput}
              onChange={(e) => setCmpInput(e.target.value)}
            />
            <button
              className="px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              onClick={async () => {
                try {
                  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
                  const cmp = JSON.parse(cmpInput);
                  const res = await analyticsService.cmp(cmp, token);
                  setCmpResult(res);
                } catch (e) {
                  setCmpResult({ error: e?.message || 'Failed to analyze CMP' });
                }
              }}
            >
              Analyze
            </button>
            {cmpResult && (
              <pre className="mt-2 bg-white border text-xs p-2 rounded overflow-auto max-h-48">{JSON.stringify(cmpResult, null, 2)}</pre>
            )}
          </div>

          {/* BMI */}
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h4 className="font-medium text-gray-800 mb-2">BMI</h4>
            <div className="flex gap-2 mb-2">
              <input
                className="w-1/2 p-2 border border-gray-300 rounded text-sm"
                placeholder="Height (cm)"
                value={bmiHeight}
                onChange={(e) => setBmiHeight(e.target.value)}
              />
              <input
                className="w-1/2 p-2 border border-gray-300 rounded text-sm"
                placeholder="Weight (kg)"
                value={bmiWeight}
                onChange={(e) => setBmiWeight(e.target.value)}
              />
            </div>
            <button
              className="px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              onClick={async () => {
                try {
                  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
                  const res = await analyticsService.bmi(parseFloat(bmiHeight), parseFloat(bmiWeight), token);
                  setBmiResult(res);
                } catch (e) {
                  setBmiResult({ error: e?.message || 'Failed to compute BMI' });
                }
              }}
            >
              Compute
            </button>
            {bmiResult && (
              <pre className="mt-2 bg-white border text-xs p-2 rounded overflow-auto max-h-48">{JSON.stringify(bmiResult, null, 2)}</pre>
            )}
          </div>

          {/* GAD-7 */}
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h4 className="font-medium text-gray-800 mb-2">GAD-7 (Anxiety)</h4>
            <p className="text-xs text-gray-500 mb-2">Enter 7 values between 0-3, comma-separated (e.g., 1,2,1,0,2,1,1)</p>
            <input
              className="w-full p-2 border border-gray-300 rounded mb-2 text-sm"
              placeholder="1,2,1,0,2,1,1"
              value={gad7Input}
              onChange={(e) => setGad7Input(e.target.value)}
            />
            <button
              className="px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              onClick={async () => {
                try {
                  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
                  const responses = gad7Input.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n));
                  const res = await analyticsService.gad7(responses, token);
                  setGad7Result(res);
                } catch (e) {
                  setGad7Result({ error: e?.message || 'Failed to score GAD-7' });
                }
              }}
            >
              Analyze
            </button>
            {gad7Result && (
              <pre className="mt-2 bg-white border text-xs p-2 rounded overflow-auto max-h-48">{JSON.stringify(gad7Result, null, 2)}</pre>
            )}
          </div>

          {/* Infection Markers */}
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h4 className="font-medium text-gray-800 mb-2">Infection Markers</h4>
            <p className="text-xs text-gray-500 mb-2">Provide infection markers JSON (CRP, ESR, Procalcitonin). Example provided.</p>
            <textarea
              className="w-full p-2 border border-gray-300 rounded mb-2 text-xs h-24"
              value={markersInput}
              onChange={(e) => setMarkersInput(e.target.value)}
            />
            <button
              className="px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              onClick={async () => {
                try {
                  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
                  const markers = JSON.parse(markersInput);
                  const res = await analyticsService.infectionMarkers(markers, token);
                  setMarkersResult(res);
                } catch (e) {
                  setMarkersResult({ error: e?.message || 'Failed to analyze infection markers' });
                }
              }}
            >
              Analyze
            </button>
            {markersResult && (
              <pre className="mt-2 bg-white border text-xs p-2 rounded overflow-auto max-h-48">{JSON.stringify(markersResult, null, 2)}</pre>
            )}
          </div>

          {/* SIRS */}
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h4 className="font-medium text-gray-800 mb-2">SIRS (Systemic Inflammatory Response)</h4>
            <p className="text-xs text-gray-500 mb-2">Provide vitals JSON (temperature, heart rate, respiratory rate, WBC). Example provided.</p>
            <textarea
              className="w-full p-2 border border-gray-300 rounded mb-2 text-xs h-24"
              value={sirsInput}
              onChange={(e) => setSirsInput(e.target.value)}
            />
            <button
              className="px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              onClick={async () => {
                try {
                  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
                  const vitals = JSON.parse(sirsInput);
                  const res = await analyticsService.sirs(vitals, token);
                  setSirsResult(res);
                } catch (e) {
                  setSirsResult({ error: e?.message || 'Failed to evaluate SIRS' });
                }
              }}
            >
              Evaluate
            </button>
            {sirsResult && (
              <pre className="mt-2 bg-white border text-xs p-2 rounded overflow-auto max-h-48">{JSON.stringify(sirsResult, null, 2)}</pre>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;