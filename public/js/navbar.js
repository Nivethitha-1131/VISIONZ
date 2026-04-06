(function () {
  const token = localStorage.getItem('visionz_token');
  const raw   = localStorage.getItem('visionz_user');
  if (!token || !raw) { window.location.replace('login.html'); return; }

  let user;
  try { user = JSON.parse(raw); }
  catch { window.location.replace('login.html'); return; }

  const page  = window.location.pathname.split('/').pop() || 'index.html';
  const a     = (p) => page === p ? 'class="active"' : '';
  const rc    = { admin:'#38bdf8', manager:'#a78bfa', operator:'#34d399' };
  const ri    = { admin:'👑', manager:'📊', operator:'🏭' };

  document.head.insertAdjacentHTML('beforeend', `<style>
  .vz-nav{position:sticky;top:0;z-index:999;background:rgba(9,14,27,.97);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-bottom:1px solid rgba(56,189,248,.12);box-shadow:0 2px 24px rgba(0,0,0,.5);}
  .vz-nav-inner{display:flex;align-items:center;height:62px;padding:0 1.5rem;gap:.5rem;}
  .vz-brand{display:flex;align-items:center;gap:10px;text-decoration:none;margin-right:.5rem;}
  .vz-brand-ico{width:36px;height:36px;background:linear-gradient(135deg,rgba(56,189,248,.18),rgba(129,140,248,.12));border:1px solid rgba(56,189,248,.3);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1rem;}
  .vz-brand-txt{font-family:'Orbitron',sans-serif;font-size:1.05rem;font-weight:900;color:#fff;letter-spacing:3px;}
  .vz-brand-txt span{color:#38bdf8;}
  .vz-links{display:flex;align-items:center;gap:2px;list-style:none;margin:0;padding:0;}
  .vz-links a{display:flex;align-items:center;gap:6px;padding:.42rem .9rem;border-radius:9px;font-size:.81rem;font-weight:600;color:#64748b;text-decoration:none;font-family:'Outfit',sans-serif;border:1px solid transparent;transition:all .2s;}
  .vz-links a:hover{color:#e2e8f0;background:rgba(30,41,59,.7);}
  .vz-links a.active{color:#38bdf8;background:rgba(56,189,248,.08);border-color:rgba(56,189,248,.2);}
  .vz-right{margin-left:auto;display:flex;align-items:center;gap:.5rem;}
  .vz-live{display:flex;align-items:center;gap:5px;background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.22);border-radius:20px;padding:4px 10px;font-size:.63rem;font-weight:800;color:#22c55e;}
  .vz-live-dot{width:6px;height:6px;border-radius:50%;background:#22c55e;animation:liveblink 1.2s ease-in-out infinite;}
  @keyframes liveblink{0%,100%{opacity:1;}50%{opacity:.2;}}
  .vz-user{display:flex;align-items:center;gap:7px;background:rgba(30,41,59,.7);border:1px solid rgba(56,189,248,.15);border-radius:10px;padding:4px 9px 4px 4px;text-decoration:none;transition:all .2s;}
  .vz-user:hover{border-color:rgba(56,189,248,.35);}
  .vz-avatar{width:28px;height:28px;border-radius:7px;background:linear-gradient(135deg,#3b82f6,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:.62rem;font-weight:800;color:#fff;flex-shrink:0;}
  .vz-uname{font-size:.76rem;font-weight:700;color:#e2e8f0;font-family:'Outfit',sans-serif;line-height:1.2;}
  .vz-urole{font-size:.58rem;font-weight:700;font-family:'Outfit',sans-serif;}
  .vz-logout{background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.2);border-radius:8px;color:#ef4444;font-size:.72rem;font-weight:600;padding:5px 11px;cursor:pointer;font-family:'Outfit',sans-serif;transition:all .2s;display:flex;align-items:center;gap:5px;}
  .vz-logout:hover{background:rgba(239,68,68,.14);border-color:rgba(239,68,68,.4);}
  @media(max-width:768px){.vz-links{display:none;}.vz-live{display:none;}}
  </style>`);

  document.body.insertAdjacentHTML('afterbegin', `
  <div class="vz-nav">
    <div class="vz-nav-inner">
      <a href="index.html" class="vz-brand">
        <div class="vz-brand-ico">👁️</div>
        <div class="vz-brand-txt">VISION<span>Z</span></div>
      </a>
      <ul class="vz-links" id="vzLinks">
        <li><a href="landing.html" ${a('landing.html')}><i class="bi bi-camera-video-fill"></i> Monitor</a></li>
        <li><a href="analytics.html" ${a('analytics.html')}><i class="bi bi-bar-chart-fill"></i> Analytics</a></li>
        <li><a href="reports.html" ${a('reports.html')}><i class="bi bi-file-earmark-bar-graph"></i> Reports</a></li>
      </ul>
      <div class="vz-right">
        <div class="vz-live"><div class="vz-live-dot"></div>LIVE</div>
        <a href="profile.html" class="vz-user">
          <div class="vz-avatar">${user.avatar || 'U'}</div>
          <div>
            <div class="vz-uname">${(user.name||'User').split(' ')[0]}</div>
            <div class="vz-urole" style="color:${rc[user.role]||'#38bdf8'}">${ri[user.role]||''} ${(user.role||'').toUpperCase()}</div>
          </div>
        </a>
        <button class="vz-logout" onclick="vzLogout()"><i class="bi bi-box-arrow-right"></i> Logout</button>
      </div>
    </div>
  </div>`);

  window.vzLogout = async function() {
    if (!confirm('Sign out of VISIONZ?')) return;
    Auth.clearSession();
    window.location.href = 'index.html';
  };
})();
