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
import { Button, ButtonGroup, Dropdown } from 'react-bootstrap';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const ComputationResults = ({ computationId }) => {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [visualizationType, setVisualizationType] = useState('line');
  const [exportFormat, setExportFormat] = useState('json');
  const [isExporting, setIsExporting] = useState(false);
  const { token } = useAuth();

  useEffect(() => {
    if (computationId) {
      fetchResult();
    }
  }, [computationId]);

  const fetchResult = async () => {
    try {
      const response = await fetch(`http://localhost:8000/secure-computations/${computationId}/result`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch computation result');
      }

      const data = await response.json();
      
  const handleExport = async (format) => {
    setIsExporting(true);
    try {
      // Use the export endpoint
      const response = await fetch(`http://localhost:8000/secure-computations/computations/${computationId}/export?format=${format}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to export computation result: ${response.statusText}`);
      }

      // Get the filename from the Content-Disposition header if available
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `computation_${computationId}.${format}`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=([^;]+)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/"/g, '');
        }
      }

      // Create a blob from the response
      const blob = await response.blob();
      
      // Create a download link and trigger the download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      
      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success(`Exported computation result as ${format.toUpperCase()}`);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setIsExporting(false);
    }
  };
      
      // Check if computation is still in progress or has error
      if (data.status && data.status !== 'completed') {
        if (data.status === 'error') {
          toast.error(`Computation error: ${data.error_message || 'Unknown error'}`);
        } else {
          toast.info(`Computation status: ${data.status_message || data.status}`);
          // If still processing, set up polling
          if (data.status === 'processing' || data.status === 'initialized') {
            setTimeout(fetchResult, 5000); // Poll every 5 seconds
          }
        }
      }
      
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
    // Handle loading, error, or in-progress states
    if (isLoading) {
      return <div className="text-center py-10">Loading results...</div>;
    }
    
    if (!result) {
      return <div className="text-center py-10">No result data available</div>;
    }
    
    // Handle non-completed computation status
    if (result.status && result.status !== 'completed') {
      return (
        <div className="text-center py-10">
          <div className="text-lg font-medium mb-2">
            Computation Status: {result.status}
          </div>
          <div className="text-gray-500">
            {result.status_message || 'Waiting for computation to complete'}
          </div>
          {result.progress && (
            <div className="mt-4 w-full max-w-md mx-auto">
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  className="bg-blue-600 h-2.5 rounded-full" 
                  style={{ width: `${result.progress_percentage || 0}%` }}
                ></div>
              </div>
              <div className="text-sm mt-1">{result.progress}</div>
            </div>
          )}
        </div>
      );
    }
    
    // If we have result data, render the visualization
    if (!result.data) return <div className="text-center py-10">No visualization data available</div>;

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

  const renderStatisticsTable = () => {
    if (!result || !result.data) return null;
    
    // Extract statistics from result data
    const stats = {};
    
    // Basic statistics
    if (result.data.mean !== undefined) stats['Mean'] = result.data.mean;
    if (result.data.median !== undefined) stats['Median'] = result.data.median;
    if (result.data.std_dev !== undefined) stats['Standard Deviation'] = result.data.std_dev;
    if (result.data.min !== undefined) stats['Minimum'] = result.data.min;
    if (result.data.max !== undefined) stats['Maximum'] = result.data.max;
    if (result.data.count !== undefined) stats['Count'] = result.data.count;
    
    // Advanced statistics
    if (result.data.variance !== undefined) stats['Variance'] = result.data.variance;
    if (result.data.range !== undefined) stats['Range'] = result.data.range;
    if (result.data.quartile_1 !== undefined) stats['First Quartile (Q1)'] = result.data.quartile_1;
    if (result.data.quartile_3 !== undefined) stats['Third Quartile (Q3)'] = result.data.quartile_3;
    if (result.data.iqr !== undefined) stats['Interquartile Range (IQR)'] = result.data.iqr;
    if (result.data.mode !== undefined) stats['Mode'] = result.data.mode;
    
    return (
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Statistic
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Value
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {Object.entries(stats).map(([name, value]) => (
              <tr key={name}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {typeof value === 'number' ? value.toFixed(4) : value}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
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
        
        <div className="flex justify-between items-center mb-4">
          <div className="flex flex-wrap gap-2 mb-2">
            <button
              onClick={() => setVisualizationType('statistics')}
              className={`px-4 py-2 rounded-md ${
                visualizationType === 'statistics'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Statistics Table
            </button>
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
          
          <div>
            <Dropdown as={ButtonGroup}>
              <Button 
                variant="outline-primary" 
                onClick={() => handleExport(exportFormat)}
                disabled={isExporting}
              >
                {isExporting ? 'Exporting...' : `Export as ${exportFormat.toUpperCase()}`}
              </Button>
              <Dropdown.Toggle split variant="outline-primary" id="dropdown-split-basic" />
              <Dropdown.Menu>
                <Dropdown.Item onClick={() => setExportFormat('json')}>JSON Format</Dropdown.Item>
                <Dropdown.Item onClick={() => setExportFormat('csv')}>CSV Format</Dropdown.Item>
              </Dropdown.Menu>
            </Dropdown>
          </div>
        </div>

        <div className="flex justify-center">
          {visualizationType === 'statistics' ? renderStatisticsTable() : renderVisualization()}
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