import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, ReferenceLine, ReferenceDot } from 'recharts';
import { Eyebrow, PanelTitle, MonoValue } from '../../../shared/ui/Typography';
import { Panel, PanelHeader } from '../../../shared/ui/Panel';

interface MonteCarloChartProps {
  chartData: any[];
  worst5?: number;
  median?: number;
  best5?: number;
}

export const MonteCarloChart: React.FC<MonteCarloChartProps> = ({ chartData, worst5, median, best5 }) => {
  return (
    <Panel>
      <PanelHeader className="flex-row justify-between items-start">
        <div>
          <Eyebrow>SIMULATION ENGINE</Eyebrow>
          <PanelTitle>Monte Carlo Projection</PanelTitle>
          <div className="font-sans text-[11px] text-ink/70 mt-1">
            Regional Bank Liquidity Index - 10,000 paths - 6-month horizon
          </div>
        </div>
        <div className="flex gap-4">
          <div className="flex items-center gap-1.5 font-sans text-[10px] uppercase tracking-wider text-ink/70">
            <div className="w-4 h-0.5 bg-ink" /> MEDIAN
          </div>
          <div className="flex items-center gap-1.5 font-sans text-[10px] uppercase tracking-wider text-ink/70">
            <div className="w-4 h-0.5 bg-ink/20" /> 90% CI
          </div>
          <div className="flex items-center gap-1.5 font-sans text-[10px] uppercase tracking-wider text-ink/70">
            <div className="w-4 h-0.5 bg-success" /> EXPANSION
          </div>
        </div>
      </PanelHeader>

      <div className="h-[240px] w-full mt-4 relative">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 20, right: 30, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e2e2" />
            <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#1a1a1a', opacity: 0.7, fontFamily: 'monospace' }} dy={10} />
            <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#1a1a1a', opacity: 0.7, fontFamily: 'monospace' }} tickFormatter={(val) => `${val > 0 ? '+' : ''}${val}%`} domain={[-10, 10]} ticks={[-10, -5, 0, 5, 10]} />
            
            {/* Background paths */}
            {Array.from({ length: 15 }).map((_, i) => (
              <Area key={i} type="monotone" dataKey={`path${i}`} stroke="#1a1a1a" strokeOpacity={0.03} fill="none" isAnimationActive={false} />
            ))}
            
            {/* Confidence interval */}
            <Area type="monotone" dataKey="upper90" stroke="none" fill="#1a1a1a" fillOpacity={0.05} isAnimationActive={false} />
            <Area type="monotone" dataKey="lower90" stroke="none" fill="#f8f8f6" fillOpacity={1} isAnimationActive={false} />
            
            {/* Median line */}
            <Area type="monotone" dataKey="median" stroke="#1a1a1a" strokeWidth={2} fill="none" />
            
            {/* Target point (Q4 expansion) */}
            <ReferenceDot x="M+4" y={median !== undefined ? (median / 6) * 4 : 5.8} r={4} fill="#228b22" stroke="none" />
            <ReferenceLine segment={[{x: "M+4", y: median !== undefined ? (median / 6) * 4 : 5.8}, {x: "M+4", y: -4}]} stroke="#228b22" strokeDasharray="3 3" />
          </AreaChart>
        </ResponsiveContainer>
        
        {/* Label for target */}
        <div className="absolute top-[24%] left-[68%] font-mono text-[10px]">
          P(expansion Q4) = 68.2%
        </div>
      </div>

      <div className="flex justify-between border-t border-border mt-4 pt-4">
        <div className="flex flex-col gap-1">
          <Eyebrow>WORST 5%</Eyebrow>
          <MonoValue className="text-xl text-danger">{worst5 !== undefined ? `${worst5}%` : '-14.2%'}</MonoValue>
        </div>
        <div className="flex flex-col gap-1 items-center">
          <Eyebrow>MEDIAN</Eyebrow>
          <MonoValue className="text-xl text-success">{median !== undefined ? `${median > 0 ? '+' : ''}${median}%` : '+6.8%'}</MonoValue>
        </div>
        <div className="flex flex-col gap-1 items-end">
          <Eyebrow>BEST 5%</Eyebrow>
          <MonoValue className="text-xl text-success">{best5 !== undefined ? `${best5 > 0 ? '+' : ''}${best5}%` : '+22.1%'}</MonoValue>
        </div>
      </div>
    </Panel>
  );
};
