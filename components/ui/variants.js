import { cva } from "class-variance-authority";

export const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
  {
    variants: {
      color: {
        green: "bg-green-500 text-white hover:bg-green-600",
        blue: "bg-blue-500 text-white hover:bg-blue-600",
        red: "bg-red-500 text-white hover:bg-red-600",
      },
      size: {
        small: "px-3 py-1 text-sm",
        medium: "px-4 py-2 text-base",
        large: "px-6 py-3 text-lg",
      },
    },
    defaultVariants: {
      color: "green",
      size: "medium",
    },
  }
);
