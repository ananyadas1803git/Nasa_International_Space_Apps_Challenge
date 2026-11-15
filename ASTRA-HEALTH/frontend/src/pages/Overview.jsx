import React from 'react';
import { Users, ShieldAlert, Database, CalendarDays, Satellite, ArrowUpRight, Activity, RadioTower, Orbit, HeartPulse, Moon, Thermometer, Dna } from 'lucide-react';
import { Metric, PageHeading, initials } from '../components/ui.jsx';
import { HAZARDS } from '../data/knowledge.js';
const ICONS = { radiation: RadioTower, isolation: Users, distance: Orbit, gravity: Activity, closed: Thermometer };
const levelClass = (s) => String(s || 'Unknown').toLowerCase().replace(/[^a-z]/g, '');
export default function Overview({ data, go, refreshDashboard }) {
  const { mission, crew, metrics, dataset } = data;
  const totals = metrics.risk_level_counts || {};
  const sorted = [...crew].sort((a,b) => b.high_risk_count-a.high_risk_count || b.moderate_risk_count-a.moderate_risk_count);
  return <>
    <PageHeading eyebrow={`${mission?.code || 'MISSION'} · DAY ${mission?.day_number ?? '—'}`} title="Mission health overview" subtitle="A live view of the supplied astronaut health dataset across the complete simulated mission." onRefresh={refreshDashboard} />
    <div className="mission-banner"><div className="mission-icon"><Satellite size={24}/></div><div className="mission-info"><small>DATASET MISSION · {dataset?.mission_phases?.join(' / ')}</small><h3>{mission?.name}</h3><span>{mission?.spacecraft} <i/> {mission?.destination} <i/> {mission?.environment}</span></div><div className="mission-day"><b>{mission?.day_number ?? '—'}</b><small>MISSION DAYS</small></div></div>
    <div className="metric-grid">
      <Metric icon={Users} label="Astronauts" value={metrics.crew_count} note="Unique astronaut IDs in source dataset"/>
      <Metric icon={Database} label="Observations" value={metrics.total_observations?.toLocaleString()} note="Imported astronaut × mission-day rows"/>
      <Metric icon={ShieldAlert} label="High-level signals" value={totals.High || totals.Higher || 0} note="High / Higher category counts across latest crew rows"/>
      <Metric icon={CalendarDays} label="Dataset coverage" value={metrics.mission_day} suffix=" days" note="Mission-day span represented in source data"/>
    </div>
    <div className="section-grid">
      <section className="panel crew-panel"><div className="panel-head"><div><h3>Astronaut roster</h3><p>Latest available observation for each astronaut · sorted by number of High signals</p></div><button className="text-btn" onClick={()=>go('Crew health')}>View crew <ArrowUpRight size={15}/></button></div>
        <div className="crew-table"><div className="table-head overview-cols"><span>ASTRONAUT</span><span>HEART RATE</span><span>SLEEP</span><span>MISSION DAY</span><span>RISK SIGNALS</span></div>
          {sorted.map(c=><button className="crew-row overview-cols row-btn" key={c.id} onClick={()=>go('Crew health',c.id)}><div className="crew-person"><div className={`crew-avatar av-${c.id}`}>{initials(c.name)}</div><div><b>{c.crew_code}</b><small>{c.role}</small></div></div><div className="vital"><HeartPulse size={14}/>{c.heart_rate ?? '—'} <small>bpm</small></div><div className="vital"><Moon size={14}/>{c.sleep_hours ?? '—'} <small>h</small></div><div>{c.mission_day} <small>{c.mission_phase}</small></div><div><span className={`severity ${c.high_risk_count?'high':c.moderate_risk_count?'monitor':'info'}`}>{c.high_risk_count} high</span><small className="muted"> · {c.moderate_risk_count} moderate</small></div></button>)}
        </div>
      </section>
      <section className="panel"><div className="panel-head"><div><h3>Risk-level distribution</h3><p>Latest record per astronaut across 17 risk domains</p></div><Dna size={20} className="muted-icon"/></div>
        {['High','Higher','Moderate','Lower','Low'].filter(k=>totals[k]).map(k=><div className="risk-count-row" key={k}><span className={`severity ${levelClass(k)==='higher'?'high':levelClass(k)==='moderate'?'monitor':'info'}`}>{k}</span><b>{totals[k]}</b></div>)}
        <div className="callout">These are dataset-provided risk categories, not diagnoses or clinical alert thresholds. Counts combine the latest available row for each astronaut.</div>
      </section>
    </div>
    <div className="section-grid second"><section className="panel"><div className="panel-head"><div><h3>Five human-spaceflight hazards</h3><p>Hazard categories linked to the integrated dataset</p></div></div><div className="hazard-mini">{HAZARDS.map(h=>{const I=ICONS[h.id]||Activity;return <button key={h.id} className="hazard-mini-card" onClick={()=>go('Hazard watch')}><I size={18}/><b>{h.name}</b><small>{h.short}</small></button>})}</div></section><section className="panel"><div className="panel-head"><div><h3>Dataset integrity</h3><p>Imported source coverage</p></div></div><div className="data-facts"><div><b>147</b><span>columns per observation</span></div><div><b>5</b><span>hazard domains</span></div><div><b>17</b><span>risk domains</span></div><div><b>{dataset?.mission_phases?.length || 0}</b><span>mission phases</span></div></div><div className="callout">Source: {dataset?.source}. Values and labels are displayed as supplied; this prototype does not independently validate medical meaning.</div></section></div>
  </>;
}
