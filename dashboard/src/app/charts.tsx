"use client";

import React from 'react';
import { 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer, BarChart, Bar, AreaChart, Area,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ScatterChart, Scatter, ZAxis, Cell
} from 'recharts';

interface Feature {
  date: string;
  country: string;
  n_conflict_events: number;
  avg_goldstein: number;
  n_mentions: number;
  n_ucdp_events: number;
  total_fatalities: number;
  n_news_articles: number;
  n_hotspots: number;
  avg_frp: number;
  n_social_posts: number;
  avg_social_engagement: number;
  escalation_level: number;
}

interface OverallIntensity {
  date: string;
  overall_intensity: number;
}

interface ChartProps {
  type: 'timeline' | 'distribution' | 'heatmap' | 'radar' | 'scatter';
  data: Feature[] | OverallIntensity[];
}

const COLORS: Record<string, string> = {
  IRN: '#10b981',
  ISR: '#3b82f6',
  USA: '#f59e0b',
};

const LEVEL_COLORS = ['#10b981', '#f59e0b', '#ef4444'];

export default function Charts({ type, data }: ChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-slate-500">
        <p>Sin datos para visualizar</p>
      </div>
    );
  }

  if (type === 'timeline') {
    const timelineData = data as OverallIntensity[];
    const sampledData = timelineData.filter((_, i) => i % 7 === 0);
    
    return (
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={sampledData} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
          <defs>
            <linearGradient id="colorIntensity" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis 
            dataKey="date" 
            stroke="#64748b" 
            fontSize={11} 
            tickFormatter={(val: string) => {
              const d = new Date(val);
              return `${d.getMonth() + 1}/${String(d.getFullYear()).slice(2)}`;
            }}
          />
          <YAxis stroke="#64748b" fontSize={11} domain={[0, 2]} ticks={[0, 1, 2]} label={{ value: 'Nivel', angle: -90, position: 'insideLeft', fill: '#64748b' }} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f1f5f9' }}
            formatter={(value) => [Number(value).toFixed(2), "Intensidad"]}
            labelFormatter={(label) => `Fecha: ${label}`}
          />
          <Area 
            type="monotone" 
            dataKey="overall_intensity" 
            stroke="#ef4444" 
            strokeWidth={2} 
            fill="url(#colorIntensity)"
            activeDot={{ r: 6, fill: '#ef4444' }}
          />
        </AreaChart>
      </ResponsiveContainer>
    );
  }

  if (type === 'distribution') {
    const featureData = data as Feature[];
    const countries = [...new Set(featureData.map(d => d.country))];
    const dist: Record<string, Record<string, number>> = {
      'Bajo': { name: 0 },
      'Medio': { name: 0 },
      'Alto': { name: 0 }
    };
    
    countries.forEach(c => {
      dist['Bajo'][c] = 0;
      dist['Medio'][c] = 0;
      dist['Alto'][c] = 0;
    });
    
    featureData.forEach(row => {
      const level = row.escalation_level === 0 ? 'Bajo' : row.escalation_level === 1 ? 'Medio' : 'Alto';
      const country = row.country;
      if (dist[level]) {
        dist[level][country] = (dist[level][country] || 0) + 1;
      }
    });

    const chartData = Object.entries(dist).map(([key, val]) => ({
      name: key,
      ...val
    }));

    return (
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
          <YAxis stroke="#64748b" fontSize={12} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f1f5f9' }} 
          />
          <Legend wrapperStyle={{ paddingTop: '20px' }} />
          {countries.map(c => (
            <Bar key={c} dataKey={c} fill={COLORS[c] || '#64748b'} radius={[4, 4, 0, 0]} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    );
  }

  if (type === 'heatmap') {
    const featureData = data as Feature[];
    const monthlyData: Record<string, { month: string; country: string; events: number }> = {};
    
    featureData.forEach(row => {
      const month = row.date.slice(0, 7);
      const key = `${row.country}-${month}`;
      if (!monthlyData[key]) {
        monthlyData[key] = { month, country: row.country, events: 0 };
      }
      monthlyData[key].events += row.n_conflict_events;
    });

    const chartData = Object.values(monthlyData).sort((a, b) => a.month.localeCompare(b.month));
    const sampled = chartData.filter((_, i) => i % 3 === 0);

    return (
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={sampled} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
          <XAxis 
            dataKey="month" 
            stroke="#64748b" 
            fontSize={10}
            tickFormatter={(val: string) => val.slice(2)}
          />
          <YAxis stroke="#64748b" fontSize={11} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f1f5f9' }}
            formatter={(value, _name, props) => [value, `${props.payload.country}: Eventos`]}
          />
          <Bar dataKey="events" radius={[2, 2, 0, 0]}>
            {sampled.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[entry.country] || '#64748b'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    );
  }

  if (type === 'radar') {
    const featureData = data as Feature[];
    const avgMetrics = {
      'Eventos': featureData.reduce((s, d) => s + d.n_conflict_events, 0) / featureData.length,
      'Menciones': featureData.reduce((s, d) => s + d.n_mentions, 0) / featureData.length / 100,
      'UCDP': featureData.reduce((s, d) => s + d.n_ucdp_events, 0) / featureData.length,
      'Noticias': featureData.reduce((s, d) => s + d.n_news_articles, 0) / featureData.length,
      'Hotspots': featureData.reduce((s, d) => s + d.n_hotspots, 0) / featureData.length,
      'Social': featureData.reduce((s, d) => s + d.n_social_posts, 0) / featureData.length / 100,
    };

    const radarData = Object.entries(avgMetrics).map(([key, value]) => ({
      subject: key,
      value: Math.min(value, 10),
      fullMark: 10,
    }));

    return (
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={radarData}>
          <PolarGrid stroke="#334155" />
          <PolarAngleAxis dataKey="subject" stroke="#94a3b8" fontSize={12} />
          <PolarRadiusAxis stroke="#475569" fontSize={10} />
          <Radar 
            name="Promedio Fuentes" 
            dataKey="value" 
            stroke="#06b6d4" 
            fill="#06b6d4" 
            fillOpacity={0.3} 
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f1f5f9' }}
          />
        </RadarChart>
      </ResponsiveContainer>
    );
  }

  if (type === 'scatter') {
    const featureData = data as Feature[];
    const scatterData = featureData.map(d => ({
      events: d.n_conflict_events,
      fatalities: d.total_fatalities,
      country: d.country,
      level: d.escalation_level,
    }));

    const sampled = scatterData.filter((_, i) => i % 5 === 0);

    return (
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis 
            type="number" 
            dataKey="events" 
            name="Eventos" 
            stroke="#64748b" 
            fontSize={11}
            label={{ value: 'Eventos', position: 'bottom', fill: '#64748b', fontSize: 11 }}
          />
          <YAxis 
            type="number" 
            dataKey="fatalities" 
            name="Fatalidades" 
            stroke="#64748b" 
            fontSize={11}
            label={{ value: 'Fatalidades', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }}
          />
          <ZAxis range={[30, 100]} />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f1f5f9' }}
          />
          <Scatter data={sampled}>
            {sampled.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={LEVEL_COLORS[entry.level]} 
                fillOpacity={0.7}
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    );
  }

  return null;
}
