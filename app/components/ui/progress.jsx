"use client";

import * as React from "react";
import * as ProgressPrimitive from "@radix-ui/react-progress";

export function Progress({
  value,
  className = "",
  ...props
}) {
  return (
    <ProgressPrimitive.Root
      className={`relative h-2 w-full overflow-hidden rounded-full bg-gray-200 ${className}`}
      {...props}
    >
      <ProgressPrimitive.Indicator
        className="h-full w-full flex-1 bg-blue-500 transition-all"
        style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
      />
    </ProgressPrimitive.Root>
  );
} 