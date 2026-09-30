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

/* ── State ─────────────────────────────────────────────────── */
let S = null;
let isDirty = false;

/* ── Section collapse state ────────────────────────────────── */
const sectionCollapsed = {};
const entryExpanded = {};

/* ── Active dropdown ──────────────────────────────────────── */
let activeMenu = null;

/* ── Init ──────────────────────────────────────────────────── */
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
  initSectionNav();
  initScrollSpy();

  // Delegated listener: update S on any input/change without re-rendering
  document.addEventListener('input',  handleInput);
  document.addEventListener('change', handleInput);

  // Close dropdown on outside click
  document.addEventListener('click', (e) => {
    if (activeMenu && !e.target.closest('.entry-menu-btn') && !e.target.closest('.entry-menu-dropdown')) {
      closeMenus();
    }
  });

  // Keyboard shortcut: Cmd/Ctrl+S to save
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 's') {
      e.preventDefault();
      saveResume();
      return;
    }

    // Keyboard activation: Enter / Space on section or entry headers
    if ((e.key === 'Enter' || e.key === ' ') && !e.target.closest('button, input, textarea, a, select')) {
      const header = e.target.closest('.section-header, .entry-header');
      if (header && header === e.target) {
        e.preventDefault();
        header.click();
      }
    }
  });
});

/* ── Input sync ────────────────────────────────────────────── */
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
  markDirty();
}

/* ── Dirty state ───────────────────────────────────────────── */
function markDirty() {
  if (isDirty) return;
  isDirty = true;
  const bar = document.getElementById('save-bar');
  const text = document.getElementById('save-bar-text');
  const dot = document.getElementById('save-status-dot');
  if (dot) dot.className = 'save-status-dot dot-unsaved';
  if (text) {
    text.textContent = 'Unsaved changes';
    text.className = 'save-bar-text status-unsaved';
  }
  if (bar) bar.classList.add('visible');
}

function markClean() {
  isDirty = false;
  const text = document.getElementById('save-bar-text');
  const dot = document.getElementById('save-status-dot');
  if (dot) dot.className = 'save-status-dot dot-saved';
  if (text) {
    text.textContent = 'Saved ✓';
    text.className = 'save-bar-text status-saved';
  }
  // Gracefully hide the bar after a brief display
  setTimeout(() => {
    if (!isDirty) {
      const bar = document.getElementById('save-bar');
      if (bar) bar.classList.remove('visible');
    }
  }, 2200);
}

/* ── Path utilities ────────────────────────────────────────── */
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

function getAt(obj, path) {
  const parts = path.split('.');
  let curr = obj;
  for (const p of parts) {
    curr = curr[isNaN(p) ? p : +p];
    if (curr === undefined) return undefined;
  }
  return curr;
}

/* ── HTML helpers ──────────────────────────────────────────── */
function esc(s) {
  return String(s ?? '')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

const tagsStr = tags => (tags || []).join(', ');

function makeFieldId(path) {
  return 'field-' + String(path).replace(/[^a-zA-Z0-9_-]/g, '_');
}

function field(path, label, value, required = false, hint = '') {
  const id = makeFieldId(path);
  return `
    <div class="field-group">
      <label for="${id}">${esc(label)}${required ? ' <span class="req">*</span>' : ''}</label>
      <input type="text" id="${id}" class="field-input" data-path="${esc(path)}"
             value="${esc(value)}" ${required ? 'required' : ''}
             placeholder="${esc(label)}">
      ${hint ? `<span class="field-hint">${hint}</span>` : ''}
    </div>`;
}

function inlineTagsField(path, tags, inputId = '') {
  const tagArr = tags || [];
  const chips = tagArr.map((t, idx) => `
    <span class="tag-chip">
      <span class="tag-chip-text">${esc(t)}</span>
      <button type="button" class="tag-chip-remove" onclick="removeTag('${esc(path)}', ${idx}, event)" aria-label="Remove ${esc(t)}">×</button>
    </span>
  `).join('');

  return `
    <div class="tag-chips-wrapper">
      ${chips}
      <input type="text" class="tag-input-inline" ${inputId ? `id="${inputId}"` : ''}
             placeholder="+ tag"
             onkeydown="handleTagKeydown(event, '${esc(path)}')"
             aria-label="Add tag">
    </div>
    <input type="hidden" class="tag-hidden-input field-input" data-path="${esc(path)}" data-type="tags"
           value="${esc(tagsStr(tagArr))}">`;
}

function tagsField(path, label, tags) {
  const id = makeFieldId(path);
  return `
    <div class="field-group tag-chips-container">
      <label for="${id}">${esc(label)}</label>
      ${inlineTagsField(path, tags, id)}
    </div>`;
}

function numField(path, label, value) {
  const id = makeFieldId(path);
  return `
    <div class="field-group">
      <label for="${id}">${esc(label)}</label>
      <input type="number" id="${id}" class="field-input" data-path="${esc(path)}" data-type="number"
             value="${+(value ?? 0)}" min="0" max="99">
    </div>`;
}

function textArea(path, label, value, rows = 3) {
  const id = makeFieldId(path);
  return `
    <div class="field-group">
      <label for="${id}">${esc(label)}</label>
      <textarea id="${id}" class="field-input" data-path="${esc(path)}" rows="${rows}"
                placeholder="${esc(label)}">${esc(value)}</textarea>
    </div>`;
}

/* ── Tag chip interactions ─────────────────────────────────── */
function handleTagKeydown(e, path) {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault();
    const val = e.target.value.trim().replace(/,/g, '');
    if (!val) return;

    const arr = getAt(S, path);
    if (!Array.isArray(arr)) return;
    if (!arr.includes(val)) {
      arr.push(val);
    }

    e.target.value = '';
    markDirty();
    reRenderForPath(path);
  }
}

function removeTag(path, idx, e) {
  const chip = e ? e.target.closest('.tag-chip') : null;
  if (chip) {
    chip.classList.add('item-exit');
    setTimeout(() => {
      const arr = getAt(S, path);
      if (Array.isArray(arr)) {
        arr.splice(idx, 1);
        markDirty();
        reRenderForPath(path);
      }
    }, 140);
  } else {
    const arr = getAt(S, path);
    if (Array.isArray(arr)) {
      arr.splice(idx, 1);
      markDirty();
      reRenderForPath(path);
    }
  }
}

function reRenderForPath(path) {
  if (path.startsWith('education'))       renderEducation();
  else if (path.startsWith('experience')) renderExperience();
  else if (path.startsWith('projects'))   renderProjects();
  else if (path.startsWith('_skillsList'))renderSkills();
  else if (path.startsWith('achievements'))renderAchievements();
}

/* ── Section collapse/expand ───────────────────────────────── */
function toggleSection(name) {
  sectionCollapsed[name] = !sectionCollapsed[name];
  const section = document.getElementById(`section-${name}`);
  if (!section) return;
  const header = section.querySelector('.section-header');
  const body = document.getElementById(`section-body-${name}`);
  if (sectionCollapsed[name]) {
    header.classList.add('collapsed');
    header.setAttribute('aria-expanded', 'false');
    body.classList.add('collapsed');
  } else {
    header.classList.remove('collapsed');
    header.setAttribute('aria-expanded', 'true');
    body.classList.remove('collapsed');
  }
}

/* ── Entry expand/collapse ─────────────────────────────────── */
function toggleEntry(section, idx) {
  const key = `${section}-${idx}`;
  entryExpanded[key] = !entryExpanded[key];
  const row = document.getElementById(`entry-${key}`);
  if (!row) return;
  const header = row.querySelector('.entry-header');
  if (entryExpanded[key]) {
    row.classList.add('expanded');
    if (header) header.setAttribute('aria-expanded', 'true');
  } else {
    row.classList.remove('expanded');
    if (header) header.setAttribute('aria-expanded', 'false');
  }
}

/* ── Three-dot menu ────────────────────────────────────────── */
function toggleMenu(e, section, idx) {
  e.stopPropagation();
  const btn = e.currentTarget;
  const existingDropdown = btn.parentElement.querySelector('.entry-menu-dropdown');

  if (existingDropdown) {
    closeMenus();
    return;
  }

  closeMenus();

  const dropdown = document.createElement('div');
  dropdown.className = 'entry-menu-dropdown';
  dropdown.innerHTML = `
    <button class="entry-menu-item danger" onclick="confirmDelete('${section}', ${idx})">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
      </svg>
      Delete
    </button>
  `;

  btn.classList.add('open');
  btn.parentElement.style.position = 'relative';
  btn.parentElement.appendChild(dropdown);
  activeMenu = { btn, dropdown };
}

function closeMenus() {
  if (activeMenu) {
    activeMenu.btn.classList.remove('open');
    activeMenu.dropdown.remove();
    activeMenu = null;
  }
}

function confirmDelete(section, idx) {
  closeMenus();
  // Simple inline confirmation with smooth exit animation
  const entry = document.getElementById(`entry-${section}-${idx}`);
  if (!entry) return;

  const header = entry.querySelector('.entry-header');
  const originalBg = header.style.background;
  header.style.background = 'rgba(248, 113, 113, 0.06)';

  const confirmed = confirm('Remove this entry?');
  header.style.background = originalBg;

  if (confirmed) {
    entry.classList.add('item-exit');
    setTimeout(() => {
      removeEntry(section, idx);
    }, 180);
  }
}

/* ── Empty state helper ────────────────────────────────────── */
function emptyState(title, btnText, btnAction) {
  return `
    <div class="empty-state">
      <p class="empty-state-title">${title}</p>
      <button class="btn-add" onclick="${btnAction}">${btnText}</button>
    </div>`;
}

/* ── Section nav ───────────────────────────────────────────── */
function initSectionNav() {
  const nav = document.getElementById('section-nav');
  if (!nav) return;

  const sections = document.querySelectorAll('.form-section[data-nav-label]');
  if (!sections.length) return;

  let html = '<p class="section-nav-label">Sections</p>';
  sections.forEach(sec => {
    const label = sec.dataset.navLabel;
    const id = sec.id;
    html += `<a class="section-nav-link" data-target="${id}" onclick="scrollToSection('${id}')">${label}</a>`;
  });

  nav.innerHTML = html;
  nav.classList.add('visible');
}

function scrollToSection(id) {
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

/* ── Scroll spy ────────────────────────────────────────────── */
function initScrollSpy() {
  const sections = document.querySelectorAll('.form-section[data-nav-label]');
  if (!sections.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        document.querySelectorAll('.section-nav-link').forEach(link => {
          link.classList.toggle('active', link.dataset.target === id);
        });
      }
    });
  }, {
    rootMargin: '-10% 0px -80% 0px',
    threshold: 0
  });

  sections.forEach(s => observer.observe(s));
}

/* ── renderAll ─────────────────────────────────────────────── */
function renderAll() {
  renderPersonal();
  renderEducation();
  renderExperience();
  renderProjects();
  renderSkills();
  renderAchievements();
}

/* ── Personal ──────────────────────────────────────────────── */
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

/* ── Education ─────────────────────────────────────────────── */
function renderEducation() {
  const list = S.education;
  const container = document.getElementById('education-list');
  container.innerHTML =
    list.length ? list.map((e, i) => renderEduEntry(e, i)).join('') :
    emptyState('No education entries yet', '+ Add Education', "addEntry('education')");
  updateCount('edu-count', list.length);
}

function renderEduEntry(e, i) {
  const expanded = entryExpanded[`education-${i}`];
  const subtitle = [e.degree, e.dates].filter(Boolean).join(' · ');
  const cw = e.coursework || [];

  return `
    <div class="entry-row ${expanded ? 'expanded' : ''}" id="entry-education-${i}">
      <div class="entry-header" role="button" tabindex="0" aria-expanded="${expanded ? 'true' : 'false'}" onclick="toggleEntry('education', ${i})">
        <svg class="entry-expand-indicator" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 6 15 12 9 18"/>
        </svg>
        <div class="entry-meta">
          <span class="entry-title">${esc(e.institution || 'New Education')}</span>
          ${subtitle ? `<span class="entry-subtitle">${esc(subtitle)}</span>` : ''}
        </div>
        <button class="entry-menu-btn" onclick="toggleMenu(event, 'education', ${i})" aria-label="Entry options">⋮</button>
      </div>
      <div class="entry-body">
        <div class="entry-body-inner">
          <div class="entry-body-content">
            <div class="fields-grid fields-grid-2">
              ${field(`education.${i}.institution`, 'Institution', e.institution || '', true)}
              ${field(`education.${i}.degree`,      'Degree',      e.degree      || '', true)}
              ${field(`education.${i}.dates`,       'Dates',       e.dates       || '')}
              ${field(`education.${i}.gpa`,         'GPA',         e.gpa         || '')}
            </div>
            ${renderCoursework(i, cw)}
          </div>
        </div>
      </div>
    </div>`;
}

/* ── Coursework — compact rows ─────────────────────────────── */
function renderCoursework(eduIdx, cw) {
  const rows = cw.map((c, ci) => `
    <div class="cw-row">
      <input type="text" class="cw-name" data-path="education.${eduIdx}.coursework.${ci}.name"
             value="${esc(c.name || '')}" placeholder="Course name">
      <div class="cw-tags">
        ${inlineTagsField(`education.${eduIdx}.coursework.${ci}.tags`, c.tags)}
      </div>
      <button class="cw-remove" onclick="removeCoursework(${eduIdx},${ci},event)" aria-label="Remove course">×</button>
    </div>`).join('');

  return `
    <div class="coursework-section">
      <div class="coursework-label">
        <span>Coursework</span>
        <button class="btn-add-inline" onclick="addCoursework(${eduIdx})">+ Add course</button>
      </div>
      ${rows}
    </div>`;
}

function addCoursework(eduIdx) {
  S.education[eduIdx].coursework = S.education[eduIdx].coursework || [];
  S.education[eduIdx].coursework.push({ name: '', tags: [] });
  markDirty();
  renderEducation();
  // Re-expand the entry
  entryExpanded[`education-${eduIdx}`] = true;
  const row = document.getElementById(`entry-education-${eduIdx}`);
  if (row) row.classList.add('expanded');
  setTimeout(() => {
    const rows = row ? row.querySelectorAll('.cw-row') : [];
    if (rows.length) {
      const last = rows[rows.length - 1];
      last.classList.add('item-enter');
      const input = last.querySelector('.cw-name');
      if (input) input.focus();
    }
  }, 40);
}
function removeCoursework(eduIdx, cwIdx, e) {
  const rowEl = e ? e.target.closest('.cw-row') : null;
  if (rowEl) {
    rowEl.classList.add('item-exit');
    setTimeout(() => {
      S.education[eduIdx].coursework.splice(cwIdx, 1);
      markDirty();
      renderEducation();
      entryExpanded[`education-${eduIdx}`] = true;
      const row = document.getElementById(`entry-education-${eduIdx}`);
      if (row) row.classList.add('expanded');
    }, 160);
  } else {
    S.education[eduIdx].coursework.splice(cwIdx, 1);
    markDirty();
    renderEducation();
    entryExpanded[`education-${eduIdx}`] = true;
    const row = document.getElementById(`entry-education-${eduIdx}`);
    if (row) row.classList.add('expanded');
  }
}

/* ── Experience ────────────────────────────────────────────── */
function renderExperience() {
  const list = S.experience;
  const container = document.getElementById('experience-list');
  container.innerHTML =
    list.length ? list.map((j, i) => renderJobEntry(j, i)).join('') :
    emptyState('No experience entries yet', '+ Add Experience', "addEntry('experience')");
  updateCount('exp-count', list.length);
}

function renderJobEntry(job, i) {
  const expanded = entryExpanded[`experience-${i}`];
  const subtitle = [job.role, job.dates, job.location].filter(Boolean).join(' · ');
  const bullets = job.bullets || [];

  return `
    <div class="entry-row ${expanded ? 'expanded' : ''}" id="entry-experience-${i}">
      <div class="entry-header" role="button" tabindex="0" aria-expanded="${expanded ? 'true' : 'false'}" onclick="toggleEntry('experience', ${i})">
        <svg class="entry-expand-indicator" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 6 15 12 9 18"/>
        </svg>
        <div class="entry-meta">
          <span class="entry-title">${esc(job.company || 'New Experience')}</span>
          ${subtitle ? `<span class="entry-subtitle">${esc(subtitle)}</span>` : ''}
        </div>
        <button class="entry-menu-btn" onclick="toggleMenu(event, 'experience', ${i})" aria-label="Entry options">⋮</button>
      </div>
      <div class="entry-body">
        <div class="entry-body-inner">
          <div class="entry-body-content">
            <div class="fields-grid fields-grid-2">
              ${field(`experience.${i}.company`,  'Company',  job.company  || '', true)}
              ${field(`experience.${i}.role`,     'Role',     job.role     || '', true)}
              ${field(`experience.${i}.dates`,    'Dates',    job.dates    || '')}
              ${field(`experience.${i}.location`, 'Location', job.location || '')}
            </div>
            ${renderBullets(i, bullets)}
          </div>
        </div>
      </div>
    </div>`;
}

/* ── Bullets — compact inline ──────────────────────────────── */
function renderBullets(expIdx, bullets) {
  const items = bullets.map((b, bi) => `
    <div class="bullet-item">
      <span class="bullet-marker"></span>
      <div class="bullet-content">
        <textarea class="bullet-textarea" data-path="experience.${expIdx}.bullets.${bi}.text"
                  placeholder="Describe an achievement…" rows="1"
                  oninput="autoResize(this)">${esc(b.text || '')}</textarea>
        <div class="bullet-meta">
          ${inlineTagsField(`experience.${expIdx}.bullets.${bi}.tags`, b.tags)}
          <div class="bullet-priority">
            <span>P</span>
            <input type="number" data-path="experience.${expIdx}.bullets.${bi}.priority" data-type="number"
                   value="${+(b.priority ?? 0)}" min="0" max="99" aria-label="Priority">
          </div>
          <button class="bullet-delete" onclick="removeBullet(${expIdx},${bi},event)" aria-label="Delete bullet">Delete</button>
        </div>
      </div>
    </div>`).join('');

  return `
    <div class="bullets-section">
      <div class="bullets-label">
        <span>Bullets ${bullets.length ? `(${bullets.length})` : ''}</span>
        <button class="btn-add-inline" onclick="addBullet(${expIdx})">+ Add bullet</button>
      </div>
      ${items}
    </div>`;
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = el.scrollHeight + 'px';
}

function addBullet(expIdx) {
  S.experience[expIdx].bullets = S.experience[expIdx].bullets || [];
  S.experience[expIdx].bullets.push({ text: '', tags: [], priority: 0 });
  markDirty();
  renderExperience();
  entryExpanded[`experience-${expIdx}`] = true;
  const row = document.getElementById(`entry-experience-${expIdx}`);
  if (row) row.classList.add('expanded');
  setTimeout(() => {
    const bullets = row ? row.querySelectorAll('.bullet-item') : [];
    if (bullets.length) {
      const last = bullets[bullets.length - 1];
      last.classList.add('item-enter');
      const ta = last.querySelector('.bullet-textarea');
      if (ta) ta.focus();
    }
  }, 40);
}
function removeBullet(expIdx, bi, e) {
  const bulletItem = e ? e.target.closest('.bullet-item') : null;
  if (bulletItem) {
    bulletItem.classList.add('item-exit');
    setTimeout(() => {
      S.experience[expIdx].bullets.splice(bi, 1);
      markDirty();
      renderExperience();
      entryExpanded[`experience-${expIdx}`] = true;
      const row = document.getElementById(`entry-experience-${expIdx}`);
      if (row) row.classList.add('expanded');
    }, 160);
  } else {
    S.experience[expIdx].bullets.splice(bi, 1);
    markDirty();
    renderExperience();
    entryExpanded[`experience-${expIdx}`] = true;
    const row = document.getElementById(`entry-experience-${expIdx}`);
    if (row) row.classList.add('expanded');
  }
}

/* ── Projects ──────────────────────────────────────────────── */
function renderProjects() {
  const list = S.projects;
  const container = document.getElementById('projects-list');
  container.innerHTML =
    list.length ? list.map((p, i) => renderProjectEntry(p, i)).join('') :
    emptyState('No projects yet', '+ Add Project', "addEntry('projects')");
  updateCount('proj-count', list.length);
}

function renderProjectEntry(p, i) {
  const expanded = entryExpanded[`projects-${i}`];
  const subtitle = (p.tech || []).join(', ');

  return `
    <div class="entry-row ${expanded ? 'expanded' : ''}" id="entry-projects-${i}">
      <div class="entry-header" role="button" tabindex="0" aria-expanded="${expanded ? 'true' : 'false'}" onclick="toggleEntry('projects', ${i})">
        <svg class="entry-expand-indicator" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 6 15 12 9 18"/>
        </svg>
        <div class="entry-meta">
          <span class="entry-title">${esc(p.name || 'New Project')}</span>
          ${subtitle ? `<span class="entry-subtitle">${esc(subtitle)}</span>` : ''}
        </div>
        <button class="entry-menu-btn" onclick="toggleMenu(event, 'projects', ${i})" aria-label="Entry options">⋮</button>
      </div>
      <div class="entry-body">
        <div class="entry-body-inner">
          <div class="entry-body-content">
            <div class="fields-grid fields-grid-2">
              ${field(`projects.${i}.name`,   'Name',       p.name   || '', true)}
              ${field(`projects.${i}.github`, 'GitHub URL', p.github || '')}
            </div>
            <div class="fields-grid fields-grid-1" style="margin-top:14px">
              ${textArea(`projects.${i}.description`, 'Description', p.description || '')}
            </div>
            <div class="fields-grid fields-grid-2" style="margin-top:14px">
              ${tagsField(`projects.${i}.tags`, 'Target Tags', p.tags)}
              ${numField(`projects.${i}.priority`, 'Priority', p.priority)}
            </div>
            <div class="fields-grid fields-grid-1" style="margin-top:14px">
              ${tagsField(`projects.${i}.tech`, 'Tech Stack', p.tech)}
            </div>
          </div>
        </div>
      </div>
    </div>`;
}

/* ── Skills — compact chip flow ────────────────────────────── */
function skillsDictToList(dict) {
  return Object.entries(dict).map(([cat, skills]) => ({ category: cat, skills: skills || [] }));
}

function skillsListToDict(list) {
  return Object.fromEntries(list.map(({ category, skills }) => [category, skills]));
}

function renderSkills() {
  const list = S._skillsList;
  const container = document.getElementById('skills-list');
  container.innerHTML =
    list.length ? list.map((cat, i) => renderSkillCategory(cat, i)).join('') :
    emptyState('No skills added yet', '+ Add Category', 'addSkillCategory()');
  updateCount('skills-count', list.length);
}

function renderSkillCategory(cat, i) {
  const skills = cat.skills || [];
  const chips = skills.map((s, si) => {
    const tagBadges = (s.tags || []).map(t => `<span class="skill-chip-tag">${esc(t)}</span>`).join('');
    return `
      <span class="skill-chip">
        ${esc(s.name || 'Unnamed')}
        ${tagBadges ? `<span class="skill-chip-tags">${tagBadges}</span>` : ''}
        <button class="skill-chip-remove" onclick="removeSkill(${i},${si},event)" aria-label="Remove ${esc(s.name)}">×</button>
      </span>`;
  }).join('');

  return `
    <div class="skill-category" id="skill-cat-${i}">
      <div class="skill-cat-header">
        <input type="text" class="skill-cat-name" data-path="_skillsList.${i}.category"
               value="${esc(cat.category)}" placeholder="Category name">
        <button class="skill-cat-remove" onclick="confirmDeleteCategory(${i},event)" aria-label="Remove category">✕</button>
      </div>
      <div class="skill-chips-flow">
        ${chips}
        <button class="skill-add-btn" onclick="startAddSkill(${i})">+ Add</button>
      </div>
    </div>`;
}

function startAddSkill(catIdx) {
  S._skillsList[catIdx].skills = S._skillsList[catIdx].skills || [];
  S._skillsList[catIdx].skills.push({ name: '', tags: [] });
  markDirty();
  renderSkills();
  const lastIdx = S._skillsList[catIdx].skills.length - 1;
  editSkillInline(catIdx, lastIdx);
}

function editSkillInline(catIdx, skillIdx) {
  const chip = document.querySelector(`#skill-cat-${catIdx} .skill-chips-flow .skill-chip:nth-child(${skillIdx + 1})`);
  if (!chip) return;

  const skill = S._skillsList[catIdx].skills[skillIdx];
  const editor = document.createElement('span');
  editor.className = 'skill-inline-editor item-enter';
  editor.innerHTML = `<input type="text" value="${esc(skill.name)}" placeholder="Skill name"
    data-cat="${catIdx}" data-skill="${skillIdx}">`;

  chip.replaceWith(editor);

  const input = editor.querySelector('input');
  input.focus();

  const finishEdit = () => {
    const val = input.value.trim();
    if (val) {
      S._skillsList[catIdx].skills[skillIdx].name = val;
    } else {
      S._skillsList[catIdx].skills.splice(skillIdx, 1);
    }
    markDirty();
    renderSkills();
  };

  input.addEventListener('blur', finishEdit);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); finishEdit(); }
    if (e.key === 'Escape') { e.preventDefault(); S._skillsList[catIdx].skills.splice(skillIdx, 1); renderSkills(); }
  });
}

function addSkillCategory() {
  if (sectionCollapsed['skills']) {
    toggleSection('skills');
  }
  S._skillsList.push({ category: 'New Category', skills: [] });
  markDirty();
  renderSkills();
  setTimeout(() => {
    const cats = document.querySelectorAll('.skill-category');
    if (cats.length) {
      const last = cats[cats.length - 1];
      last.classList.add('item-enter');
      const input = last.querySelector('.skill-cat-name');
      if (input) {
        input.focus();
        input.select();
      }
    }
  }, 40);
}

function confirmDeleteCategory(i, e) {
  const rowEl = e ? e.target.closest('.skill-category') : document.getElementById(`skill-cat-${i}`);
  if (confirm('Remove this skill category and all its skills?')) {
    if (rowEl) {
      rowEl.classList.add('item-exit');
      setTimeout(() => removeSkillCategory(i), 160);
    } else {
      removeSkillCategory(i);
    }
  }
}

function removeSkillCategory(i) {
  S._skillsList.splice(i, 1);
  markDirty();
  renderSkills();
}
function removeSkill(catIdx, si, e) {
  const chip = e ? e.target.closest('.skill-chip') : null;
  if (chip) {
    chip.classList.add('item-exit');
    setTimeout(() => {
      S._skillsList[catIdx].skills.splice(si, 1);
      markDirty();
      renderSkills();
    }, 140);
  } else {
    S._skillsList[catIdx].skills.splice(si, 1);
    markDirty();
    renderSkills();
  }
}

/* ── Achievements ──────────────────────────────────────────── */
function renderAchievements() {
  const list = S.achievements;
  const container = document.getElementById('achievements-list');
  container.innerHTML =
    list.length ? list.map((a, i) => renderAchievementEntry(a, i)).join('') :
    emptyState('No achievements yet', '+ Add Achievement', "addEntry('achievements')");
  updateCount('ach-count', list.length);
}

function renderAchievementEntry(a, i) {
  const expanded = entryExpanded[`achievements-${i}`];
  const subtitle = [a.issuer, a.date].filter(Boolean).join(' · ');

  return `
    <div class="entry-row ${expanded ? 'expanded' : ''}" id="entry-achievements-${i}">
      <div class="entry-header" role="button" tabindex="0" aria-expanded="${expanded ? 'true' : 'false'}" onclick="toggleEntry('achievements', ${i})">
        <svg class="entry-expand-indicator" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 6 15 12 9 18"/>
        </svg>
        <div class="entry-meta">
          <span class="entry-title">${esc(a.title || 'New Achievement')}</span>
          ${subtitle ? `<span class="entry-subtitle">${esc(subtitle)}</span>` : ''}
        </div>
        <button class="entry-menu-btn" onclick="toggleMenu(event, 'achievements', ${i})" aria-label="Entry options">⋮</button>
      </div>
      <div class="entry-body">
        <div class="entry-body-inner">
          <div class="entry-body-content">
            <div class="fields-grid fields-grid-2">
              ${field(`achievements.${i}.title`,  'Title',  a.title  || '', true)}
              ${field(`achievements.${i}.issuer`, 'Issuer', a.issuer || '')}
              ${field(`achievements.${i}.date`,   'Date',   a.date   || '')}
              ${numField(`achievements.${i}.priority`, 'Priority', a.priority)}
            </div>
            <div class="fields-grid fields-grid-1" style="margin-top:14px">
              ${tagsField(`achievements.${i}.tags`, 'Tags', a.tags)}
            </div>
          </div>
        </div>
      </div>
    </div>`;
}

/* ── Generic add/remove ────────────────────────────────────── */
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
  if (sectionCollapsed[section]) {
    toggleSection(section);
  }
  S[section].push({ ...DEFAULTS[section] });
  const idx = S[section].length - 1;
  entryExpanded[`${section}-${idx}`] = true;
  markDirty();
  RENDERS[section]();
  // Auto-scroll and auto-focus the first field of the new entry with a natural enter animation
  setTimeout(() => {
    const el = document.getElementById(`entry-${section}-${idx}`);
    if (el) {
      el.classList.add('item-enter');
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      const firstInput = el.querySelector('input:not([type="hidden"]), textarea');
      if (firstInput) firstInput.focus();
    }
  }, 40);
}

function removeEntry(section, idx) {
  S[section].splice(idx, 1);
  delete entryExpanded[`${section}-${idx}`];
  markDirty();
  RENDERS[section]();
}

/* ── Count badge ───────────────────────────────────────────── */
function updateCount(id, count) {
  const el = document.getElementById(id);
  if (el) {
    el.textContent = count > 0 ? count : '';
  }
}

/* ── Save ──────────────────────────────────────────────────── */
async function saveResume() {
  clearErrors();

  const saveBtn = document.getElementById('save-btn');
  const barText = document.getElementById('save-bar-text');
  const dot     = document.getElementById('save-status-dot');

  saveBtn.disabled = true;
  saveBtn.classList.add('is-loading');
  saveBtn.textContent = 'Saving…';
  if (dot) dot.className = 'save-status-dot dot-saving';
  if (barText) {
    barText.textContent = 'Saving…';
    barText.className = 'save-bar-text status-saving';
  }

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
      markClean();
      toast('Resume saved successfully', 'success');
    } else {
      const body = await resp.json().catch(() => ({ detail: [] }));
      const errors = body.detail || [];
      showErrors(errors);
      const n = errors.length;
      if (barText) {
        barText.textContent = `${n} error${n !== 1 ? 's' : ''}`;
        barText.className = 'save-bar-text';
      }
      if (dot) dot.className = 'save-status-dot dot-unsaved';
    }
  } catch (err) {
    if (barText) {
      barText.textContent = 'Save failed';
      barText.className = 'save-bar-text';
    }
    if (dot) dot.className = 'save-status-dot dot-unsaved';
    toast(`Save failed: ${err.message}`, 'error');
  } finally {
    saveBtn.disabled = false;
    saveBtn.classList.remove('is-loading');
    saveBtn.textContent = 'Save Changes';
  }
}

/* ── Validation error display ──────────────────────────────── */
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

    // Auto-expand the entry containing this field
    const entryRow = input.closest('.entry-row');
    if (entryRow && !entryRow.classList.contains('expanded')) {
      entryRow.classList.add('expanded');
      const key = entryRow.id.replace('entry-', '');
      entryExpanded[key] = true;
    }
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

/* ── Toast ─────────────────────────────────────────────────── */
function toast(message, type = 'info', durationMs = 3000) {
  const el = document.getElementById('toast');
  el.textContent = message;
  el.className   = `toast toast-${type} toast-show`;
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.classList.remove('toast-show'); }, durationMs);
}

/* ── Utility ───────────────────────────────────────────────── */
function focusLast(selector) {
  setTimeout(() => {
    const els = document.querySelectorAll(selector);
    if (els.length) els[els.length - 1].focus();
  }, 80);
}

/* ── Auto-resize textareas on load ─────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Use mutation observer to auto-resize textareas when they appear
  const observer = new MutationObserver(() => {
    document.querySelectorAll('.bullet-textarea').forEach(el => {
      if (!el.dataset.sized) {
        el.style.height = 'auto';
        el.style.height = el.scrollHeight + 'px';
        el.dataset.sized = '1';
      }
    });
  });
  observer.observe(document.body, { childList: true, subtree: true });
});
