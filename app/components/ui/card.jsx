"use client";

import { motion } from "framer-motion";

export function Card({ 
  children, 
  className = "", 
  animate = true,
  ...props 
}) {
  const Component = animate ? motion.div : "div";
  
  return (
    <Component
      initial={animate ? { opacity: 0, y: 20 } : undefined}
      animate={animate ? { opacity: 1, y: 0 } : undefined}
      transition={{ duration: 0.3 }}
      className={`bg-white rounded-xl shadow-lg p-6 ${className}`}
      {...props}
    >
      {children}
    </Component>
  );
}

export function CardTitle({ children, className = "", ...props }) {
  return (
    <h2 className={`text-2xl font-bold mb-4 ${className}`} {...props}>
      {children}
    </h2>
  );
}

export function CardContent({ children, className = "", ...props }) {
  return (
    <div className={`space-y-4 ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardFooter({ children, className = "", ...props }) {
  return (
    <div className={`mt-6 flex items-center justify-end space-x-4 ${className}`} {...props}>
      {children}
    </div>
  );
} 