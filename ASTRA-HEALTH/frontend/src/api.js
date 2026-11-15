const BASE = (import.meta.env.VITE_API_URL || '/api').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status; }
}

function explain(detail, status) {
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => {
      const field = (d.loc || []).filter((x) => x !== 'body').join(' → ');
      const msg = (d.msg || 'Invalid input').replace(/^Value error, /, '');
      return field && !msg.toLowerCase().includes(field.toLowerCase()) ? `${field}: ${msg}` : msg;
    }).join('; ');
  }
  return `Request failed (${status})`;
}

export async function api(path, { token, method = 'GET', body } = {}) {
  let res;
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      headers: { Accept: 'application/json', ...(body ? { 'Content-Type': 'application/json' } : {}), ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError('Cannot reach the mission API. Make sure the backend is running (http://127.0.0.1:8000/health).', 0);
  }
  let data = null;
  try { data = await res.json(); } catch { /* non-JSON body */ }
  if (!res.ok) throw new ApiError(explain(data?.detail, res.status), res.status);
  return data;
}

export async function downloadFile(path, token, filename) {
  const res = await fetch(`${BASE}${path}`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new ApiError(`Export failed (${res.status})`, res.status);
  const url = URL.createObjectURL(await res.blob());
  const a = Object.assign(document.createElement('a'), { href: url, download: filename });
  document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
}
