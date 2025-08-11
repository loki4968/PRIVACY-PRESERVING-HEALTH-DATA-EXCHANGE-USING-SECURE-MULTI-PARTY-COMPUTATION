import React from "react";

export default function FormInput({ icon, register, name, placeholder, errors }) {
  return (
    <div className="relative mb-4">
      <div className="absolute left-3 top-3 text-gray-400">{icon}</div>
      <input
        {...register(name)}
        placeholder={placeholder}
        className="pl-10 w-full border rounded px-3 py-2"
      />
      {errors[name] && <p className="text-red-500 text-sm mt-1">{errors[name].message}</p>}
    </div>
  );
}
