"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, AlertCircle, Eye, EyeOff } from "lucide-react";
import { login } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password) return;

    setLoading(true);
    setError(null);

    try {
      await login(email.trim(), password);
      router.push("/");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center p-4"
      style={{
        background: "linear-gradient(135deg, #f5f0e8 0%, #ede8df 40%, #e8e0d4 100%)",
      }}
    >
      {/* Decorative background grid */}
      <div
        className="absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage:
            "repeating-linear-gradient(0deg, #000 0px, #000 1px, transparent 1px, transparent 40px), repeating-linear-gradient(90deg, #000 0px, #000 1px, transparent 1px, transparent 40px)",
        }}
      />

      <div className="relative w-full max-w-sm">
        {/* Brand Header */}
        <div className="text-center mb-10">
          <div className="flex items-center justify-center gap-3 mb-4">
            <span className="size-3.5 bg-[#ff5a24] shadow-[0_0_0_4px_rgba(255,90,36,0.15)]" />
            <span className="text-2xl font-medium tracking-[0.22em] text-black">
              RENTSENSE
            </span>
          </div>
          <p className="text-xs tracking-wider uppercase text-[#7a7a7a] font-medium">
            Control Tower OS
          </p>
        </div>

        {/* Login Card */}
        <div
          className="rounded-2xl border border-black/10 p-8 shadow-[0_32px_80px_rgba(0,0,0,0.08),inset_0_1px_0_rgba(255,255,255,0.9)]"
          style={{ background: "rgba(255,255,255,0.75)", backdropFilter: "blur(20px)" }}
        >
          <div className="mb-6">
            <h1
              className="text-2xl font-medium text-black tracking-tight"
              style={{ fontFamily: "var(--font-playfair), Georgia, serif" }}
            >
              Fleet Command Access
            </h1>
            <p className="text-xs text-[#7a7a7a] mt-1">
              Sign in to access your fleet intelligence dashboard.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div>
              <label
                htmlFor="email"
                className="block text-xs font-semibold uppercase tracking-wider text-[#6a6a6a] mb-1.5"
              >
                Email Address
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@rentsense.local"
                className="w-full rounded-xl border border-black/10 bg-white/80 px-4 py-2.5 text-sm text-black placeholder:text-[#9a9a9a] focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#ff5a24]/30 focus:border-[#ff5a24]/50 transition-all"
              />
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="password"
                className="block text-xs font-semibold uppercase tracking-wider text-[#6a6a6a] mb-1.5"
              >
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full rounded-xl border border-black/10 bg-white/80 px-4 py-2.5 pr-11 text-sm text-black placeholder:text-[#9a9a9a] focus:bg-white focus:outline-none focus:ring-2 focus:ring-[#ff5a24]/30 focus:border-[#ff5a24]/50 transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-[#9a9a9a] hover:text-black transition-colors"
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="flex items-start gap-2.5 rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-700">
                <AlertCircle className="size-4 shrink-0 text-red-500 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            {/* Submit */}
            <button
              id="sign-in-button"
              type="submit"
              disabled={loading || !email.trim() || !password}
              className="w-full mt-2 flex items-center justify-center gap-2 rounded-xl bg-[#111111] px-6 py-3 text-sm font-semibold text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.15)] hover:bg-black transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="size-4 animate-spin" />
                  <span>Authenticating…</span>
                </>
              ) : (
                <span>Sign In to Control Tower</span>
              )}
            </button>
          </form>
        </div>

        {/* Footer */}
        <p className="mt-6 text-center text-[11px] text-[#9a9a9a]">
          RentSense Control Tower · Fleet Intelligence OS
        </p>
      </div>
    </div>
  );
}
