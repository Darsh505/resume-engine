/**
 * generate.js — Generate page logic.
 *
 * Workflow:
 * - Select target profile & optional Git commit checkbox.
 * - Primary Action: "Generate PDF" -> "[ spinner ] Generating…" -> "PDF ready ✓".
 * - Automatically triggers file download.
 * - Advanced Action: "Push to Remote" (secondary, explicit confirmation).
 */

/* ── Reset Button to Default State ─────────────────────────── */
function resetGenerateBtn() {
  const btn = document.getElementById('generate-btn');
  if (!btn || btn.disabled) return;
  btn.className = 'btn btn-primary btn-generate';
  btn.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
    </svg>
    <span class="btn-text">Generate PDF</span>`;
}

/* ── Generate PDF ──────────────────────────────────────────── */
async function generatePDF() {
  const btn       = document.getElementById('generate-btn');
  const result    = document.getElementById('gen-result');
  const targetSel = document.getElementById('target-select');
  const commit    = document.getElementById('commit-checkbox');

  if (!targetSel || !targetSel.value) {
    showResult(result, 'error', 'No target profile selected.');
    return;
  }

  const target = targetSel.value;

  // Clear any existing reset timer
  if (btn._resetTimer) {
    clearTimeout(btn._resetTimer);
    btn._resetTimer = null;
  }

  // 1. Loading State
  btn.disabled = true;
  btn.className = 'btn btn-primary btn-generate is-loading';
  btn.innerHTML = `
    <svg class="spin-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="15" height="15">
      <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
      <path d="M12 2a10 10 0 0110 10"/>
    </svg>
    <span class="btn-text">Generating…</span>`;

  result.style.display = 'none';

  try {
    const body = new FormData();
    body.append('target', target);
    if (commit && commit.checked) {
      body.append('commit', 'on');
    }

    const resp = await fetch('/generate', { method: 'POST', body });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: 'Unknown error occurred during PDF generation.' }));
      const msg = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail);
      showResult(result, 'error', `Generation failed: ${msg}`);
      toast(`Generation failed: ${msg}`, 'error');
      resetGenerateBtn();
      return;
    }

    // 2. Download generated PDF
    const blob     = await resp.blob();
    const url      = URL.createObjectURL(blob);
    const anchor   = document.createElement('a');
    anchor.href    = url;
    anchor.download = `resume_${target}.pdf`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);

    // 3. Commit status info
    const commitStatus = resp.headers.get('X-Commit-Status') || 'skipped';
    let commitMessage = '';
    if (commitStatus === 'success') {
      commitMessage = ' (saved to Git commit)';
    } else if (commitStatus === 'failed') {
      commitMessage = ' (Git commit failed)';
    }

    // 4. Success State
    btn.disabled = false;
    btn.className = 'btn btn-success btn-generate is-success';
    btn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="15" height="15">
        <polyline points="20 6 9 17 4 12"/>
      </svg>
      <span class="btn-text">PDF ready ✓</span>`;

    toast(`resume_${target}.pdf ready${commitMessage}`, 'success');

    // Revert button after 3.5 seconds
    btn._resetTimer = setTimeout(() => {
      resetGenerateBtn();
    }, 3500);

  } catch (err) {
    showResult(result, 'error', `Network error: ${err.message}`);
    toast(`Network error: ${err.message}`, 'error');
    resetGenerateBtn();
  }
}

/* ── Git push to remote ─────────────────────────────────────── */
async function pushToRemote() {
  const confirmed = window.confirm(
    'Push current branch to configured remote repository?'
  );
  if (!confirmed) return;

  const btn    = document.getElementById('push-btn');
  const result = document.getElementById('push-result');

  btn.disabled = true;
  btn.className = 'btn btn-secondary btn-push is-loading';
  btn.innerHTML = `
    <svg class="spin-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
      <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
      <path d="M12 2a10 10 0 0110 10"/>
    </svg>
    <span class="btn-text">Pushing…</span>`;
  result.style.display = 'none';

  try {
    const resp = await fetch('/git/push', { method: 'POST' });
    const data = await resp.json();

    if (data.ok) {
      showResult(result, 'success', data.message || 'Successfully pushed to remote.');
      toast(data.message || 'Pushed to remote', 'success');
    } else {
      showResult(result, 'error', data.message || 'Push to remote failed.');
      toast(data.message || 'Push failed', 'error');
    }
  } catch (err) {
    showResult(result, 'error', `Network error: ${err.message}`);
    toast(`Network error: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.className = 'btn btn-secondary btn-push';
    btn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
        <line x1="12" y1="19" x2="12" y2="5"/>
        <polyline points="5 12 12 5 19 12"/>
      </svg>
      <span class="btn-text">Push to Remote</span>`;
  }
}

/* ── Shared helpers ────────────────────────────────────────── */
function showResult(el, type, message) {
  if (!el) return;
  el.className = `gen-result result-${type}`;
  el.textContent = message;
  el.style.display = 'block';
}

function toast(message, type = 'info', durationMs = 3500) {
  const el = document.getElementById('toast');
  if (!el) return;
  el.textContent = message;
  el.className   = `toast toast-${type} toast-show`;
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.classList.remove('toast-show'); }, durationMs);
}

/* ── Reset state on user interaction ───────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const targetSel = document.getElementById('target-select');
  const commitBox = document.getElementById('commit-checkbox');

  if (targetSel) {
    targetSel.addEventListener('change', () => resetGenerateBtn());
  }
  if (commitBox) {
    commitBox.addEventListener('change', () => resetGenerateBtn());
  }
});
