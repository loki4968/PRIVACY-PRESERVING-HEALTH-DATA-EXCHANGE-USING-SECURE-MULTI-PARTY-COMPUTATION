"use client";

import React, { useState, useEffect } from "react";
import { useForm, Controller } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { useDropzone } from "react-dropzone";
import Stepper from "../components/Stepper";
import { CustomButton } from "../components/ui/custom-button.jsx";
import { Card, CardTitle, CardContent, CardFooter } from "../components/ui/card.jsx";
import { Progress } from "../components/ui/progress.jsx";
import OTPVerification from "../components/OTPVerification";
import { API_ENDPOINTS, API_BASE_URL } from "../config/api.js";
import {
  Building2,
  Mail,
  Phone,
  Landmark,
  MapPin,
  ShieldCheck,
  UploadCloud,
  FileText,
  AlertCircle,
  Heart,
  Brain,
  Baby,
  Bone,
  Pill,
  Thermometer,
  Microscope,
  Stethoscope,
  Activity,
  Image,
  Files,
  Check,
  TestTube,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { toast } from 'react-hot-toast';

// Form validation schema
const uploadFormSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
  contact: z.string().min(1),
  type: z.string().min(1),
  location: z.string().min(1),
  privacyAccepted: z.literal(true),
});

// Health data categories
const healthCategories = [
  { 
    id: "blood_test", 
    label: "Blood Test", 
    icon: TestTube,
    description: "Complete blood count, metabolic panels, etc."
  },
  { 
    id: "vital_signs", 
    label: "Vital Signs", 
    icon: Activity,
    description: "Blood pressure, heart rate, temperature"
  },
  { 
    id: "medical_history", 
    label: "Medical History", 
    icon: Files,
    description: "Patient history and records"
  },
  { 
    id: "prescription", 
    label: "Prescription", 
    icon: Pill,
    description: "Medication and treatment plans"
  },
  { 
    id: "lab_results", 
    label: "Lab Results", 
    icon: Microscope,
    description: "Laboratory test results and analysis"
  },
  { 
    id: "imaging", 
    label: "Imaging", 
    icon: Image,
    description: "X-rays, MRI, CT scans"
  },
  { 
    id: "cardiology", 
    label: "Cardiology", 
    icon: Heart,
    description: "Heart-related data and ECGs"
  },
  { 
    id: "neurology", 
    label: "Neurology", 
    icon: Brain,
    description: "Neurological assessments and tests"
  },
  { 
    id: "pediatrics", 
    label: "Pediatrics", 
    icon: Baby,
    description: "Children's health records"
  },
  { 
    id: "orthopedics", 
    label: "Orthopedics", 
    icon: Bone,
    description: "Bone and joint related data"
  },
  { 
    id: "oncology", 
    label: "Oncology", 
    icon: FileText,
    description: "Cancer treatment and monitoring"
  },
  { 
    id: "endocrinology", 
    label: "Endocrinology", 
    icon: Thermometer,
    description: "Hormone and metabolic data"
  },
  { 
    id: "immunology", 
    label: "Immunology", 
    icon: ShieldCheck,
    description: "Immune system tests and data"
  },
  { 
    id: "gastroenterology", 
    label: "Gastroenterology", 
    icon: Stethoscope,
    description: "Digestive system records"
  },
  { 
    id: "pulmonology", 
    label: "Pulmonology", 
    icon: Activity,
    description: "Respiratory system data"
  },
  { 
    id: "other", 
    label: "Other", 
    icon: FileText,
    description: "Other medical records"
  },
];

export default function UploadPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, refreshToken } = useAuth();

  const initialStep = Number(searchParams.get("step")) || (user ? 2 : 1);
  const [step, setStep] = useState(initialStep);
  const [category, setCategory] = useState(null);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  // Add navigation state
  const [isNavigating, setIsNavigating] = useState(false);

  const [showVerification, setShowVerification] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [pendingUpload, setPendingUpload] = useState(null);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(uploadFormSchema),
    defaultValues: {
      name: "",
      email: "",
      contact: "",
      type: "",
      location: "",
      privacyAccepted: false,
    },
  });

  useEffect(() => {
    const checkUserAccess = async () => {
      if (!user) {
        console.log("No user, redirecting to login");
        router.push('/login');
        return;
      }

      if (!user.token) {
        console.log("No token, attempting to refresh");
        const refreshed = await refreshToken();
        if (!refreshed) {
          console.log("Token refresh failed, redirecting to login");
          router.push('/login');
          return;
        }
      }

      // Check for upload permission
      if (!user.permissions?.includes('write_patient_data')) {
        console.log("User lacks upload permission");
        toast.error("You don't have permission to upload files. Please contact your administrator.");
        // Only redirect if we're not already on the upload page
        if (!window.location.pathname.includes('/upload')) {
          router.push('/dashboard');
        }
        return;
      }

      console.log("User has required permissions");
      setStep(Number(searchParams.get("step")) || 2);
    };

    checkUserAccess();
  }, [user, searchParams, router, refreshToken]);

  const nextStep = () => setStep((prev) => prev + 1);

  const onSubmitOrg = () => handleSubmit(() => nextStep())();

  const handleCategorySelect = (cat) => {
    setCategory(cat);
    nextStep();
  };

  const handleUpload = async () => {
    if (!user || !user.token) {
      console.log("No user or token, redirecting to login");
      toast.error("Please login first");
      await navigateToPage("/login");
      return;
    }

    if (!file) {
      toast.error("Please select a file to upload");
      return;
    }

    if (!category) {
      toast.error("Please select a category");
      return;
    }

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
      toast.error("Only CSV files are allowed");
      return;
    }

    // Validate file size (10MB limit)
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB in bytes
    if (file.size > MAX_FILE_SIZE) {
      toast.error("File size must be less than 10MB");
      return;
    }

    setUploading(true);
    setProgress(20);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("category", category);

      // Use XMLHttpRequest instead of fetch for more reliable file upload
      const xhr = new XMLHttpRequest();
      
      // Create a Promise to handle the XHR request
      const uploadPromise = new Promise((resolve, reject) => {
        xhr.open('POST', API_ENDPOINTS.upload, true);
        
        // Set headers
        xhr.setRequestHeader('Authorization', `Bearer ${user.token}`);
        xhr.setRequestHeader('X-Force-Upload', 'true');
        
        // Handle response
        xhr.onload = function() {
          if (xhr.status >= 200 && xhr.status < 300) {
            try {
              const jsonResponse = JSON.parse(xhr.responseText);
              resolve(jsonResponse);
            } catch (e) {
              console.error("Failed to parse response:", e);
              reject(new Error("Failed to read server response"));
            }
          } else {
            try {
              const errorData = JSON.parse(xhr.responseText);
              reject(new Error(errorData.detail || 'Upload failed'));
            } catch (e) {
              reject(new Error('Upload failed'));
            }
          }
        };
        
        // Handle network errors
        xhr.onerror = function() {
          reject(new Error('Network error during upload'));
        };
        
        // Track upload progress
        xhr.upload.onprogress = function(e) {
          if (e.lengthComputable) {
            const percentComplete = Math.round((e.loaded / e.total) * 100);
            setProgress(percentComplete);
          }
        };
        
        // Send the form data
        xhr.send(formData);
      });
      
      // Wait for the upload to complete
      let responseData;
      try {
        responseData = await uploadPromise;
      } catch (e) {
        console.error("Upload error:", e);
        toast.error(e.message || "Failed to upload file");
        setUploading(false);
        setProgress(0);
        return;
      }

      // Check response status from responseData instead of uploadRes
      if (responseData?.status === 'error' || !responseData?.result_id) {
        toast.error(responseData?.detail || "Upload failed");
        setUploading(false);
        setProgress(0);
        return;
      }

      // Handle successful upload
      if (!responseData?.result_id) {
        console.error("Invalid success response:", responseData);
        toast.error("Invalid server response");
        setUploading(false);
        setProgress(0);
        return;
      }

      setProgress(100);
      setUploadSuccess(true);
      toast.success("File uploaded successfully!");
      
      // Wait briefly before redirecting
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Redirect to dashboard with result ID
      await navigateToPage(`/dashboard?view=results&id=${responseData.result_id}`);

    } catch (error) {
      console.error("Upload error:", error);
      toast.error("Upload failed. Please try again.");
      setUploading(false);
      setProgress(0);
    }
  };

  const handleVerifyOTP = async (otp) => {
    setVerifying(true);
    try {
      const response = await fetch(API_ENDPOINTS.verifyOtp, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify({
          email: user.email,
          otp: otp
        })
      });

      if (response.ok) {
        toast.success('Email verified successfully!');
        // Redirect to dashboard immediately after verification
        router.push('/dashboard');
      } else {
        const data = await response.json();
        toast.error(data.detail || 'Invalid OTP');
      }
    } catch (error) {
      console.error('Verification error:', error);
      toast.error('Failed to verify OTP');
    } finally {
      setVerifying(false);
      setPendingUpload(null);
    }
  };

  const handleResendOTP = async () => {
    await sendOTP();
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (files) => setFile(files[0]),
    accept: { "text/csv": [".csv"] },
    multiple: false,
  });

  // Function to handle navigation
  const navigateToPage = async (path) => {
    setIsNavigating(true);
    try {
      await router.push(path);
    } catch (error) {
      console.error("Navigation failed:", error);
      window.location.href = path;
    }
    setIsNavigating(false);
  };

  return (
    <div className="min-h-screen p-6 bg-gradient-to-br from-blue-50 via-white to-green-50">
      <div className="max-w-3xl mx-auto">
        <Stepper step={step} />

        {showVerification ? (
          <Card className="shadow-lg">
            <CardTitle className="text-2xl font-semibold text-gray-800 border-b border-gray-200 p-6">
              Email Verification Required
            </CardTitle>
            <CardContent className="p-6">
              <OTPVerification
                email={user.email}
                onVerify={handleVerifyOTP}
                resendOTP={handleResendOTP}
                loading={verifying}
              />
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Step 1: Organization Registration */}
            {step === 1 && (
              <Card>
                <CardTitle>Register Your Organization</CardTitle>
                <CardContent>
                  <form onSubmit={onSubmitOrg} className="space-y-4">
                    {[
                      { icon: Building2, key: "name", placeholder: "Organization Name" },
                      { icon: Mail, key: "email", placeholder: "Email" },
                      { icon: Phone, key: "contact", placeholder: "Contact Number" },
                      { icon: Landmark, key: "type", placeholder: "Type" },
                      { icon: MapPin, key: "location", placeholder: "Location" },
                    ].map(({ icon: Icon, key, placeholder }) => (
                      <div className="relative" key={key}>
                        <div className="absolute left-3 top-3 text-gray-400">
                          <Icon size={20} />
                        </div>
                        <Controller
                          name={key}
                          control={control}
                          render={({ field }) => (
                            <input
                              {...field}
                              placeholder={placeholder}
                              className="w-full pl-10 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            />
                          )}
                        />
                        {errors[key] && (
                          <p className="mt-1 text-sm text-red-500">{errors[key].message}</p>
                        )}
                      </div>
                    ))}

                    <div className="flex items-center space-x-2">
                      <Controller
                        name="privacyAccepted"
                        control={control}
                        render={({ field }) => (
                          <input
                            {...field}
                            type="checkbox"
                            checked={field.value}
                            onChange={(e) => field.onChange(e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                            id="privacy-accept"
                          />
                        )}
                      />
                      <label htmlFor="privacy-accept" className="text-sm text-gray-700 cursor-pointer flex items-center">
                        <ShieldCheck className="w-4 h-4 mr-1 text-green-500" />
                        I accept the privacy policy
                      </label>
                    </div>
                    {errors.privacyAccepted && (
                      <p className="text-sm text-red-500">You must accept the privacy policy</p>
                    )}

                    <CardFooter>
                      <CustomButton
                        type="submit"
                        variant="success"
                        size="large"
                        className="w-full"
                      >
                        Continue
                      </CustomButton>
                    </CardFooter>
                  </form>
                </CardContent>
              </Card>
            )}

            {/* Step 2: Category Selection */}
            {step === 2 && (
              <Card className="shadow-lg">
                <CardTitle className="text-2xl font-semibold text-gray-800 border-b border-gray-200 p-6">
                  Select Health Category
                </CardTitle>
                <CardContent className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {healthCategories.map(({ id, label, icon: Icon, description }) => {
                      if (!Icon) return null;
                      const isSelected = category === id;
                      return (
                        <motion.div
                          key={id}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          <button
                            onClick={() => handleCategorySelect(id)}
                            className={`
                              w-full h-full p-4 rounded-xl border-2 transition-all duration-200
                              ${isSelected 
                                ? 'border-blue-500 bg-blue-50 shadow-md ring-2 ring-blue-200' 
                                : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                              }
                              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                            `}
                          >
                            <div className="flex items-start space-x-4">
                              <div className={`
                                p-3 rounded-lg shrink-0
                                ${isSelected ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600'}
                              `}>
                                <Icon className="w-6 h-6" />
                              </div>
                              <div className="flex-1 text-left min-w-0">
                                <h3 className={`font-medium truncate ${isSelected ? 'text-blue-700' : 'text-gray-900'}`}>
                                  {label}
                                </h3>
                                <p className={`text-sm mt-1 line-clamp-2 ${isSelected ? 'text-blue-600' : 'text-gray-500'}`}>
                                  {description}
                                </p>
                              </div>
                              {isSelected && (
                                <div className="text-blue-500 shrink-0">
                                  <Check className="w-5 h-5" />
                                </div>
                              )}
                            </div>
                          </button>
                        </motion.div>
                      );
                    })}
                  </div>
                </CardContent>
                <CardFooter className="p-6 border-t border-gray-200">
                  <CustomButton
                    onClick={() => setStep(3)}
                    disabled={!category}
                    variant={category ? "success" : "default"}
                    size="large"
                    className="w-full"
                  >
                    Continue with {category ? healthCategories.find(c => c.id === category)?.label || "Selected Category" : "Selected Category"}
                  </CustomButton>
                </CardFooter>
              </Card>
            )}

            {/* Step 3: File Upload */}
            {step === 3 && (
              <Card className="shadow-lg">
                <CardTitle className="text-2xl font-semibold text-gray-800 border-b border-gray-200 p-6">
                  Upload Report: <span className="text-blue-600">{healthCategories.find(c => c.id === category)?.label}</span>
                </CardTitle>
                <CardContent className="p-6">
                  <div
                    {...getRootProps()}
                    className={`
                      p-8 border-2 border-dashed rounded-xl text-center cursor-pointer
                      transition-colors duration-200 relative
                      ${isDragActive 
                        ? "border-blue-500 bg-blue-50 ring-2 ring-blue-200" 
                        : "border-gray-300 hover:border-blue-400 hover:bg-gray-50"
                      }
                    `}
                  >
                    <input {...getInputProps()} />
                    <UploadCloud 
                      className={`mx-auto mb-4 w-12 h-12 ${file ? 'text-green-500' : 'text-gray-400'}`}
                    />
                    <div className="text-lg font-medium mb-2">
                      {file ? (
                        <span className="text-green-600">{file.name}</span>
                      ) : isDragActive ? (
                        "Drop the file here"
                      ) : (
                        "Drag & drop CSV file here or click to browse"
                      )}
                    </div>
                    {file && (
                      <p className="text-sm text-gray-500">
                        Size: {(file.size / 1024).toFixed(2)} KB
                      </p>
                    )}
                    {!file && (
                      <p className="text-sm text-gray-500">
                        Only CSV files are accepted
                      </p>
                    )}
                  </div>

                  {uploading && (
                    <div className="mt-6">
                      <Progress value={progress} className="h-2 bg-gray-100" />
                      <p className="text-sm text-gray-600 text-center mt-2">
                        {progress}% Complete
                      </p>
                    </div>
                  )}

                  <div className="mt-6">
                    <CustomButton
                      onClick={handleUpload}
                      disabled={uploading || !file}
                      loading={uploading}
                      variant={uploadSuccess ? "success" : "default"}
                      size="large"
                      className="w-full"
                      icon={uploadSuccess ? Check : UploadCloud}
                    >
                      {uploading ? `Uploading... ${progress}%` : 
                       uploadSuccess ? "Upload Complete!" : 
                       "Upload Report"}
                    </CustomButton>
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </div>
    </div>
  );
}
