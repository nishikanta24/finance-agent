export interface TickerData {
  symbol: string;
  value: string;
  change: string;
  isPositive: boolean;
}

export interface KPI {
  label: string;
  value: string;
  subValue?: string;
  isPositive?: boolean;
}

export interface ChatMessage {
  role: 'user' | 'agent';
  content: string;
  sources?: string[];
}

export interface FeedItem {
  time: string;
  headline: string;
  source: string;
  confidence: string;
}

export interface SentimentData {
  region: string;
  label: string;
  score: number; // -1 to 1
  status: 'BULLISH' | 'NEUTRAL' | 'BEARISH' | 'CAUTIOUS';
}

export interface MethodTraceItem {
  step: string;
  description: string;
}

export const TICKERS: TickerData[] = [
  { symbol: 'NDX', value: '18,241.02', change: '+0.62%', isPositive: true },
  { symbol: 'US10Y', value: '4.214%', change: '-1.2 bp', isPositive: false },
  { symbol: 'US2Y', value: '4.612%', change: '-0.4 bp', isPositive: false },
  { symbol: 'DXY', value: '103.82', change: '+0.12%', isPositive: true },
  { symbol: 'EUR/USD', value: '1.0842', change: '-0.09%', isPositive: false },
  { symbol: 'WTI', value: '82.14', change: '+1.04%', isPositive: true },
  { symbol: 'XAU', value: '2,341.20', change: '+0.21%', isPositive: true },
  { symbol: 'BTC', value: '64,281.00', change: '+2.41%', isPositive: true },
  { symbol: 'VIX', value: '13.42', change: '-3.38%', isPositive: false },
  { symbol: 'SPX', value: '5,137.08', change: '+0.41%', isPositive: true },
];

export const KPIS: KPI[] = [
  { label: 'P(RECESSION | 12M)', value: '22.4%', subValue: '+1.2%', isPositive: false },
  { label: 'EXPECTED RETURN | ANN.', value: '8.1%', subValue: 'vs 9.4%', isPositive: true },
  { label: '95% VAR | DAILY', value: '-2.41%', subValue: 'α = 0.94', isPositive: false },
  { label: 'CAUSAL CONFIDENCE', value: '0.87', subValue: 'high', isPositive: true },
  { label: 'PATHS SAMPLED', value: '10,000', subValue: 'n', isPositive: true },
  { label: 'SOURCES INGESTED | 24H', value: '4,218', subValue: '+312', isPositive: true },
];

export const CHAT_HISTORY: ChatMessage[] = [
  {
    role: 'user',
    content: 'How will a 25 bps Fed cut in September propagate through regional bank liquidity by Q4?',
  },
  {
    role: 'agent',
    content: 'Reading the causal graph, the dominant channel is not funding cost — it\'s the yield curve. A 25 bps front-end cut with a sticky long end (10Y anchored above 4.15%) steepens the curve ~15 bps, expanding NIM for banks with floating-rate books but compressing it for regionals overweight fixed-rate CRE. Monte Carlo across 10,000 macro paths puts P(regional liquidity expansion by Q4) at 68.2%, but the left tail is fat: 12% of paths show a CRE-driven contraction if delinquencies breach 8.0%.',
    sources: ['FRB H.8', 'Goldman GIR', 'NY Fed Q4 Survey'],
  }
];

export const PROMPTS = [
  'Stress test my 60/40 for a 50 bps hike',
  'Decompose the DXY rally into causal factors',
  'Probability of a Fed pivot before June',
  'Second-order effects of a Taiwan Strait shock on semis',
];

export const FEED_ITEMS: FeedItem[] = [
  { time: '14:22', headline: 'U.S. housing starts fall 14.7% in February — largest decline since early 2022; permits softer across South & West.', source: 'REUTERS', confidence: '0.98' },
  { time: '13:05', headline: 'ECB\'s Lagarde signals a June window for possible rate adjustment as core inflation cools to 3.1%.', source: 'BLOOMBERG', confidence: '0.93' },
  { time: '12:41', headline: 'Japan Q1 GDP revised higher on capex; BoJ hawks gain internal support ahead of April meeting.', source: 'FT', confidence: '0.87' },
  { time: '11:58', headline: 'Regional lenders quietly building cash buffers as CRE delinquency rate climbs to 5.4%.', source: 'WSJ', confidence: '0.83' },
  { time: '10:33', headline: 'Panama Canal draft restrictions ease; freight rates on U.S. Gulf routes down 6% week-over-week.', source: 'NYT', confidence: '0.79' },
];

export const SENTIMENT_DATA: SentimentData[] = [
  { region: 'North America', label: 'BULLISH', score: 0.6, status: 'BULLISH' },
  { region: 'Eurozone', label: 'NEUTRAL', score: 0.1, status: 'NEUTRAL' },
  { region: 'Emerging Markets', label: 'BEARISH', score: -0.4, status: 'BEARISH' },
  { region: 'Asia Pacific', label: 'CAUTIOUS', score: -0.1, status: 'CAUTIOUS' },
];

export const METHOD_TRACE: MethodTraceItem[] = [
  { step: '01', description: 'Parsed intent = macro / regional banks' },
  { step: '02', description: 'Retrieved 312 documents from feed (72h)' },
  { step: '03', description: 'Updated causal DAG (7 nodes touched)' },
  { step: '04', description: 'Ran 10,000 MC paths - GPU 42ms' },
  { step: '05', description: 'Aggregated tail statistics - flagged CRE' },
  { step: '06', description: 'Composed synthesis with source pins' },
];

// Generate fake Monte Carlo data
export const generateMonteCarloData = () => {
  const paths = [];
  for (let i = 0; i <= 6; i++) {
    const point: any = { month: `M+${i}` };
    // Median
    point.median = i * 1.1 + Math.random() * 0.5;
    
    // 90% CI bands
    point.upper90 = point.median + (i * 0.8 + Math.random());
    point.lower90 = point.median - (i * 0.8 + Math.random());
    
    // Some random background paths for visual density
    for(let j=0; j<15; j++) {
      point[`path${j}`] = (Math.random() - 0.5) * i * 2.5 + (i * 0.8);
    }
    
    paths.push(point);
  }
  return paths;
};
