"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Search, TrendingUp, X } from "lucide-react";
import { searchTickers } from "@/lib/api";

export const HeaderSearch: React.FC = () => {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (query.trim().length === 0) {
      setSuggestions([]);
      return;
    }
    const timer = setTimeout(async () => {
      const results = await searchTickers(query);
      setSuggestions(results);
    }, 150);
    return () => clearTimeout(timer);
  }, [query]);

  // Click outside listener
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (symbol: string) => {
    setIsOpen(false);
    setQuery("");
    router.push(`/stock/${symbol}`);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && query.trim()) {
      handleSelect(query.trim().toUpperCase());
    }
  };

  return (
    <div ref={containerRef} className="relative w-full max-w-md mx-auto">
      <div className="relative flex items-center">
        <div className="absolute left-3.5 pointer-events-none text-slate-400">
          <Search className="w-4 h-4" />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder="Search ticker (e.g. MCX, POLYCAB, APARINDS)..."
          className="w-full pl-10 pr-9 py-2.5 bg-slate-900/90 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/80 transition-all shadow-inner"
        />
        {query && (
          <button
            onClick={() => setQuery("")}
            className="absolute right-3 text-slate-400 hover:text-slate-200 p-1"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Auto-suggest dropdown */}
      {isOpen && suggestions.length > 0 && (
        <div className="absolute z-50 left-0 right-0 mt-2 bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-xl divide-y divide-slate-800">
          {suggestions.map((item) => (
            <div
              key={item.symbol}
              onClick={() => handleSelect(item.symbol)}
              className="flex items-center justify-between px-4 py-3 hover:bg-slate-800/80 active:bg-emerald-500/10 cursor-pointer transition-colors"
            >
              <div className="flex items-center gap-2.5">
                <div className="w-7 h-7 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-emerald-400 font-bold text-xs">
                  {item.symbol.slice(0, 2)}
                </div>
                <div>
                  <div className="text-sm font-semibold text-slate-100 flex items-center gap-1.5">
                    {item.symbol}
                    <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">NSE</span>
                  </div>
                  <div className="text-xs text-slate-400 truncate max-w-[200px]">
                    {item.name}
                  </div>
                </div>
              </div>
              <div className="text-right">
                <span className="text-[11px] text-slate-400 block">{item.sector}</span>
                <span className="text-[11px] text-emerald-400 flex items-center gap-0.5 justify-end">
                  <TrendingUp className="w-3 h-3" /> View Setup
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
