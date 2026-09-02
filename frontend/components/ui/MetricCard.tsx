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
  const isWordValue = typeof value === "string" && !/\d/.test(value) && value.length > 5;

  return (
    <GlassCard
      isHoverable
      className={cn(
        "p-4 sm:p-7 flex flex-col justify-between overflow-hidden min-w-0 w-full",
        className
      )}
    >
      {/* Top Header */}
      <div className="flex items-center justify-between gap-1.5 sm:gap-2">
        <p className="text-[11px] sm:text-xs font-semibold uppercase tracking-wider text-[#6a6a6a] truncate">
          {title}
        </p>
        {statusDotColor ? (
          <span className={cn("size-2 shrink-0 rounded-full animate-pulse", statusDotColor)} />
        ) : (
          <span className="size-2 shrink-0 rounded-full bg-[#ff5a24] animate-pulse" />
        )}
      </div>

      {/* Mini Sparkline SVG */}
      <div className="mt-2.5 sm:mt-4 h-5 sm:h-6 w-full opacity-70">
        <svg viewBox="0 0 160 30" className="h-full w-full" preserveAspectRatio="none" fill="none">
          <path
            d="M0 24 L20 18 L40 22 L65 10 L85 18 L110 8 L135 16 L160 6"
            stroke={sparklineColor}
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>

      {/* Big Metric Readout + Badge */}
      <div
        className={cn(
          "mt-2.5 sm:mt-3 flex min-w-0",
          isWordValue
            ? "flex-col sm:flex-row sm:items-baseline sm:justify-between gap-1.5 sm:gap-2"
            : "flex-col sm:flex-row sm:items-end sm:justify-between gap-1.5 sm:gap-2"
        )}
      >
        <p
          className={cn(
            "font-medium tracking-tight text-black leading-none min-w-0",
            isWordValue
              ? "text-2xl sm:text-[1.65rem] lg:text-[1.5rem] xl:text-[1.75rem] 2xl:text-[2rem]"
              : "text-2xl sm:text-5xl"
          )}
          style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
        >
          {value}
        </p>

        {trend && (
          <div className="self-start sm:self-auto sm:text-right shrink-0">
            <span
              className={cn(
                "inline-flex items-center text-[10px] sm:text-xs font-medium px-2 py-0.5 rounded-full border leading-tight whitespace-nowrap",
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
        <p className="mt-2 sm:mt-3 text-[11px] sm:text-xs text-[#7a7a7a] font-normal leading-normal">
          {subtext}
        </p>
      )}
    </GlassCard>
  );
}
