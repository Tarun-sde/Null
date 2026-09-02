import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getErrorMessage(error: unknown, fallback: string) {
  return error instanceof Error ? error.message : fallback;
}

/**
 * Formats a monetary amount in Indian Rupees (INR) using Indian number grouping (Lakhs / Crores).
 * Example: 18500 -> "₹18,500", 106000 -> "₹1,06,000", 55500.5 -> "₹55,501"
 */
export function formatCurrency(
  amount: number | string | null | undefined,
  options?: { showDecimals?: boolean; compact?: boolean }
): string {
  const num = typeof amount === "string" ? parseFloat(amount) : Number(amount);
  if (amount === null || amount === undefined || isNaN(num)) {
    return "₹0";
  }

  if (options?.compact && Math.abs(num) >= 100000) {
    if (Math.abs(num) >= 10000000) {
      return `₹${(num / 10000000).toFixed(2)} Cr`;
    }
    return `₹${(num / 100000).toFixed(2)} L`;
  }

  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: options?.showDecimals ? 2 : 0,
    minimumFractionDigits: options?.showDecimals ? 2 : 0,
  }).format(num);
}

/**
 * Formats a day rate e.g. "₹18,500/day" or "₹18,500/d"
 */
export function formatDayRate(
  rate: number | string | null | undefined,
  suffix: string = "/day"
): string {
  return `${formatCurrency(rate)}${suffix}`;
}
