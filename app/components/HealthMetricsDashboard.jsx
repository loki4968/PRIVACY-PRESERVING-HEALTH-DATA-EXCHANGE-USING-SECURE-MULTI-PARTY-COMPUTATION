"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { TrendingUp, TrendingDown, Activity, AlertCircle, Filter, Download, RefreshCw, Heart, Droplet, Activity as PulseIcon } from 'lucide-react';
import TimeSeriesChart from './TimeSeriesChart';
import DataExport from './DataExport';
import { toast } from 'react-hot-toast';

const HealthMetricsDashboard = ({ patientData }) => {
  const [selectedTimeRange, setSelectedTimeRange] = useState('all');
  const [filteredData, setFilteredData] = useState(patientData);
  const [websocket, setWebsocket] = useState(null);
  const [reconnectAttempt, setReconnectAttempt] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [lastActivity, setLastActivity] = useState(null);
  const [pingStatus, setPingStatus] = useState(null);
  const [connectionHealth, setConnectionHealth] = useState(null);
  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY = 3000;
  const PING_INTERVAL = 30000; // 30 seconds

  const connectWebSocket = useCallback(() => {
    try {
      // Get token from localStorage using the correct key
      const token = localStorage.getItem('token');
      if (!token) {
        console.error('No auth token found');
        return;
      }

      // Get user info for connection metadata
      const userEmail = localStorage.getItem('userEmail') || 'unknown';
      const userRole = localStorage.getItem('userRole') || 'unknown';
      const userAgent = navigator.userAgent;

      // Create WebSocket connection with token only
      // The backend will extract email, role, and user agent from the token
      console.log('Attempting to connect to WebSocket with token:', token);
      const ws = new WebSocket(`ws://localhost:8000/ws/metrics?token=${token}`);
      setWebsocket(ws);
      
      setConnectionStatus('connecting');
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setReconnectAttempt(0); // Reset reconnect attempts on successful connection
        setConnectionStatus('connected');
        setLastActivity(new Date());
        toast.success('Connected to real-time metrics');
      };

      ws.onmessage = (event) => {
        try {
          setLastActivity(new Date());
          const message = JSON.parse(event.data);
          
          // Handle different message types
          if (message.type === 'metrics_update') {
            setFilteredData(prevData => ({
              ...prevData,
              ...message.data
            }));
          } else if (message.type === 'connection_health') {
            setConnectionHealth(message.data);
          } else if (message.type === 'pong') {
            setPingStatus({
              latency: new Date().getTime() - message.data.timestamp,
              serverTime: message.data.server_time
            });
          } else if (message.type === 'system_notification') {
            toast(message.data.message, {
              icon: message.data.level === 'error' ? '❌' : 
                    message.data.level === 'warning' ? '⚠️' : '✅',
              duration: 5000
            });
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
        toast.error(`Error connecting to real-time metrics: ${error.message || 'Unknown error'}`);
        
        // Log detailed error information
        console.error('WebSocket connection details:', {
          url: `ws://localhost:8000/ws/metrics?token=${token.substring(0, 10)}...`,
          readyState: ws.readyState,
          error: error
        });
      };

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setConnectionStatus('disconnected');
        
        // Log detailed close information
        console.error('WebSocket connection closed:', {
          code: event.code,
          reason: event.reason,
          wasClean: event.wasClean
        });
        
        // Attempt to reconnect if we haven't exceeded max attempts
        if (reconnectAttempt < MAX_RECONNECT_ATTEMPTS) {
          console.log(`Attempting to reconnect (${reconnectAttempt + 1}/${MAX_RECONNECT_ATTEMPTS})...`);
          setConnectionStatus('reconnecting');
          setTimeout(() => {
            setReconnectAttempt(prev => prev + 1);
            connectWebSocket();
          }, RECONNECT_DELAY);
        } else {
          toast.error(`Failed to connect to real-time metrics after multiple attempts. Last error code: ${event.code}`);
        }
      };

      setWebsocket(ws);
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      setConnectionStatus('error');
      toast.error('Error connecting to real-time metrics');
    }
  }, [reconnectAttempt]);

  // Send periodic ping to keep connection alive and monitor health
  useEffect(() => {
    let pingInterval;
    
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      pingInterval = setInterval(() => {
        try {
          websocket.send(JSON.stringify({
            type: 'ping',
            data: { timestamp: new Date().getTime() }
          }));
        } catch (error) {
          console.error('Error sending ping:', error);
        }
      }, PING_INTERVAL);
    }
    
    return () => {
      if (pingInterval) clearInterval(pingInterval);
    };
  }, [websocket, PING_INTERVAL]);

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [connectWebSocket]);

  useEffect(() => {
    if (!patientData) return;

    const filterDataByTimeRange = () => {
      const now = new Date();
      const filtered = {};

      Object.entries(patientData).forEach(([metric, data]) => {
        if (!data.raw_values) return;

        let filteredValues = [...data.raw_values];
        if (selectedTimeRange !== 'all') {
          const daysToFilter = {
            'week': 7,
            'month': 30,
            'quarter': 90
          }[selectedTimeRange];

          filteredValues = data.raw_values.slice(-daysToFilter);
        }

        filtered[metric] = {
          ...data,
          raw_values: filteredValues,
          average: filteredValues.length ? 
            filteredValues.reduce((a, b) => a + b, 0) / filteredValues.length : 
            null,
          min: filteredValues.length ? Math.min(...filteredValues) : null,
          max: filteredValues.length ? Math.max(...filteredValues) : null
        };
      });

      setFilteredData(filtered);
    };

    filterDataByTimeRange();
  }, [patientData, selectedTimeRange]);

  const getMetricIcon = (metricKey) => {
    switch(metricKey) {
      case 'blood_pressure':
        return <Activity className="w-6 h-6" />;
      case 'blood_sugar':
        return <Droplet className="w-6 h-6" />;
      case 'heart_rate':
        return <Heart className="w-6 h-6" />;
      default:
        return <PulseIcon className="w-6 h-6" />;
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      // Simulate refresh delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      filterDataByTimeRange();
      toast.success('Data refreshed successfully');
    } catch (error) {
      toast.error('Failed to refresh data');
    } finally {
      setIsRefreshing(false);
    }
  };

  const getMetricCard = (metricKey, data) => {
    if (!data || !data.raw_values || data.raw_values.length === 0) {
      return (
        <div className="bg-white rounded-xl shadow-lg p-6 transform transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {getMetricIcon(metricKey)}
              <h3 className="text-lg font-semibold text-gray-900">
                {metricKey.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
              </h3>
            </div>
            <AlertCircle className="w-6 h-6 text-gray-400" />
          </div>
          <div className="mt-4 flex items-center justify-center h-32 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-500">No data available</p>
          </div>
        </div>
      );
    }

    const latestValue = data.raw_values[data.raw_values.length - 1];
    const previousValue = data.raw_values[data.raw_values.length - 2];
    const trend = latestValue > previousValue ? 'up' : 'down';
    const trendPercentage = previousValue 
      ? Math.abs(((latestValue - previousValue) / previousValue) * 100).toFixed(1)
      : 0;

    const getMetricRange = (metric) => {
      switch(metric) {
        case 'blood_pressure':
          return { normal: [90, 120], unit: 'mmHg', color: 'blue' };
        case 'blood_sugar':
          return { normal: [70, 140], unit: 'mg/dL', color: 'purple' };
        case 'heart_rate':
          return { normal: [60, 100], unit: 'bpm', color: 'red' };
        default:
          return { normal: [0, 0], unit: '', color: 'gray' };
      }
    };

    const { normal, unit, color } = getMetricRange(metricKey);
    const isNormal = latestValue >= normal[0] && latestValue <= normal[1];
    const statusColor = isNormal ? 'green' : 'yellow';

    return (
      <div className={`bg-white rounded-xl shadow-lg p-6 transform transition-all duration-300 hover:shadow-xl hover:-translate-y-1 border-l-4 border-${color}-500`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {getMetricIcon(metricKey)}
            <h3 className="text-lg font-semibold text-gray-900">
              {metricKey.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
            </h3>
          </div>
          <div className={`px-3 py-1 rounded-full bg-${statusColor}-100 text-${statusColor}-800 text-sm font-medium`}>
            {isNormal ? 'Normal' : 'Attention'}
          </div>
        </div>

        <div className="mt-4">
          <div className="flex items-baseline justify-between">
            <div>
              <p className="text-3xl font-bold text-gray-900">
                {latestValue} <span className="text-sm font-normal text-gray-500">{unit}</span>
              </p>
              <div className={`mt-1 flex items-center text-sm ${
                trend === 'up' ? 'text-red-600' : 'text-green-600'
              }`}>
                {trend === 'up' ? (
                  <TrendingUp className="w-4 h-4 mr-1" />
                ) : (
                  <TrendingDown className="w-4 h-4 mr-1" />
                )}
                {trendPercentage}% from previous
              </div>
            </div>
          </div>
          
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-600">
              <span>Normal Range:</span>
              <span className="font-medium">{normal[0]} - {normal[1]} {unit}</span>
            </div>
            <div className="mt-2 h-2 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full bg-${statusColor}-500 transition-all duration-500 ease-in-out`}
                style={{ 
                  width: `${Math.min(100, (latestValue / normal[1]) * 100)}%`
                }}
              />
            </div>
          </div>

          <div className="mt-4">
            <TimeSeriesChart data={data.raw_values} metricType={metricKey} />
          </div>
        </div>

        <div className="mt-4 grid grid-cols-3 gap-4 bg-gray-50 rounded-lg p-4">
          <div>
            <p className="text-sm text-gray-500">Average</p>
            <p className="text-lg font-semibold">{data.average?.toFixed(1)} {unit}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Min</p>
            <p className="text-lg font-semibold">{data.min} {unit}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Max</p>
            <p className="text-lg font-semibold">{data.max} {unit}</p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6 p-6 bg-gray-50 min-h-screen">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Health Data Exchange</h1>
          <p className="mt-1 text-gray-500">Monitor and analyze your health metrics in real-time</p>
          <div className="mt-1 flex items-center">
            <span className={`inline-block w-2 h-2 rounded-full mr-2 ${{
              'connected': 'bg-green-500',
              'connecting': 'bg-yellow-500 animate-pulse',
              'reconnecting': 'bg-yellow-500 animate-pulse',
              'disconnected': 'bg-red-500',
              'error': 'bg-red-500'
            }[connectionStatus]}`}></span>
            <span className="text-xs text-gray-500">
              {connectionStatus === 'connected' && 'Connected'}
              {connectionStatus === 'connecting' && 'Connecting...'}
              {connectionStatus === 'reconnecting' && `Reconnecting (${reconnectAttempt}/${MAX_RECONNECT_ATTEMPTS})...`}
              {connectionStatus === 'disconnected' && 'Disconnected'}
              {connectionStatus === 'error' && 'Connection Error'}
              {lastActivity && connectionStatus === 'connected' && ` · Last activity: ${new Date(lastActivity).toLocaleTimeString()}`}
            </span>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 bg-white rounded-lg shadow px-4 py-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <select
              value={selectedTimeRange}
              onChange={(e) => setSelectedTimeRange(e.target.value)}
              className="border-none bg-transparent focus:ring-0 text-gray-700"
            >
              <option value="all">All Time</option>
              <option value="week">Last Week</option>
              <option value="month">Last Month</option>
              <option value="quarter">Last Quarter</option>
            </select>
          </div>

          <button
            onClick={handleRefresh}
            className={`p-2 rounded-lg bg-white shadow hover:shadow-md transition-all duration-300 ${isRefreshing ? 'animate-spin' : ''}`}
            disabled={isRefreshing}
          >
            <RefreshCw className="w-5 h-5 text-gray-700" />
          </button>

          <DataExport healthData={filteredData} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {getMetricCard('blood_pressure', filteredData?.blood_pressure)}
        {getMetricCard('blood_sugar', filteredData?.blood_sugar)}
        {getMetricCard('heart_rate', filteredData?.heart_rate)}
      </div>
    </div>
  );
};

export default HealthMetricsDashboard;