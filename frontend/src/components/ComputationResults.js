import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-toastify';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  BoxPlot,
  ResponsiveContainer,
  HeatMapGrid
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const ComputationResults = ({ computationId }) => {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [visualizationType, setVisualizationType] = useState('line');
  const { token } = useAuth();

  useEffect(() => {
    if (computationId) {
      fetchResult();
    }
  }, [computationId]);

  const fetchResult = async () => {
    try {
      const response = await fetch(`http://localhost:8000/secure-computation/${computationId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch computation result');
      }

      const data = await response.json();
      setResult(data);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const prepareBoxPlotData = (data) => {
    if (!data || !data.percentile_25 || !data.percentile_75) return null;
    
    return [{
      min: data.min,
      q1: data.percentile_25,
      median: data.median,
      q3: data.percentile_75,
      max: data.max
    }];
  };

  const prepareScatterData = (data) => {
    if (!data || !data.data_points) return null;
    
    return data.data_points.map((point, index) => ({
      x: index,
      y: point.value,
      name: point.name || `Point ${index + 1}`
    }));
  };

  const prepareHeatMapData = (data) => {
    if (!data || !data.correlation_matrix) return null;
    
    return data.correlation_matrix.map((row, i) => 
      row.map((value, j) => ({
        x: i,
        y: j,
        value: value
      }))
    ).flat();
  };

  const renderVisualization = () => {
    if (!result || !result.data) return null;

    switch (visualizationType) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={result.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#8884d8" />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={result.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={result.data}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={150}
                label
              >
                {result.data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );

      case 'box':
        const boxPlotData = prepareBoxPlotData(result.data);
        return boxPlotData ? (
          <ResponsiveContainer width="100%" height={400}>
            <BoxPlot
              data={boxPlotData}
              width={400}
              height={400}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
            </BoxPlot>
          </ResponsiveContainer>
        ) : null;

      case 'scatter':
        const scatterData = prepareScatterData(result.data);
        return scatterData ? (
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="x" name="Index" />
              <YAxis dataKey="y" name="Value" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Legend />
              <Scatter name="Data Points" data={scatterData} fill="#8884d8" />
            </ScatterChart>
          </ResponsiveContainer>
        ) : null;

      case 'heatmap':
        const heatMapData = prepareHeatMapData(result.data);
        return heatMapData ? (
          <ResponsiveContainer width="100%" height={400}>
            <HeatMapGrid
              data={heatMapData}
              xAxis="x"
              yAxis="y"
              value="value"
              colors={['#ffeda0', '#feb24c', '#f03b20']}
            />
          </ResponsiveContainer>
        ) : null;

      default:
        return null;
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="text-center text-gray-500 py-8">
        No results available
      </div>
    );
  }

  return (
    <div className="bg-white shadow sm:rounded-lg p-6">
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Computation Results
        </h3>
        
        <div className="flex flex-wrap gap-2 mb-6">
          <button
            onClick={() => setVisualizationType('line')}
            className={`px-4 py-2 rounded-md ${
              visualizationType === 'line'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Line Chart
          </button>
          <button
            onClick={() => setVisualizationType('bar')}
            className={`px-4 py-2 rounded-md ${
              visualizationType === 'bar'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Bar Chart
          </button>
          <button
            onClick={() => setVisualizationType('pie')}
            className={`px-4 py-2 rounded-md ${
              visualizationType === 'pie'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Pie Chart
          </button>
          <button
            onClick={() => setVisualizationType('box')}
            className={`px-4 py-2 rounded-md ${
              visualizationType === 'box'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Box Plot
          </button>
          <button
            onClick={() => setVisualizationType('scatter')}
            className={`px-4 py-2 rounded-md ${
              visualizationType === 'scatter'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Scatter Plot
          </button>
          <button
            onClick={() => setVisualizationType('heatmap')}
            className={`px-4 py-2 rounded-md ${
              visualizationType === 'heatmap'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Heat Map
          </button>
        </div>

        <div className="flex justify-center">
          {renderVisualization()}
        </div>
      </div>

      <div className="mt-8">
        <h4 className="text-md font-medium text-gray-900 mb-4">
          Computation Details
        </h4>
        <div className="bg-gray-50 rounded-lg p-4">
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Type</dt>
              <dd className="mt-1 text-sm text-gray-900">{result.type}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className="mt-1 text-sm text-gray-900">{result.status}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Created At</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {new Date(result.created_at).toLocaleString()}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Completed At</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {result.completed_at ? new Date(result.completed_at).toLocaleString() : 'Pending'}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
};

export default ComputationResults; 