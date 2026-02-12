"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { IconCheck } from "@/components/icons";

export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Check if already logged in
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch("/api/auth/me");
        if (res.ok) {
          // Get redirect parameter from URL
          const urlParams = new URLSearchParams(window.location.search);
          const redirectTo = urlParams.get("redirect") || "/dashboard";
          router.push(redirectTo);
        }
      } catch (err) {
        // Not authenticated, stay on login page
      }
    };
    checkAuth();
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Failed to authenticate");
      }

      // Get redirect parameter from URL or default to dashboard
      const urlParams = new URLSearchParams(window.location.search);
      const redirectTo = urlParams.get("redirect") || "/dashboard";
      
      // Small delay to ensure cookie is set
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Redirect to target page
      window.location.href = redirectTo;
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 px-4 py-12">
      <div className="w-full max-w-md">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <div className="flex flex-col items-center mb-6">
            {/* Logo dalam bentuk kotak yang menarik - diperbesar */}
            <div className="relative group">
              {/* Kotak utama dengan efek glow */}
              <div className="w-36 h-36 sm:w-40 sm:h-40 md:w-48 md:h-48 rounded-xl bg-gradient-to-br from-bagana-primary/20 via-white to-bagana-muted/30 border-2 border-bagana-primary/40 shadow-lg shadow-bagana-primary/20 p-3 transition-all duration-300 group-hover:shadow-xl group-hover:shadow-bagana-primary/30 group-hover:scale-105 group-hover:border-bagana-primary/60">
                {/* Inner container dengan padding */}
                <div className="w-full h-full rounded-lg bg-white/50 backdrop-blur-sm flex items-center justify-center overflow-hidden">
                  <Image
                    src="/bagana-ai-logo.png"
                    alt="BAGANA AI Logo"
                    width={128}
                    height={128}
                    className="object-contain w-full h-full p-2"
                    priority
                  />
                </div>
              </div>
              {/* Efek glow animasi */}
              <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-bagana-primary/0 via-bagana-primary/10 to-bagana-primary/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none blur-sm" />
              {/* Corner accents */}
              <div className="absolute -top-1 -left-1 w-4 h-4 border-t-2 border-l-2 border-bagana-primary/60 rounded-tl-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="absolute -top-1 -right-1 w-4 h-4 border-t-2 border-r-2 border-bagana-primary/60 rounded-tr-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="absolute -bottom-1 -left-1 w-4 h-4 border-b-2 border-l-2 border-bagana-primary/60 rounded-bl-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <div className="absolute -bottom-1 -right-1 w-4 h-4 border-b-2 border-r-2 border-bagana-primary/60 rounded-br-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </div>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-800 mb-2">
            AI Content Strategy Platform
          </h1>
          <p className="text-sm sm:text-base text-slate-600">
            Agentic AI untuk Strategi Konten KOL & Influencer
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-8">
          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1.5">
                Email or Username
              </label>
              <input
                id="email"
                type="text"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-bagana-primary focus:outline-none focus:ring-2 focus:ring-bagana-primary/20"
                placeholder="Enter your email or username"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-700 mb-1.5">
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:border-bagana-primary focus:outline-none focus:ring-2 focus:ring-bagana-primary/20"
                placeholder="Enter your password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-bagana-primary px-5 py-3 text-sm font-medium text-white hover:bg-bagana-secondary disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  {IconCheck}
                  Sign In
                </>
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
