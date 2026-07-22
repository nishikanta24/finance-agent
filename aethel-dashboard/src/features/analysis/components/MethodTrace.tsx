import React from 'react';
import { Eyebrow, PanelTitle, MonoValue } from '../../../shared/ui/Typography';
import { Panel, PanelHeader } from '../../../shared/ui/Panel';

interface MethodTraceProps {
  executionTrace: any[];
}

export const MethodTrace: React.FC<MethodTraceProps> = ({ executionTrace }) => {
  return (
    <Panel className="shrink-0 mb-8">
      <PanelHeader>
        <Eyebrow>METHOD</Eyebrow>
        <PanelTitle>How this answer was made</PanelTitle>
        <div className="font-sans text-[11px] text-ink/70 mt-1">
          Full reasoning trace
        </div>
      </PanelHeader>

      <div className="flex flex-col mt-2 border-t border-border pt-4 relative">
        <div className="absolute left-4 top-4 bottom-2 w-px border-l border-dashed border-border" />
        {executionTrace.map((item, i) => (
          <div key={i} className="flex gap-4 py-2 relative">
            <MonoValue className="text-ink/60 bg-paper w-8 text-center shrink-0 z-10">{item.step}</MonoValue>
            <MonoValue className="text-ink text-[12px] pt-px">{item.description}</MonoValue>
          </div>
        ))}
      </div>
    </Panel>
  );
};
