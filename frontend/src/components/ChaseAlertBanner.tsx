"use client";

import React from "react";
import { AlertTriangle, Compass, CheckCircle2 } from "lucide-react";
import { StockRecord } from "@/lib/api";

interface ChaseAlertBannerProps {
  stock: StockRecord;
}

export const ChaseAlertBanner: React.FC<ChaseAlertBannerProps> = ({ stock }) => {
  if (!stock.chase_alert_active) {
    return (
      <div className="flex items-center gap-2.5 px-3.5 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400">
        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
        <span>No Chase Alert — Technical base is unextended and healthy for structured entry.</span>
      </div>
    );
  }

  const isHigh = stock.chase_alert_severity === "HIGH";

  return (
    <div className={`rounded-2xl p-4 border transition-all ${
      isHigh 
        ? "bg-gradient-to-r from-rose-950/70 via-red-900/50 to-amber-950/60 border-rose-500/60 glow-rose"
        : "bg-amber-950/40 border-amber-500/50 glow-amber"
    }`}>
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-xl shrink-0 mt-0.5 ${isHigh ? "bg-rose-500 text-white" : "bg-amber-500 text-slate-950"}`}>
          <AlertTriangle className="w-5 h-5 font-bold" />
        </div>

        <div className="space-y-1.5 flex-1">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-black tracking-wide uppercase text-white flex items-center gap-1.5">
              <span>{isHigh ? "🔴 HIGH CHASE RISK" : "🟠 CAUTION"}</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40">
                DO NOT CHASE
              </span>
            </h4>
          </div>

          <p className="text-xs text-slate-200 leading-relaxed font-medium">
            {stock.chase_alert_reason || "Price has advanced rapidly and is significantly extended above the 20 DMA."}
          </p>

          <div className="pt-2 border-t border-white/10 mt-2">
            <div className="text-[10px] uppercase font-bold text-amber-300 tracking-wider flex items-center gap-1">
              <Compass className="w-3 h-3" /> Recommended Entry Blueprint:
            </div>
            <p className="text-[11px] text-slate-300 font-mono mt-0.5 bg-black/30 px-2.5 py-1.5 rounded-lg border border-white/5">
              {stock.chase_strategy || "Consolidation ➔ Volume Contraction ➔ Support Formation ➔ Breakout ➔ Volume Expansion"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
