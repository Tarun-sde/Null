import React from "react";
import { EquipmentStatus } from "@/types";
import { STATUS_CONFIG } from "@/lib/constants";
import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: EquipmentStatus | string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function StatusBadge({ status, size = "md", className }: StatusBadgeProps) {
  const normStatus = (status.toUpperCase() as EquipmentStatus) in STATUS_CONFIG
    ? (status.toUpperCase() as EquipmentStatus)
    : "UNASSIGNED";

  const config = STATUS_CONFIG[normStatus];

  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-full font-medium tracking-wide uppercase border backdrop-blur-sm transition-all",
        config.bgLight,
        config.borderLight,
        config.textColor,
        size === "sm" && "px-2.5 py-0.5 text-[10px]",
        size === "md" && "px-3 py-1 text-xs",
        size === "lg" && "px-4 py-1.5 text-sm",
        className
      )}
    >
      <span
        className={cn(
          "rounded-full shrink-0",
          config.dotColor,
          size === "sm" && "size-1.5",
          size === "md" && "size-2",
          size === "lg" && "size-2.5",
          (normStatus === "ACTIVE" || normStatus === "DUE_SOON" || normStatus === "OVERDUE") && "animate-pulse"
        )}
      />
      {config.label}
    </span>
  );
}
