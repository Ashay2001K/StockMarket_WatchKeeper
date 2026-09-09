"use client";

import React from "react";
import Link from "next/link";
import { WatchlistItem } from "@/lib/api";
import { TrendingUp, AlertTriangle, ArrowRight, CheckCircle2, ChevronRight } from "lucide-react";

interface WatchlistDeltaProps {
  watchlist: WatchlistItem[];
}

export const WatchlistDelta: React.FC<WatchlistDeltaProps> = ({ watchlist }) => {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between px-1">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Daily Score Acceleration & Trajectory
        </h3>
        <span className="text-[11px] text-slate-500 font-mono">T-2 ➔ T-1 ➔ Today</span>
      </div>

      <div className="space-y-2.5">
        {watchlist.map((item) => {
          const isAccelerating = item.delta_1d > 0;
          const isExhausted = item.chase_alert_active;

          return (
            <Link
              key={item.symbol}
              href={`/stock/${item.symbol}`}
              className="block glass-panel rounded-2xl p-3.5 hover:border-emerald-500/50 active:scale-[0.99] transition-all"
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-sm font-black text-white">{item.symbol}</span>
                    <span className="text-xs font-mono text-slate-400">₹{item.close_price}</span>
                  </div>

                  {/* 3-day trajectory progression */}
                  <div className="flex items-center gap-1.5 mt-1.5 font-mono text-xs text-slate-300">
                    <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
                      {item.history_3d[0]}
                    </span>
                    <ArrowRight className="w-3 h-3 text-slate-600" />
                    <span className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-300">
                      {item.history_3d[1]}
                    </span>
                    <ArrowRight className="w-3 h-3 text-slate-600" />
                    <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 font-bold">
                      {item.history_3d[2]}
                    </span>
                    <span className={`text-[11px] font-bold ml-1 ${isAccelerating ? 'text-emerald-400' : 'text-slate-400'}`}>
                      ({isAccelerating ? '+' : ''}{item.delta_1d})
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <div className={`text-[10px] font-bold px-2 py-0.5 rounded-full border inline-flex items-center gap-1 ${
                    isExhausted
                      ? "bg-rose-500/10 border-rose-500/40 text-rose-300"
                      : item.status_flag === "Healthy Acceleration"
                      ? "bg-emerald-500/10 border-emerald-500/40 text-emerald-400"
                      : "bg-cyan-500/10 border-cyan-500/40 text-cyan-300"
                  }`}>
                    {isExhausted ? <AlertTriangle className="w-2.5 h-2.5" /> : <CheckCircle2 className="w-2.5 h-2.5" />}
                    {item.status_flag}
                  </div>

                  <div className="text-xs font-bold text-white uppercase tracking-tight mt-1.5">
                    {item.action}
                  </div>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
};
