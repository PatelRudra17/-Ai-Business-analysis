import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatINR(amount: number): string {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);
}

export function formatNumber(n: number): string {
  return new Intl.NumberFormat("en-IN").format(n);
}

export function decisionColor(decision: string): string {
  if (decision.includes("STRONG")) return "text-green-700 bg-green-50 border-green-200";
  if (decision.includes("PROMISING")) return "text-blue-700 bg-blue-50 border-blue-200";
  if (decision.includes("NEEDS")) return "text-yellow-700 bg-yellow-50 border-yellow-200";
  if (decision.includes("HIGH_RISK")) return "text-red-700 bg-red-50 border-red-200";
  return "text-gray-700 bg-gray-50 border-gray-200";
}

export function decisionLabel(decision: string): string {
  return decision.replace(/_/g, " ").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
}
