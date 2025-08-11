"use client";

import { motion } from "framer-motion";
import { Check, Building2, Grid, Upload } from "lucide-react";

const steps = [
  { id: 1, title: "Organization", icon: Building2 },
  { id: 2, title: "Category", icon: Grid },
  { id: 3, title: "Upload", icon: Upload },
];

export default function Stepper({ step }) {
  return (
    <nav className="mb-8">
      <ol className="flex items-center w-full">
        {steps.map((s, i) => {
          const Icon = s.icon;
          const isActive = step === s.id;
          const isComplete = step > s.id;
          
          return (
            <li key={s.id} className="flex items-center w-full">
              <div className="flex flex-col items-center flex-1">
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: i * 0.2 }}
                  className={`
                    flex items-center justify-center w-10 h-10 rounded-full
                    transition-colors duration-200
                    ${isComplete ? "bg-green-500" : isActive ? "bg-blue-500" : "bg-gray-200"}
                  `}
                >
                  {isComplete ? (
                    <Check className="w-6 h-6 text-white" />
                  ) : (
                    <Icon className={`w-5 h-5 ${isActive ? "text-white" : "text-gray-500"}`} />
                  )}
                </motion.div>
                <motion.span
                  initial={{ y: 10, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: i * 0.2 + 0.1 }}
                  className={`
                    mt-2 text-sm font-medium
                    ${isComplete ? "text-green-500" : isActive ? "text-blue-500" : "text-gray-500"}
                  `}
                >
                  {s.title}
                </motion.span>
              </div>
              {i < steps.length - 1 && (
                <div
                  className={`
                    h-0.5 w-full mx-2
                    ${step > i + 1 ? "bg-green-500" : "bg-gray-200"}
                  `}
                />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
} 