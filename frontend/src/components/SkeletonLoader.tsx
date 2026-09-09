"use client";

import React from "react";
import { Zap, Activity } from "lucide-react";

interface SkeletonLoaderProps {
  message?: string;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  message = "Waking up market engine (free tier container)..."
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center glass-card rounded-2xl border border-slate-800 animate-pulse my-6">
      <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center mb-4 text-emerald-400 glow-emerald">
        <Activity className="w-7 h-7 animate-spin" />
      </div>
      <h3 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
        <Zap className="w-4 h-4 text-emerald-400 fill-emerald-400" />
        {message}
      </h3>
      <p className="text-xs text-slate-400 max-w-xs mt-2">
        Render free containers spin down after inactivity. Fetching live calculations from memory...
      </p>

      {/* Mini skeletons */}
      <div className="w-full max-w-sm mt-6 space-y-3">
        <div className="h-4 bg-slate-800/60 rounded-full w-3/4 mx-auto" />
        <div className="h-8 bg-slate-800/40 rounded-xl w-full" />
        <div className="h-8 bg-slate-800/30 rounded-xl w-5/6 mx-auto" />
      </div>
    </div>
  );
};
