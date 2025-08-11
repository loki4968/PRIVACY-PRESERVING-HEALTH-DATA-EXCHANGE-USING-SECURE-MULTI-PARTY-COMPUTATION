"use client";

import { forwardRef } from "react";

const Button = forwardRef(({ 
  className = "",
  children,
  ...props
}, ref) => {
  return (
    <button
      ref={ref}
      className={`inline-flex items-center justify-center rounded-lg font-medium transition-all ${className}`}
      {...props}
    >
      {children}
    </button>
  );
});

Button.displayName = "Button";

export { Button }; 