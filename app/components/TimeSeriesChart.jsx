import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const TimeSeriesChart = ({ data, metricType }) => {
  const getMetricConfig = (type) => {
    const configs = {
      blood_pressure: {
        label: 'Blood Pressure',
        color: 'rgb(239, 68, 68)',
        unit: 'mmHg'
      },
      blood_sugar: {
        label: 'Blood Sugar',
        color: 'rgb(59, 130, 246)',
        unit: 'mg/dL'
      },
      heart_rate: {
        label: 'Heart Rate',
        color: 'rgb(34, 197, 94)',
        unit: 'bpm'
      }
    };
    return configs[type] || configs.blood_pressure;
  };

  const config = getMetricConfig(metricType);
  const labels = Array.from({ length: data.length }, (_, i) => `Reading ${i + 1}`);

  const chartData = {
    labels,
    datasets: [
      {
        label: config.label,
        data: data,
        fill: true,
        borderColor: config.color,
        backgroundColor: `${config.color}20`,
        tension: 0.4
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.parsed.y} ${config.unit}`
        }
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          callback: (value) => `${value} ${config.unit}`
        }
      },
      x: {
        grid: {
          display: false
        }
      }
    }
  };

  return (
    <div className="bg-white rounded-lg p-4 shadow">
      <h3 className="text-lg font-medium mb-4">{config.label} Trend</h3>
      <div className="h-[300px]">
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
};

export default TimeSeriesChart; 