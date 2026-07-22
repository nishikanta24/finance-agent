import React, { useState } from 'react';
import { Header } from '../features/market-overview/components/Header';
import { KpiBar } from '../features/market-overview/components/KpiBar';
import { SignalFeed } from '../features/market-overview/components/SignalFeed';
import { Sentiment } from '../features/market-overview/components/Sentiment';
import { Sidebar } from '../features/analysis/components/Sidebar';
import { MonteCarloChart } from '../features/analysis/components/MonteCarloChart';
import { CausalGraph } from '../features/analysis/components/CausalGraph';
import { MethodTrace } from '../features/analysis/components/MethodTrace';
import { CHAT_HISTORY, METHOD_TRACE, generateMonteCarloData } from '../features/market-overview/data/dashboardData';

const extractTickerFromQuery = (query: string): string => {
  const q = query.toLowerCase();
  
  const mappings: { [key: string]: string } = {
    'palantir': 'PLTR',
    'pltr': 'PLTR',
    'nvidia': 'NVDA',
    'nvda': 'NVDA',
    'tesla': 'TSLA',
    'tsla': 'TSLA',
    'apple': 'AAPL',
    'aapl': 'AAPL',
    'microsoft': 'MSFT',
    'msft': 'MSFT',
    'google': 'GOOG',
    'goog': 'GOOG',
    'alphabet': 'GOOG',
    'amazon': 'AMZN',
    'amzn': 'AMZN',
    'meta': 'META',
    'facebook': 'META',
    'amd': 'AMD',
    'intel': 'INTC',
    'intc': 'INTC',
    'netflix': 'NFLX',
    'nflx': 'NFLX',
    'broadcom': 'AVGO',
    'avgo': 'AVGO',
    'qualcomm': 'QCOM',
    'qcom': 'QCOM',
    'goldman': 'GS',
    'gs': 'GS',
    'jpmorgan': 'JPM',
    'jpm': 'JPM',
  };

  for (const key of Object.keys(mappings)) {
    if (q.includes(key)) {
      return mappings[key];
    }
  }

  const words = query.replace(/[^a-zA-Z]/g, ' ').split(/\s+/);
  for (const word of words) {
    if (word.length >= 2 && word.length <= 5) {
      if (word === word.toUpperCase()) {
        return word;
      }
    }
  }

  for (const word of words) {
    if (word.length >= 2 && word.length <= 5) {
      return word.toUpperCase();
    }
  }

  return 'PLTR';
};

function App() {
  const [query, setQuery] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [aiResponse, setAiResponse] = useState('');
  const [chatHistory, setChatHistory] = useState<any[]>(CHAT_HISTORY);

  // Dynamic metrics state
  const [metrics, setMetrics] = useState<any>({
    expectedReturn: undefined,
    var95: undefined,
    worst5: undefined,
    median: undefined,
    best5: undefined
  });

  // Default trace from dummyData
  const [executionTrace, setExecutionTrace] = useState<any[]>(METHOD_TRACE);

  // Default chart data
  const [chartData, setChartData] = useState<any[]>(() => generateMonteCarloData());

  // Causal simulation parameter states for Relationship Graph
  const [primaryCausalDriver, setPrimaryCausalDriver] = useState<string>('');
  const [inflationShockValue, setInflationShockValue] = useState<number>(0.0);
  const [sentimentShockValue, setSentimentShockValue] = useState<number>(0.0);

  const generateDynamicChartData = (medianVal: number, lowerVal: number, upperVal: number) => {
    const paths = [];
    let seed = 1337;
    const pseudoRandom = () => {
      const x = Math.sin(seed++) * 10000;
      return x - Math.floor(x);
    };

    for (let i = 0; i <= 6; i++) {
      const point: any = { month: `M+${i}` };
      point.median = (medianVal / 6) * i;
      point.lower90 = (lowerVal / 6) * i;
      point.upper90 = (upperVal / 6) * i;

      for (let j = 0; j < 15; j++) {
        const randOffset = pseudoRandom() - 0.5;
        const width = (upperVal - lowerVal) * (i / 6);
        point[`path${j}`] = point.median + randOffset * width * 1.5;
      }
      paths.push(point);
    }
    return paths;
  };

  const handleAnalyze = async (searchQuery: string) => {
    if (!searchQuery.trim() || isAnalyzing) return;

    setQuery(searchQuery);
    setIsAnalyzing(true);
    setAiResponse('');
    setPrimaryCausalDriver(''); // Reset primary driver at query start

    const ticker = extractTickerFromQuery(searchQuery);

    let inflationShock = 0.0;
    const inflationMatch = searchQuery.match(/inflation\s*(?:up|down|shock|change)?\s*(?:by|of)?\s*([+-]?\d+(?:\.\d+)?)\s*%/i);
    if (inflationMatch) {
      inflationShock = parseFloat(inflationMatch[1]) / 100.0;
    }

    let sentimentShock = 0.0;
    const sentimentMatch = searchQuery.match(/sentiment\s*(?:up|down|shock|change)?\s*(?:by|of)?\s*([+-]?\d+(?:\.\d+)?)\s*%/i);
    if (sentimentMatch) {
      sentimentShock = parseFloat(sentimentMatch[1]) / 100.0;
    }

    setInflationShockValue(inflationShock);
    setSentimentShockValue(sentimentShock);

    const newTrace = [
      { step: '01', description: `Parsed intent → ticker: ${ticker} / shocks: INF ${(inflationShock * 100).toFixed(1)}%, SEN ${(sentimentShock * 100).toFixed(1)}%` }
    ];
    setExecutionTrace(newTrace);

    const userMsg = {
      role: 'user' as const,
      content: searchQuery
    };
    setChatHistory(prev => [...prev, userMsg]);

    const processLine = (trimmed: string) => {
      if (!trimmed || !trimmed.startsWith('data: ')) return;

      try {
        const parsed = JSON.parse(trimmed.substring(6));
        const { status, message, data } = parsed;

        if (status === 'ingesting') {
          setExecutionTrace(prev => {
            const next = [...prev];
            next[1] = { step: '02', description: message };
            return next;
          });
        } else if (status === 'extracting') {
          setExecutionTrace(prev => {
            const next = [...prev];
            next[2] = { step: '03', description: message };
            return next;
          });
        } else if (status === 'causal_modeling') {
          setExecutionTrace(prev => {
            const next = [...prev];
            next[3] = { step: '04', description: message };
            return next;
          });
        } else if (status === 'simulating') {
          setExecutionTrace(prev => {
            const next = [...prev];
            next[4] = { step: '05', description: message };
            return next;
          });
        } else if (status === 'synthesizing') {
          setExecutionTrace(prev => {
            const next = [...prev];
            next[5] = { step: '06', description: message };
            return next;
          });
        } else if (status === 'complete' && data) {
          const expectedVal = data.expected_valuation_change_pct;
          const lowerVal = data.confidence_intervals["95_pct"][0];
          const upperVal = data.confidence_intervals["95_pct"][1];
          const summary = data.summary;

          setMetrics({
            expectedReturn: expectedVal,
            var95: lowerVal,
            worst5: lowerVal,
            median: expectedVal,
            best5: upperVal
          });

          const nextChartData = generateDynamicChartData(expectedVal, lowerVal, upperVal);
          setChartData(nextChartData);
          setAiResponse(summary);
          setPrimaryCausalDriver(data.primary_causal_driver);

          const agentMsg = {
            role: 'agent' as const,
            content: summary,
            sources: ['FRB H.8', 'Goldman GIR', 'NY Fed Q4 Survey']
          };
          setChatHistory(prev => [...prev, agentMsg]);
        } else if (status === 'error') {
          const errorMsg = message || 'Simulation failed.';
          setChatHistory(prev => [
            ...prev,
            {
              role: 'agent' as const,
              content: `Error: ${errorMsg}`,
              sources: []
            }
          ]);
        }
      } catch (err) {
        console.error('Failed to parse SSE payload line:', trimmed, err);
      }
    };

    try {
      const url = `http://localhost:8000/api/v1/analytics/stream?ticker=${encodeURIComponent(ticker)}&inflation_shock_pct=${inflationShock}&sentiment_shock_pct=${sentimentShock}`;
      const response = await fetch(url);
      
      if (!response.body) {
        throw new Error('ReadableStream not supported');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          processLine(line);
        }
      }

      // Flush remaining buffer content
      if (buffer.trim()) {
        processLine(buffer);
      }
    } catch (error) {
      console.error('Error during streaming fetch:', error);
      setExecutionTrace(prev => [
        ...prev,
        { step: 'ERR', description: 'Stream failed or server disconnected' }
      ]);
      setChatHistory(prev => [
        ...prev,
        {
          role: 'agent' as const,
          content: `Error: Failed to connect to the simulation engine. Please verify that the FastAPI backend server is running on http://localhost:8000.`,
          sources: []
        }
      ]);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="h-screen w-screen overflow-hidden flex flex-col bg-border">
      <Header />
      <KpiBar metrics={metrics} />
      
      <div className="flex-1 min-h-0 overflow-hidden grid grid-cols-12 gap-px bg-border">
        {/* Sidebar */}
        <div className="col-span-3 h-full bg-paper min-h-0">
          <Sidebar 
            chatHistory={chatHistory} 
            onAnalyze={handleAnalyze} 
            isAnalyzing={isAnalyzing} 
          />
        </div>
        
        {/* Main Shared Scroll Region */}
        <div className="col-span-9 h-full grid grid-cols-9 bg-paper -space-x-px overflow-hidden">
          {/* Center Column */}
          <div className="col-span-6 h-full overflow-y-auto overflow-x-hidden flex flex-col -space-y-px scroll-smooth">
            <MonteCarloChart 
              chartData={chartData} 
              worst5={metrics.worst5} 
              median={metrics.median} 
              best5={metrics.best5} 
            />
            <SignalFeed />
          </div>
          
          {/* Right Column */}
          <div className="col-span-3 h-full overflow-y-auto overflow-x-hidden flex flex-col -space-y-px scroll-smooth">
            <CausalGraph 
              primaryCausalDriver={primaryCausalDriver}
              inflationShock={inflationShockValue}
              sentimentShock={sentimentShockValue}
            />
            <Sentiment />
            <MethodTrace executionTrace={executionTrace} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
