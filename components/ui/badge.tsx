import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "border-transparent bg-[#2d2a26] text-[#efece4]",
        secondary: "border-transparent bg-[#e8e4da] text-[#1a1a1a]",
        destructive: "border-transparent bg-red-600 text-white",
        outline: "border-[#d8d4c8] text-[#1a1a1a]",
        accept: "border-green-200 bg-green-50 text-green-700",
        reject: "border-red-200 bg-red-50 text-red-700",
        uncertain: "border-amber-200 bg-amber-50 text-amber-700",
        leader: "border-indigo-200 bg-indigo-50 text-indigo-700",
        appealed: "border-purple-200 bg-purple-50 text-purple-700",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
