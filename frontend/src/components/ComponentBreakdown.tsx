"use client";

import React from "react";
import { StockRecord } from "@/lib/api";
import { Gauge, Flame, BarChart3, Truck, Crosshair, Building2 } from "lucide-react";

interface ComponentBreakdownProps {
  stock: StockRecord;
}

interface ComponentItem {
  id: string;
  name: string;
  earned: number;
  max: number;
  icon: React.ReactNode;
  color: string;
  detail: string;
}

export const ComponentBreakdown: React.FC<ComponentBreakdownProps> = ({ stock }) => {
  const components: ComponentItem[] = [
    {
      id: "price_mom",
      name: "Price Momentum",
      earned: stock.price_momentum_score,
      max: 25,
      icon: <Gauge className="w-4 h-4" />,
      color: "bg-emerald-500",
      detail: "20d/50d returns, Nifty 50 relative strength & MA alignment"
    },
    {
      id: "vol_exp",
      name: "Volume Expansion",
      earned: stock.volume_expansion_score,
      max: 20,
      icon: <BarChart3 className="w-4 h-4" />,
      color: "bg-cyan-500",
      detail: "Current volume ratio vs 20 DMA & distribution check"
    },
    {
      id: "deliv_str",
      name: "Delivery Strength",
      earned: stock.delivery_score,
      max: 15,
      icon: <Truck className="w-4 h-4" />,
      color: "bg-blue-500",
      detail: "NSE cash delivery percentage & institutional accumulation"
    },
    {
      id: "breakout_q",
      name: "Breakout Quality",
      earned: stock.breakout_score,
      max: 15,
      icon: <Crosshair className="w-4 h-4" />,
      color: "bg-purple-500",
      detail: "Resistance breakout confirmation with volume backing"
    },
    {
      id: "inst_part",
      name: "Institutional Flow",
      earned: stock.institutional_score,
      max: 10,
      icon: <Building2 className="w-4 h-4" />,
      color: "bg-indigo-500",
      detail: "FII/DII accumulation & Futures Open Interest buildup"
    },
    {
      id: "exhaust_adj",
      name: "Exhaustion Buffer",
      earned: stock.exhaustion_adjustment,
      max: 15,
      icon: <Flame className="w-4 h-4" />,
      color: stock.raw_exhaustion_score > 10 ? "bg-rose-500" : "bg-amber-500",
      detail: `Contributes 15 - Exhaustion (${stock.raw_exhaustion_score.toFixed(1)} penalty)`
    }
  ];

  return (
    <div className="glass-panel rounded-2xl p-4 shadow-lg space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-emerald-400" />
          6-Component Momentum Breakdown
        </h3>
        <span className="text-xs font-mono font-bold text-emerald-400">
          {stock.bem_score.toFixed(1)} / 100
        </span>
      </div>

      <div className="space-y-3.5">
        {components.map((c) => {
          const pct = Math.min(100, Math.max(0, (c.earned / c.max) * 100));
          return (
            <div key={c.id} className="space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300 font-semibold flex items-center gap-1.5">
                  <span className="text-slate-400">{c.icon}</span>
                  {c.name}
                </span>
                <span className="font-mono font-bold text-slate-200">
                  <span className="text-white">{c.earned.toFixed(1)}</span>
                  <span className="text-slate-500 text-[10px]"> / {c.max}</span>
                </span>
              </div>

              {/* Progress Bar */}
              <div className="w-full h-2 rounded-full bg-slate-800/80 overflow-hidden p-0.5 border border-slate-700/50">
                <div
                  className={`h-full rounded-full ${c.color} transition-all duration-500`}
                  style={{ width: `${pct}%` }}
                />
              </div>

              <div className="text-[10px] text-slate-500 truncate">
                {c.detail}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
