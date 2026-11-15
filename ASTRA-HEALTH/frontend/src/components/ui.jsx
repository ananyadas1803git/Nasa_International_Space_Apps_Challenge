import React, { useCallback, useEffect, useRef, useState } from 'react';
import { RefreshCw, AlertTriangle, CheckCircle2 } from 'lucide-react';

export const STATUS = {
  normal: { label: 'Within personal range', cls: 'ok' },
  attention: { label: 'Change from baseline', cls: 'warn' },
  review: { label: 'Marked change · review', cls: 'bad' },
  insufficient_data: { label: 'Not enough history', cls: 'idle' },
};

export function StatusChip({ status, label }) {
  const s = STATUS[status] || STATUS.insufficient_data;
  return <span className={`status-chip ${s.cls}`}><i />{label || s.label}</span>;
}

export function Metric({ icon: Icon, label, value, suffix = '', note }) {
  return (
    <div className="metric-card">
      <div className="metric-top"><span>{label}</span><div className="metric-icon"><Icon size={17} /></div></div>
      <div className="metric-value">{value}<small>{suffix}</small></div>
      <div className="metric-note">{note}</div>
    </div>
  );
}

export function PageHeading({ eyebrow, title, subtitle, onRefresh, children }) {
  return (
    <div className="page-heading">
      <div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{subtitle}</p></div>
      <div className="heading-actions">{children}{onRefresh && <button className="outline-btn" onClick={onRefresh}><RefreshCw size={15} /> Refresh</button>}</div>
    </div>
  );
}

export const Loading = ({ text = 'Loading…' }) => <div className="loading-inline"><RefreshCw className="spin" size={18} /><span>{text}</span></div>;
export const ErrorBox = ({ error, onRetry }) => error ? <div className="alert-banner inline"><AlertTriangle size={17} />{error}{onRetry && <button onClick={onRetry}>Retry</button>}</div> : null;
export const Success = ({ children }) => children ? <div className="success-banner"><CheckCircle2 size={17} />{children}</div> : null;

/** Fetch helper: { data, error, loading, reload }. Re-runs when deps change. */
export function useAsync(fn, deps) {
  const [state, setState] = useState({ data: null, error: '', loading: true });
  const alive = useRef(true);
  const run = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: '' }));
    try { const data = await fn(); if (alive.current) setState({ data, error: '', loading: false }); }
    catch (e) { if (alive.current) setState((s) => ({ ...s, error: e.message, loading: false })); }
  }, deps); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { alive.current = true; run(); return () => { alive.current = false; }; }, [run]);
  return { ...state, reload: run };
}

export function CrewPicker({ crew, value, onChange }) {
  return (
    <div className="chips" role="tablist" aria-label="Crew member">
      {crew.map((c) => (
        <button key={c.id} role="tab" aria-selected={value === c.id} className={`chip ${value === c.id ? 'active' : ''}`} onClick={() => onChange(c.id)}>
          <span className={`crew-avatar mini av-${c.id}`}>{c.name.split(' ').filter((w) => !w.endsWith('.')).map((x) => x[0]).slice(0, 2).join('')}</span>{c.name}
        </button>
      ))}
    </div>
  );
}

export function fmtDate(iso, withTime = false) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleString(undefined, withTime ? { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' } : { month: 'short', day: 'numeric' });
}

export function ago(iso) {
  if (!iso) return 'no data';
  const mins = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 60000));
  if (mins < 2) return 'just now';
  if (mins < 60) return `${mins} min ago`;
  if (mins < 1440) return `${Math.round(mins / 60)} h ago`;
  return `${Math.round(mins / 1440)} d ago`;
}

export const initials = (name) => name.split(' ').filter((w) => !w.endsWith('.')).map((x) => x[0]).slice(0, 2).join('');
