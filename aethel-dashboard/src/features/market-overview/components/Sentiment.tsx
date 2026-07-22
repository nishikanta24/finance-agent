import React from 'react';
import { SENTIMENT_DATA } from '../data/dashboardData';
import { Eyebrow, PanelTitle } from '../../../shared/ui/Typography';
import { Panel, PanelHeader } from '../../../shared/ui/Panel';
import { cn } from '../../../shared/lib/utils';

export const Sentiment: React.FC = () => {
  return (
    <Panel className="shrink-0">
      <PanelHeader>
        <Eyebrow>REGIONAL</Eyebrow>
        <PanelTitle>Sentiment</PanelTitle>
        <div className="font-sans text-[11px] text-ink/70 mt-1">
          24h weighted average · news + rates
        </div>
      </PanelHeader>

      <div className="flex flex-col gap-5 mt-3 border-t border-border pt-4">
        {SENTIMENT_DATA.map((item, i) => (
          <div key={i} className="flex flex-col gap-2 relative">
            <div className="flex justify-between items-end">
              <span className="font-mono text-[12px]">{item.region}</span>
              <span className={cn(
                "font-sans uppercase tracking-widest text-[9px] font-medium",
                item.status === 'BULLISH' ? "text-success" :
                item.status === 'BEARISH' ? "text-danger" :
                "text-ink/60"
              )}>
                {item.label}
              </span>
            </div>
            
            <div className="w-full h-1 bg-ink/10 relative">
              <div className="absolute w-px h-2 bg-ink/30 left-1/2 -top-0.5" />
              {item.score !== 0 && (
                <div 
                  className={cn(
                    "absolute h-full",
                    item.score > 0 ? "bg-success" : "bg-danger"
                  )}
                  style={{
                    left: item.score > 0 ? '50%' : `${50 + (item.score * 50)}%`,
                    width: `${Math.abs(item.score) * 50}%`
                  }}
                />
              )}
            </div>
          </div>
        ))}
      </div>
    </Panel>
  );
};
