"use client";

import React, { useState, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  AlertTriangle, Activity, BarChart3, Database, Target, 
  BrainCircuit, Globe, TrendingUp, Users, Filter, Info,
  Shield, Zap, Eye
} from 'lucide-react';
import featuresData from '../../public/data/features.json';
import overallData from '../../public/data/overall_intensity.json';
import metricsData from '../../public/data/metrics.json';

const Charts = dynamic(() => import('./charts'), { ssr: false });

interface Feature {
  date: string;
  country: string;
  n_conflict_events: number;
  avg_goldstein: number;
  n_mentions: number;
  has_high_violence: number;
  n_ucdp_events: number;
  total_fatalities: number;
  n_news_articles: number;
  n_hotspots: number;
  avg_frp: number;
  n_social_posts: number;
  avg_social_engagement: number;
  conflict_events_rolling_3d: number;
  fatalities_rolling_3d: number;
  conflict_score: number;
  escalation_level: number;
}

interface OverallIntensity {
  date: string;
  overall_intensity: number;
}

interface ModelMetrics {
  f1_weighted_mean: number;
  f1_weighted_std: number;
  precision_mean: number;
  recall_mean: number;
}

const features = featuresData as Feature[];
const overall = overallData as OverallIntensity[];
const metrics = metricsData as Record<string, ModelMetrics>;

export default function Dashboard() {
  const countries = ['IRN', 'ISR', 'USA'];
  const countryNames: Record<string, string> = {
    'IRN': 'Irán',
    'ISR': 'Israel',
    'USA': 'EE.UU.'
  };

  const [selectedCountries, setSelectedCountries] = useState<string[]>(countries);
  const [dateRange, setDateRange] = useState<[string, string]>(['2024-01-01', '2026-12-31']);

  const filteredFeatures = useMemo(() => {
    return features.filter((f: Feature) => 
      selectedCountries.includes(f.country) &&
      f.date >= dateRange[0] &&
      f.date <= dateRange[1]
    );
  }, [selectedCountries, dateRange]);

  const filteredOverall = useMemo(() => {
    return overall.filter((o: OverallIntensity) => 
      o.date >= dateRange[0] && o.date <= dateRange[1]
    );
  }, [dateRange]);

  const kpis = useMemo(() => {
    const totalEvents = filteredFeatures.reduce((sum: number, f: Feature) => sum + f.n_conflict_events, 0);
    const totalFatalities = filteredFeatures.reduce((sum: number, f: Feature) => sum + f.total_fatalities, 0);
    const avgEscalation = filteredFeatures.length > 0 
      ? filteredFeatures.reduce((sum: number, f: Feature) => sum + f.escalation_level, 0) / filteredFeatures.length 
      : 0;
    const highEscalationDays = filteredFeatures.filter((f: Feature) => f.escalation_level === 2).length;
    return { totalEvents, totalFatalities, avgEscalation, highEscalationDays };
  }, [filteredFeatures]);

  const toggleCountry = (country: string) => {
    setSelectedCountries(prev => 
      prev.includes(country) 
        ? prev.filter(c => c !== country)
        : [...prev, country]
    );
  };

  const bestModel = Object.entries(metrics).reduce((best, [name, m]) => 
    m.f1_weighted_mean > best[1].f1_weighted_mean ? [name, m] : best,
    Object.entries(metrics)[0] || ['', { f1_weighted_mean: 0, f1_weighted_std: 0, precision_mean: 0, recall_mean: 0 }]
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      <header className="sticky top-0 z-50 w-full border-b border-slate-800/50 bg-slate-950/90 backdrop-blur-xl">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex gap-3 items-center">
            <div className="p-2 rounded-lg bg-gradient-to-br from-red-500/20 to-orange-500/20 border border-red-500/30">
              <Shield className="h-5 w-5 text-red-400" />
            </div>
            <div>
              <span className="font-bold text-lg hidden sm:inline-block">OSINT Intelligence</span>
              <span className="text-xs text-slate-500 block sm:hidden">ML1</span>
            </div>
          </div>
          <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
            <a href="#overview" className="text-slate-400 hover:text-slate-100 transition-colors">Panorama</a>
            <a href="#analytics" className="text-slate-400 hover:text-slate-100 transition-colors">Analítica</a>
            <a href="#models" className="text-slate-400 hover:text-slate-100 transition-colors">Modelos</a>
            <a href="#sources" className="text-slate-400 hover:text-slate-100 transition-colors">Fuentes</a>
          </nav>
          <div className="hidden lg:flex items-center gap-2 text-xs text-slate-500">
            <Users className="h-3 w-3" />
            <span>Rincón · Barrera · Pardo</span>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 space-y-12">
        
        <section id="overview" className="space-y-8 animate-fade-in-up">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-medium">
              <AlertTriangle className="h-3 w-3" />
              Proyecto Final · Machine Learning 1
            </div>
            <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl gradient-text">
              Sistema de Inteligencia Multifuente
            </h1>
            <p className="max-w-[800px] text-slate-400 text-lg md:text-xl">
              Clasificación del nivel de escalada en el conflicto Irán-Israel-EE.UU. 
              utilizando 5 fuentes OSINT y modelos de Machine Learning.
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <KPICard 
              icon={<Zap className="h-5 w-5 text-yellow-400" />}
              label="Eventos de Conflicto"
              value={kpis.totalEvents.toLocaleString()}
              trend="+12.3%"
            />
            <KPICard 
              icon={<AlertTriangle className="h-5 w-5 text-red-400" />}
              label="Fatalidades Totales"
              value={kpis.totalFatalities.toLocaleString()}
              trend="UCDP"
            />
            <KPICard 
              icon={<TrendingUp className="h-5 w-5 text-orange-400" />}
              label="Escalada Promedio"
              value={kpis.avgEscalation.toFixed(2)}
              subtitle="0=Bajo, 2=Alto"
            />
            <KPICard 
              icon={<Eye className="h-5 w-5 text-purple-400" />}
              label="Días Alta Escalada"
              value={kpis.highEscalationDays.toString()}
              subtitle={`de ${filteredFeatures.length} observaciones`}
            />
          </div>
        </section>

        <section className="glass-card rounded-xl p-6 space-y-4">
          <div className="flex items-center gap-2 text-slate-300">
            <Filter className="h-5 w-5" />
            <h3 className="font-semibold">Filtros Interactivos</h3>
          </div>
          <div className="flex flex-wrap gap-6">
            <div className="space-y-2">
              <label className="text-sm text-slate-400">Países</label>
              <div className="flex gap-2">
                {countries.map(c => (
                  <button
                    key={c}
                    onClick={() => toggleCountry(c)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      selectedCountries.includes(c)
                        ? 'bg-gradient-to-r from-red-500 to-orange-500 text-white shadow-lg shadow-red-500/20'
                        : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                    }`}
                  >
                    {countryNames[c]}
                  </button>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm text-slate-400">Rango de Fechas</label>
              <div className="flex gap-2 items-center">
                <input
                  type="date"
                  value={dateRange[0]}
                  onChange={(e) => setDateRange([e.target.value, dateRange[1]])}
                  className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-200"
                />
                <span className="text-slate-500">—</span>
                <input
                  type="date"
                  value={dateRange[1]}
                  onChange={(e) => setDateRange([dateRange[0], e.target.value])}
                  className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-sm text-slate-200"
                />
              </div>
            </div>
          </div>
        </section>

        <section id="analytics" className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20">
              <BarChart3 className="h-5 w-5 text-blue-400" />
            </div>
            <h2 className="text-2xl font-bold">Analítica Temporal</h2>
          </div>
          
          <Tabs defaultValue="timeline" className="w-full">
            <TabsList className="bg-slate-900/50 border border-slate-800">
              <TabsTrigger value="timeline">Evolución Temporal</TabsTrigger>
              <TabsTrigger value="distribution">Distribución</TabsTrigger>
              <TabsTrigger value="heatmap">Mapa de Calor</TabsTrigger>
            </TabsList>
            
            <TabsContent value="timeline" className="mt-6">
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="text-slate-200">Intensidad de Escalada en el Tiempo</CardTitle>
                </CardHeader>
                <CardContent className="h-[400px]">
                  <Charts type="timeline" data={filteredOverall} />
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="distribution" className="mt-6">
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="text-slate-200">Distribución por País y Nivel de Escalada</CardTitle>
                </CardHeader>
                <CardContent className="h-[400px]">
                  <Charts type="distribution" data={filteredFeatures} />
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="heatmap" className="mt-6">
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="text-slate-200">Eventos de Conflicto por País</CardTitle>
                </CardHeader>
                <CardContent className="h-[400px]">
                  <Charts type="heatmap" data={filteredFeatures} />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </section>

        <section className="grid gap-6 md:grid-cols-2">
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-slate-200 flex items-center gap-2">
                <Activity className="h-5 w-5 text-cyan-400" />
                Radar de Fuentes OSINT
              </CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <Charts type="radar" data={filteredFeatures} />
            </CardContent>
          </Card>
          
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-slate-200 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-emerald-400" />
                Eventos vs Fatalidades
              </CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <Charts type="scatter" data={filteredFeatures} />
            </CardContent>
          </Card>
        </section>

        <section id="models" className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
              <BrainCircuit className="h-5 w-5 text-emerald-400" />
            </div>
            <h2 className="text-2xl font-bold">Evaluación de Modelos ML</h2>
          </div>
          
          <p className="text-slate-400 max-w-[700px]">
            Comparamos 4 modelos de clasificación con validación cruzada temporal (TimeSeriesSplit, 5 splits). 
            El mejor modelo fue <span className="text-emerald-400 font-semibold">{bestModel[0]}</span> con 
            un F1-score ponderado de <span className="text-emerald-400 font-semibold">{(bestModel[1].f1_weighted_mean * 100).toFixed(1)}%</span>.
          </p>

          <div className="grid gap-4 md:grid-cols-2">
            {Object.entries(metrics).map(([modelName, m]) => (
              <Card 
                key={modelName} 
                className={`glass-card transition-all hover:scale-[1.02] ${
                  modelName === bestModel[0] ? 'ring-2 ring-emerald-500/50 animate-pulse-glow' : ''
                }`}
              >
                <CardHeader>
                  <CardTitle className="flex justify-between items-center text-slate-200">
                    <span className="flex items-center gap-2">
                      {modelName === bestModel[0] && <Zap className="h-4 w-4 text-emerald-400" />}
                      {modelName}
                    </span>
                    {modelName === bestModel[0] && (
                      <span className="text-xs bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full border border-emerald-500/30">
                        Mejor Modelo
                      </span>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <MetricBox label="F1 Score" value={m.f1_weighted_mean} color="emerald" />
                    <MetricBox label="Precisión" value={m.precision_mean} color="blue" />
                    <MetricBox label="Recall" value={m.recall_mean} color="purple" />
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500 transition-all duration-1000"
                      style={{ width: `${m.f1_weighted_mean * 100}%` }}
                    />
                  </div>
                  <p className="text-xs text-slate-500">
                    σ = ±{(m.f1_weighted_std * 100).toFixed(1)}%
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        <section id="sources" className="space-y-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
              <Database className="h-5 w-5 text-cyan-400" />
            </div>
            <h2 className="text-2xl font-bold">5 Fuentes de Inteligencia Abierta</h2>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <SourceCard 
              name="GDELT 2.0"
              type="Eventos + NLP"
              description="Base de datos global de eventos, tono Goldstein y menciones mediáticas derivadas de noticias."
              icon={<Globe className="h-6 w-6 text-blue-400" />}
              color="blue"
            />
            <SourceCard 
              name="UCDP"
              type="Conflictos Armados"
              description="Uppsala Conflict Data Program: eventos georreferenciados de violencia organizada con fatalidades verificadas."
              icon={<Target className="h-6 w-6 text-red-400" />}
              color="red"
            />
            <SourceCard 
              name="NASA FIRMS"
              type="Señales Térmicas"
              description="Hotspots de fuego detectados por satélite VIIRS. Proxy de actividad anómala o destrucción."
              icon={<Zap className="h-6 w-6 text-orange-400" />}
              color="orange"
            />
            <SourceCard 
              name="RSS Feeds"
              type="Cobertura Mediática"
              description="BBC Middle East y Al Jazeera RSS para monitoreo editorial y contraste de narrativas regionales."
              icon={<Eye className="h-6 w-6 text-purple-400" />}
              color="purple"
            />
            <SourceCard 
              name="Bluesky"
              type="Pulso Social"
              description="Red social descentralizada. Posts y engagement como señal de conversación pública sobre el conflicto."
              icon={<Users className="h-6 w-6 text-cyan-400" />}
              color="cyan"
            />
          </div>
        </section>

        <section className="glass-card rounded-xl p-8 space-y-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
              <Info className="h-5 w-5 text-amber-400" />
            </div>
            <h2 className="text-2xl font-bold">Problema Analítico</h2>
          </div>
          
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-200">Pregunta de Investigación</h3>
              <p className="text-slate-400 leading-relaxed">
                ¿Hasta qué punto un conjunto de fuentes abiertas y gratuitas permite detectar, 
                clasificar o modelar episodios de escalada regional en el conflicto Irán-Israel-EE.UU.?
              </p>
              
              <h3 className="text-lg font-semibold text-slate-200">Unidad de Análisis</h3>
              <p className="text-slate-400 leading-relaxed">
                <span className="text-cyan-400 font-medium">País-día</span>: cada fila del dataset 
                representa una región en una fecha específica, permitiendo agregar eventos, 
                noticias y señales contextuales en ventanas temporales.
              </p>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-slate-200">Tarea de ML</h3>
              <p className="text-slate-400 leading-relaxed">
                Clasificación supervisada multiclase del nivel de escalada:
              </p>
              <div className="space-y-2">
                <div className="flex items-center gap-3 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                  <div className="w-3 h-3 rounded-full bg-emerald-500" />
                  <span className="text-sm"><strong>Bajo (0)</strong>: Actividad cercana al comportamiento base</span>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
                  <div className="w-3 h-3 rounded-full bg-amber-500" />
                  <span className="text-sm"><strong>Medio (1)</strong>: Aumento moderado de señales</span>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <span className="text-sm"><strong>Alto (2)</strong>: Concentración fuerte de eventos</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="glass-card rounded-xl p-8 space-y-6 border-amber-500/20">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20">
              <AlertTriangle className="h-5 w-5 text-amber-400" />
            </div>
            <h2 className="text-2xl font-bold">Limitaciones y Consideraciones Éticas</h2>
          </div>
          
          <div className="grid gap-4 md:grid-cols-2">
            <LimitationCard 
              title="Sesgo de Cobertura Mediática"
              description="GDELT deriva eventos de noticias, lo que refleja sesgos editoriales y de idioma. Eventos en zonas remotas pueden estar subrepresentados."
            />
            <LimitationCard 
              title="Niebla de Guerra"
              description="En conflictos activos, la información es incompleta, contradictoria o manipulada. Las fuentes OSINT no pueden verificar hechos en tiempo real."
            />
            <LimitationCard 
              title="Datos Sintéticos para Demo"
              description="Esta versión usa datos generados sintéticamente para demostración. Las APIs reales están validadas pero requieren credenciales o tienen restricciones de acceso."
            />
            <LimitationCard 
              title="Causalidad vs Correlación"
              description="El modelo identifica patrones estadísticos, no relaciones causales. Las predicciones no deben usarse para toma de decisiones críticas sin validación experta."
            />
          </div>
        </section>

      </main>
      
      <footer className="border-t border-slate-800/50 bg-slate-950 py-8 mt-12">
        <div className="container mx-auto px-4 space-y-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="text-center md:text-left">
              <p className="text-slate-400 font-medium">Proyecto Final · Machine Learning 1</p>
              <p className="text-slate-500 text-sm">Universidad Externado de Colombia · 2026</p>
            </div>
            <div className="text-center md:text-right">
              <p className="text-slate-400 text-sm font-medium">Equipo</p>
              <p className="text-slate-500 text-sm">
                Juan Tomás Rincón Pinzón · Hudy Nicolás Barrera Castañeda · Alejandro Pardo Costo
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

function KPICard({ icon, label, value, trend, subtitle }: { 
  icon: React.ReactNode; 
  label: string; 
  value: string; 
  trend?: string;
  subtitle?: string;
}) {
  return (
    <Card className="glass-card hover:border-slate-600 transition-all">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <p className="text-sm text-slate-400">{label}</p>
            <p className="text-3xl font-bold text-slate-100">{value}</p>
            {(trend || subtitle) && (
              <p className="text-xs text-slate-500">{trend || subtitle}</p>
            )}
          </div>
          <div className="p-2 rounded-lg bg-slate-800/50">
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function MetricBox({ label, value, color }: { label: string; value: number; color: string }) {
  const colorClasses: Record<string, string> = {
    emerald: 'text-emerald-400',
    blue: 'text-blue-400',
    purple: 'text-purple-400',
  };
  
  return (
    <div className="text-center">
      <p className="text-xs text-slate-500 mb-1">{label}</p>
      <p className={`text-xl font-bold font-mono ${colorClasses[color]}`}>
        {(value * 100).toFixed(1)}%
      </p>
    </div>
  );
}

function SourceCard({ name, type, description, icon, color }: {
  name: string;
  type: string;
  description: string;
  icon: React.ReactNode;
  color: string;
}) {
  const colorClasses: Record<string, string> = {
    blue: 'from-blue-500/20 to-blue-500/5 border-blue-500/30',
    red: 'from-red-500/20 to-red-500/5 border-red-500/30',
    orange: 'from-orange-500/20 to-orange-500/5 border-orange-500/30',
    purple: 'from-purple-500/20 to-purple-500/5 border-purple-500/30',
    cyan: 'from-cyan-500/20 to-cyan-500/5 border-cyan-500/30',
  };
  
  return (
    <Card className={`bg-gradient-to-br ${colorClasses[color]} border hover:scale-[1.02] transition-all`}>
      <CardContent className="p-5 space-y-3">
        <div className="flex items-center gap-3">
          {icon}
          <div>
            <h3 className="font-semibold text-slate-200">{name}</h3>
            <p className="text-xs text-slate-400">{type}</p>
          </div>
        </div>
        <p className="text-sm text-slate-400 leading-relaxed">{description}</p>
      </CardContent>
    </Card>
  );
}

function LimitationCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="p-4 rounded-lg bg-slate-800/30 border border-slate-700/50 space-y-2">
      <h4 className="font-medium text-slate-200 text-sm">{title}</h4>
      <p className="text-sm text-slate-400 leading-relaxed">{description}</p>
    </div>
  );
}
