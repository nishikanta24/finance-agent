import React from 'react';
import { cn } from '../lib/utils';

export const NarrativeText: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({ className, ...props }) => (
  <p className={cn("font-serif italic text-base leading-relaxed text-ink", className)} {...props} />
);

export const PanelTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ className, ...props }) => (
  <h2 className={cn("font-serif italic text-2xl text-ink tracking-tight", className)} {...props} />
);

export const Eyebrow: React.FC<React.HTMLAttributes<HTMLSpanElement>> = ({ className, ...props }) => (
  <span className={cn("font-sans uppercase tracking-[0.2em] text-[10px] font-medium text-ink/70", className)} {...props} />
);

export const MonoValue: React.FC<React.HTMLAttributes<HTMLSpanElement>> = ({ className, ...props }) => (
  <span className={cn("font-mono text-[13px] tracking-tight", className)} {...props} />
);
