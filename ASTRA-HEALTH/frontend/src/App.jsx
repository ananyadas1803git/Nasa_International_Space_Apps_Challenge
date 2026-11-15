import React, { useCallback, useEffect, useState } from 'react';
import { Brain, Orbit, LayoutDashboard, Users, ShieldAlert, ClipboardPlus, Bell, LogOut, Menu, X, AlertTriangle, PersonStanding, RefreshCw, FilePlus2 } from 'lucide-react';
import { api } from './api.js';
import Login from './components/Login.jsx';
import { initials } from './components/ui.jsx';
import Overview from './pages/Overview.jsx';
import CrewHealth from './pages/CrewHealth.jsx';
import Records from './pages/Records.jsx';
import BodyExplorer from './pages/BodyExplorer.jsx';
import Hazards from './pages/Hazards.jsx';
import Assessments from './pages/Assessments.jsx';
import MLPrediction from './pages/MLPrediction.jsx';

const NAV = [
  ['Overview', LayoutDashboard], ['Crew health', Users], ['Health records', FilePlus2],
  ['Body explorer', PersonStanding], ['Hazard watch', ShieldAlert], ['Assessments', ClipboardPlus], ['ML prediction', Brain],
];
const slug = (p) => p.toLowerCase().replace(/\s+/g, '-');
const fromHash = () => NAV.find(([p]) => slug(p) === window.location.hash.slice(1))?.[0] || 'Overview';

export default function App() {
  const [auth, setAuth] = useState(() => { try { return JSON.parse(localStorage.getItem('av_session') || 'null'); } catch { return null; } });
  const [page, setPageState] = useState(fromHash);
  const [focus, setFocus] = useState(null);       // astronaut id to pre-select on other pages
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [mobile, setMobile] = useState(false);
  const token = auth?.access_token;

  const go = useCallback((p, astronautId = null) => { setFocus(astronautId); setPageState(p); window.location.hash = slug(p); setMobile(false); }, []);
  useEffect(() => { const h = () => setPageState(fromHash()); window.addEventListener('hashchange', h); return () => window.removeEventListener('hashchange', h); }, []);

  const logout = useCallback(() => { localStorage.removeItem('av_session'); setAuth(null); setData(null); }, []);
  const load = useCallback(async () => {
    if (!token) return;
    setError('');
    try { setData(await api('/dataset/dashboard', { token })); }
    catch (e) { if (e.status === 401) logout(); else setError(e.message); }
  }, [token, logout]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => { if (!token) return; const t = setInterval(load, 60000); return () => clearInterval(t); }, [token, load]); // live-ish refresh

  if (!auth) return <Login onLogin={(d) => { localStorage.setItem('av_session', JSON.stringify(d)); setAuth(d); }} />;

  const highRiskCrew = data?.metrics?.high_risk_astronauts || 0;
  const shared = { token, crew: data?.crew || [], focus, go, refreshDashboard: load };
  const View = { 'Overview': Overview, 'Crew health': CrewHealth, 'Health records': Records, 'Body explorer': BodyExplorer, 'Hazard watch': Hazards, 'Assessments': Assessments, 'ML prediction': MLPrediction }[page];

  return (
    <div className="app-shell">
      {mobile && <div className="scrim" onClick={() => setMobile(false)} />}
      <aside className={`sidebar ${mobile ? 'open' : ''}`}>
        <div className="side-brand">
          <div className="brand-symbol"><Orbit size={21} /></div>
          <div><b>ASTRA-HEALTH</b><small>ASTRONAUT HEALTH</small></div>
          <button className="mobile-close" onClick={() => setMobile(false)} aria-label="Close menu"><X /></button>
        </div>
        <div className="mission-chip"><span className="pulse-dot" /><div><small>ACTIVE MISSION</small><b>{data?.mission?.code || 'LOADING DATASET…'}</b></div></div>
        <div className="nav-label">WORKSPACE</div>
        <nav>
          {NAV.map(([label, Icon]) => (
            <button key={label} className={`nav-item ${page === label ? 'active' : ''}`} onClick={() => go(label)}>
              <Icon size={18} />{label}{label === 'Hazard watch' && highRiskCrew > 0 && <span className="nav-count" title="Astronauts with at least one High dataset label">{highRiskCrew}</span>}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className={`system-status ${error ? 'down' : ''}`}>
            <span className="pulse-dot" />
            <div><b>{error ? 'API unreachable' : 'Dataset connected'}</b><small>{(data?.metrics?.total_observations || 0).toLocaleString()} imported observations</small></div>
          </div>
          <button className="nav-item" onClick={logout}><LogOut size={18} />Sign out</button>
          <div className="operator">
            <div className="avatar">{initials(auth.user?.full_name || 'Mission Control')}</div>
            <div><b>{auth.user?.full_name || 'Mission Control'}</b><small>{auth.user?.email}</small></div>
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <button className="mobile-menu" onClick={() => setMobile(true)} aria-label="Open menu"><Menu /></button>
          <div className="crumb">MISSION CONTROL <span>/</span> <b>{page.toUpperCase()}</b></div>
          <div className="top-actions">
            <div className="live-pill"><span className="pulse-dot" /> DATASET CONNECTED</div>
            <button className="icon-btn" title={`${highRiskCrew} astronauts have at least one High dataset label`} onClick={() => go('Hazard watch')} aria-label="Open alerts"><Bell size={18} />{highRiskCrew > 0 && <i />}</button>
            <div className="top-avatar">{initials(auth.user?.full_name || 'MC')}</div>
          </div>
        </header>
        {error && <div className="alert-banner"><AlertTriangle size={17} />{error}<button onClick={load}>Retry</button></div>}
        {!data ? (
          error ? null : <div className="loading-state"><RefreshCw className="spin" /><span>Synchronising mission telemetry…</span></div>
        ) : (
          <div className="content">
            <View key={page} data={data} {...shared} />
            <footer className="app-footer"><span>ASTRA-HEALTH ASTRONAUT HEALTH SYSTEM</span><span>PROTOTYPE · SYNTHETIC DATA · NOT FOR CLINICAL USE</span></footer>
          </div>
        )}
      </main>
    </div>
  );
}
