"use client";

import React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Truck,
  QrCode,
  Zap,
  TrendingUp,
  DollarSign,
  Settings,
  LogOut,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { logout } from "@/lib/auth";

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  exact?: boolean;
  badge?: string;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard, exact: true },
  { label: "Fleet Assets", href: "/assets", icon: Truck },
  { label: "Handoff Scan", href: "/scan", icon: QrCode },
  { label: "Action Queue", href: "/actions", icon: Zap },
  { label: "Demand Forecast", href: "/forecast", icon: TrendingUp },
  { label: "Avoided Impact", href: "/impact", icon: DollarSign },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  const isLinkActive = (item: typeof NAV_ITEMS[0]) => {
    if (item.exact) {
      return pathname === "/" || pathname === "/dashboard";
    }
    return pathname.startsWith(item.href);
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={cn(
          "fixed top-0 bottom-0 left-0 z-50 w-72 flex flex-col justify-between p-6 transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static",
          "bg-white/70 border-r border-black/10 shadow-[0_32px_80px_rgba(0,0,0,0.06),inset_0_1px_0_rgba(255,255,255,0.8)] backdrop-blur-xl",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Top Brand Header */}
        <div>
          <Link
            href="/"
            className="flex items-center gap-3 select-none group"
            onClick={onClose}
          >
            <span className="size-3.5 bg-[#ff5a24] shadow-[0_0_0_1px_rgba(255,90,36,0.24)] group-hover:scale-110 transition-transform" />
            <div>
              <span className="text-xl font-medium tracking-[0.22em] text-black block leading-none">
                RENTSENSE
              </span>
              <span className="text-[10px] tracking-wider uppercase text-[#7a7a7a] font-medium block mt-1">
                Control Tower OS
              </span>
            </div>
          </Link>

          <div className="mt-8 h-px w-full bg-black/10" />

          {/* Navigation Links */}
          <nav className="mt-6 space-y-1.5">
            {NAV_ITEMS.map((item) => {
              const active = isLinkActive(item);
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onClose}
                  className={cn(
                    "flex items-center justify-between px-3.5 py-3 rounded-xl text-sm font-medium transition-all group",
                    active
                      ? "bg-[#111111] text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.14),0_12px_24px_rgba(0,0,0,0.12)]"
                      : "text-[#333333] hover:bg-black/5 hover:text-black"
                  )}
                >
                  <div className="flex items-center gap-3.5">
                    <Icon
                      className={cn(
                        "size-4.5 transition-colors",
                        active ? "text-[#ff5a24]" : "text-[#7a7a7a] group-hover:text-black"
                      )}
                    />
                    <span>{item.label}</span>
                  </div>

                  {item.badge && (
                    <span
                      className={cn(
                        "text-[10px] px-2 py-0.5 rounded-full font-normal uppercase tracking-wider",
                        active
                          ? "bg-white/10 text-white/70"
                          : "bg-black/5 text-[#7a7a7a]"
                      )}
                    >
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Bottom Status & Utility Card */}
        <div className="pt-6 border-t border-black/10 space-y-4">
          <div className="rounded-xl border border-black/10 bg-white/60 p-3.5 backdrop-blur-sm">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <span className="size-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="font-semibold text-black">Telemetry Engine</span>
              </div>
              <span className="text-[10px] uppercase font-mono text-[#7a7a7a]">v0.1.0</span>
            </div>
            <p className="mt-1.5 text-[11px] text-[#6a6a6a]">
              PostgreSQL Connected • 7 Fleet Nodes Active
            </p>
          </div>

          <div className="flex items-center justify-between text-xs text-[#7a7a7a] px-1">
            <button className="flex items-center gap-1.5 hover:text-black transition-colors">
              <Settings className="size-3.5" />
              <span>Settings</span>
            </button>
            <button
              id="logout-button"
              onClick={handleLogout}
              className="flex items-center gap-1.5 hover:text-red-600 transition-colors"
              aria-label="Sign out"
            >
              <LogOut className="size-3.5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
