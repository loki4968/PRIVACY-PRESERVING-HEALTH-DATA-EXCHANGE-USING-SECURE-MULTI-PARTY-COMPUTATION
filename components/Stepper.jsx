import React from "react";

export default function Stepper({ step }) {
  const steps = ["Register", "Category", "Upload"];
  return (
    <div className="flex justify-between mb-6">
      {steps.map((label, index) => (
        <div
          key={label}
          className={`flex-1 text-center text-sm font-semibold ${index + 1 === step ? "text-blue-600" : "text-gray-500"}`}
        >
          {index + 1}. {label}
        </div>
      ))}
    </div>
  );
}

