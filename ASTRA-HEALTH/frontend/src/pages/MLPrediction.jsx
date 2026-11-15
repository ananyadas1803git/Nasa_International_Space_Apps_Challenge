import React from 'react';
import {Brain,Activity,AlertTriangle,CheckCircle2,Clock3,Play,RefreshCw} from 'lucide-react';
import {api} from '../api.js';
import {PageHeading,CrewPicker,Loading,ErrorBox,Success} from '../components/ui.jsx';

const GROUPS = [
 ['Behavioral / psychiatric',['behavioral_stress_score','anxiety_indicator_score','mood_wellbeing_score','motivation_score']],
 ['Bone changes',['bone_mineral_density_g_cm3','bone_resorption_marker_index','serum_calcium_mg_dl','resistance_exercise_hours']],
 ['Cardiovascular',['heart_rate_bpm','systolic_bp_mmhg','diastolic_bp_mmhg','cardiovascular_heart_rate_variability_ms']],
 ['Decompression sickness',['decompression_spacewalk_event','oxygen_prebreathing_minutes','pressure_change_psi','suit_pressure_psi']],
 ['Dynamic load injury',['acceleration_g','load_factor','movement_frequency_score','dynamic_load_fatigue_score','restraint_effectiveness_percent']],
 ['Food / nutrition',['calorie_target_kcal','calorie_intake_kcal','protein_intake_g','water_intake_liters','nutrition_status_index']],
 ['Host / microorganism',['host_microorganism_load_index','surface_contamination_index','host_microorganism_immune_response_index','hygiene_compliance_percent']],
 ['Hypoxia',['cabin_oxygen_percent','spo2_percent','respiratory_rate_bpm']],
 ['Immune system',['white_blood_cell_count','inflammation_marker_index','immune_response_index']],
 ['Physical fitness',['vo2_max_ml_kg_min','fitness_muscle_strength_index','endurance_index','daily_exercise_hours']],
 ['Radiation / cancer',['radiation_rate_mSv_day','cumulative_radiation_mSv','shielding_factor','relative_susceptibility_factor','long_term_radiation_exposure_index']],
 ['SANS',['intraocular_pressure_mmhg','retinal_thickness_um','visual_acuity_index','vision_symptom_score']],
 ['Sensorimotor / vestibular',['balance_score','coordination_score','dizziness_score','reaction_time_ms']],
 ['Sleep irregularity',['sleep_risk_sleep_duration_hours','sleep_risk_sleep_quality_score','schedule_irregularity_score','circadian_disruption_score']],
 ['Spacewalk injury',['injury_spacewalk_event','eva_duration_minutes','spacewalk_fatigue_score','workload_score','mobility_score']],
 ['Systems operations',['equipment_reliability_percent','maintenance_delay_hours','ground_support_availability_percent','system_failure_event','procedure_deviation_score']],
 ['Teamwork',['communication_score','cooperation_score','crew_conflict_indicator','task_coordination_score','workload_imbalance_score']],
];
const human = (s) => s.replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase());
const numeric = (v) => v === '' || v === null || v === undefined ? null : Number(v);
export default function MLPrediction({token,crew,focus}) {
 const [id,setId]=React.useState(focus||crew[0]?.id||'AST001');
 const [features,setFeatures]=React.useState(null); const [result,setResult]=React.useState(null);
 const [error,setError]=React.useState(''); const [busy,setBusy]=React.useState(false); const [history,setHistory]=React.useState([]);
 const load=React.useCallback(async()=>{setError('');setResult(null);try{const [t,h]=await Promise.all([api(`/ml/template/${id}`,{token}),api(`/ml/history/${id}`,{token})]);setFeatures(t.features);setHistory(h);}catch(e){setError(e.message);setFeatures(null);}},[id,token]);
 React.useEffect(()=>{load();},[load]);
 const update=(key,value)=>setFeatures(old=>({...old,[key]:value}));
 const submit=async()=>{setBusy(true);setError('');setResult(null);try{const r=await api('/ml/predict',{token,method:'POST',body:{crew_code:id,features}});setResult(r);setHistory(old=>[{id:r.prediction_id,crew_code:id,mission_day:r.mission_day,mission_phase:r.mission_phase,triage_status:r.triage_status,high_risk_count:r.high_risk_count,moderate_risk_count:r.moderate_risk_count,created_at:r.created_at,result:r},...old]);}catch(e){setError(e.message);}finally{setBusy(false);}};
 const domains=result?.domain_predictions?Object.entries(result.domain_predictions):[];
 return <><PageHeading eyebrow="MACHINE LEARNING · 17 RISK DOMAINS" title="ML health prediction" subtitle="Edit a prefilled astronaut telemetry snapshot and run the team's trained multi-domain classifier." onRefresh={load}/>
 <div className="callout"><Brain size={16}/> Inputs are prefilled from the selected astronaut's latest integrated observation. Review and edit the measurements before prediction. The model expects 69 risk-domain features plus mission day and phase.</div>
 <CrewPicker crew={crew} value={id} onChange={v=>{setId(v);setFeatures(null);setResult(null);}}/><ErrorBox error={error}/>
 {!features?<Loading text="Loading model inputs and prediction history…"/>:<>
 <section className="panel spaced"><div className="panel-head"><div><h3>Mission context</h3><p>Context fields required by the trained pipelines</p></div><Activity size={19}/></div><div className="form-grid"><label>Mission day<input type="number" min="1" value={features.mission_day??1} onChange={e=>update('mission_day',numeric(e.target.value))}/></label><label>Mission phase<select value={features.mission_phase??'Cruise'} onChange={e=>update('mission_phase',e.target.value)}>{['Outbound','Cruise','Return'].map(x=><option key={x}>{x}</option>)}</select></label></div></section>
 <section className="panel spaced"><div className="panel-head"><div><h3>Health and mission telemetry</h3><p>All model inputs, grouped by risk domain. Values are initialized from the selected astronaut's latest source row.</p></div><span className="severity info">69 model inputs</span></div>
 {GROUPS.map(([group,keys])=><details className="ml-domain" key={group} open><summary>{group}<span>{keys.filter(k=>features[k]!==undefined).length} fields</span></summary><div className="form-grid">{keys.map(k=><label key={k}>{human(k)}<input type="number" step="any" value={features[k]??''} onChange={e=>update(k,numeric(e.target.value))}/></label>)}</div></details>)}
 <div className="form-actions"><button className="primary-btn" disabled={busy} onClick={submit}>{busy?<RefreshCw className="spin" size={16}/>:<Play size={16}/>} {busy?'Running 17 models…':'Predict astronaut health status'}</button></div></section>
 </>}
 {result&&<><section className="panel spaced"><div className="panel-head"><div><h3>Prediction result · {result.astronaut_id}</h3><p>Mission day {result.mission_day} · {result.mission_phase} · Prediction #{result.prediction_id}</p></div><span className={`severity ${result.triage_status==='RED'?'high':result.triage_status==='AMBER'?'monitor':'info'}`}>{result.triage_status}</span></div><div className="metric-grid"><div className="metric-card"><div className="metric-top">Overall model status</div><div className="metric-value">{result.triage_status}</div><div className="metric-note">Composite triage label</div></div><div className="metric-card"><div className="metric-top">High classifications</div><div className="metric-value">{result.high_risk_count}</div><div className="metric-note">Of 17 domains</div></div><div className="metric-card"><div className="metric-top">Moderate classifications</div><div className="metric-value">{result.moderate_risk_count}</div><div className="metric-note">Of 17 domains</div></div></div><div className="callout"><AlertTriangle size={16}/>{result.triage_action}</div><div className="risk-grid">{domains.map(([key,d])=><div className="risk-card" key={key}><b>{human(key)}</b><span className={`severity ${d.label==='HIGH'?'high':d.label==='MODERATE'?'monitor':'info'}`}>{d.label}</span><small>Top-class score {(d.confidence*100).toFixed(1)}% · P(High) {(d.prob_high*100).toFixed(1)}%</small><small>{human(d.algorithm)}</small></div>)}</div><div className="callout"><CheckCircle2 size={16}/> {result.disclaimer}<br/>{result.model.probability_note}</div></section></>}
 <section className="panel spaced"><div className="panel-head"><div><h3>Prediction history</h3><p>Saved model outputs for {id}</p></div><Clock3 size={18}/></div>{history.length?<div className="table-scroll"><table className="data"><thead><tr><th>Time</th><th>Mission day</th><th>Phase</th><th>Status</th><th>High</th><th>Moderate</th></tr></thead><tbody>{history.map(h=><tr key={h.id}><td>{h.created_at?new Date(h.created_at).toLocaleString():'—'}</td><td>{h.mission_day}</td><td>{h.mission_phase}</td><td><span className={`severity ${h.triage_status==='RED'?'high':h.triage_status==='AMBER'?'monitor':'info'}`}>{h.triage_status}</span></td><td>{h.high_risk_count}</td><td>{h.moderate_risk_count}</td></tr>)}</tbody></table></div>:<p className="muted">No predictions have been saved for this astronaut yet.</p>}</section>
 </>;
}
