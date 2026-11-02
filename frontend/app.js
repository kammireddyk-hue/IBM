const API_ROOT = "/api/v1";
const grid = document.querySelector("#dataset-grid");
const filterInput = document.querySelector("#institution-filter");
const emptyState = document.querySelector("#empty-state");
const filterTotal = document.querySelector("#filter-total");
const dialog = document.querySelector("#document-dialog");
const dialogTitle = document.querySelector("#dialog-title");
const documentFrame = document.querySelector("#document-frame");
const downloadLink = document.querySelector("#download-link");
const searchForm = document.querySelector("#document-search");
const searchInput = document.querySelector("#document-query");
const searchFeedback = document.querySelector("#search-feedback");
const searchResults = document.querySelector("#search-results");
const toast = document.querySelector("#toast");

let institutions = [];
let toastTimeout;

async function apiRequest(path) {
  const response = await fetch(`${API_ROOT}${path}`);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || `Request failed (${response.status}).`);
  }
  return payload;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  })[character]);
}

function coverIcon(index) {
  const icons = [
    '<path d="M5 4.5h9l4 4v11H5z"/><path d="M14 4.5v4h4M8 12h7m-7 3h7"/>',
    '<path d="M4 19.5V8l8-4 8 4v11.5"/><path d="M8 19.5v-7h8v7M8 9h.01M16 9h.01"/>',
    '<circle cx="12" cy="8" r="3.5"/><path d="M5 20c.5-4 3-6 7-6s6.5 2 7 6M12 4.5v7"/>',
    '<path d="M5 19.5h14M7 17V9m5 8V5m5 12v-6M5 9h4m1-4h4m1 6h4"/>',
  ];
  return `<svg viewBox="0 0 24 24" aria-hidden="true">${icons[index % icons.length]}</svg>`;
}

function renderInstitution(institution, index) {
  const name = escapeHtml(institution.name);
  const id = escapeHtml(institution.id);
  const filename = escapeHtml(institution.filename);
  return `
    <article class="dataset-card">
      <div class="dataset-cover tone-${index % 5}">${coverIcon(index)}</div>
      <div class="dataset-copy">
        <div class="dataset-id">INSTITUTION ${id}</div>
        <div class="dataset-name" title="${name}">${name}</div>
        <div class="dataset-meta"><span class="meta-pill">Annual packet</span><span>PDF</span><span>·</span><span>${Number(institution.pages) || 32} pages</span></div>
      </div>
      <button class="dataset-open" type="button" data-open-id="${id}" data-open-name="${name}" aria-label="Open ${name} packet">↗</button>
      <span class="hidden" data-filename="${filename}"></span>
    </article>`;
}

function renderInstitutions() {
  const term = filterInput.value.trim().toLowerCase();
  const filtered = institutions.filter((institution) =>
    `${institution.name} ${institution.id}`.toLowerCase().includes(term),
  );
  grid.innerHTML = filtered.map((institution) =>
    renderInstitution(institution, Number(institution.id) - 1),
  ).join("");
  emptyState.classList.toggle("hidden", filtered.length > 0);
  filterTotal.textContent = term ? `${filtered.length} of ${institutions.length} shown` : `${filtered.length} datasets`;
  document.querySelector("#heading-count").textContent = String(institutions.length).padStart(2, "0");
  document.querySelector("#institution-stat").textContent = String(institutions.length).padStart(2, "0");
  document.querySelector("#document-stat").textContent = String(institutions.length).padStart(2, "0");
  document.querySelector("#page-stat").textContent = String(
    institutions.reduce((total, institution) => total + (Number(institution.pages) || 32), 0),
  );
  document.querySelector("#sidebar-count").textContent = institutions.length;
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  window.clearTimeout(toastTimeout);
  toastTimeout = window.setTimeout(() => toast.classList.remove("show"), 3600);
}

function openDocument(id, name, page = 1) {
  const url = `${API_ROOT}/institutions/${encodeURIComponent(id)}/document`;
  documentFrame.src = `${url}#page=${Math.max(1, Number(page) || 1)}&view=FitH`;
  downloadLink.href = url;
  downloadLink.download = `institution-${id}-packet.pdf`;
  dialogTitle.textContent = name;
  if (!dialog.open) dialog.showModal();
}

function highlightSnippet(snippet, query) {
  const safe = escapeHtml(snippet);
  const escapedQuery = escapeHtml(query).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  if (!escapedQuery) return safe;
  return safe.replace(new RegExp(`(${escapedQuery})`, "ig"), "<mark>$1</mark>");
}

function renderSearchResults(results, query) {
  if (results.length === 0) {
    searchResults.innerHTML = "";
    searchResults.classList.add("hidden");
    searchFeedback.textContent = `No matches found for “${query}”. Try a different phrase.`;
    return;
  }

  searchFeedback.textContent = `${results.length} matching page${results.length === 1 ? "" : "s"} for “${query}”`;
  searchResults.innerHTML = results.map((result) => `
    <article class="result-card">
      <div class="result-topline">
        <span class="result-institution">${escapeHtml(result.institution)}</span>
        <span>·</span><span>Institution ${escapeHtml(result.institution_id)}</span>
        <span class="result-page">Page ${Number(result.page)}</span>
      </div>
      <div class="result-snippet">${highlightSnippet(result.snippet, query)}</div>
      <button class="result-open" type="button" data-open-id="${escapeHtml(result.institution_id)}" data-open-name="${escapeHtml(result.institution)}" data-open-page="${Number(result.page)}">Open this page ↗</button>
    </article>`).join("");
  searchResults.classList.remove("hidden");
}

async function loadInstitutions() {
  try {
    const payload = await apiRequest("/institutions");
    institutions = payload.institutions;
    renderInstitutions();
  } catch (error) {
    grid.innerHTML = "";
    emptyState.classList.remove("hidden");
    emptyState.textContent = "Could not load the dataset library. Check that the Flask server is running and try refreshing.";
    filterTotal.textContent = "";
    showToast(error.message);
  }
}

filterInput.addEventListener("input", renderInstitutions);

document.addEventListener("click", (event) => {
  const openButton = event.target.closest("[data-open-id]");
  if (openButton) {
    openDocument(
      openButton.dataset.openId,
      openButton.dataset.openName,
      openButton.dataset.openPage || 1,
    );
  }

  if (event.target.closest("#dialog-close")) {
    dialog.close();
  }
});

dialog.addEventListener("close", () => {
  documentFrame.src = "about:blank";
});

dialog.addEventListener("click", (event) => {
  if (event.target === dialog) dialog.close();
});

searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = searchInput.value.trim();
  if (!query) {
    searchFeedback.textContent = "Enter a word or phrase to search the packet text.";
    searchResults.classList.add("hidden");
    searchInput.focus();
    return;
  }

  searchFeedback.textContent = "Searching across institutional packets…";
  searchResults.classList.add("hidden");
  try {
    const payload = await apiRequest(`/search?q=${encodeURIComponent(query)}&limit=20`);
    renderSearchResults(payload.results, query);
  } catch (error) {
    searchFeedback.textContent = "";
    showToast(error.message);
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
    event.preventDefault();
    filterInput.focus();
  }
});

loadInstitutions();
