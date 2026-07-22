import React from 'react';
import { Eyebrow, NarrativeText, PanelTitle } from '../../../shared/ui/Typography';
import { SourceTag } from '../../../shared/ui/Panel';
import { Plus } from 'lucide-react';

interface SidebarProps {
  chatHistory: any[];
  onAnalyze: (query: string) => void;
  isAnalyzing: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ chatHistory, onAnalyze, isAnalyzing }) => {
  const [inputVal, setInputVal] = React.useState('');
  const chatEndRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputVal.trim() && !isAnalyzing) {
      onAnalyze(inputVal);
      setInputVal('');
    }
  };

  return (
    <div className="h-full flex flex-col border-r border-border bg-paper min-h-0">
      {/* Session Header */}
      <div className="p-4 border-b border-border flex justify-between items-start shrink-0">
        <div className="flex flex-col gap-1">
          <Eyebrow>SESSION</Eyebrow>
          <PanelTitle className="text-xl">Rates & Regional Banks</PanelTitle>
        </div>
        <button className="flex items-center gap-1 text-[10px] uppercase font-sans tracking-widest text-ink hover:text-ink/70">
          <Plus size={12} strokeWidth={2} /> NEW
        </button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-8">
        {chatHistory.map((msg, i) => (
          <div key={i} className="flex flex-col gap-2">
            <Eyebrow className="text-[9px]">{msg.role === 'user' ? 'YOU' : 'AETHEL'}</Eyebrow>
            {msg.role === 'user' ? (
              <NarrativeText className="text-[17px] border-l-2 border-ink/20 pl-4">{msg.content}</NarrativeText>
            ) : (
              <div className="flex flex-col gap-3">
                <div className="bg-ink/5 p-4 text-[13px] leading-relaxed font-sans text-ink/90">
                  {msg.content}
                </div>
                {msg.sources && (
                  <div className="flex gap-2 flex-wrap">
                    {msg.sources.map((src, j) => (
                      <SourceTag key={j}>{src}</SourceTag>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-border flex flex-col shrink-0 bg-paper">
        <form onSubmit={handleSubmit} className="flex border border-border">
          <input 
            type="text" 
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            disabled={isAnalyzing}
            placeholder="Ask about markets, macro, or a specific position..." 
            className="flex-1 bg-transparent px-3 py-2 text-sm font-serif italic outline-none placeholder:text-ink/40 disabled:opacity-50"
          />
          <button 
            type="submit"
            disabled={isAnalyzing}
            className="bg-ink text-paper px-4 font-sans text-[11px] uppercase tracking-wider font-medium hover:bg-ink/90 transition-colors disabled:opacity-50"
          >
            {isAnalyzing ? 'ANALYZING...' : 'ANALYZE'}
          </button>
        </form>
      </div>
    </div>
  );
};
