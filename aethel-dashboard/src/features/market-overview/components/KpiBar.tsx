import React from 'react';
import { Eyebrow, MonoValue } from '../../../shared/ui/Typography';
import { cn } from '../../../shared/lib/utils';

interface KpiBarProps {
  metrics: {
    expectedReturn?: number;
    var95?: number;
  };
}

export const KpiBar: React.FC<KpiBarProps> = ({ metrics }) => {
  const displayKpis = [
    { label: 'P(RECESSION | 12M)', value: '22.4%', subValue: '+1.2%', isPositive: false },
    { 
      label: 'EXPECTED RETURN | ANN.', 
      value: metrics.expectedReturn !== undefined ? `${metrics.expectedReturn > 0 ? '+' : ''}${metrics.expectedReturn}%` : '8.1%', 
      subValue: 'vs 9.4%', 
      isPositive: metrics.expectedReturn !== undefined ? metrics.expectedReturn >= 8.1 : true 
    },
    { 
      label: '95% VAR | DAILY', 
      value: metrics.var95 !== undefined ? `${metrics.var95}%` : '-2.41%', 
      subValue: 'α = 0.94', 
      isPositive: metrics.var95 !== undefined ? metrics.var95 >= -2.41 : false 
    },
    { label: 'CAUSAL CONFIDENCE', value: '0.87', subValue: 'high', isPositive: true },
    { label: 'PATHS SAMPLED', value: '10,000', subValue: 'n', isPositive: true },
    { label: 'SOURCES INGESTED | 24H', value: '4,218', subValue: '+312', isPositive: true },
  ];

  return (
    <div className="flex border-b border-border bg-paper shrink-0">
      {displayKpis.map((kpi, i) => (
        <div key={i} className={cn("flex-1 p-3 flex flex-col gap-1 border-r border-solid border-border last:border-r-0", i === 0 && "pl-4")}>
          <Eyebrow>{kpi.label}</Eyebrow>
          <div className="flex items-baseline gap-2">
            <span className="font-mono text-3xl tracking-tight">{kpi.value}</span>
            {kpi.subValue && (
              <MonoValue className={cn("text-[11px]", kpi.isPositive ? "text-success" : "text-danger")}>
                {kpi.subValue}
              </MonoValue>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
