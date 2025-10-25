import React from 'react';
import { FiAlertTriangle } from 'react-icons/fi';

/**
 * A reusable error display component that shows an error message with an icon
 * and optional action buttons.
 */
const ErrorDisplay = ({ 
  title = 'Error', 
  message, 
  icon = <FiAlertTriangle className="text-red-500" size={48} />,
  primaryAction,
  secondaryAction
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 bg-white rounded-lg shadow-sm">
      <div className="flex flex-col items-center text-center max-w-md">
        <div className="mb-4">
          {icon}
        </div>
        
        <h2 className="text-xl font-semibold text-gray-800 mb-2">{title}</h2>
        
        <p className="text-gray-600 mb-6">{message}</p>
        
        {(primaryAction || secondaryAction) && (
          <div className="flex gap-4">
            {primaryAction && (
              <button
                onClick={primaryAction.onClick}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                {primaryAction.label}
              </button>
            )}
            
            {secondaryAction && (
              <button
                onClick={secondaryAction.onClick}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                {secondaryAction.label}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ErrorDisplay;