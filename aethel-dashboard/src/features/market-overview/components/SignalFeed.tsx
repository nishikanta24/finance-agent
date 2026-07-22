import React from 'react';
import { FEED_ITEMS } from '../data/dashboardData';
import { Eyebrow, PanelTitle, NarrativeText, MonoValue } from '../../../shared/ui/Typography';
import { Panel, PanelHeader } from '../../../shared/ui/Panel';

export const SignalFeed: React.FC = () => {
  return (
    <Panel className="flex flex-col">
      <PanelHeader className="flex-row justify-between items-start shrink-0">
        <div>
          <Eyebrow>GLOBAL INTELLIGENCE</Eyebrow>
          <PanelTitle>Signal Feed</PanelTitle>
          <div className="font-sans text-[11px] text-ink/70 mt-1">
            Live · 4,218 sources · dedup + causal tagging
          </div>
        </div>
        <div className="flex items-center gap-1.5 font-sans text-[10px] uppercase tracking-wider text-success">
          <div className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" />
          STREAMING
        </div>
      </PanelHeader>

      <div className="mt-2 pr-2 flex flex-col gap-0">
        {FEED_ITEMS.map((item, i) => (
          <div key={i} className="flex gap-4 py-4 border-b border-border last:border-b-0 group cursor-pointer hover:bg-ink/5 -mx-5 px-5 transition-colors">
            <MonoValue className="text-[11px] text-ink/50 mt-1 w-10 shrink-0">{item.time}</MonoValue>
            <div className="flex flex-col gap-2">
              <NarrativeText className="text-[15px]">{item.headline}</NarrativeText>
              <div className="flex gap-3 items-center">
                <span className="font-sans text-[10px] uppercase tracking-widest text-ink/70 font-medium">{item.source}</span>
                <span className="font-mono text-[10px] text-ink/40">conf {item.confidence}</span>
              </div>
            </div>
            <div className="ml-auto mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
               <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-ink/40"><path d="M7 17L17 7M17 7H7M17 7V17"/></svg>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  );
};
