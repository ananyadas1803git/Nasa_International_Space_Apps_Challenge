import React, { useState } from 'react';
import { Orbit, LockKeyhole, Mail, ArrowRight, CheckCircle2, AlertTriangle, User } from 'lucide-react';
import { api } from '../api.js';

const DEMO = { email: 'demo@astravault.test', password: 'OrbitReady!2026' };

export default function Login({ onLogin }) {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ ...DEMO, full_name: '' });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });
  const register = mode === 'register';

  async function submit(e) {
    e.preventDefault(); setBusy(true); setError('');
    try {
      const body = register ? { email: form.email, password: form.password, full_name: form.full_name } : { email: form.email, password: form.password };
      onLogin(await api(register ? '/auth/register' : '/auth/login', { method: 'POST', body }));
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }
  function switchMode() {
    setError(''); setMode(register ? 'login' : 'register');
    setForm(register ? { ...DEMO, full_name: '' } : { email: '', password: '', full_name: '' });
  }

  return (
    <main className="login-shell">
      <div className="login-art">
        <div className="orbit orbit-a" /><div className="orbit orbit-b" /><div className="planet" />
        <div className="art-copy">
          <div className="brand-mark"><Orbit size={20} /> ASTRA-HEALTH</div>
          <div className="eyebrow">ASTRONAUT HEALTH INTELLIGENCE</div>
          <h1>Human performance,<br /><em>in deep space.</em></h1>
          <p>One clear view of crew wellbeing, mission context and emerging health signals.</p>
          <div className="art-footer"><span><span className="pulse-dot" /> SYSTEMS NOMINAL</span><span>MISSION CONTROL · 07</span></div>
        </div>
      </div>
      <section className="login-panel">
        <div className="login-top"><div className="brand-mark mobile-brand"><Orbit size={19} /> ASTRA-HEALTH</div><span className="secure"><LockKeyhole size={13} /> SECURE ACCESS</span></div>
        <div className="login-content">
          <div className="eyebrow">{register ? 'NEW OPERATOR' : 'WELCOME BACK, OPERATOR'}</div>
          <h2>{register ? <>Create your<br />account.</> : <>Access your<br />mission console.</>}</h2>
          <p className="muted">{register ? 'Register to use the crew health console.' : 'Sign in to continue to the crew health overview.'}</p>
          <form onSubmit={submit}>
            {register && <><label htmlFor="fn">Full name</label><div className="input-wrap"><User size={17} /><input id="fn" value={form.full_name} onChange={set('full_name')} required minLength={2} autoComplete="name" /></div></>}
            <label htmlFor="em">Email address</label>
            <div className="input-wrap"><Mail size={17} /><input id="em" type="email" value={form.email} onChange={set('email')} required autoComplete="username" /></div>
            <label htmlFor="pw">Password{register && ' (min. 10 characters)'}</label>
            <div className="input-wrap"><LockKeyhole size={17} /><input id="pw" type="password" value={form.password} onChange={set('password')} required minLength={register ? 10 : undefined} autoComplete={register ? 'new-password' : 'current-password'} /></div>
            {error && <div className="error-msg" role="alert"><AlertTriangle size={15} />{error}</div>}
            <button className="primary-btn" disabled={busy}>{busy ? 'Please wait…' : register ? 'Create account' : 'Enter mission control'} <ArrowRight size={17} /></button>
          </form>
          <button type="button" className="link-btn" onClick={switchMode}>{register ? 'Already have an account? Sign in' : 'Need an account? Create one'}</button>
          {!register && <div className="demo-note"><CheckCircle2 size={16} /><div><b>Demo access enabled</b><span>Credentials are prefilled for your first visit.</span></div></div>}
          <div className="login-disclaimer">Prototype environment · Dataset-backed simulated mission data · Not a medical device.</div>
        </div>
        <div className="login-bottom"><span>ASTRA-HEALTH / FLIGHT SYSTEMS</span><span>BUILD 2.0.0</span></div>
      </section>
    </main>
  );
}
