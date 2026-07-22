import React from 'react';
import { TICKERS } from '../data/dashboardData';
import { MonoValue } from '../../../shared/ui/Typography';
import { cn } from '../../../shared/lib/utils';
import { motion } from 'framer-motion';

export const Header: React.FC = () => {
  return (
    <header className="h-[40px] border-b border-border flex items-center px-4 bg-paper shrink-0 justify-between overflow-hidden">
      <div className="flex items-center gap-2 shrink-0 z-10 bg-paper pr-4">
        <div className="w-5 h-5 rounded-full border border-ink flex items-center justify-center">
          <div className="w-2.5 h-2.5 rounded-full bg-ink" />
        </div>
        <div className="flex flex-col justify-center">
          <span className="font-serif italic text-lg leading-none -mt-0.5">Aethel</span>
          <span className="font-sans uppercase tracking-[0.2em] text-[8px] text-ink/60">Causal Intelligence - V1.4</span>
        </div>
      </div>

      <div className="flex-1 overflow-hidden relative h-full flex items-center mx-4 mask-edges">
        <motion.div
          className="flex whitespace-nowrap gap-8 absolute"
          animate={{ x: ["0%", "-50%"] }}
          transition={{ ease: "linear", duration: 30, repeat: Infinity }}
        >
          {/* Double the tickers for seamless loop */}
          {[...TICKERS, ...TICKERS].map((ticker, i) => (
            <div key={i} className="flex items-baseline gap-2">
              <span className="font-mono text-[11px] text-ink/60">{ticker.symbol}</span>
              <MonoValue>{ticker.value}</MonoValue>
              <MonoValue className={cn("text-[11px]", ticker.isPositive ? "text-success" : "text-danger")}>
                {ticker.change}
              </MonoValue>
            </div>
          ))}
        </motion.div>
      </div>

      <div className="flex items-center gap-4 shrink-0 z-10 bg-paper pl-4 font-mono text-[11px] uppercase tracking-wider text-ink/70">
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
          LIVE <span className="text-ink/40">-</span> 14MS
        </div>
        <div className="border border-border px-2 py-0.5 rounded-[2px] bg-ink/5">
          ⌘K COMMAND
        </div>
      </div>
    </header>
  );
};
