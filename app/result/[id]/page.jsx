"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Bar, Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  Title
} from "chart.js";
import { useAuth } from "../../context/AuthContext";
import { toast } from "sonner";
import { formatDateTime, formatDate, analyzeHealthMetrics } from "../../utils/formatters";
import { API_ENDPOINTS } from "../../config/api";
import { AlertTriangle, AlertCircle, CheckCircle, TrendingUp, TrendingDown, Activity, Heart, Thermometer, Droplet, Activity as Pulse } from "lucide-react";
import HealthMetricsDashboard from '../../components/HealthMetricsDashboard';

// Register necessary chart components
ChartJS.register(
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  Title
);

export default function ResultPage() {
  const { id } = useParams();
  const router = useRouter();
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [healthIssues, setHealthIssues] = useState([]);
  const { user, refreshToken } = useAuth();
  const [token, setToken] = useState('');

  useEffect(() => {
    // Access localStorage only on client side
    const storedToken = user?.token || localStorage.getItem('access_token');
    if (storedToken !== token) {
      setToken(storedToken);
    }
  }, [user]);

  useEffect(() => {
    async function fetchResult() {
      if (!token) {
        console.log("No token available, redirecting to login");
        router.push('/login');
        return;
      }

      try {
        setLoading(true);
        console.log("Fetching result for ID:", id);
        console.log("Using token:", token.substring(0, 10) + "...");
        
        const response = await fetch(API_ENDPOINTS.uploadById(id), {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        });
        
        console.log("Response status:", response.status);
        const responseText = await response.text();
        console.log("Raw response:", responseText);
        
        if (!response.ok) {
          if (response.status === 401) {
            console.log("Token expired, attempting refresh");
            const refreshed = await refreshToken();
            if (refreshed) {
              console.log("Token refreshed, retrying fetch");
              return; // The useEffect will run again with the new token
            } else {
              setError('Your session has expired. Please log in again.');
              router.push('/login');
              return;
            }
          } else if (response.status === 404) {
            setError('Analysis not found (404)');
            return;
          } else {
            setError(`Failed to load analysis: ${response.statusText || 'Unknown error'}`);
            return;
          }
        }
        
        // Try to parse the response as JSON
        let data;
        try {
          data = JSON.parse(responseText);
        } catch (e) {
          console.error("Failed to parse JSON:", e);
          setError('Invalid response format from server');
          return;
        }
        
        console.log("Parsed data:", data);
        
        // Check if we have valid result data
        if (!data.result) {
          console.log("No result data found");
          setError('No analysis results available');
          return;
        }

        // Check if we have analysis data
        if (!data.result.analysis || Object.keys(data.result.analysis).length === 0) {
          console.log("No analysis data found");
          setError('No analysis results available');
          return;
        }
        
        setResult(data);
        setError(null); // Clear any previous errors
        
        // Process health issues
        const issues = [];
        Object.entries(data.result.analysis).forEach(([metric, values]) => {
          console.log(`Processing metric: ${metric}`, values);
          
          if (values.trend_analysis) {
            console.log(`Found trend analysis for ${metric}:`, values.trend_analysis);
            
            if (values.trend_analysis.trend === 'increasing' && values.trend_analysis.percent_change > 10) {
              issues.push({
                metric,
                change: values.trend_analysis.percent_change,
                type: 'increase'
              });
            }
            if (values.trend_analysis.trend === 'decreasing' && values.trend_analysis.percent_change < -10) {
              issues.push({
                metric,
                change: values.trend_analysis.percent_change,
                type: 'decrease'
              });
            }
          }
        });
        
        console.log("Found issues:", issues);
        setHealthIssues(issues);
        
      } catch (err) {
        console.error("Error in fetchResult:", err);
        setError(err.message || 'An unexpected error occurred');
      } finally {
        setLoading(false);
      }
    }

    if (token) {
      fetchResult();
    }
  }, [id, token, router, refreshToken]);

  const renderHealthIssues = () => {
    if (!healthIssues.length) {
      return (
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex">
            <div className="flex-shrink-0">
              <CheckCircle className="h-5 w-5 text-green-400" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-green-800">No Health Issues Detected</h3>
              <p className="mt-2 text-sm text-green-700">All measured parameters are within normal ranges.</p>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        {healthIssues.map((issue, index) => (
          <div key={index} className={`p-4 rounded-lg ${issue.type === 'danger' ? 'bg-red-50' : 'bg-yellow-50'}`}>
            <div className="flex">
              <div className="flex-shrink-0">
                {issue.type === 'danger' ? (
                  <AlertCircle className="h-5 w-5 text-red-400" />
                ) : (
                  <AlertTriangle className="h-5 w-5 text-yellow-400" />
                )}
              </div>
              <div className="ml-3">
                <h3 className={`text-sm font-medium ${issue.type === 'danger' ? 'text-red-800' : 'text-yellow-800'}`}>
                  {issue.type === 'increase' ? 'Significant Increase' : 'Significant Decrease'} in {issue.metric}
                </h3>
                <div className="mt-2 text-sm">
                  <p className={issue.type === 'danger' ? 'text-red-700' : 'text-yellow-700'}>
                    {Math.abs(issue.change).toFixed(1)}% {issue.type === 'increase' ? 'increase' : 'decrease'} detected
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderColumnAnalysis = () => {
    if (!result?.result?.analysis) {
      console.log("No analysis data to render:", result);
      return null;
    }
    
    const analysis = result.result.analysis;
    console.log("Rendering analysis data:", analysis);
    
    return Object.entries(analysis).map(([columnName, columnData]) => {
      if (!columnData) {
        console.log("No data for column:", columnName);
        return null;
      }

      console.log("Processing column:", columnName, "data:", columnData);

      // Prepare data for time series if available
      const timeSeriesData = columnData.time_series_data ? {
        labels: columnData.time_series_data.map(d => formatDate(d.timestamp)),
        datasets: [{
          label: columnName,
          data: columnData.time_series_data.map(d => d.value),
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1
        }]
      } : null;

      const chartData = {
        labels: ["Minimum", "Average", "Maximum"],
        datasets: [
          {
            label: columnName,
            data: [
              columnData.min,
              columnData.average,
              columnData.max
            ],
            backgroundColor: ["#60a5fa", "#10b981", "#f59e0b"],
            borderRadius: 6,
          },
        ],
      };

      const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "top",
          },
          tooltip: {
            enabled: true,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      };

      return (
        <div key={columnName} className="mb-8 bg-white p-6 shadow-lg rounded-lg">
          <h3 className="text-xl font-semibold mb-4">{columnName}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Total Values</p>
              <p className="text-2xl font-bold">{columnData.count}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Unique Values</p>
              <p className="text-2xl font-bold">{columnData.unique_values}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Missing Values</p>
              <p className="text-2xl font-bold">{columnData.missing_values}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Non-numeric Values</p>
              <p className="text-2xl font-bold">{columnData.non_numeric_count}</p>
            </div>
          </div>
          
          {/* Bar Chart */}
          <div className="h-[300px] mb-6">
            <Bar data={chartData} options={chartOptions} />
          </div>

          {/* Time Series Chart if available */}
          {timeSeriesData && (
            <div className="h-[300px]">
              <h4 className="text-lg font-medium mb-4">Time Series Analysis</h4>
              <Line data={timeSeriesData} options={{
                ...chartOptions,
                plugins: {
                  ...chartOptions.plugins,
                  title: {
                    display: true,
                    text: `${columnName} Over Time`
                  }
                }
              }} />
            </div>
          )}
        </div>
      );
    });
  };

  const TrendIndicator = ({ trend }) => {
    if (!trend || !trend.is_significant) return null;

    const isPositive = trend.trend === 'increasing';
    const Icon = isPositive ? TrendingUp : TrendingDown;
    const color = Math.abs(trend.percent_change) > 20 ? 'text-red-500' : 
                  Math.abs(trend.percent_change) > 10 ? 'text-yellow-500' : 
                  'text-blue-500';

    return (
      <div className={`flex items-center ${color}`}>
        <Icon className="w-4 h-4 mr-1" />
        <span className="text-sm">
          {trend.percent_change.toFixed(1)}% {trend.trend}
        </span>
      </div>
    );
  };

  const MetricCard = ({ title, value, trend, icon: Icon, unit, insights }) => {
    const getStatusColor = (status) => {
      if (!insights) return 'gray';
      switch (insights.status.toLowerCase()) {
        case 'normal':
          return 'green';
        case 'elevated':
        case 'out of range':
          return 'yellow';
        default:
          return 'red';
      }
    };

    const statusColor = getStatusColor(insights?.status);

    return (
      <div className="bg-white rounded-lg p-4 border">
        <div className="flex items-center justify-between mb-2">
          <div className={`p-2 rounded-lg bg-${statusColor}-100`}>
            <Icon className={`h-5 w-5 text-${statusColor}-600`} />
          </div>
          {trend && (
            <TrendIndicator trend={trend} />
          )}
        </div>
        <h4 className="text-sm font-medium text-gray-500">{title}</h4>
        <div className="mt-1 flex items-baseline">
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
          {unit && <span className="ml-1 text-sm text-gray-500">{unit}</span>}
        </div>
        {insights && (
          <div className={`mt-1 text-sm text-${statusColor}-600`}>
            {insights.status}
          </div>
        )}
      </div>
    );
  };

  const CorrelationCard = ({ correlations }) => {
    if (!correlations || correlations.length === 0) return null;

    return (
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Significant Correlations</h3>
        <div className="space-y-3">
          {correlations.map((corr, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-700">
                  {corr.metrics[0]} ↔ {corr.metrics[1]}
                </p>
              </div>
              <div className={`text-sm font-medium ${
                Math.abs(corr.correlation) > 0.7 ? 'text-blue-600' : 'text-blue-400'
              }`}>
                {(corr.correlation * 100).toFixed(1)}%
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const getBloodTestMetricInfo = (metric) => {
    const normalRanges = {
      'Hemoglobin': { range: '12-17 g/dL', unit: 'g/dL' },
      'White Blood Cells': { range: '4,500-11,000 cells/µL', unit: 'cells/µL' },
      'Red Blood Cells': { range: '4.5-5.9 million/µL', unit: 'million/µL' },
      'Platelets': { range: '150,000-450,000/µL', unit: '/µL' },
      'Glucose': { range: '70-100 mg/dL', unit: 'mg/dL' }
    };

    const getStatus = (metric, value) => {
      switch(metric) {
        case 'Hemoglobin':
          return value < 12 ? 'Low' : value > 17 ? 'High' : 'Normal';
        case 'White Blood Cells':
          return value < 4500 ? 'Low' : value > 11000 ? 'High' : 'Normal';
        case 'Red Blood Cells':
          return value < 4.5 ? 'Low' : value > 5.9 ? 'High' : 'Normal';
        case 'Platelets':
          return value < 150000 ? 'Low' : value > 450000 ? 'High' : 'Normal';
        case 'Glucose':
          return value < 70 ? 'Low' : value > 100 ? 'High' : 'Normal';
        default:
          return 'Unknown';
      }
    };

    const getRecommendation = (metric, status) => {
      const recommendations = {
        'Hemoglobin': {
          'Low': 'Consider iron supplementation and consult healthcare provider.',
          'High': 'Follow up with healthcare provider for evaluation.',
          'Normal': 'Maintain healthy diet and regular exercise.'
        },
        'White Blood Cells': {
          'Low': 'Monitor for infections and consult healthcare provider.',
          'High': 'May indicate infection or inflammation. Consult healthcare provider.',
          'Normal': 'Immune system functioning well. Maintain healthy lifestyle.'
        },
        'Red Blood Cells': {
          'Low': 'May indicate anemia. Consult healthcare provider.',
          'High': 'Follow up with healthcare provider for evaluation.',
          'Normal': 'Good oxygen-carrying capacity. Maintain healthy habits.'
        },
        'Platelets': {
          'Low': 'Monitor for bleeding risk and consult healthcare provider.',
          'High': 'May indicate increased clotting risk. Consult provider.',
          'Normal': 'Good clotting function. Maintain healthy lifestyle.'
        },
        'Glucose': {
          'Low': 'Monitor blood sugar and consider quick sugar source.',
          'High': 'Monitor diet and consult healthcare provider.',
          'Normal': 'Good blood sugar control. Maintain healthy diet.'
        }
      };
      return recommendations[metric]?.[status] || 'Consult healthcare provider for interpretation.';
    };

    return {
      ...normalRanges[metric],
      getStatus,
      getRecommendation
    };
  };

  const renderAnalysis = () => {
    if (!result?.result?.analysis) {
      return (
        <div className="bg-yellow-50 p-4 rounded-lg">
          <div className="flex">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-5 w-5 text-yellow-400" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">No Analysis Available</h3>
              <p className="mt-2 text-sm text-yellow-700">The analysis results are not available for this upload.</p>
            </div>
          </div>
        </div>
      );
    }
    
    // Handle case where analysis contains only _info field (no analyzable metrics found)
    if (result?.result?.analysis?._info) {
      return (
        <div className="bg-yellow-50 p-4 rounded-lg">
          <div className="flex">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-5 w-5 text-yellow-400" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">{result.result.analysis._info.message}</h3>
              <p className="mt-2 text-sm text-yellow-700">{result.result.analysis._info.recommendation}</p>
              {result.result.analysis._info.available_columns && (
                <div className="mt-2">
                  <p className="text-sm font-medium text-yellow-800">Available Columns:</p>
                  <ul className="list-disc pl-5 text-sm text-yellow-700">
                    {result.result.analysis._info.available_columns.map((col, index) => (
                      <li key={index}>{col}</li>
                    ))}
                  </ul>
                </div>
              )}
              {result.result.analysis._info.expected_columns && (
                <div className="mt-2">
                  <p className="text-sm font-medium text-yellow-800">Expected Columns:</p>
                  <ul className="list-disc pl-5 text-sm text-yellow-700">
                    {result.result.analysis._info.expected_columns.map((col, index) => (
                      <li key={index}>{col}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-8">
        {/* Summary Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Blood Test Analysis Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(result.result.analysis)
              .filter(([metric]) => metric !== '_info') // Filter out the _info field
              .map(([metric, data]) => {
                const metricInfo = getBloodTestMetricInfo(metric);
                const status = metricInfo.getStatus(metric, data.average);
              
              return (
                <div key={metric} className="bg-white rounded-lg p-4 border">
                  <div className="flex items-center justify-between mb-2">
                    <div className={`p-2 rounded-lg ${
                      status === 'Normal' ? 'bg-green-100' :
                      status === 'Low' ? 'bg-yellow-100' : 'bg-red-100'
                    }`}>
                      <Activity className={`h-5 w-5 ${
                        status === 'Normal' ? 'text-green-600' :
                        status === 'Low' ? 'text-yellow-600' : 'text-red-600'
                      }`} />
                    </div>
                    {data.trend_analysis && (
                      <TrendIndicator trend={data.trend_analysis} />
                    )}
                  </div>
                  <h4 className="text-sm font-medium text-gray-500">{metric}</h4>
                  <div className="mt-1 flex items-baseline">
                    <p className="text-2xl font-semibold text-gray-900">
                      {metric === 'Platelets' || metric === 'White Blood Cells' 
                        ? (data.average || 0).toLocaleString()
                        : (data.average || 0).toFixed(1)}
                    </p>
                    <span className="ml-1 text-sm text-gray-500">{metricInfo.unit}</span>
                  </div>
                  <div className={`mt-1 text-sm ${
                    status === 'Normal' ? 'text-green-600' :
                    status === 'Low' ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {status}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Detailed Analysis Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Detailed Analysis</h3>
          <div className="space-y-6">
            {Object.entries(result.result.analysis)
              .filter(([metric]) => metric !== '_info') // Filter out the _info field
              .map(([metric, data]) => {
                const metricInfo = getBloodTestMetricInfo(metric);
                const status = metricInfo.getStatus(metric, data.average);
              
              return (
                <div key={metric} className="border-b pb-6 last:border-b-0">
                  <h4 className="text-md font-medium mb-3">{metric}</h4>
                  
                  {/* Statistics */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="text-sm text-gray-500">Average</div>
                      <div className="text-lg font-semibold">
                        {metric === 'Platelets' || metric === 'White Blood Cells'
                          ? (data.average || 0).toLocaleString()
                          : (data.average || 0).toFixed(1)}
                        <span className="text-sm text-gray-500 ml-1">{metricInfo.unit}</span>
                      </div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="text-sm text-gray-500">Range</div>
                      <div className="text-lg font-semibold">
                        {metric === 'Platelets' || metric === 'White Blood Cells'
                          ? `${(data.min || 0).toLocaleString()} - ${(data.max || 0).toLocaleString()}`
                          : `${(data.min || 0).toFixed(1)} - ${(data.max || 0).toFixed(1)}`}
                      </div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="text-sm text-gray-500">Standard Deviation</div>
                      <div className="text-lg font-semibold">{(data.std_dev || 0).toFixed(2)}</div>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="text-sm text-gray-500">Measurements</div>
                      <div className="text-lg font-semibold">{data.count}</div>
                    </div>
                  </div>

                  {/* Health Insights */}
                  <div className="bg-blue-50 p-4 rounded-lg mb-4">
                    <h5 className="text-sm font-medium text-blue-800 mb-2">Health Insights</h5>
                    <div className="space-y-2">
                      <div className="flex items-center text-sm text-blue-700">
                        <span className="font-medium mr-2">Normal Range:</span>
                        {metricInfo.range}
                      </div>
                      <div className="flex items-center text-sm">
                        <span className="font-medium mr-2">Status:</span>
                        <span className={`px-2 py-1 rounded ${
                          status === 'Normal' ? 'bg-green-100 text-green-800' :
                          status === 'Low' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {status}
                        </span>
                      </div>
                      <div className="text-sm text-blue-700">
                        <span className="font-medium mr-2">Recommendation:</span>
                        {metricInfo.getRecommendation(metric, status)}
                      </div>
                    </div>
                  </div>

                  {/* Trend Analysis */}
                  {data.trend_analysis && (
                    <div className="flex items-center space-x-2 text-sm">
                      <span className="font-medium">Trend:</span>
                      <TrendIndicator trend={data.trend_analysis} />
                      <span className={data.trend_analysis.trend === 'increasing' ? 'text-red-600' : 'text-green-600'}>
                        {Math.abs(data.trend_analysis.percent_change).toFixed(1)}% {data.trend_analysis.trend}
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between items-center mt-8">
          <button
            onClick={() => router.push("/dashboard")}
            className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Back to Dashboard
          </button>
          <button
            onClick={() => router.push("/upload")}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Upload Another File
          </button>
        </div>
      </div>
    );
  };

  const renderMedicalHistory = () => {
    if (!result?.result?.analysis) {
      return (
        <div className="bg-yellow-50 p-4 rounded-lg">
          <div className="flex">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-5 w-5 text-yellow-400" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">No Medical History Available</h3>
              <p className="mt-2 text-sm text-yellow-700">The medical history data is not available for this upload.</p>
            </div>
          </div>
        </div>
      );
    }

    const { record_types = [], conditions = [], treatments = [] } = result.result.analysis;

    return (
      <div className="space-y-8">
        {/* Summary Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Medical History Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-500">Total Records</div>
              <div className="text-2xl font-semibold">{result.result.summary.total_records}</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-500">Date Range</div>
              <div className="text-lg font-semibold">
                {result.result.summary.date_range.start} - {result.result.summary.date_range.end}
              </div>
            </div>
          </div>
        </div>

        {/* Record Types Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Record Types</h3>
          <div className="grid grid-cols-1 gap-3">
            {record_types.map((type, index) => (
              <div key={index} className="bg-blue-50 p-3 rounded-lg">
                <span className="text-blue-700">{type}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Conditions Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Medical Conditions</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {conditions.map((condition, index) => (
              <div key={index} className="bg-yellow-50 p-3 rounded-lg">
                <span className="text-yellow-700">{condition}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Treatments Section */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Treatments</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {treatments.map((treatment, index) => (
              <div key={index} className="bg-green-50 p-3 rounded-lg">
                <span className="text-green-700">{treatment}</span>
              </div>
            ))}
          </div>
        </div>

        {/* File Information */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">File Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Original Filename</p>
              <p className="font-medium">{result.filename}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">File Size</p>
              <p className="font-medium">{(result.file_size / 1024).toFixed(2)} KB</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Upload Date</p>
              <p className="font-medium">{new Date(result.created_at).toLocaleDateString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Processing Status</p>
              <p className="font-medium">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  result.status === 'completed' ? 'bg-green-100 text-green-800' : 
                  result.status === 'processing' ? 'bg-yellow-100 text-yellow-800' : 
                  'bg-red-100 text-red-800'
                }`}>
                  {result.status.charAt(0).toUpperCase() + result.status.slice(1)}
                </span>
              </p>
            </div>
          </div>
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between items-center mt-8">
          <button
            onClick={() => router.push("/dashboard")}
            className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Back to Dashboard
          </button>
          <button
            onClick={() => router.push("/upload")}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Upload Another File
          </button>
        </div>
      </div>
    );
  };

  const renderBloodSugarAnalysis = () => {
    if (!result?.result?.patient_analysis) {
      return (
        <div className="bg-yellow-50 p-4 rounded-lg">
          <div className="flex">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-5 w-5 text-yellow-400" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">No Blood Sugar Analysis Available</h3>
              <p className="mt-2 text-sm text-yellow-700">The blood sugar analysis results are not available for this upload.</p>
            </div>
          </div>
        </div>
      );
    }

    const { patient_analysis, overall_insights } = result.result;

    return (
      <div className="space-y-8">
        {/* Overall Summary */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Population Overview</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-blue-600">Total Patients</p>
              <p className="text-2xl font-bold text-blue-800">{overall_insights.total_patients}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-sm text-green-600">Total Readings</p>
              <p className="text-2xl font-bold text-green-800">{overall_insights.total_readings}</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="text-sm text-purple-600">Average Blood Sugar</p>
              <p className="text-2xl font-bold text-purple-800">
                {overall_insights.population_stats.average.toFixed(1)} mg/dL
              </p>
            </div>
          </div>

          {/* Risk Distribution */}
          <div className="mt-6">
            <h4 className="text-md font-medium mb-3">Risk Distribution</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-red-50 p-4 rounded-lg">
                <p className="text-sm text-red-600">High Risk</p>
                <p className="text-2xl font-bold text-red-800">{overall_insights.risk_distribution.high_risk}</p>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <p className="text-sm text-yellow-600">Moderate Risk</p>
                <p className="text-2xl font-bold text-yellow-800">{overall_insights.risk_distribution.moderate_risk}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-sm text-green-600">Low Risk</p>
                <p className="text-2xl font-bold text-green-800">{overall_insights.risk_distribution.low_risk}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Patient-specific Analysis */}
        {Object.entries(patient_analysis).map(([patientId, data]) => (
          <div key={patientId} className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">Patient {patientId} Analysis</h3>
            
            {/* Statistics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-sm text-gray-500">Average</div>
                <div className="text-lg font-semibold">
                  {data.statistics.average.toFixed(1)}
                  <span className="text-sm text-gray-500 ml-1">mg/dL</span>
                </div>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-sm text-gray-500">Range</div>
                <div className="text-lg font-semibold">
                  {data.statistics.min.toFixed(1)} - {data.statistics.max.toFixed(1)}
                </div>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-sm text-gray-500">Standard Deviation</div>
                <div className="text-lg font-semibold">{data.statistics.std_dev.toFixed(2)}</div>
              </div>
              <div className="bg-gray-50 p-3 rounded">
                <div className="text-sm text-gray-500">Total Readings</div>
                <div className="text-lg font-semibold">{data.statistics.count}</div>
              </div>
            </div>

            {/* Risk Assessment */}
            <div className={`p-4 rounded-lg mb-6 ${
              data.risk_assessment.level === 'High' ? 'bg-red-50' :
              data.risk_assessment.level === 'Moderate' ? 'bg-yellow-50' :
              'bg-green-50'
            }`}>
              <h4 className="text-md font-medium mb-2">Risk Assessment</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className={`text-sm ${
                    data.risk_assessment.level === 'High' ? 'text-red-600' :
                    data.risk_assessment.level === 'Moderate' ? 'text-yellow-600' :
                    'text-green-600'
                  }`}>
                    Risk Level: <span className="font-semibold">{data.risk_assessment.level}</span>
                  </p>
                  <p className="text-sm mt-1">
                    High Readings: {data.risk_assessment.high_readings} of {data.risk_assessment.total_readings}
                  </p>
                  <p className="text-sm mt-1">
                    Low Readings: {data.risk_assessment.low_readings} of {data.risk_assessment.total_readings}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium mb-1">Recommendation:</p>
                  <p className="text-sm">
                    {data.risk_assessment.level === 'High' 
                      ? 'Immediate consultation with healthcare provider recommended.'
                      : data.risk_assessment.level === 'Moderate'
                      ? 'Schedule follow-up with healthcare provider.'
                      : 'Continue current management plan.'}
                  </p>
                </div>
              </div>
            </div>

            {/* Trend Analysis */}
            <div className="bg-blue-50 p-4 rounded-lg mb-6">
              <h4 className="text-md font-medium mb-2">Trend Analysis</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-blue-600">
                    Trend: <span className="font-semibold">{data.trend_analysis.interpretation}</span>
                  </p>
                  <p className="text-sm mt-1">
                    Change: {Math.abs(data.trend_analysis.percent_change).toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium mb-1">Interpretation:</p>
                  <p className="text-sm">
                    Blood sugar levels are {data.trend_analysis.interpretation} over time.
                    {Math.abs(data.trend_analysis.percent_change) > 10
                      ? ' Significant change detected.'
                      : ' Changes are within normal variation.'}
                  </p>
                </div>
              </div>
            </div>

            {/* Anomalies */}
            {data.anomalies.count > 0 && (
              <div className="bg-yellow-50 p-4 rounded-lg mb-6">
                <h4 className="text-md font-medium mb-2">Anomaly Detection</h4>
                <p className="text-sm text-yellow-600">
                  {data.anomalies.count} unusual readings detected
                </p>
                <div className="mt-2">
                  <p className="text-sm font-medium mb-1">Anomalous Values:</p>
                  <div className="flex flex-wrap gap-2">
                    {data.anomalies.values.map((value, index) => (
                      <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        {value.toFixed(1)} mg/dL
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Pattern Analysis */}
            {data.pattern_analysis && (
              <div className="bg-purple-50 p-4 rounded-lg">
                <h4 className="text-md font-medium mb-2">Pattern Analysis</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(data.pattern_analysis.cluster_centers).map(([label, value]) => (
                    <div key={label} className="bg-white p-3 rounded-lg">
                      <p className="text-sm text-purple-600">{label} Range Center</p>
                      <p className="text-lg font-semibold">{value.toFixed(1)} mg/dL</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}

        {/* Navigation Buttons */}
        <div className="flex justify-between items-center mt-8">
          <button
            onClick={() => router.push("/dashboard")}
            className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            Back to Dashboard
          </button>
          <button
            onClick={() => router.push("/upload")}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Upload Another File
          </button>
        </div>
      </div>
    );
  };

  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-500">Loading analysis...</span>
        </div>
      );
    }

    if (error) {
      return (
        <div className="min-h-[400px] flex items-center justify-center">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
            <div className="flex flex-col items-center text-center">
              <div className="mb-4">
                {error.includes('404') || error.includes('not found') ? (
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                    <AlertCircle className="h-8 w-8 text-gray-400" />
                  </div>
                ) : (
                  <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                    <AlertTriangle className="h-8 w-8 text-red-400" />
                  </div>
                )}
              </div>
              
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {error.includes('404') || error.includes('not found')
                  ? 'Analysis Not Found'
                  : 'Error Loading Analysis'}
              </h3>
              
              <p className="text-gray-600 mb-6">
                {error.includes('404') || error.includes('not found')
                  ? 'The requested analysis could not be found. It may have been deleted or the ID might be incorrect.'
                  : error}
              </p>
              
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Return to Dashboard
                </button>
                <button
                  onClick={() => router.push('/upload')}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Upload New File
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    // Handle old format data
    if (result?.result?.metrics || !result?.result?.status) {
      // Convert old format to new format
      const convertedResult = {
        ...result,
        result: {
          status: "success",
          category: result.category,
          summary: result.result.summary || {
            total_records: 0,
            date_range: { start: null, end: null }
          },
          analysis: {}
        }
      };
      
      // If there are metrics, add them to analysis
      if (result.result.metrics) {
        convertedResult.result.analysis = Object.entries(result.result.metrics).reduce((acc, [key, value]) => {
          acc[key] = {
            ...value,
            insights: value.insights || {
              normal_range: "Not available",
              status: "Unknown",
              recommendation: "Please consult healthcare provider"
            }
          };
          return acc;
        }, {});
      }
      
      return renderAnalysisBasedOnCategory(convertedResult);
    }

    return renderAnalysisBasedOnCategory(result);
  };

  const renderAnalysisBasedOnCategory = (data) => {
    const category = data.category || data.result?.category;
    
    switch (category) {
      case "blood_sugar":
        return renderBloodSugarAnalysis();
      case "blood_test":
        return renderAnalysis();
      case "medical_history":
        return renderMedicalHistory();
      case "vital_signs":
        return renderVitalSigns();
      default:
        return (
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="flex">
              <div className="flex-shrink-0">
                <AlertTriangle className="h-5 w-5 text-yellow-400" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">Generic Analysis</h3>
                <p className="mt-2 text-sm text-yellow-700">
                  Detailed analysis view for {category ? category.replace(/_/g, ' ') : 'this category'} is not yet available.
                  Basic information is shown below.
                </p>
              </div>
            </div>
            
            <div className="mt-6 space-y-6">
              {/* Summary Information */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">Summary Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-500">Total Records</div>
                    <div className="text-2xl font-semibold">
                      {data.result?.summary?.total_records || 0}
                    </div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-500">Category</div>
                    <div className="text-2xl font-semibold capitalize">
                      {category?.replace(/_/g, ' ') || 'Unknown'}
                    </div>
                  </div>
                </div>
              </div>

              {/* File Details */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">File Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Filename</p>
                    <p className="font-medium">{data.filename}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Upload Date</p>
                    <p className="font-medium">
                      {new Date(data.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">File Size</p>
                    <p className="font-medium">{(data.file_size / 1024).toFixed(2)} KB</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Status</p>
                    <p className="font-medium">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        data.status === 'completed' ? 'bg-green-100 text-green-800' : 
                        data.status === 'processing' ? 'bg-yellow-100 text-yellow-800' : 
                        'bg-red-100 text-red-800'
                      }`}>
                        {data.status.charAt(0).toUpperCase() + data.status.slice(1)}
                      </span>
                    </p>
                  </div>
                </div>
              </div>

              {/* Navigation */}
              <div className="flex justify-between items-center mt-8">
                <button
                  onClick={() => router.push("/dashboard")}
                  className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Back to Dashboard
                </button>
                <button
                  onClick={() => router.push("/upload")}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Upload Another File
                </button>
              </div>
            </div>
          </div>
        );
    }
  };

  if (!user) {
    return null; // Don't render anything while redirecting
  }

  return (
    <div className="min-h-screen bg-gray-50 w-full">
      <div className="container mx-auto px-4 py-8 bg-gray-50">
        <h2 className="text-2xl font-bold mb-6 text-gray-900">
          {result?.category ? (
            <span className="capitalize">{result.category.replace(/_/g, ' ')} Analysis</span>
          ) : (
            'Health Data Analysis'
          )}
        </h2>
        {renderContent()}
      </div>
    </div>
  );
}
