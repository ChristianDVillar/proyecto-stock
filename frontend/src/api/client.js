/**
 * Cliente API: base URL (relativa con proxy en dev o REACT_APP_API_URL en prod),
 * fetch con credenciales y token, y reintento automático con refresh token en 401.
 */
const getBaseUrl = () => {
  if (typeof process !== 'undefined' && process.env?.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL.replace(/\/$/, '');
  }
  return '';
};

export const apiBase = getBaseUrl();

function buildHeaders(options, token) {
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
    ...options.headers,
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}

export async function apiFetch(path, options = {}) {
  const url = path.startsWith('http') ? path : `${apiBase}${path}`;
  let token = typeof localStorage !== 'undefined' ? localStorage.getItem('jwt_token') : null;
  const isRefresh = path.includes('/api/auth/refresh');

  let res = await fetch(url, {
    ...options,
    headers: buildHeaders(options, token),
    credentials: 'include',
  });

  // En 401, intentar refresh (solo si tenemos token y no es ya la petición de refresh/login)
  if (res.status === 401 && token && !isRefresh && !options._skipRefresh) {
    try {
      const refreshRes = await fetch(`${apiBase}/api/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Accept': 'application/json' },
      });
      if (refreshRes.ok) {
        const data = await refreshRes.json().catch(() => ({}));
        const newToken = data.access_token || refreshRes.headers.get('Authorization')?.replace(/^Bearer\s+/i, '');
        if (newToken) {
          if (typeof localStorage !== 'undefined') localStorage.setItem('jwt_token', newToken);
          res = await fetch(url, {
            ...options,
            headers: buildHeaders(options, newToken),
            credentials: 'include',
          });
        }
      }
    } catch (_) {
      // Si refresh falla, se devuelve el 401 original
    }
  }

  return res;
}
