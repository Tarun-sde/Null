import React from "react";
import { cn } from "@/lib/utils";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "light" | "dark" | "orange";
  hasCornerBrackets?: boolean;
  isHoverable?: boolean;
  children: React.ReactNode;
}

export function GlassCard({
  variant = "light",
  hasCornerBrackets = false,
  isHoverable = false,
  className,
  children,
  ...props
}: GlassCardProps) {
  return (
    <div
      className={cn(
        "relative rounded-2xl transition-all duration-300",
        // Variants
        variant === "light" &&
          "bg-white/45 border border-black/10 shadow-[0_18px_45px_rgba(0,0,0,0.04),inset_0_1px_0_rgba(255,255,255,0.72)] backdrop-blur-md text-[#090909]",
        variant === "dark" &&
          "bg-[#111111] border border-black/20 shadow-[0_22px_50px_rgba(0,0,0,0.22),inset_0_1px_0_rgba(255,255,255,0.12)] text-white",
        variant === "orange" &&
          "bg-[#ff5a24] border border-[#ff6330] shadow-[0_22px_50px_rgba(255,90,36,0.18),inset_0_1px_0_rgba(255,255,255,0.2)] text-white",
        // Hover
        isHoverable && "hover:-translate-y-1 hover:shadow-[0_26px_60px_rgba(0,0,0,0.09)]",
        className
      )}
      {...props}
    >
      {/* Corner Brackets */}
      {hasCornerBrackets && (
        <>
          <div
            className={cn(
              "absolute right-4 top-4 h-6 w-6 border-r border-t pointer-events-none",
              variant === "dark" ? "border-white/30" : "border-black/15"
            )}
          />
          <div
            className={cn(
              "absolute bottom-4 left-4 h-6 w-6 border-b border-l pointer-events-none",
              variant === "dark" ? "border-white/30" : "border-black/15"
            )}
          />
        </>
      )}
      {children}
    </div>
  );
}
