/**
 * VISIONZ api.js — Final Stable Version
 * CRITICAL RULES:
 *  1. apiRequest() NEVER redirects — it only returns null on failure
 *  2. 401 from backend = silent null (local token not in DB = normal)
 *  3. Network error = silent null
 *  4. Only Auth.guard() on page load redirects to login
 *  5. Session is only cleared by vzLogout()
 */

const API_BASE = 'https://visionz-backend.onrender.com/api';  // Render backend

const LOCAL_USERS = [
  { name:'Arun Kumar',    email:'arun@visionz.com',       password:'arun123',     role:'admin',    avatar:'AK', department:'Quality Control' },
  { name:'Priya Sharma',  email:'priya@visionz.com',      password:'priya123',    role:'manager',  avatar:'PS', department:'Production Management' },
  { name:'Ravi Operator', email:'ravi@visionz.com',       password:'ravi123',     role:'operator', avatar:'RO', department:'Line Operations' },
  { name:'Meena Devi',    email:'meena@visionz.com',      password:'meena123',    role:'admin',    avatar:'MD', department:'Quality Control' },
  { name:'Karthik Raja',  email:'karthik@visionz.com',    password:'karthik123',  role:'manager',  avatar:'KR', department:'Analytics' },
  { name:'Nivethitha S',  email:'nivethitha@visionz.com', password:'Nive!@#1131', role:'admin',    avatar:'NS', department:'Quality Control' },
];

async function apiRequest(method, path, body = null, requireAuth = false) {
  const headers = { 'Content-Type': 'application/json' };
  if (requireAuth) {
    const t = localStorage.getItem('visionz_token');
    if (t) headers['Authorization'] = 'Bearer ' + t;
  }
  
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 15000); // 15s timeout
  
  const opts = { method, headers, signal: controller.signal };
  if (body) opts.body = JSON.stringify(body);
  try {
    const res = await fetch(API_BASE + path, opts);
    clearTimeout(timeoutId);
    if (!res.ok) return null; // 401, 403, 404, 500 → all silent null
    return await res.json();
  } catch (e) {
    clearTimeout(timeoutId);
    return null; // network error / timeout / offline → silent null
  }
}

const Auth = {
  saveSession(data) {
    const token = data.token || ('local_' + Date.now());
    localStorage.setItem('visionz_token', token);
    localStorage.setItem('visionz_user', JSON.stringify({
      id: data.user_id || data.id || 1,
      name: data.name || 'User',
      email: data.email || '',
      role: data.role || 'admin',
      avatar: data.avatar || (data.name || 'U').substring(0,2).toUpperCase(),
      department: data.department || '',
      loginTime: data.loginTime || new Date().toISOString(),
      sessionStart: Date.now(),
      reportsDownloaded: 0,
    }));
  },
  getUser() {
    try { return JSON.parse(localStorage.getItem('visionz_user') || 'null'); }
    catch { return null; }
  },
  getToken() { return localStorage.getItem('visionz_token'); },
  clearSession() {
    localStorage.removeItem('visionz_token');
    localStorage.removeItem('visionz_user');
  },
  guard() {
    if (!localStorage.getItem('visionz_token') || !localStorage.getItem('visionz_user')) {
      window.location.replace('login.html');
    }
  },
  localLogin(email, password, role) {
    const u = LOCAL_USERS.find(x =>
      x.email.toLowerCase() === email.toLowerCase() && x.password === password
    );
    if (!u) return { ok: false, error: 'Incorrect email or password.' };
    if (u.role !== role.toLowerCase()) {
      return { ok: false, error: `This account is "${u.role}", not "${role}". Select correct role.` };
    }
    return { ok: true, user: u };
  },
};

const AuthAPI = {
  login: (email, password, role) => apiRequest('POST', '/auth/login', { email, password, role }),
  logout: (token) => apiRequest('POST', '/auth/logout', { token }),
};

const VideoAPI = {
  async upload(file) {
    try {
      const form = new FormData();
      form.append('file', file);
      const res = await fetch(API_BASE + '/video/upload', { method: 'POST', body: form });
      if (!res.ok) return null;
      return await res.json();
    } catch { return null; }
  },
  list: () => apiRequest('GET', '/video/list'),
};

const DetectionAPI = {
  save: (d) => apiRequest('POST', '/detections/', d),
  live: () => apiRequest('GET', '/detections/live'),
};

const AnalyticsAPI = {
  summary: () => apiRequest('GET', '/analytics/summary'),
  trend:   () => apiRequest('GET', '/analytics/trend'),
};

const ReportsAPI = {
  list:         () => apiRequest('GET', '/reports/'),
  create:       (d) => apiRequest('POST', '/reports/', d),
  markDownload: (id) => apiRequest('POST', '/reports/' + id + '/download'),
};

// ════════════════════════════════════
//  AI Analysis with Llama & YOLOv6
// ════════════════════════════════════

const AIAPI = {
  // Analysis endpoint (supports Claude and Llama)
  analyze: (data) => apiRequest('POST', '/ai/analyze', data),
  
  // Get available models
  getModels: () => apiRequest('GET', '/ai/models'),
  
  // YOLOv6 Detection endpoints
  detectVideo: (videoPath, maxFrames = null, skipFrames = 1) => {
    const params = new URLSearchParams();
    params.append('video_path', videoPath);
    if (maxFrames) params.append('max_frames', maxFrames);
    params.append('skip_frames', skipFrames);
    return apiRequest('POST', `/ai/detect/video?${params.toString()}`, null);
  },
  
  detectHealth: () => apiRequest('GET', '/ai/detect/health'),
};

const LlamaAPI = {
  // Analyze with Llama
  analyze: (framesScanned, defectCount, passCount, defectRate, catCounts, filename = "Unknown") => 
    AIAPI.analyze({
      framesScanned,
      defectCount,
      passCount,
      defectRate,
      catCounts,
      filename,
      use_llama: true
    }),
};

const YOLOv6API = {
  // Detect video with YOLOv6
  detectVideo: (videoPath, maxFrames = null) => 
    AIAPI.detectVideo(videoPath, maxFrames),
  
  // Check service health
  health: () => AIAPI.detectHealth(),
};
