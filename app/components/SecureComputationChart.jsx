'use client';

import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

const SecureComputationChart = ({ computation, metricTypes, data, type }) => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  
  // Helper function to get security method display name
  const getSecurityMethodDisplay = (method) => {
    switch(method) {
      case 'standard': return 'Standard Encryption';
      case 'homomorphic': return 'Homomorphic Encryption';
      case 'hybrid': return 'Hybrid (SMPC + Homomorphic)';
      default: return method || 'Standard Encryption';
    }
  };

  useEffect(() => {
    // Clean up previous chart instance if it exists
    if (chartInstance.current) {
      chartInstance.current.destroy();
    }

    // Handle both direct data passing and computation object
    if (!computation?.result && !data) return;

    const ctx = chartRef.current.getContext('2d');
    
    // Determine if we're using direct data or computation object
    const isDirectData = !!data;
    
    // Get metric type information
    let metricType = { label: 'Value', unit: '' };
    if (metricTypes && computation?.metric_type) {
      metricType = metricTypes.find(m => m.id === computation.metric_type) || {
        label: computation.metric_type,
        unit: ''
      };
    }

    // Prepare data for the chart
    const chartData = {
      labels: ['Aggregate Result'],
      datasets: [
        {
          label: isDirectData ? (type || 'Value') : `${metricType.label} (${metricType.unit})`,
          data: [isDirectData ? (Array.isArray(data) ? data[0] : data) : computation.result.final_result],
          backgroundColor: 'rgba(54, 162, 235, 0.5)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }
      ]
    };

    // If there's individual data (for comparison), add it
    if (isDirectData && Array.isArray(data) && data.length > 1) {
      // Add labels for each data point when direct data is provided
      chartData.labels = data.map((_, idx) => idx === 0 ? 'Aggregate Result' : `Data Point ${idx}`);
      chartData.datasets[0].data = data;
    } else if (computation?.result?.individual_contributions) {
      const individualData = {
        label: 'Individual Contributions',
        data: computation.result.individual_contributions.map(c => c.value),
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1
      };
      
      chartData.labels = [
        'Aggregate Result',
        ...computation.result.individual_contributions.map((_, i) => `Participant ${i+1}`)
      ];
      
      chartData.datasets[0].data = [
        computation.result.final_result,
        ...Array(computation.result.individual_contributions.length).fill(null)
      ];
      
      chartData.datasets.push({
        label: 'Individual Contributions',
        data: [
          null,
          ...computation.result.individual_contributions.map(c => c.value)
        ],
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1
      });
    }

    // Create the chart
    chartInstance.current = new Chart(ctx, {
      type: 'bar',
      data: chartData,
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: `Secure Computation Results: ${metricType.label}`,
            font: {
              size: 16
            }
          },
          subtitle: {
            display: true,
            text: `Security: ${getSecurityMethodDisplay(computation.security_method)}${computation.threshold ? ` | Threshold: ${computation.threshold}` : ''}`,
            font: {
              size: 14,
              style: 'italic'
            },
            padding: {
              bottom: 10
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                let label = context.dataset.label || '';
                if (label) {
                  label += ': ';
                }
                if (context.parsed.y !== null) {
                  label += context.parsed.y.toFixed(2) + ' ' + metricType.unit;
                }
                return label;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            title: {
              display: true,
              text: metricType.unit
            }
          }
        }
      }
    });

    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [computation, metricTypes]);

  if (!computation?.result && !data) {
    return <div className="p-4 text-center text-gray-500">No results available to display</div>;
  }

  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <h3 className="text-lg font-medium mb-4">Result Visualization</h3>
      <div className="h-64">
        <canvas ref={chartRef} />
      </div>
      {computation && (
        <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-600">Security Method:</p>
            <p className="font-medium">{computation.security_method || 'Standard'}</p>
          </div>
          <div>
            <p className="text-gray-600">Participants:</p>
            <p className="font-medium">{computation.result.num_parties}</p>
          </div>
          {computation.result.computation_time && (
            <div>
              <p className="text-gray-600">Computation Time:</p>
              <p className="font-medium">{computation.result.computation_time.toFixed(2)}ms</p>
            </div>
          )}
          {computation.threshold && (
            <div>
              <p className="text-gray-600">Threshold:</p>
              <p className="font-medium">{computation.threshold} of {computation.participating_orgs.length}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SecureComputationChart;