"use client";

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { CustomButton } from './ui/custom-button';
import { toast } from 'react-hot-toast';

const UploadForm = ({ onUploadSuccess }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

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

    setUploading(true);

    try {
      for (const fileObj of files) {
        const formData = new FormData();
        formData.append('file', fileObj.file);

        setFiles(prev =>
          prev.map(f =>
            f.id === fileObj.id ? { ...f, status: 'uploading', progress: 0 } : f
          )
        );

        try {
          const response = await fetch('http://localhost:8000/upload', {
            method: 'POST',
            body: formData
          });

          if (!response.ok) {
            throw new Error('Upload failed');
          }

          setFiles(prev =>
            prev.map(f =>
              f.id === fileObj.id ? { ...f, status: 'completed', progress: 100 } : f
            )
          );

          toast.success(`${fileObj.file.name} uploaded successfully`);
        } catch (error) {
          setFiles(prev =>
            prev.map(f =>
              f.id === fileObj.id ? { ...f, status: 'error', progress: 0 } : f
            )
          );
          toast.error(`Failed to upload ${fileObj.file.name}`);
        }
      }

      onUploadSuccess?.();

      setTimeout(() => {
        setFiles(prev => prev.filter(f => f.status !== 'completed'));
      }, 3000);
    } finally {
      setUploading(false);
    }
  };

  const getFileIcon = (file) => {
    const extension = file.name.split('.').pop().toLowerCase();
    switch (extension) {
      case 'csv':
        return <FileText className="w-5 h-5 text-green-500" />;
      case 'json':
        return <FileText className="w-5 h-5 text-blue-500" />;
      case 'xls':
      case 'xlsx':
        return <FileText className="w-5 h-5 text-purple-500" />;
      default:
        return <FileText className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'uploading':
        return (
          <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <Upload className={`w-12 h-12 mx-auto mb-4 ${
          isDragActive ? 'text-blue-500' : 'text-gray-400'
        }`} />
        <p className="text-lg font-medium text-gray-700">
          {isDragActive
            ? 'Drop the files here...'
            : 'Drag & drop files here, or click to select files'
          }
        </p>
        <p className="mt-2 text-sm text-gray-500">
          Supports CSV, JSON, XLS, and XLSX files
        </p>
      </div>

      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden"
          >
            <div className="p-4">
              <h3 className="text-lg font-semibold text-gray-900">Selected Files</h3>
            </div>
            <div className="border-t border-gray-200">
              {files.map((fileObj) => (
                <motion.div
                  key={fileObj.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center justify-between p-4 border-b border-gray-200 last:border-0"
                >
                  <div className="flex items-center space-x-3">
                    {getFileIcon(fileObj.file)}
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {fileObj.file.name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {(fileObj.file.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(fileObj.status)}
                    {fileObj.status === 'pending' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          removeFile(fileObj.id);
                        }}
                        className="p-1 hover:bg-gray-100 rounded-full"
                      >
                        <X className="w-5 h-5 text-gray-400" />
                      </button>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {files.length > 0 && (
        <div className="flex justify-end">
          <CustomButton
            onClick={uploadFiles}
            disabled={uploading}
            className={`flex items-center space-x-2 ${
              uploading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {uploading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Uploading...</span>
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                <span>Upload {files.length} {files.length === 1 ? 'File' : 'Files'}</span>
              </>
            )}
          </CustomButton>
        </div>
      )}
    </div>
  );
};

export default UploadForm; 