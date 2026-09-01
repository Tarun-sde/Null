"use client";

import React from "react";
import { Menu, Search, Bell, Shield, User } from "lucide-react";
import { cn } from "@/lib/utils";

interface TopBarProps {
  onMenuToggle?: () => void;
  openAlertsCount?: number;
}

export function TopBar({ onMenuToggle, openAlertsCount = 4 }: TopBarProps) {
  return (
    <header className="sticky top-0 z-30 flex h-20 w-full items-center justify-between px-6 sm:px-10 lg:px-12 bg-white/40 border-b border-black/10 backdrop-blur-xl transition-all">
      {/* Left: Mobile Menu & Live Badge */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuToggle}
          className="grid size-10 place-items-center rounded-xl border border-black/15 bg-white/70 text-black shadow-sm lg:hidden hover:bg-white transition-colors"
          aria-label="Open navigation menu"
        >
          <Menu className="size-5" />
        </button>

        <div className="hidden sm:flex items-center gap-2.5 rounded-full border border-black/10 bg-white/70 px-3.5 py-1.5 shadow-sm">
          <span className="size-2 rounded-full bg-[#ff5a24] animate-pulse" />
          <span className="text-xs font-semibold uppercase tracking-wider text-[#222222]">
            CONTROL TOWER LIVE
          </span>
          <span className="text-[10px] text-[#7a7a7a] font-mono border-l border-black/10 pl-2">
            99.9% SLA
          </span>
        </div>
      </div>

      {/* Center: Search Bar */}
      <div className="flex-1 max-w-md mx-4 hidden md:block">
        <div className="relative flex items-center">
          <Search className="absolute left-3.5 size-4 text-[#7a7a7a]" />
          <input
            type="text"
            placeholder="Search equipment ID, serial, model, dealer, site..."
            className="w-full rounded-xl border border-black/10 bg-white/60 pl-10 pr-4 py-2 text-xs font-normal text-black placeholder:text-[#8a8a8a] focus:bg-white focus:outline-none focus:ring-1 focus:ring-[#ff5a24] shadow-[inset_0_1px_0_rgba(255,255,255,0.8)] transition-all"
          />
        </div>
      </div>

      {/* Right: Notification & Profile */}
      <div className="flex items-center gap-3.5">
        {/* Notifications button */}
        <button
          className="relative grid size-10 place-items-center rounded-xl border border-black/10 bg-white/60 text-black hover:bg-white transition-colors shadow-sm"
          aria-label="Alerts and notifications"
        >
          <Bell className="size-4.5" />
          {openAlertsCount > 0 && (
            <span className="absolute -top-1 -right-1 flex size-5 items-center justify-center rounded-full bg-[#ff5a24] text-[10px] font-bold text-white shadow-sm animate-pulse">
              {openAlertsCount}
            </span>
          )}
        </button>

        {/* User Profile Chip */}
        <div className="flex items-center gap-3 rounded-xl border border-black/10 bg-white/60 px-3 py-1.5 shadow-sm">
          <div className="size-7 rounded-lg bg-[#111111] grid place-items-center text-white text-xs font-semibold">
            OP
          </div>
          <div className="hidden sm:block text-left">
            <p className="text-xs font-semibold text-black leading-tight">Marcus Vance</p>
            <p className="text-[10px] text-[#7a7a7a] leading-none">Fleet Commander</p>
          </div>
        </div>
      </div>
    </header>
  );
}
