import React from "react";
import { GlassCard } from "./GlassCard";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: number | string;
  subtext?: string;
  trend?: string;
  trendPositive?: boolean;
  sparklineColor?: string;
  statusDotColor?: string;
  className?: string;
}

export function MetricCard({
  title,
  value,
  subtext,
  trend,
  trendPositive = true,
  sparklineColor = "#ff5a24",
  statusDotColor,
  className,
}: MetricCardProps) {
  return (
    <GlassCard
      isHoverable
      className={cn("p-6 sm:p-7 flex flex-col justify-between overflow-hidden", className)}
    >
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-wider text-[#6a6a6a]">
          {title}
        </p>
        {statusDotColor ? (
          <span className={cn("size-2 rounded-full animate-pulse", statusDotColor)} />
        ) : (
          <span className="size-2 rounded-full bg-[#ff5a24] animate-pulse" />
        )}
      </div>

      {/* Mini Sparkline SVG */}
      <div className="mt-4 h-6 w-full opacity-70">
        <svg viewBox="0 0 160 30" className="h-full w-full overflow-visible" fill="none">
          <path
            d="M0 24 L20 18 L40 22 L65 10 L85 18 L110 8 L135 16 L160 6"
            stroke={sparklineColor}
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>

      {/* Big Metric Readout */}
      <div className="mt-3 flex items-end justify-between gap-2">
        <p
          className="text-4xl sm:text-5xl font-medium tracking-tight text-black leading-none"
          style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
        >
          {value}
        </p>

        {trend && (
          <div className="text-right">
            <span
              className={cn(
                "inline-flex items-center text-xs font-medium px-2 py-0.5 rounded-full border",
                trendPositive
                  ? "text-emerald-700 bg-emerald-50 border-emerald-200"
                  : "text-[#ff5a24] bg-orange-50 border-[#ff5a24]/30"
              )}
            >
              {trend}
            </span>
          </div>
        )}
      </div>

      {subtext && (
        <p className="mt-3 text-xs text-[#7a7a7a] font-normal">
          {subtext}
        </p>
      )}
    </GlassCard>
  );
}
