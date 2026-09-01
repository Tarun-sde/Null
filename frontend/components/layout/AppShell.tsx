"use client";

import React, { useState } from "react";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

interface AppShellProps {
  children: React.ReactNode;
  openAlertsCount?: number;
}

export function AppShell({ children, openAlertsCount = 4 }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen w-full bg-transparent">
      {/* Sidebar Navigation */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col min-w-0 overflow-x-hidden">
        <TopBar
          onMenuToggle={() => setSidebarOpen((prev) => !prev)}
          openAlertsCount={openAlertsCount}
        />
        <main className="flex-1 p-6 sm:p-10 lg:p-12 max-w-[112rem] w-full mx-auto animate-in-reveal">
          {children}
        </main>
      </div>
    </div>
  );
}
