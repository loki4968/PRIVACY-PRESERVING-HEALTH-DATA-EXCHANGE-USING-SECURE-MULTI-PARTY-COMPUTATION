"use client";

import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";

export function CustomButton({ 
  children, 
  className = "", 
  variant = "default",
  loading = false,
  disabled = false,
  onClick,
  type = "button",
  size = "default",
  icon: Icon,
  ...props 
}) {
  const baseStyles = "inline-flex items-center justify-center rounded-lg font-medium transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";
  
  const variants = {
    default: "bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500",
    success: "bg-green-600 hover:bg-green-700 text-white focus:ring-green-500",
    danger: "bg-red-600 hover:bg-red-700 text-white focus:ring-red-500",
    outline: "border-2 border-blue-600 text-blue-600 hover:bg-blue-50 focus:ring-blue-500",
    ghost: "hover:bg-gray-100 text-gray-700 focus:ring-gray-500",
  };

  const sizes = {
    small: "px-3 py-1.5 text-sm",
    default: "px-4 py-2",
    large: "px-6 py-3 text-lg",
  };

  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      type={type}
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      onClick={onClick}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
      ) : Icon ? (
        <Icon className="w-4 h-4 mr-2" />
      ) : null}
      {children}
    </motion.button>
  );
} 