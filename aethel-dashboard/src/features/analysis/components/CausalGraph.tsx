import React from 'react';
import { Eyebrow, PanelTitle, MonoValue } from '../../../shared/ui/Typography';
import { Panel, PanelHeader } from '../../../shared/ui/Panel';
import { cn } from '../../../shared/lib/utils';

interface CausalGraphProps {
  primaryCausalDriver?: string;
  inflationShock?: number;
  sentimentShock?: number;
}

export const CausalGraph: React.FC<CausalGraphProps> = ({
  primaryCausalDriver = '',
  inflationShock = 0.0,
  sentimentShock = 0.0
}) => {
  // Dynamic beta calculations based on baseline parameters adjusted by user shocks
  const fedFundsTo2s10sVal = -0.62 - (inflationShock * 1.5);
  const twoS10sToRegLiqVal = 0.48 - (inflationShock * 0.5);
  const creDelinqToRegLiqVal = -0.71 + (sentimentShock * 1.2);

  const fedFundsTo2s10s = fedFundsTo2s10sVal.toFixed(2);
  const twoS10sToRegLiq = twoS10sToRegLiqVal.toFixed(2);
  const creDelinqToRegLiq = creDelinqToRegLiqVal.toFixed(2);

  const isInflationActive = primaryCausalDriver === 'Macro_Inflation';
  const isSentimentActive = primaryCausalDriver === 'Market_Sentiment';

  return (
    <Panel>
      <PanelHeader className="flex-row justify-between items-start">
        <div>
          <Eyebrow>CAUSAL INFERENCE</Eyebrow>
          <PanelTitle>Relationship Graph</PanelTitle>
          <div className="font-sans text-[11px] text-ink/70 mt-1">
            Structural DAG · 42 nodes shown · edge weight = |partial effect|
          </div>
        </div>
        <button className="font-sans text-[10px] uppercase tracking-wider text-ink/70 hover:text-ink">
          RECOMPUTE
        </button>
      </PanelHeader>

      <div className="flex flex-col pt-4">
        <div className="h-[180px] w-full relative flex items-center justify-center">
          <svg viewBox="0 0 300 180" className="w-full h-full overflow-visible">
            {/* Edges */}
            <line 
              x1="150" y1="20" x2="150" y2="90" 
              stroke={isInflationActive ? '#d32f2f' : '#1a1a1a'} 
              strokeWidth={isInflationActive ? '4.5' : '3'} 
              className={cn(isInflationActive && "transition-all duration-500")}
            /> {/* Fed -> 2s10s */}
            <line 
              x1="150" y1="90" x2="250" y2="130" 
              stroke={isInflationActive ? '#d32f2f' : '#e2e2e2'} 
              strokeWidth={isInflationActive ? '3.5' : '2.5'} 
              className={cn(isInflationActive && "transition-all duration-500")}
            /> {/* 2s10s -> Reg Liq */}
            <line 
              x1="80" y1="130" x2="250" y2="130" 
              stroke={isSentimentActive ? '#d32f2f' : '#e2e2e2'} 
              strokeWidth={isSentimentActive ? '3.5' : '2.5'} 
              className={cn(isSentimentActive && "transition-all duration-500")}
            /> {/* CRE -> Reg Liq */}
            
            {/* Thin background edges */}
            <line x1="150" y1="20" x2="80" y2="70" stroke="#e2e2e2" strokeWidth="1" /> {/* Fed -> CPI */}
            <line x1="80" y1="70" x2="80" y2="130" stroke="#e2e2e2" strokeWidth="1" /> {/* CPI -> CRE */}
            <line x1="150" y1="20" x2="230" y2="70" stroke="#e2e2e2" strokeWidth="1" /> {/* Fed -> Base R */}
            <line x1="230" y1="70" x2="250" y2="130" stroke="#e2e2e2" strokeWidth="1" /> {/* Base R -> Reg Liq */}
            <line x1="80" y1="130" x2="150" y2="160" stroke="#e2e2e2" strokeWidth="1" /> {/* CRE -> Housing */}
            <line x1="150" y1="160" x2="250" y2="130" stroke="#e2e2e2" strokeWidth="1" /> {/* Housing -> Reg Liq */}

            {/* Nodes */}
            <circle 
              cx="150" cy="20" r="4.5" 
              fill={isInflationActive ? '#d32f2f' : '#1a1a1a'} 
            /> {/* Fed Funds */}
            <text x="150" y="10" fontSize="7" fontFamily="monospace" textAnchor="middle" fill="#1a1a1a">FED FUNDS</text>

            <circle 
              cx="150" cy="90" r="4.5" 
              fill={isInflationActive ? '#d32f2f' : '#1a1a1a'} 
            /> {/* 2s10s */}
            <text x="150" y="80" fontSize="7" fontFamily="monospace" textAnchor="middle" fill="#1a1a1a">2s10s</text>

            {/* Reg Liquidity Circle Pulse */}
            {(isInflationActive || isSentimentActive) && (
              <circle cx="250" cy="130" r="8" fill="#228b22" fillOpacity="0.35" className="animate-ping" />
            )}
            <circle cx="250" cy="130" r="4.5" fill="#228b22" /> {/* Reg Liq */}
            <text x="250" y="120" fontSize="7" fontFamily="monospace" textAnchor="middle" fill="#1a1a1a">REG. LIQ.</text>

            <circle 
              cx="80" cy="130" r="3.5" 
              fill={isSentimentActive ? '#d32f2f' : '#f8f8f6'} 
              stroke={isSentimentActive ? '#d32f2f' : '#1a1a1a'} 
              strokeWidth="1.5" 
            /> {/* CRE */}
            <text x="80" y="120" fontSize="7" fontFamily="monospace" textAnchor="middle" fill="#1a1a1a">CRE DELINQ.</text>

            <circle cx="80" cy="70" r="3.5" fill="#f8f8f6" stroke="#1a1a1a" strokeWidth="1.5" /> {/* CPI */}
            <text x="80" y="60" fontSize="7" fontFamily="monospace" textAnchor="middle" fill="#1a1a1a">CPI</text>

            <circle cx="230" cy="70" r="3.5" fill="#f8f8f6" stroke="#1a1a1a" strokeWidth="1.5" /> {/* Wage */}
            <text x="230" y="60" fontSize="7" fontFamily="monospace" textAnchor="middle" fill="#1a1a1a">WAGE Δ</text>

            <circle cx="150" cy="160" r="3.5" fill="#f8f8f6" stroke="#1a1a1a" strokeWidth="1.5" /> {/* Housing */}
            <text x="150" y="172" fontSize="7" fontFamily="monospace" textAnchor="middle" fill="#1a1a1a">HOUSING</text>
          </svg>
        </div>
        
        {/* Beta values list */}
        <div className="flex flex-col gap-2 mt-2 pt-4 border-t border-border">
          <div className={cn("flex justify-between items-center text-[11px] font-mono p-1 transition-all duration-300", isInflationActive && "font-bold text-ink bg-ink/5 border border-dashed border-border")}>
            <span>FED FUNDS → 2s10s</span>
            <div className="flex gap-4">
              <span className="w-16 text-right">β = {fedFundsTo2s10s}</span>
              <span className="font-sans uppercase tracking-widest text-[9px] font-medium w-12 text-right">
                {Math.abs(fedFundsTo2s10sVal) > 0.6 ? 'STRONG' : 'MODERATE'}
              </span>
            </div>
          </div>
          <div className={cn("flex justify-between items-center text-[11px] font-mono p-1 transition-all duration-300", isInflationActive && "font-bold text-ink bg-ink/5 border border-dashed border-border")}>
            <span>2s10s → REG. LIQ.</span>
            <div className="flex gap-4">
              <span className="w-16 text-right">β = {twoS10sToRegLiqVal > 0 ? '+' : ''}{twoS10sToRegLiq}</span>
              <span className="font-sans uppercase tracking-widest text-[9px] font-medium w-12 text-right">
                {Math.abs(twoS10sToRegLiqVal) > 0.4 ? 'STRONG' : 'MODERATE'}
              </span>
            </div>
          </div>
          <div className={cn("flex justify-between items-center text-[11px] font-mono p-1 transition-all duration-300", isSentimentActive && "font-bold text-ink bg-ink/5 border border-dashed border-border")}>
            <span>CRE DELINQ → REG. LIQ.</span>
            <div className="flex gap-4">
              <span className="w-16 text-right">β = {creDelinqToRegLiq}</span>
              <span className={cn("font-sans uppercase tracking-widest text-[9px] font-medium w-12 text-right", Math.abs(creDelinqToRegLiqVal) > 0.7 ? "text-danger" : "text-ink/80")}>
                {Math.abs(creDelinqToRegLiqVal) > 0.7 ? 'CRITICAL' : 'MODERATE'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </Panel>
  );
};
