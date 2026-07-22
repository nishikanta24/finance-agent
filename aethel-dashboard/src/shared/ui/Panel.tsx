import React from 'react';
import { cn } from '../lib/utils';

export const Panel: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, ...props }) => (
  <div className={cn("border border-border bg-paper p-5 flex flex-col gap-3 rounded-none shadow-none", className)} {...props} />
);

export const PanelHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, ...props }) => (
  <div className={cn("flex flex-col gap-1 mb-2", className)} {...props} />
);

export const Pill: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement> & { active?: boolean }> = ({ className, active, ...props }) => (
  <button 
    className={cn(
      "rounded-full border border-border px-3 py-1 font-sans text-[11px] uppercase tracking-wider transition-colors hover:bg-ink/5",
      active && "bg-ink text-paper hover:bg-ink/90",
      className
    )} 
    {...props} 
  />
);

export const SourceTag: React.FC<React.HTMLAttributes<HTMLSpanElement>> = ({ className, ...props }) => (
  <span className={cn("rounded-md border border-border px-1.5 py-0.5 font-sans text-[10px] uppercase tracking-wider text-ink/70", className)} {...props} />
);
