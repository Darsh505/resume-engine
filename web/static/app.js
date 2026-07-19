/**
 * app.js — Resume editor logic for the Edit page.
 *
 * Architecture
 * ────────────
 * S (state) is the single source of truth — a plain JS object matching
 * the ResumeData Pydantic model.  Skills are stored internally as an array
 * (_skillsList) for easy add/remove, then converted back to a dict before
 * posting.
 *
 * Rendering: each section has a render*() function that replaces the inner
 * HTML of its container element from S.  re-rendering on add/remove is
 * fine because these operations are infrequent and the sections are small.
 *
 * Input sync: a single delegated 'input' listener on document updates S
 * via data-path attributes.  data-type="tags" splits on commas.
 * data-type="number" parses as int.  No re-render happens — state stays
 * in sync, DOM stays unchanged.
 *
 * Save: collectState() builds the final JSON dict (converting _skillsList
 * back to the skills dict), then POSTs to /save.  FastAPI's 422 error
 * format (detail[]) is parsed and shown inline.
 */

/* ── State ─────────────────────────────────────────────────────────────── */
let S = null;

/* ── Init ──────────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const raw = JSON.parse(document.getElementById('resume-data').textContent);

  // Normalise: ensure all arrays exist, convert skills dict → list
  S = {
    personal: raw.personal || {},
    education: raw.education || [],
    experience: raw.experience || [],
    projects: raw.projects || [],
    achievements: raw.achievements || [],
    // Internal representation: array of {category, skills[]}
    _skillsList: skillsDictToList(raw.skills || {}),
  };

  renderAll();

  // Delegated listener: update S on any input/change without re-rendering
  document.addEventListener('input',  handleInput);
  document.addEventListener('change', handleInput);
});

/* ── Input sync ────────────────────────────────────────────────────────── */
function handleInput(e) {
  const path = e.target.dataset.path;
  if (!path) return;

  let value = e.target.value;
  if (e.target.dataset.type === 'tags') {
    value = value.split(',').map(t => t.trim()).filter(Boolean);
  } else if (e.target.dataset.type === 'number') {
    value = parseInt(value, 10) || 0;
  }
  setAt(S, path, value);
}

/* ── Path utilities ────────────────────────────────────────────────────── */
function setAt(obj, path, value) {
  const parts = path.split('.');
  let curr = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    const k = isNaN(parts[i]) ? parts[i] : +parts[i];
    curr = curr[k];
  }
  const last = parts[parts.length - 1];
  curr[isNaN(last) ? last : +last] = value;
}

/* ── HTML helpers ──────────────────────────────────────────────────────── */
function esc(s) {
  return String(s ?? '')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

const tagsStr = tags => (tags || []).join(', ');

function field(path, label, value, required = false, hint = '') {
  return `
    <div class="field-group">
      <label>${esc(label)}${required ? ' <span class="req">*</span>' : ''}</label>
      <input type="text" class="field-input" data-path="${esc(path)}"
             value="${esc(value)}" ${required ? 'required' : ''}
             placeholder="${esc(label)}">
      ${hint ? `<span class="field-hint">${hint}</span>` : ''}
    </div>`;
}

function tagsField(path, label, tags) {
  return `
    <div class="field-group">
      <label>${esc(label)} <span class="field-hint" style="display:inline">(comma-separated)</span></label>
      <input type="text" class="field-input tags-input" data-path="${esc(path)}" data-type="tags"
             value="${esc(tagsStr(tags))}" placeholder="backend, general">
    </div>`;
}

function numField(path, label, value) {
  return `
    <div class="field-group">
      <label>${esc(label)}</label>
      <input type="number" class="field-input" data-path="${esc(path)}" data-type="number"
             value="${+(value ?? 0)}" min="0" max="99">
    </div>`;
}

function textArea(path, label, value, rows = 3) {
  return `
    <div class="field-group">
      <label>${esc(label)}</label>
      <textarea class="field-input" data-path="${esc(path)}" rows="${rows}"
                placeholder="${esc(label)}">${esc(value)}</textarea>
    </div>`;
}

/* ── renderAll ─────────────────────────────────────────────────────────── */
function renderAll() {
  renderPersonal();
  renderEducation();
  renderExperience();
  renderProjects();
  renderSkills();
  renderAchievements();
}

/* ── Personal ──────────────────────────────────────────────────────────── */
function renderPersonal() {
  const p = S.personal;
  document.getElementById('personal-fields').innerHTML = `
    <div class="fields-grid fields-grid-2">
      ${field('personal.name',     'Full Name',  p.name     || '', true)}
      ${field('personal.email',    'Email',      p.email    || '', true)}
      ${field('personal.phone',    'Phone',      p.phone    || '')}
      ${field('personal.linkedin', 'LinkedIn',   p.linkedin || '')}
      ${field('personal.github',   'GitHub',     p.github   || '')}
      ${field('personal.website',  'Website',    p.website  || '')}
    </div>`;
}

/* ── Education ─────────────────────────────────────────────────────────── */
function renderEducation() {
  const list = S.education;
  document.getElementById('education-list').innerHTML =
    list.length ? list.map((e, i) => renderEduCard(e, i)).join('') :
    '<p style="color:var(--text-muted);font-size:13px">No education entries yet.</p>';
  document.getElementById('edu-count').textContent = list.length;
}

function renderEduCard(e, i) {
  const cw = e.coursework || [];
  return `
    <div class="entry-card">
      <div class="card-header">
        <span class="card-title">${esc(e.institution || 'New Education Entry')}</span>
        <button class="btn-remove" onclick="removeEntry('education',${i})" title="Remove">✕</button>
      </div>
      <div class="card-body">
        <div class="fields-grid fields-grid-2">
          ${field(`education.${i}.institution`, 'Institution', e.institution || '', true)}
          ${field(`education.${i}.degree`,      'Degree',      e.degree      || '', true)}
          ${field(`education.${i}.dates`,       'Dates',       e.dates       || '')}
          ${field(`education.${i}.gpa`,         'GPA',         e.gpa         || '')}
        </div>
        <div class="sub-section">
          <div class="sub-header">
            <span class="sub-title">Coursework</span>
            <button class="btn-add-sub" onclick="addCoursework(${i})">+ Add Course</button>
          </div>
          <div id="edu-${i}-cw">
            ${cw.map((c, ci) => `
              <div class="bullet-card" id="cw-${i}-${ci}">
                <div class="bullet-fields">
                  <div class="fields-grid fields-grid-2">
                    ${field(`education.${i}.coursework.${ci}.name`, 'Course Name', c.name || '')}
                    ${tagsField(`education.${i}.coursework.${ci}.tags`, 'Tags', c.tags)}
                  </div>
                </div>
                <button class="btn-remove-small" onclick="removeCoursework(${i},${ci})" title="Remove">✕</button>
              </div>`).join('')}
          </div>
        </div>
      </div>
    </div>`;
}

function addCoursework(eduIdx) {
  S.education[eduIdx].coursework = S.education[eduIdx].coursework || [];
  S.education[eduIdx].coursework.push({ name: '', tags: [] });
  renderEducation();
  focusLast(`[id^="cw-${eduIdx}-"] input`);
}
function removeCoursework(eduIdx, cwIdx) {
  S.education[eduIdx].coursework.splice(cwIdx, 1);
  renderEducation();
}

/* ── Experience ────────────────────────────────────────────────────────── */
function renderExperience() {
  const list = S.experience;
  document.getElementById('experience-list').innerHTML =
    list.length ? list.map((j, i) => renderJobCard(j, i)).join('') :
    '<p style="color:var(--text-muted);font-size:13px">No experience entries yet.</p>';
  document.getElementById('exp-count').textContent = list.length;
}

function renderJobCard(job, i) {
  const bullets = job.bullets || [];
  return `
    <div class="entry-card">
      <div class="card-header">
        <span class="card-title">${esc(job.company || 'New Job')}</span>
        <button class="btn-remove" onclick="removeEntry('experience',${i})" title="Remove">✕</button>
      </div>
      <div class="card-body">
        <div class="fields-grid fields-grid-2">
          ${field(`experience.${i}.company`,  'Company',  job.company  || '', true)}
          ${field(`experience.${i}.role`,     'Role',     job.role     || '', true)}
          ${field(`experience.${i}.dates`,    'Dates',    job.dates    || '')}
          ${field(`experience.${i}.location`, 'Location', job.location || '')}
        </div>
        <div class="sub-section">
          <div class="sub-header">
            <span class="sub-title">Bullets (${bullets.length})</span>
            <button class="btn-add-sub" onclick="addBullet(${i})">+ Add Bullet</button>
          </div>
          <div id="exp-${i}-bullets">
            ${bullets.map((b, bi) => renderBulletCard(i, b, bi)).join('')}
          </div>
        </div>
      </div>
    </div>`;
}

function renderBulletCard(expIdx, b, bi) {
  return `
    <div class="bullet-card" id="b-${expIdx}-${bi}">
      <div class="bullet-fields">
        ${textArea(`experience.${expIdx}.bullets.${bi}.text`, 'Bullet text', b.text || '')}
        <div class="fields-grid fields-grid-2">
          ${tagsField(`experience.${expIdx}.bullets.${bi}.tags`, 'Tags', b.tags)}
          ${numField(`experience.${expIdx}.bullets.${bi}.priority`, 'Priority', b.priority)}
        </div>
      </div>
      <button class="btn-remove-small" onclick="removeBullet(${expIdx},${bi})" title="Remove">✕</button>
    </div>`;
}

function addBullet(expIdx) {
  S.experience[expIdx].bullets = S.experience[expIdx].bullets || [];
  S.experience[expIdx].bullets.push({ text: '', tags: [], priority: 0 });
  renderExperience();
  focusLast(`[id^="b-${expIdx}-"] textarea`);
}
function removeBullet(expIdx, bi) {
  S.experience[expIdx].bullets.splice(bi, 1);
  renderExperience();
}

/* ── Projects ──────────────────────────────────────────────────────────── */
function renderProjects() {
  const list = S.projects;
  document.getElementById('projects-list').innerHTML =
    list.length ? list.map((p, i) => renderProjectCard(p, i)).join('') :
    '<p style="color:var(--text-muted);font-size:13px">No projects yet.</p>';
  document.getElementById('proj-count').textContent = list.length;
}

function renderProjectCard(p, i) {
  return `
    <div class="entry-card">
      <div class="card-header">
        <span class="card-title">${esc(p.name || 'New Project')}</span>
        <button class="btn-remove" onclick="removeEntry('projects',${i})" title="Remove">✕</button>
      </div>
      <div class="card-body">
        <div class="fields-grid fields-grid-2">
          ${field(`projects.${i}.name`,   'Name',         p.name   || '', true)}
          ${field(`projects.${i}.github`, 'GitHub URL',   p.github || '')}
        </div>
        <div class="fields-grid fields-grid-1" style="margin-top:10px">
          ${textArea(`projects.${i}.description`, 'Description', p.description || '')}
        </div>
        <div class="fields-grid fields-grid-2" style="margin-top:10px">
          ${tagsField(`projects.${i}.tags`, 'Target Tags', p.tags)}
          ${numField(`projects.${i}.priority`, 'Priority', p.priority)}
        </div>
        <div class="fields-grid fields-grid-1" style="margin-top:10px">
          <div class="field-group">
            <label>Tech Stack <span class="field-hint" style="display:inline">(comma-separated)</span></label>
            <input type="text" class="field-input tags-input"
                   data-path="projects.${i}.tech" data-type="tags"
                   value="${esc(tagsStr(p.tech))}"
                   placeholder="Go, gRPC, Redis, Docker">
          </div>
        </div>
      </div>
    </div>`;
}

/* ── Skills ────────────────────────────────────────────────────────────── */
function skillsDictToList(dict) {
  return Object.entries(dict).map(([cat, skills]) => ({ category: cat, skills: skills || [] }));
}

function skillsListToDict(list) {
  return Object.fromEntries(list.map(({ category, skills }) => [category, skills]));
}

function renderSkills() {
  const list = S._skillsList;
  document.getElementById('skills-list').innerHTML =
    list.length ? list.map((cat, i) => renderSkillCategory(cat, i)).join('') :
    '<p style="color:var(--text-muted);font-size:13px">No skill categories yet.</p>';
  document.getElementById('skills-count').textContent = list.length;
}

function renderSkillCategory(cat, i) {
  const skills = cat.skills || [];
  return `
    <div class="entry-card">
      <div class="card-header">
        <input type="text" class="category-name-input"
               data-path="_skillsList.${i}.category"
               value="${esc(cat.category)}"
               placeholder="Category name (e.g. languages)">
        <button class="btn-remove" onclick="removeSkillCategory(${i})" title="Remove category">✕</button>
      </div>
      <div class="card-body">
        <div id="skill-cat-${i}-items">
          ${skills.map((s, si) => renderSkillItem(i, s, si)).join('')}
        </div>
        <button class="btn-add-sub" style="margin-top:8px" onclick="addSkill(${i})">+ Add Skill</button>
      </div>
    </div>`;
}

function renderSkillItem(catIdx, s, si) {
  return `
    <div class="skill-item" id="sk-${catIdx}-${si}">
      ${field(`_skillsList.${catIdx}.skills.${si}.name`, 'Skill name', s.name || '')}
      ${tagsField(`_skillsList.${catIdx}.skills.${si}.tags`, 'Tags', s.tags)}
      <button class="btn-remove-small" style="margin-bottom:4px"
              onclick="removeSkill(${catIdx},${si})" title="Remove skill">✕</button>
    </div>`;
}

function addSkillCategory() {
  S._skillsList.push({ category: 'new-category', skills: [] });
  renderSkills();
}
function removeSkillCategory(i) {
  S._skillsList.splice(i, 1);
  renderSkills();
}
function addSkill(catIdx) {
  S._skillsList[catIdx].skills = S._skillsList[catIdx].skills || [];
  S._skillsList[catIdx].skills.push({ name: '', tags: [] });
  renderSkills();
  focusLast(`[id^="sk-${catIdx}-"] input`);
}
function removeSkill(catIdx, si) {
  S._skillsList[catIdx].skills.splice(si, 1);
  renderSkills();
}

/* ── Achievements ──────────────────────────────────────────────────────── */
function renderAchievements() {
  const list = S.achievements;
  document.getElementById('achievements-list').innerHTML =
    list.length ? list.map((a, i) => renderAchievementCard(a, i)).join('') :
    '<p style="color:var(--text-muted);font-size:13px">No achievements yet.</p>';
  document.getElementById('ach-count').textContent = list.length;
}

function renderAchievementCard(a, i) {
  return `
    <div class="entry-card">
      <div class="card-header">
        <span class="card-title">${esc(a.title || 'New Achievement')}</span>
        <button class="btn-remove" onclick="removeEntry('achievements',${i})" title="Remove">✕</button>
      </div>
      <div class="card-body">
        <div class="fields-grid fields-grid-2">
          ${field(`achievements.${i}.title`,  'Title',  a.title  || '', true)}
          ${field(`achievements.${i}.issuer`, 'Issuer', a.issuer || '')}
          ${field(`achievements.${i}.date`,   'Date',   a.date   || '')}
          ${numField(`achievements.${i}.priority`, 'Priority', a.priority)}
        </div>
        <div class="fields-grid fields-grid-1" style="margin-top:10px">
          ${tagsField(`achievements.${i}.tags`, 'Tags', a.tags)}
        </div>
      </div>
    </div>`;
}

/* ── Generic add/remove ────────────────────────────────────────────────── */
const DEFAULTS = {
  education:    { institution:'', degree:'', dates:'', gpa:'', coursework:[] },
  experience:   { company:'', role:'', dates:'', location:'', bullets:[] },
  projects:     { name:'', description:'', tech:[], github:'', tags:[], priority:0 },
  achievements: { title:'', issuer:'', date:'', tags:[], priority:0 },
};

const RENDERS = {
  education:    renderEducation,
  experience:   renderExperience,
  projects:     renderProjects,
  achievements: renderAchievements,
};

function addEntry(section) {
  S[section].push({ ...DEFAULTS[section] });
  RENDERS[section]();
}

function removeEntry(section, idx) {
  S[section].splice(idx, 1);
  RENDERS[section]();
}

/* ── Save ──────────────────────────────────────────────────────────────── */
async function saveResume() {
  clearErrors();

  const saveBtn  = document.getElementById('save-btn');
  const statusEl = document.getElementById('save-status');

  saveBtn.disabled = true;
  saveBtn.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"
         style="animation:spin 1s linear infinite">
      <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
      <path d="M12 2a10 10 0 0110 10"/>
    </svg> Saving…`;
  statusEl.textContent = '';
  statusEl.className   = 'save-status';

  // Build the payload: convert _skillsList back to the dict form Pydantic expects
  const payload = {
    personal:     S.personal,
    education:    S.education,
    experience:   S.experience,
    projects:     S.projects,
    skills:       skillsListToDict(S._skillsList),
    achievements: S.achievements,
  };

  try {
    const resp = await fetch('/save', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });

    if (resp.ok) {
      statusEl.textContent = '✓ Saved';
      statusEl.className   = 'save-status status-success';
      toast('Resume saved successfully', 'success');
    } else {
      const body = await resp.json().catch(() => ({ detail: [] }));
      const errors = body.detail || [];
      showErrors(errors);
      const n = errors.length;
      statusEl.textContent = `${n} error${n !== 1 ? 's' : ''} — see fields above`;
      statusEl.className   = 'save-status status-error';
    }
  } catch (err) {
    statusEl.textContent = `Network error: ${err.message}`;
    statusEl.className   = 'save-status status-error';
    toast(`Save failed: ${err.message}`, 'error');
  } finally {
    saveBtn.disabled = false;
    saveBtn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/>
        <polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>
      </svg> Save Changes`;
  }
}

/* ── Validation error display ──────────────────────────────────────────── */
function showErrors(details) {
  const banner = document.getElementById('error-banner');
  const bannerText = document.getElementById('error-banner-text');
  const n = details.length;

  if (!n) { banner.style.display = 'none'; return; }

  banner.style.display = 'flex';
  bannerText.textContent = `${n} validation error${n !== 1 ? 's' : ''}. Please fix the highlighted fields.`;
  banner.scrollIntoView({ behavior: 'smooth', block: 'center' });

  for (const err of details) {
    // FastAPI loc: ["body", "personal", "name"] → "personal.name"
    const loc  = (err.loc || []).slice(1);
    const path = loc.join('.');
    const msg  = (err.msg || 'Invalid value').replace(/^Value error,\s*/i, '');

    // Find the input by data-path
    const input = document.querySelector(`[data-path="${CSS.escape(path)}"]`);
    if (!input) continue;

    input.classList.add('field-invalid');

    // Remove any previous error for this field
    const prev = input.parentElement.querySelector('.field-error');
    if (prev) prev.remove();

    const errEl = document.createElement('span');
    errEl.className   = 'field-error';
    errEl.textContent = msg;
    input.parentElement.appendChild(errEl);
  }

  // Scroll to the first errored field
  const first = document.querySelector('.field-invalid');
  if (first) first.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function clearErrors() {
  document.getElementById('error-banner').style.display = 'none';
  document.querySelectorAll('.field-invalid').forEach(el => el.classList.remove('field-invalid'));
  document.querySelectorAll('.field-error').forEach(el => el.remove());
}

/* ── Toast ─────────────────────────────────────────────────────────────── */
function toast(message, type = 'info', durationMs = 3000) {
  const el = document.getElementById('toast');
  el.textContent = message;
  el.className   = `toast toast-${type} toast-show`;
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.classList.remove('toast-show'); }, durationMs);
}

/* ── Utility ────────────────────────────────────────────────────────────── */
function focusLast(selector) {
  setTimeout(() => {
    const els = document.querySelectorAll(selector);
    if (els.length) els[els.length - 1].focus();
  }, 50);
}

// CSS keyframe for spinner
const style = document.createElement('style');
style.textContent = '@keyframes spin { to { transform: rotate(360deg); } }';
document.head.appendChild(style);
