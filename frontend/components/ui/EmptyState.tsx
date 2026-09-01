import React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { GlassCard } from "./GlassCard";

interface EmptyStateProps {
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
}

export function EmptyState({
  title,
  description,
  actionText,
  onAction,
  icon,
}: EmptyStateProps) {
  return (
    <GlassCard className="p-12 text-center flex flex-col items-center justify-center max-w-lg mx-auto my-8">
      <div className="size-14 rounded-2xl bg-black/5 flex items-center justify-center text-[#ff5a24] mb-5 border border-black/10">
        {icon || <AlertCircle className="size-7" />}
      </div>
      <h3
        className="text-2xl font-medium text-black tracking-tight"
        style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
      >
        {title}
      </h3>
      <p className="mt-2 text-sm text-[#6a6a6a] max-w-sm leading-relaxed">
        {description}
      </p>
      {actionText && onAction && (
        <button
          onClick={onAction}
          className="mt-6 inline-flex items-center gap-2 rounded-lg bg-[#111111] px-5 py-2.5 text-sm font-medium text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.15)] hover:bg-black transition-all"
        >
          <RefreshCw className="size-4" />
          {actionText}
        </button>
      )}
    </GlassCard>
  );
}
