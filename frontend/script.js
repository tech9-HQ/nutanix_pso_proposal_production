// script.js — minimal FE for Nutanix Proposal Builder
window.addEventListener('DOMContentLoaded', () => {
  if (window.__pso_init) {
    console.warn('[PSO-FE] script already initialized');
    return;
  }
  window.__pso_init = true;

  const API_BASE = '';
  const LOG = '[PSO-FE]';

  // ---------------- AUTH HELPERS ----------------
  function getToken() {
    return localStorage.getItem('access_token') || '';
  }
  function isAuthed() {
    return !!getToken();
  }
  function authHeaders(h = {}) {
    const token = getToken();
    return token ? { ...h, Authorization: `Bearer ${token}` } : h;
  }
  function toast(msg) {
    if (window.toast) return window.toast(msg);
    try { console.info('TOAST:', msg); } catch (e) {}
  }
  function handle401(resp) {
    if (resp && resp.status === 401) {
      toast('Session expired or not logged in. Please login.');
      window.location.href = 'login.html';
      return true;
    }
    return false;
  }

  // ---------------- DOM ----------------
  const el = id => document.getElementById(id) || null;

  const clientNameEl     = el('client_name');
  const industrySelect   = el('industry_select');
  const industryCustomEl = el('industry_custom');
  const deploymentEl     = el('deployment_type');
  const proposalTypeEl   = el('proposal_type');
  const requirementsEl   = el('requirements_text');
  const boqTextEl        = el('boq_text');
  const hwprovGroupEl    = el('hardware_providers_group');
  const hwprovClearBtn   = el('hwprov_clear');

  const generateBtn      = el('generateBtn');

  // Progress elements (optional – not in current HTML but kept harmless)
  const wrap = el('genProgressWrap');
  const bar  = el('genProgress');
  const lab  = el('genProgressLabel');

  function showProgress(msg) {
    console.log(LOG, 'showProgress:', msg);
    if (wrap) wrap.style.display = 'flex';
    if (lab) lab.textContent = msg || 'Preparing…';
    if (bar) bar.classList.remove('ok', 'err');
  }
  function setPhase(msg) {
    if (lab) lab.textContent = msg;
  }
  function doneProgress(ok = true) {
    if (bar) {
      bar.classList.toggle('ok', ok);
      bar.classList.toggle('err', !ok);
    }
    if (lab) lab.textContent = ok ? 'Completed' : 'Failed';
    setTimeout(() => {
      if (wrap) wrap.style.display = 'none';
      if (bar) bar.classList.remove('ok', 'err');
    }, 1200);
  }

  function getSelectedHardwareProviders() {
    if (!hwprovGroupEl) return '';
    const vals = Array.from(
      hwprovGroupEl.querySelectorAll('input[name="hwprov"]:checked')
    )
      .map(i => i.value.trim())
      .filter(Boolean);
    return vals.join(', ');
  }

  // Clear hardware provider checkboxes
  if (hwprovClearBtn && hwprovGroupEl) {
    hwprovClearBtn.addEventListener('click', e => {
      e.preventDefault();
      Array.from(
        hwprovGroupEl.querySelectorAll('input[name="hwprov"]')
      ).forEach(cb => { cb.checked = false; });
    });
  }

  if (!generateBtn) {
    console.error(LOG, 'generateBtn not found in DOM');
    alert('generateBtn not found – check index.html id.');
    return;
  }

  // ---------------- GENERATE PROPOSAL ----------------
  generateBtn.addEventListener('click', async () => {
    console.log(LOG, 'Generate button clicked');

    if (!isAuthed()) {
      toast('Please login to generate.');
      window.location.href = 'login.html';
      return;
    }

    const clientName = (clientNameEl && clientNameEl.value) || 'Client';
    const reqText    = (requirementsEl && requirementsEl.value) || '';
    const rawDeployment = (deploymentEl && deploymentEl.value) || '';
    const proposalTypeVal = (proposalTypeEl && proposalTypeEl.value) || 'detailed';

    const industryVal = (industrySelect && industrySelect.value === 'other'
      ? (industryCustomEl && industryCustomEl.value) || ''
      : (industrySelect ? industrySelect.value : '')
    );

    if (!reqText.trim()) {
      alert('Please enter client requirements before generating.');
      return;
    }

    // Map UI deployment values -> API literals
    const apiDeployment =
      rawDeployment === 'onsite'    ? 'on-premise' :
      rawDeployment === 'dark_site' ? 'dark-site'  :
      rawDeployment || 'hybrid';

    const hwSelected = getSelectedHardwareProviders();
    const boqVal     = (boqTextEl && boqTextEl.value) || '';

    const payload = {
      // Names expected by backend
      customer_name: clientName,
      industry: industryVal || '',
      deployment_type: apiDeployment,             // 'on-premise' | 'remote' | 'hybrid' | 'dark-site'
      proposal_type: proposalTypeVal,             // 'detailed' | 'short'
      hardware_choice: hwSelected || 'Nutanix',   // required field; default if none selected

      // Support both naming styles used in code
      requirements_text: reqText,
      client_requirements: reqText,

      client_boq: boqVal,
      boq_text: boqVal
    };

    const url = API_BASE.replace(/\/+$/, '') + '/api/generate_proposal';
    console.log(LOG, 'POST', url, payload);

    generateBtn.disabled = true;
    const oldLabel = generateBtn.textContent;
    generateBtn.textContent = 'Generating...';

    showProgress('Preparing content…');
    const phases = ['Drafting sections…', 'Calling AI agents…', 'Formatting DOCX…', 'Finalizing…'];
    let idx = 0;
    const phaseTimer = setInterval(() => {
      setPhase(phases[idx % phases.length]);
      idx++;
    }, 1200);

    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(payload)
      });

      console.log(LOG, 'response status', resp.status);

      if (handle401(resp)) {
        clearInterval(phaseTimer);
        doneProgress(false);
        generateBtn.disabled = false;
        generateBtn.textContent = oldLabel;
        return;
      }

      if (!resp.ok) {
        const text = await resp.text().catch(() => '<no body>');
        throw new Error(`Generate API error ${resp.status}: ${text.slice(0, 500)}`);
      }

      setPhase('Downloading…');
      const blob = await resp.blob();

      let filename = 'proposal.docx';
      const cd = resp.headers.get('Content-Disposition') || resp.headers.get('content-disposition') || '';
      const m = cd && cd.match(/filename\*?=([^;]+)/i);
      if (m && m[1]) {
        filename = decodeURIComponent(m[1].replace(/UTF-8''/i, '').replace(/['"]/g, ''));
      }

      const urlBlob = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = urlBlob;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(urlBlob);

      doneProgress(true);
      toast('Proposal downloaded');
    } catch (err) {
      console.error(LOG, 'Generate failed', err);
      doneProgress(false);
      alert('Generate failed: ' + (err.message || err));
    } finally {
      clearInterval(phaseTimer);
      generateBtn.disabled = false;
      generateBtn.textContent = oldLabel;
    }
  });

  // ---------------- INIT ----------------
  if (!isAuthed()) {
    console.info(LOG, 'not authenticated');
    toast('You are not logged in. Login to generate.');
  }
  console.info(LOG, 'minimal script initialized');
});
