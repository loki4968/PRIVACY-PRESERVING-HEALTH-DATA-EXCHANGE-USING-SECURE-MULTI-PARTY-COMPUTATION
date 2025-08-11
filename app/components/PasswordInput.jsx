'use client';

import { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

export default function PasswordInput({ 
    id, 
    name, 
    value, 
    onChange, 
    placeholder, 
    required = false,
    className = "",
    label
}) {
    const [showPassword, setShowPassword] = useState(false);
    const [isFocused, setIsFocused] = useState(false);

    return (
        <div>
            {label && (
                <label htmlFor={id} className="block text-sm font-medium text-gray-700 mb-1">
                    {label}
                </label>
            )}
            <div className="relative mt-1 group">
                <input
                    id={id}
                    name={name}
                    type={showPassword ? "text" : "password"}
                    required={required}
                    className={`block w-full px-4 py-3 pr-12 border ${
                        isFocused 
                            ? 'border-blue-500 ring-2 ring-blue-200' 
                            : 'border-gray-200 group-hover:border-gray-300'
                    } rounded-lg shadow-sm placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ease-in-out ${className}`}
                    placeholder={placeholder}
                    value={value}
                    onChange={onChange}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                />
                <button
                    type="button"
                    className={`absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600 focus:outline-none transition-colors duration-200 ${
                        isFocused ? 'text-blue-500' : ''
                    }`}
                    onClick={() => setShowPassword(!showPassword)}
                >
                    {showPassword ? (
                        <EyeOff className="h-5 w-5 transition-transform duration-200 hover:scale-110" />
                    ) : (
                        <Eye className="h-5 w-5 transition-transform duration-200 hover:scale-110" />
                    )}
                </button>
            </div>
        </div>
    );
} 