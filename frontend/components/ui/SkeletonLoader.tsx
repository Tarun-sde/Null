import React from "react";
import { cn } from "@/lib/utils";

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string;
}

export function SkeletonLoader({ className, ...props }: SkeletonProps) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-xl bg-black/[0.06] dark:bg-white/[0.08]",
        className
      )}
      {...props}
    />
  );
}

export function CardSkeleton() {
  return (
    <div className="rounded-2xl border border-black/10 bg-white/40 p-6 backdrop-blur-md shadow-sm">
      <SkeletonLoader className="h-4 w-28" />
      <SkeletonLoader className="mt-4 h-6 w-full" />
      <SkeletonLoader className="mt-4 h-10 w-24" />
      <SkeletonLoader className="mt-3 h-3 w-36" />
    </div>
  );
}

export function TableSkeleton() {
  return (
    <div className="rounded-2xl border border-black/10 bg-white/40 p-6 backdrop-blur-md space-y-4">
      <div className="flex justify-between items-center pb-4 border-b border-black/10">
        <SkeletonLoader className="h-6 w-40" />
        <SkeletonLoader className="h-8 w-48" />
      </div>
      {[...Array(5)].map((_, i) => (
        <div key={i} className="flex items-center gap-4 py-2">
          <SkeletonLoader className="h-10 w-10 rounded-lg shrink-0" />
          <SkeletonLoader className="h-5 w-32" />
          <SkeletonLoader className="h-5 w-24 ml-auto" />
          <SkeletonLoader className="h-6 w-20 rounded-full" />
        </div>
      ))}
    </div>
  );
}
