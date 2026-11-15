// Educational content summarised from the project blueprint (sections 4, 5, 6). It explains WHY an indicator
// matters; it deliberately contains no clinical thresholds, diagnoses or treatment instructions.

export const HAZARDS = [
  { id: 'radiation', name: 'Space radiation', short: 'Cumulative exposure', icon: 'RadioTower',
    text: 'Invisible to the human eye and described as one of the most hazardous aspects of spaceflight. Relevant to long-duration missions; may contribute to radiation-induced cancer and other biological changes.',
    indicators: ['radiation_msv'] },
  { id: 'isolation', name: 'Isolation & confinement', short: 'Mood & team dynamics', icon: 'Users',
    text: 'Crews live for long periods in a small, isolated environment. Linked to behavioural and psychological risks, teamwork challenges, sleep disruption and changes in mood or performance.',
    indicators: ['stress_score', 'sleep_hours'] },
  { id: 'distance', name: 'Distance from Earth', short: 'Delayed support', icon: 'Orbit',
    text: 'Farther from Earth, instructions, supplies and medical care are harder to receive. Crew self-assessment, reliable onboard information and clear escalation paths matter more.',
    indicators: [] },
  { id: 'gravity', name: 'Gravity fields', short: 'Body adaptation', icon: 'Activity',
    text: 'The body adapts to microgravity and to transitions between gravity environments, affecting muscles, bones, inner ear, organs, cardiovascular function, sensorimotor function and vision.',
    indicators: ['heart_rate', 'systolic_bp', 'diastolic_bp'] },
  { id: 'closed', name: 'Hostile / closed environments', short: 'Habitat conditions', icon: 'Thermometer',
    text: 'A safe spacecraft ecosystem depends on temperature, pressure, lighting, noise, microbial communities and immune responses. Conditions can affect crew health and performance.',
    indicators: ['temperature_c', 'glucose_mg_dl'] },
];

// hazards[] is a design interpretation (the NASA material says hazards interact), not an official mapping.
export const RISKS = [
  ['Altered immune system responses', 'Spaceflight stressors may awaken inactive viruses and contribute to rashes or other symptoms; immune changes are an area of ongoing research.', ['closed', 'isolation']],
  ['Altered sensorimotor and vestibular function', 'Gravity changes can be associated with motion sickness, dizziness and hand-eye or gait coordination issues.', ['gravity']],
  ['Cardiovascular adaptations', 'Weightlessness changes blood circulation and heart/blood-vessel function and may increase cardiovascular-event risk.', ['gravity']],
  ['Decompression sickness', 'Moving from a pressurised spacecraft to a lower-pressure spacesuit can cause dissolved nitrogen to form bubbles in body tissues.', ['closed']],
  ['Host-microorganism interactions', 'Skin and gut microbiomes may change in space, potentially affecting the risk of illness.', ['closed']],
  ['Hypoxia', 'Low oxygen levels in body tissues can occur in relevant operational contexts, including spacesuit operations.', ['closed']],
  ['Inadequate food and nutrition', 'A balanced diet is important for crew health and performance; food acceptability and nutrition are active research topics.', ['distance', 'closed']],
  ['Injury and compromised performance from spacewalks', 'Spacesuit work can involve cognitive fatigue, injury, decompression risks and oxygen/carbon-dioxide management concerns.', ['gravity', 'closed']],
  ['Reduced cardiorespiratory and musculoskeletal fitness', 'Exercise is used to counter losses in bone density, muscle strength, and heart and blood-vessel performance.', ['gravity']],
  ['Spaceflight-associated neuro-ocular syndrome (SANS)', 'Spaceflight can change structures of the eyes and brain; long-term consequences and prevention are research topics.', ['gravity']],
  ['Spaceflight-induced bone changes', 'In reduced gravity bone breakdown can increase bone fragility and fracture risk; diet, exercise and medication are areas of research.', ['gravity']],
  ['Behavioural changes and psychiatric disorders', 'Isolation, radiation, distance from Earth and other stressors can affect mental health.', ['isolation', 'radiation', 'distance']],
  ['Inadequate teamwork', 'Prolonged isolation and confinement can affect crew communication, teamwork and recovery from setbacks.', ['isolation']],
  ['Inadequate sleep and irregular schedules', 'Mission stressors and irregular schedules can contribute to chronic sleep loss and circadian disruption.', ['isolation', 'closed']],
  ['Inadequate systems operations support', 'Future crews may need to solve unexpected software, vehicle or system problems with limited information, training or support.', ['distance']],
  ['Injury from dynamic loads', 'Landing and other dynamic events can create injury risks.', ['gravity']],
  ['Radiation-induced cancers', 'Crew radiation exposure may increase cancer risk; identifying mitigation and intervention strategies is a research priority.', ['radiation']],
].map(([name, text, hazards]) => ({ name, text, hazards }));

// Blueprint section 6. "How to record" is intentionally generic: exact procedures must come from approved mission references.
export const INDICATORS = {
  heart_rate:    { label: 'Heart rate', unit: 'bpm', purpose: 'Heart function and cardiovascular trends.', how: 'Wearable/device value or manual entry; note the context of the measurement.' },
  blood_pressure:{ label: 'Blood pressure', unit: 'mmHg', purpose: 'Cardiovascular health. Systolic and diastolic are stored separately.', how: 'Device reading or manual entry in mmHg.' },
  systolic_bp:   { label: 'Systolic pressure', unit: 'mmHg', purpose: 'Cardiovascular health.', how: 'Upper number of a blood-pressure reading.' },
  diastolic_bp:  { label: 'Diastolic pressure', unit: 'mmHg', purpose: 'Cardiovascular health.', how: 'Lower number of a blood-pressure reading.' },
  glucose_mg_dl: { label: 'Blood glucose', unit: 'mg/dL', purpose: 'Blood-sugar regulation.', how: 'Supported meter reading or manual entry; note timing relative to meals if known.' },
  temperature_c: { label: 'Body temperature', unit: '°C', purpose: 'Body temperature and possible illness-related changes.', how: 'Supported thermometer or manual entry in °C.' },
  sleep_hours:   { label: 'Sleep duration', unit: 'h', purpose: 'Sleep and recovery.', how: 'Wearable data or self-report of hours slept.' },
  stress_score:  { label: 'Stress score', unit: '/10', purpose: 'Behavioural and psychological wellbeing (self-report).', how: 'Self-rate from 0 (none) to 10 (very high).' },
  radiation_msv: { label: 'Radiation dose', unit: 'mSv', purpose: 'Cumulative exposure tracking (sample field only).', how: 'From the mission dosimeter; validate units and dose conventions before real use.' },
};

// Series available in the trend chart (BP draws two lines).
export const CHARTS = [
  { id: 'heart_rate', label: 'Heart rate', unit: 'bpm', lines: [['heart_rate', 'Heart rate']] },
  { id: 'blood_pressure', label: 'Blood pressure', unit: 'mmHg', lines: [['systolic_bp', 'Systolic'], ['diastolic_bp', 'Diastolic']] },
  { id: 'glucose_mg_dl', label: 'Blood glucose', unit: 'mg/dL', lines: [['glucose_mg_dl', 'Glucose']] },
  { id: 'temperature_c', label: 'Temperature', unit: '°C', lines: [['temperature_c', 'Temperature']] },
  { id: 'sleep_hours', label: 'Sleep', unit: 'h', lines: [['sleep_hours', 'Sleep']] },
  { id: 'stress_score', label: 'Stress', unit: '/10', lines: [['stress_score', 'Stress']] },
  { id: 'radiation_msv', label: 'Radiation', unit: 'mSv', lines: [['radiation_msv', 'Dose']] },
];

// Interactive body explorer (blueprint 8.2). Educational navigation only.
export const BODY = [
  { id: 'head', name: 'Head, brain & eyes', function: 'Cognition, mood regulation, sleep–wake control and vision.',
    effects: ['Spaceflight-associated neuro-ocular syndrome (SANS)', 'Behavioural changes and psychiatric disorders', 'Inadequate sleep and irregular schedules'],
    indicators: ['sleep_hours', 'stress_score'], hazards: ['gravity', 'isolation', 'radiation'] },
  { id: 'ear', name: 'Inner ear & balance', function: 'Balance and spatial orientation (vestibular system).',
    effects: ['Altered sensorimotor and vestibular function'], indicators: [], hazards: ['gravity'] },
  { id: 'chest', name: 'Heart & lungs', function: 'Circulates blood and oxygen around the body.',
    effects: ['Cardiovascular adaptations', 'Hypoxia', 'Decompression sickness'],
    indicators: ['heart_rate', 'systolic_bp', 'diastolic_bp'], hazards: ['gravity', 'closed'] },
  { id: 'abdomen', name: 'Abdomen & metabolism', function: 'Digestion, nutrient use, gut microbiome and immune activity.',
    effects: ['Inadequate food and nutrition', 'Host-microorganism interactions', 'Altered immune system responses'],
    indicators: ['glucose_mg_dl'], hazards: ['closed', 'distance'] },
  { id: 'spine', name: 'Spine & pelvis', function: 'Structural support, load bearing and bone health.',
    effects: ['Spaceflight-induced bone changes', 'Injury from dynamic loads'], indicators: [], hazards: ['gravity'] },
  { id: 'arms', name: 'Arms & shoulders', function: 'Muscle strength and mobility, including tasks during suited work.',
    effects: ['Reduced cardiorespiratory and musculoskeletal fitness', 'Injury and compromised performance from spacewalks'],
    indicators: [], hazards: ['gravity'] },
  { id: 'legs', name: 'Legs', function: 'Largest muscles and bones; fluid distribution in the body.',
    effects: ['Reduced cardiorespiratory and musculoskeletal fitness', 'Spaceflight-induced bone changes'],
    indicators: [], hazards: ['gravity'] },
  { id: 'whole', name: 'Whole body', function: 'Indicators that reflect overall state rather than one organ.',
    effects: ['Radiation-induced cancers', 'Altered immune system responses'], indicators: ['temperature_c', 'radiation_msv'], hazards: ['radiation', 'closed'] },
];
