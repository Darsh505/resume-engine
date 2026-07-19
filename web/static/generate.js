/**
 * generate.js — Generate page logic.
 *
 * generatePDF()
 * ─────────────
 * POSTs the form as multipart/form-data via fetch.
 * • If the response is application/pdf: downloads the blob as a file.
 *   A standard form POST would also work for the download itself, but
 *   fetch lets us read the X-Commit-Status header and show a toast
 *   without a second round-trip.
 * • If 4xx/5xx: shows the error in the result div.
 *
 * pushToRemote()
 * ──────────────
 * Separate function, separate button, confirm() dialog before firing.
 * Never called from generatePDF() — satisfies the "push requires its
 * own separate confirmation" requirement explicitly.
 */

/* ── Generate ──────────────────────────────────────────────────────────── */
async function generatePDF() {
  const btn       = document.getElementById('generate-btn');
  const result    = document.getElementById('gen-result');
  const targetSel = document.getElementById('target-select');
  const commit    = document.getElementById('commit-checkbox');

  const target = targetSel.value;
  if (!target) { showResult(result, 'error', 'No target selected.'); return; }

  btn.disabled = true;
  btn.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
         width="18" height="18" style="animation:spin 1s linear infinite">
      <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
      <path d="M12 2a10 10 0 0110 10"/>
    </svg> Generating…`;

  result.style.display = 'none';

  try {
    const body = new FormData();
    body.append('target', target);
    // Send "on" when checked (matches what HTML form would send),
    // omit the key when unchecked (FastAPI defaults to "off").
    if (commit.checked) body.append('commit', 'on');

    const resp = await fetch('/generate', { method: 'POST', body });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Unknown error' }));
      const msg = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
      showResult(result, 'error', `Generation failed: ${msg}`);
      return;
    }

    // ── PDF download ─────────────────────────────────────────────────────
    const blob     = await resp.blob();
    const url      = URL.createObjectURL(blob);
    const anchor   = document.createElement('a');
    anchor.href    = url;
    anchor.download = `resume_${target}.pdf`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);

    // ── Commit status ─────────────────────────────────────────────────────
    const commitStatus = resp.headers.get('X-Commit-Status') || 'skipped';
    const commitNote = {
      success: ' PDF was committed to git.',
      ignored: ' Git commit was skipped — PDF is gitignored (see README).',
      skipped: '',
      failed:  ' Git commit failed — check server logs.',
    }[commitStatus] ?? '';

    showResult(result, 'success', `✓ resume_${target}.pdf downloaded.${commitNote}`);
    toast(`resume_${target}.pdf ready`, 'success');

  } catch (err) {
    showResult(result, 'error', `Network error: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
        <polygon points="5 3 19 12 5 21 5 3"/>
      </svg> Generate &amp; Download`;
  }
}

/* ── Git push ──────────────────────────────────────────────────────────── */
async function pushToRemote() {
  // Explicit, separately confirmed action — never called from generatePDF()
  const confirmed = window.confirm(
    'Push to origin?\n\nThis will push the current branch to the remote. Continue?'
  );
  if (!confirmed) return;

  const btn    = document.getElementById('push-btn');
  const result = document.getElementById('push-result');

  btn.disabled = true;
  btn.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
         width="16" height="16" style="animation:spin 1s linear infinite">
      <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
      <path d="M12 2a10 10 0 0110 10"/>
    </svg> Pushing…`;
  result.style.display = 'none';

  try {
    const resp = await fetch('/git/push', { method: 'POST' });
    const data = await resp.json();

    showResult(result, data.ok ? 'success' : 'error', data.message);
    toast(data.message, data.ok ? 'success' : 'error');
  } catch (err) {
    showResult(result, 'error', `Network error: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>
      </svg> Push to Remote`;
  }
}

/* ── Shared helpers ────────────────────────────────────────────────────── */
function showResult(el, type, message) {
  el.className = `gen-result result-${type}`;
  el.textContent = message;
  el.style.display = 'block';
  el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function toast(message, type = 'info', durationMs = 3500) {
  const el = document.getElementById('toast');
  el.textContent = message;
  el.className   = `toast toast-${type} toast-show`;
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.classList.remove('toast-show'); }, durationMs);
}

// Spinner keyframe (base.html doesn't include app.js here)
const style = document.createElement('style');
style.textContent = '@keyframes spin { to { transform: rotate(360deg); } }';
document.head.appendChild(style);
