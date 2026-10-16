import { StrictMode, useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

const API = 'http://127.0.0.1:8000';
type CatalogRow = { norad_id:string; epoch:string; object_name:string; object_type:string; predicted_category:string|null; owner:string; altitude_km:number|null; inclination_deg:number|null; period_min:number|null };
type CatalogPage = {items:CatalogRow[]; limit:number; offset:number; total:number; has_more:boolean};
type CatalogSummary = {sample_rows:number; sample_unique_norad_ids:number; sample_label_counts:Record<string,number>; elapsed_seconds:number};
type Summary = {objects:number; screening_runs:{object_count:number;samples:number;threshold_km:number;created_at:string}[]};
type Candidate = {id:number; object_a:string; object_b:string; epoch_utc:string; distance_km:number};
type Model = {target:string; accuracy:number; macro_f1:number};
type Eda = {report:{rows:number}; charts:string[]};

async function get<T>(path:string):Promise<T> {
  const response = await fetch(API + path);
  if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
  return response.json();
}

const chartLabels:Record<string,string> = {
  'apogee_hist.png': 'Height above Earth',
  'perigee_hist.png': 'Lowest altitude',
  'inclination_hist.png': 'Orbital tilt',
  'object_type_counts.png': 'Object categories',
};

function formatNumber(value:number|undefined|null, digits=0) {
  return value === undefined || value === null ? '—' : value.toLocaleString(undefined, {maximumFractionDigits:digits});
}

function App() {
  const [catalog, setCatalog] = useState<CatalogSummary|null>(null);
  const [summary, setSummary] = useState<Summary|null>(null);
  const [page, setPage] = useState<CatalogPage|null>(null);
  const [eda, setEda] = useState<Eda|null>(null);
  const [model, setModel] = useState<Model|null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('ALL');
  const [offset, setOffset] = useState(0);
  const [error, setError] = useState('');

  useEffect(() => {
    const query = new URLSearchParams({limit:'24', offset:String(offset)});
    if (search.trim()) query.set('search', search.trim());
    if (category !== 'ALL') query.set('object_type', category);
    Promise.all([
      get<CatalogSummary>('/api/catalog/summary'),
      get<Summary>('/api/summary'),
      get<CatalogPage>(`/api/catalog/objects?${query}`),
      get<Eda>('/api/eda'),
      get<{items:Model[]}>('/api/models'),
      get<{items:Candidate[]}>('/api/close-approaches'),
    ]).then(([c,s,p,e,m,a]) => {
      setCatalog(c); setSummary(s); setPage(p); setEda(e); setModel(m.items?.[0] ?? null); setCandidates(a.items ?? []);
    }).catch((reason:Error) => setError(reason.message));
  }, [offset, search, category]);

  const categories = useMemo(() => Object.entries(catalog?.sample_label_counts ?? {}).sort((a,b) => b[1] - a[1]), [catalog]);
  const maxCategory = categories[0]?.[1] ?? 1;
  const run = summary?.screening_runs?.[0];

  if (error) return <main className="shell"><section className="error-card"><span className="eyebrow">Workspace unavailable</span><h1>We could not load the sky view.</h1><p>{error}</p><p className="muted">Please start the local application and refresh this page.</p></section></main>;
  if (!catalog || !page) return <main className="shell loading"><span className="mark">✦</span><h1>Preparing your sky view…</h1><p>Loading the latest catalog summary.</p></main>;

  return <main className="shell">
    <header className="topbar">
      <a className="brand" href="#top" aria-label="Orbital Watch home"><span className="brand-mark">✦</span><span><b>Orbital Watch</b><small>Space around us</small></span></a>
      <nav><a className="active" href="#overview">Overview</a><a href="#objects">Objects</a><a href="#insights">Insights</a></nav>
      <span className="live-pill"><i /> Live workspace</span>
    </header>

    <section className="hero" id="top">
      <div className="hero-copy"><span className="eyebrow">A clearer view of near-Earth space</span><h1>Understand what’s<br /><em>moving above us.</em></h1><p>Explore a curated view of {formatNumber(catalog.sample_rows)} catalog observations, see how they are grouped, and review the closest recorded approaches.</p><div className="hero-actions"><a className="primary" href="#objects">Explore the catalog <span>↘</span></a><a className="quiet-link" href="#insights">See the story <span>↓</span></a></div></div>
      <div className="orbit-art" aria-hidden="true"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="planet"><span>✦</span></div><div className="satellite satellite-one">◆</div><div className="satellite satellite-two">◆</div></div>
    </section>

    <section className="stat-grid" id="overview">
      <article className="stat-card accent"><span className="stat-icon">◌</span><small>Observations in view</small><strong>{formatNumber(catalog.sample_rows)}</strong><span className="stat-note">A focused, readable sample</span></article>
      <article className="stat-card"><span className="stat-icon">◎</span><small>Distinct catalog objects</small><strong>{formatNumber(catalog.sample_unique_norad_ids)}</strong><span className="stat-note">Across the selected view</span></article>
      <article className="stat-card"><span className="stat-icon">◈</span><small>Object categories</small><strong>{categories.length}</strong><span className="stat-note">A simple way to explore</span></article>
      <article className="stat-card warm"><span className="stat-icon">✧</span><small>Closest review item</small><strong>{candidates[0] ? `${formatNumber(candidates[0].distance_km, 1)} km` : 'None'}</strong><span className="stat-note">A screening result, not a collision</span></article>
    </section>

    <section className="feature-grid" id="insights">
      <article className="card category-card"><div className="section-head"><div><span className="eyebrow">At a glance</span><h2>What’s in the catalog?</h2></div><span className="soft-label">Catalog view</span></div><p className="card-intro">Each color represents a different kind of space object recorded in this view.</p><div className="bars">{categories.map(([name,count]) => <div className="bar-row" key={name}><div className="bar-label"><span><i className={`dot dot-${name.replace('/','-')}`} />{name}</span><b>{formatNumber(count)}</b></div><div className="bar-track"><span style={{width:`${Math.max(4, count / maxCategory * 100)}%`}} /></div></div>)}</div></article>
      <article className="card quality-card"><div className="section-head"><div><span className="eyebrow">Category guide</span><h2>How well does it sort?</h2></div><span className="soft-label green">Verified</span></div><div className="score-ring"><div><strong>{model ? `${(model.accuracy * 100).toFixed(0)}%` : '—'}</strong><span>overall match</span></div></div><div className="score-line"><span>Balanced score</span><b>{model ? `${(model.macro_f1 * 100).toFixed(0)}%` : '—'}</b></div><p className="card-footnote">This guide identifies object categories. It does not predict collision risk.</p></article>
    </section>

    <section className="card gallery-card"><div className="section-head"><div><span className="eyebrow">Patterns from real observations</span><h2>See the shape of the sky</h2></div><span className="soft-label">Four views</span></div><div className="chart-grid">{(eda?.charts ?? []).map(chart => <figure key={chart}><img src={`${API}/api/eda/${chart}`} alt={chartLabels[chart] ?? chart} /><figcaption>{chartLabels[chart] ?? chart}</figcaption></figure>)}</div></section>

    <section className="card catalog-card" id="objects"><div className="section-head catalog-head"><div><span className="eyebrow">Explore the records</span><h2>Find an object</h2></div><span className="soft-label">{formatNumber(page.total)} matches</span></div><div className="filters"><label className="search-box"><span>⌕</span><input value={search} onChange={e => {setOffset(0);setSearch(e.target.value)}} placeholder="Search by name or catalog ID" /></label><select value={category} onChange={e => {setOffset(0);setCategory(e.target.value)}}><option value="ALL">All categories</option>{categories.map(([name]) => <option key={name} value={name}>{name}</option>)}</select></div><div className="table-wrap"><table><thead><tr><th>Catalog ID</th><th>Object</th><th>Known category</th><th>Suggested category</th><th>Operator</th><th>Height</th></tr></thead><tbody>{page.items.map(row => <tr key={`${row.norad_id}-${row.epoch}`}><td className="mono">{row.norad_id}</td><td><b>{row.object_name}</b><small>{row.epoch.replace('T',' · ').replace('+05:30',' UTC')}</small></td><td><span className={`category category-${row.object_type.replace('/','-')}`}>{row.object_type}</span></td><td><span className={`category category-${(row.predicted_category ?? 'UNK').replace('/','-')}`}>{row.predicted_category ?? '—'}</span></td><td>{row.owner}</td><td>{formatNumber(row.altitude_km, 1)} km</td></tr>)}</tbody></table></div><div className="pager"><span>Showing {page.items.length ? offset + 1 : 0}–{Math.min(offset + page.items.length, page.total)} of {formatNumber(page.total)}</span><div><button disabled={offset===0} onClick={() => setOffset(Math.max(0, offset - 24))}>← Back</button><button disabled={!page.has_more} onClick={() => setOffset(offset + 24)}>Next →</button></div></div></section>

    <section className="bottom-grid"><article className="card approach-card"><div className="section-head"><div><span className="eyebrow">Keep an eye on</span><h2>Closest approaches</h2></div><span className="soft-label warm-label">Review only</span></div><p className="card-intro">These are threshold-based screening results for further review, not confirmed collisions.</p>{candidates.length ? <div className="approach-list">{candidates.slice(0,3).map(candidate => <div className="approach-row" key={candidate.id}><div><b>{candidate.object_a}</b><span>and</span><b>{candidate.object_b}</b><small>{candidate.epoch_utc}</small></div><strong>{formatNumber(candidate.distance_km, 2)} <small>km apart</small></strong></div>)}</div> : <p className="muted">No review items in the current view.</p>}<div className="approach-meta">{run?.object_count ?? 0} objects reviewed · {run?.samples ?? 0} moments observed</div></article><article className="card note-card"><span className="big-quote">“</span><h2>Every object tells part of the story.</h2><p>This view is designed to help you notice patterns, ask better questions, and focus attention where it matters.</p><a href="#top" className="quiet-link">Back to overview ↑</a></article></section>
    <footer><span>Orbital Watch · Space Debris Analytics</span><span>Evidence-backed view · Updated {new Date().toLocaleDateString()}</span></footer>
  </main>;
}

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>);
