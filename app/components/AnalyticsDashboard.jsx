"use client";

import React, { useState, useEffect } from 'react';
import { LineChart, BarChart2, PieChart, TrendingUp, Filter, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';
import { CustomButton } from './ui/custom-button';

const AnalyticsDashboard = ({ data }) => {
  const [timeRange, setTimeRange] = useState('month');
  const [metrics, setMetrics] = useState({
    totalUploads: 0,
    successRate: 0,
    trendingMetrics: [],
    dataTypes: {}
  });

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
    </div>
  );
};

export default AnalyticsDashboard; 