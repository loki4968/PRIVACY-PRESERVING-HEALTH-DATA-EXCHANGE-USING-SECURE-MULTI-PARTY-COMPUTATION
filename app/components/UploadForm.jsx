"use client";

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, FileText, CheckCircle, AlertCircle, FileJson, FileSpreadsheet, File, ChevronDown } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { CustomButton } from './ui/custom-button';
import { toast } from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { API_ENDPOINTS, API_BASE_URL } from '../config/api.js';

const UploadForm = ({ onUploadSuccess }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('auto');
  const { user } = useAuth(); // Get user from auth context
  
  // Available data categories
  const categories = [
    { id: 'auto', name: 'Auto-detect' },
    { id: 'blood_sugar', name: 'Blood Sugar' },
    { id: 'blood_test', name: 'Blood Test' },
    { id: 'vital_signs', name: 'Vital Signs' },
    { id: 'medical_history', name: 'Medical History' }
  ];
  
  const getFileIcon = (fileName) => {
    const extension = fileName.split('.').pop().toLowerCase();
    
    switch (extension) {
      case 'csv':
        return <FileSpreadsheet className="h-6 w-6 text-green-500" />;
      case 'json':
        return <FileJson className="h-6 w-6 text-blue-500" />;
      case 'xls':
      case 'xlsx':
        return <FileSpreadsheet className="h-6 w-6 text-yellow-500" />;
      default:
        return <File className="h-6 w-6 text-gray-500" />;
    }
  };

  const getFileItemStyle = (status) => {
    switch (status) {
      case 'success':
        return 'bg-green-50 border-green-200 shadow-sm';
      case 'error':
        return 'bg-red-50 border-red-200 shadow-sm';
      case 'uploading':
        return 'bg-blue-50 border-blue-200 shadow-sm';
      default:
        return 'bg-white border-gray-200 hover:border-gray-300 shadow-sm';
    }
  };

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      progress: 0,
      status: 'pending'
    }));
    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json'],
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    multiple: true
  });

  const removeFile = (fileId) => {
    setFiles(files => files.filter(f => f.id !== fileId));
  };

  const uploadFiles = async () => {
    if (files.length === 0) {
      toast.error('Please select files to upload');
      return;
    }

    // Check if user is authenticated
    if (!user || !user.token) {
      toast.error('Please login first');
      return;
    }

    console.log('Starting upload with token:', user.token.substring(0, 10) + '...');
    setUploading(true);
    
    // Log upload attempt for debugging
    console.log('Upload attempt initiated with', files.length, 'files');

    try {
      for (const fileObj of files) {
        const formData = new FormData();
        formData.append('file', fileObj.file);
        
        // Use the selected category from dropdown
        formData.append('category', selectedCategory); // Add selected category

        setFiles(prev =>
          prev.map(f =>
            f.id === fileObj.id ? { ...f, status: 'uploading', progress: 0 } : f
          )
        );

        try {
          // Use XMLHttpRequest instead of fetch for file upload
          const xhr = new XMLHttpRequest();
          
          // Create a Promise to handle the XHR request
          const uploadPromise = new Promise((resolve, reject) => {
            xhr.open('POST', API_ENDPOINTS.upload, true);
            
            // Set headers
            xhr.setRequestHeader('Authorization', `Bearer ${user.token}`);
            xhr.setRequestHeader('X-Force-Upload', 'true'); // This header is required for uploads to work
            
            // Log headers for debugging
            console.log('Request headers:', {
              'Authorization': 'Bearer [token]',
              'X-Force-Upload': 'true'
            });
            
            // Log request details for debugging
            console.log('Upload request to:', API_ENDPOINTS.upload);
            console.log('Headers set:', {
              'Authorization': `Bearer ${user.token.substring(0, 10)}...`,
              'X-Force-Upload': 'true'
            });
            console.log('File details:', {
              name: fileObj.file.name,
              size: fileObj.file.size,
              type: fileObj.file.type
            });
            
            // Handle response
            xhr.onload = function() {
              if (xhr.status >= 200 && xhr.status < 300) {
                console.log('Upload successful:', xhr.responseText);
                resolve({
                  ok: true,
                  json: () => JSON.parse(xhr.responseText)
                });
              } else {
                console.error('Upload failed with status:', xhr.status);
                console.error('Response:', xhr.responseText);
                try {
                  const errorData = JSON.parse(xhr.responseText);
                  resolve({
                    ok: false,
                    json: () => errorData,
                    error: errorData.detail || 'Upload failed'
                  });
                } catch (e) {
                  resolve({
                    ok: false,
                    error: 'Upload failed with status ' + xhr.status
                  });
                }
              }
            };
            
            // Handle network errors
            xhr.onerror = function() {
              console.error('Network error occurred during upload');
              reject(new Error('Network error during upload - Please check if the backend server is running and accessible'));
            };
            
            // Add timeout handling
            xhr.timeout = 30000; // 30 seconds timeout
            xhr.ontimeout = function() {
              console.error('Request timed out');
              reject(new Error('Upload request timed out - Server might be busy or unresponsive'));
            };
            
            // Track upload progress
            xhr.upload.onprogress = function(e) {
              if (e.lengthComputable) {
                const percentComplete = Math.round((e.loaded / e.total) * 100);
                setFiles(prev =>
                  prev.map(f =>
                    f.id === fileObj.id ? { ...f, progress: percentComplete } : f
                  )
                );
              }
            };
            
            // Send the form data
            xhr.send(formData);
          });
          
          // Wait for the upload to complete
          const response = await uploadPromise;
          let responseData;
          
          try {
            responseData = JSON.parse(xhr.responseText);
          } catch (e) {
            console.error('Failed to parse response:', e);
            throw new Error('Invalid response format');
          }

          if (!response.ok) {
            // Handle error response
            const errorMessage = response.error || 
              (responseData && responseData.detail ? responseData.detail : 'Upload failed');
            
            console.error('Upload error details:', errorMessage);
            throw new Error(errorMessage);
          }

          setFiles(prev =>
            prev.map(f =>
              f.id === fileObj.id ? { ...f, status: 'success', progress: 100 } : f
            )
          );

          toast.success(`File ${fileObj.file.name} uploaded successfully!`);
          
          // Get the result_id from the response
          const resultId = responseData.result_id;
          
          // Call success callback if provided
          if (onUploadSuccess) {
            onUploadSuccess(fileObj.file);
          }
          
          // Redirect to the result page if we have a result_id
          if (resultId) {
            window.location.href = `/result/${resultId}`;
          }

        } catch (error) {
          console.error('Upload error:', error);
          setFiles(prev =>
            prev.map(f =>
              f.id === fileObj.id ? { ...f, status: 'error', progress: 0, error: error.message } : f
            )
          );
          toast.error(`Failed to upload ${fileObj.file.name}: ${error.message}`);
        }
      }
    } catch (error) {
      console.error('Upload process error:', error);
      toast.error('Upload process failed');
    } finally {
      setUploading(false);
    }
  };

  const clearFiles = () => {
    setFiles([]);
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-xl p-6 border border-gray-100">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Health Data Files</h2>
          <p className="text-gray-600">Drag and drop your health data files here or click to browse</p>
        </div>
        
        <div className="mb-6">
          <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
            Select Data Category
          </label>
          <div className="relative">
            <select
              id="category"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
            <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
              <ChevronDown className="h-4 w-4 text-gray-400" />
            </div>
          </div>
          <p className="mt-2 text-sm text-gray-500">
            Select "Auto-detect" to let the system determine the data type, or choose a specific category for more accurate analysis
          </p>
        </div>

        <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-10 text-center cursor-pointer transition-all duration-300 shadow-sm ${
          isDragActive
            ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
        }`}
      >
          <input {...getInputProps()} />
          <Upload className={`mx-auto h-16 w-16 mb-4 transition-colors duration-300 ${isDragActive ? 'text-blue-500' : 'text-gray-400'}`} />
          <p className="text-lg font-medium text-gray-700 mb-3">
            {isDragActive ? 'Drop the files here' : 'Drag & drop files here, or click to select'}
          </p>
          <div className="flex justify-center space-x-2 mb-2">
            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">CSV</span>
            <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium">JSON</span>
            <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-xs font-medium">Excel</span>
          </div>
          <p className="text-sm text-gray-500">
            For best results, use properly formatted health data files
          </p>
        </div>

        {files.length > 0 && (
          <div className="mt-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Selected Files ({files.length})
              </h3>
              <div className="space-x-2">
                <CustomButton
                  onClick={clearFiles}
                  variant="outline"
                  size="sm"
                  className="shadow-sm border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 font-medium rounded-md transition-all"
                >
                  <X className="mr-2 h-4 w-4" />
                  Clear All
                </CustomButton>
                <CustomButton
                  onClick={uploadFiles}
                  disabled={uploading}
                  size="sm"
                  loading={uploading}
                  className="shadow-sm border border-blue-500 bg-blue-600 text-white hover:bg-blue-700 font-medium rounded-md transition-all"
                >
                  <Upload className="mr-2 h-4 w-4" />
                  {uploading ? 'Uploading...' : 'Upload All'}
                </CustomButton>
              </div>
            </div>

            <div className="space-y-3">
              <AnimatePresence>
                {files.map((fileObj) => (
                  <motion.div
                    key={fileObj.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className={`flex items-center justify-between p-4 rounded-lg border shadow-sm ${fileObj.status === 'success' ? 'bg-green-50 border-green-200' : fileObj.status === 'error' ? 'bg-red-50 border-red-200' : 'bg-white border-gray-200'}`}
                  >
                    <div className="flex items-center space-x-3">
                      <FileText className={`h-5 w-5 ${fileObj.status === 'success' ? 'text-green-500' : fileObj.status === 'error' ? 'text-red-500' : 'text-gray-500'}`} />
                      <div>
                        <p className="font-medium text-gray-900">{fileObj.file.name}</p>
                        <p className="text-sm text-gray-500">
                          {(fileObj.file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <div className="flex items-center space-x-2">
                        {fileObj.status === 'pending' && (
                          <span className="text-sm font-medium px-2.5 py-1 bg-gray-100 text-gray-600 rounded-full">Ready</span>
                        )}
                        {fileObj.status === 'uploading' && (
                          <div className="flex items-center space-x-2">
                            <div className="w-24 bg-gray-200 rounded-full h-2.5">
                              <div
                                className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                                style={{ width: `${fileObj.progress}%` }}
                              />
                            </div>
                            <span className="text-sm font-medium text-blue-600">{fileObj.progress}%</span>
                          </div>
                        )}
                        {fileObj.status === 'success' && (
                          <div className="flex items-center space-x-2 text-green-600 px-2.5 py-1 bg-green-100 rounded-full">
                            <CheckCircle className="h-4 w-4" />
                            <span className="text-sm font-medium">Success</span>
                          </div>
                        )}
                        {fileObj.status === 'error' && (
                          <div className="flex items-center space-x-2 text-red-600 px-2.5 py-1 bg-red-100 rounded-full">
                            <AlertCircle className="h-4 w-4" />
                            <span className="text-sm font-medium">Failed</span>
                          </div>
                        )}
                        {fileObj.status === 'error' && fileObj.error && (
                          <div className="mt-1 text-xs text-red-600">
                            {fileObj.error}
                          </div>
                        )}
                      </div>

                      <button
                        onClick={() => removeFile(fileObj.id)}
                        className="text-gray-400 hover:text-red-500 transition-colors p-1 rounded-full hover:bg-gray-100"
                        disabled={fileObj.status === 'uploading'}
                        aria-label="Remove file"
                      >
                        <X className="h-5 w-5" />
                      </button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadForm;