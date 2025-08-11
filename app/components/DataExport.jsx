"use client";

import React, { useState } from 'react';
import { Download, FileText, Table, AlertCircle, CheckCircle } from 'lucide-react';
import { CustomButton } from './ui/custom-button';
import { toast } from 'react-hot-toast';

const DataExport = ({ data }) => {
  const [exportFormat, setExportFormat] = useState('csv');
  const [isExporting, setIsExporting] = useState(false);
  const [selectedFields, setSelectedFields] = useState([
    'id',
    'filename',
    'created_at',
    'status',
    'metrics'
  ]);

  const exportFormats = [
    { id: 'csv', label: 'CSV', icon: <FileText className="w-5 h-5" /> },
    { id: 'excel', label: 'Excel', icon: <Table className="w-5 h-5" /> },
    { id: 'json', label: 'JSON', icon: <FileText className="w-5 h-5" /> }
  ];

  const availableFields = [
    { id: 'id', label: 'Record ID' },
    { id: 'filename', label: 'Filename' },
    { id: 'created_at', label: 'Creation Date' },
    { id: 'status', label: 'Status' },
    { id: 'metrics', label: 'Health Metrics' }
  ];

  const handleExport = async () => {
    if (!data || data.length === 0) {
      toast.error('No data available to export');
      return;
    }

    setIsExporting(true);
    try {
      // Filter data based on selected fields
      const filteredData = data.map(record => {
        const filtered = {};
        selectedFields.forEach(field => {
          filtered[field] = record[field];
        });
        return filtered;
      });

      // Convert data to selected format
      let exportData;
      let filename;
      let mimeType;

      switch (exportFormat) {
        case 'csv':
          exportData = convertToCSV(filteredData);
          filename = 'health_data_export.csv';
          mimeType = 'text/csv';
          break;
        case 'excel':
          exportData = convertToExcel(filteredData);
          filename = 'health_data_export.xlsx';
          mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
          break;
        case 'json':
          exportData = JSON.stringify(filteredData, null, 2);
          filename = 'health_data_export.json';
          mimeType = 'application/json';
          break;
        default:
          throw new Error('Unsupported export format');
      }

      // Create download link
      const blob = new Blob([exportData], { type: mimeType });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success('Data exported successfully');
    } catch (error) {
      console.error('Export error:', error);
      toast.error('Failed to export data');
    } finally {
      setIsExporting(false);
    }
  };

  const convertToCSV = (data) => {
    const headers = selectedFields.join(',');
    const rows = data.map(record => {
      return selectedFields.map(field => {
        const value = record[field];
        return typeof value === 'object' ? JSON.stringify(value) : value;
      }).join(',');
    });
    return [headers, ...rows].join('\n');
  };

  const convertToExcel = (data) => {
    // For simplicity, we'll use CSV format for Excel
    // In a real application, you would use a library like xlsx
    return convertToCSV(data);
  };

  return (
    <div className="space-y-6">
      {/* Export Format Selection */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Export Format</h3>
        <div className="grid grid-cols-3 gap-4">
          {exportFormats.map(format => (
            <button
              key={format.id}
              onClick={() => setExportFormat(format.id)}
              className={`flex items-center justify-center space-x-2 p-4 rounded-lg border ${
                exportFormat === format.id
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 hover:bg-gray-50'
              }`}
            >
              {format.icon}
              <span>{format.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Field Selection */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Fields to Export</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {availableFields.map(field => (
            <label
              key={field.id}
              className="flex items-center space-x-3"
            >
              <input
                type="checkbox"
                checked={selectedFields.includes(field.id)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setSelectedFields([...selectedFields, field.id]);
                  } else {
                    setSelectedFields(selectedFields.filter(f => f !== field.id));
                  }
                }}
                className="form-checkbox h-5 w-5 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
              />
              <span className="text-gray-700">{field.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Export Button */}
      <div className="flex justify-end">
        <CustomButton
          onClick={handleExport}
          disabled={isExporting || selectedFields.length === 0}
          className={`flex items-center space-x-2 ${
            isExporting ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {isExporting ? (
            <>
              <AlertCircle className="w-5 h-5 animate-spin" />
              <span>Exporting...</span>
            </>
          ) : (
            <>
              <Download className="w-5 h-5" />
              <span>Export Data</span>
            </>
          )}
        </CustomButton>
      </div>
    </div>
  );
};

export default DataExport; 