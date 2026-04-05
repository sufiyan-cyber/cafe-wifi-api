

const BASE_URL = "";

// ── State ────────────────────────────────────────────────────
const state = {
  currentPage: 1,
  totalPages: 1,
  totalCafes: 0,
  mode: 'idle',
  lastFilters: {},
};

// ── DOM refs ─────────────────────────────────────────────────
const cardsGrid        = document.getElementById('cards-grid');
const statusBar        = document.getElementById('status-bar');
const statusText       = document.getElementById('status-text');
const resultsMeta      = document.getElementById('results-meta');
const resultsCount     = document.getElementById('results-count');
const pagination       = document.getElementById('pagination');
const pageInfo         = document.getElementById('page-info');
const btnPrev          = document.getElementById('btn-prev');
const btnNext          = document.getElementById('btn-next');
const emptyState       = document.getElementById('empty-state');
const landingPH        = document.getElementById('landing-placeholder');
const modalOverlay     = document.getElementById('modal-overlay');
const modalBody        = document.getElementById('modal-body');


document.addEventListener('DOMContentLoaded', () => {
  loadLocations();
});


function loadLocations() {
  fetch(`${BASE_URL}/locations`)
    .then(r => r.json())
    .then(data => {
      const select = document.getElementById('loc-select');
      (data.locations || []).forEach(loc => {
        const opt = document.createElement('option');
        opt.value = loc;
        opt.textContent = loc;
        select.appendChild(opt);
      });
    })
    .catch(() => {

    });
}


function showStatus(msg, type = 'loading') {
  statusBar.className = `status-bar ${type}`;
  statusText.textContent = msg;
  statusBar.classList.remove('hidden');
}

function hideStatus() {
  statusBar.classList.add('hidden');
}

function showEmpty() {
  emptyState.classList.remove('hidden');
  cardsGrid.innerHTML = '';
  resultsMeta.classList.add('hidden');
}

function hideLanding() {
  landingPH.classList.add('hidden');
}


function renderCafes(cafes, total, page, pages) {
  hideLanding();
  emptyState.classList.add('hidden');
  cardsGrid.innerHTML = '';

  if (!cafes || cafes.length === 0) {
    showEmpty();
    return;
  }

  resultsMeta.classList.remove('hidden');
  resultsCount.textContent = `${total || cafes.length} café${(total || cafes.length) !== 1 ? 's' : ''} found`;


  if (pages && pages > 1) {
    pagination.style.display = 'flex';
    state.totalPages = pages;
    state.currentPage = page;
    pageInfo.textContent = `Page ${page} of ${pages}`;
    btnPrev.disabled = page <= 1;
    btnNext.disabled = page >= pages;
    btnPrev.style.opacity = page <= 1 ? '0.4' : '1';
    btnNext.style.opacity = page >= pages ? '0.4' : '1';
  } else {
    pagination.style.display = 'none';
  }

  cafes.forEach((cafe, i) => {
    const card = buildCard(cafe, i);
    cardsGrid.appendChild(card);
  });
}


function buildCard(cafe, index) {
  const card = document.createElement('div');
  card.className = 'cafe-card';
  card.style.animationDelay = `${Math.min(index, 11) * 40}ms`;
  card.onclick = () => openModal(cafe);

  const ratingClass = cafe.rate >= 4.5 ? 'high' : cafe.rate >= 4.2 ? 'mid' : 'low';
  const cuisineStr = Array.isArray(cafe.cuisines)
    ? cafe.cuisines.slice(0, 4).join(', ')
    : cafe.cuisines || 'N/A';

  const onlineTag = cafe.online_order
    ? '<span class="tag tag-green">🛵 Online Order</span>'
    : '<span class="tag tag-red">No Delivery</span>';

  const tableTag = cafe.book_table
    ? '<span class="tag tag-gold">🪑 Book Table</span>'
    : '';

  const restType = Array.isArray(cafe.rest_type)
    ? cafe.rest_type[0]
    : cafe.rest_type || '';

  const typeTag = restType
    ? `<span class="tag tag-muted">${restType}</span>`
    : '';

  card.innerHTML = `
    <div class="card-top">
      <div class="card-name">${cafe.name}</div>
      <div class="rating-pill ${ratingClass}">★ ${cafe.rate ?? 'N/A'}</div>
    </div>
    <div class="card-location">📍 ${cafe.location || 'Unknown'}</div>
    <div class="card-cuisines">${cuisineStr}</div>
    <div class="card-tags">
      ${onlineTag}
      ${tableTag}
      ${typeTag}
    </div>
    <div class="card-footer">
      <span class="card-cost">₹${cafe.approx_cost ?? 'N/A'} for two</span>
      <span class="card-votes">${formatVotes(cafe.votes)} votes</span>
    </div>
  `;
  return card;
}

function formatVotes(v) {
  if (!v) return '0';
  return v >= 1000 ? (v / 1000).toFixed(1) + 'k' : v;
}


function openModal(cafe) {
  const cuisines = Array.isArray(cafe.cuisines) ? cafe.cuisines : [];
  const dishes   = Array.isArray(cafe.dish_liked) ? cafe.dish_liked : [];
  const restType = Array.isArray(cafe.rest_type) ? cafe.rest_type : [];

  const cuisineChips = cuisines.map(c => `<span class="modal-chip">${c}</span>`).join('');
  const dishChips    = dishes.slice(0, 10).map(d => `<span class="modal-chip">${d}</span>`).join('');
  const typeChips    = restType.map(r => `<span class="modal-chip">${r}</span>`).join('');

  const onlineTag = cafe.online_order
    ? '<span class="tag tag-green">🛵 Online Order Available</span>'
    : '<span class="tag tag-red">No Online Delivery</span>';
  const tableTag = cafe.book_table
    ? '<span class="tag tag-gold">🪑 Table Booking Available</span>'
    : '<span class="tag tag-muted">No Table Booking</span>';

  modalBody.innerHTML = `
    <div class="modal-name">${cafe.name}</div>
    <div class="modal-location">📍 ${cafe.location || 'Unknown'} · ${cafe.listed_in_city || ''}</div>

    <div class="modal-stats">
      <div class="modal-stat">
        <span class="modal-stat-val">★ ${cafe.rate ?? 'N/A'}</span>
        <span class="modal-stat-label">Rating</span>
      </div>
      <div class="modal-stat">
        <span class="modal-stat-val">₹${cafe.approx_cost ?? 'N/A'}</span>
        <span class="modal-stat-label">For Two</span>
      </div>
      <div class="modal-stat">
        <span class="modal-stat-val">${formatVotes(cafe.votes)}</span>
        <span class="modal-stat-label">Votes</span>
      </div>
    </div>

    <div class="modal-tags">
      ${onlineTag}
      ${tableTag}
    </div>

    ${cafe.address ? `
      <div class="modal-section-title">Address</div>
      <div class="modal-address">${cafe.address}</div>
    ` : ''}

    ${restType.length ? `
      <div class="modal-section-title">Type</div>
      <div class="modal-list">${typeChips}</div>
    ` : ''}

    ${cuisines.length ? `
      <div class="modal-section-title">Cuisines</div>
      <div class="modal-list">${cuisineChips}</div>
    ` : ''}

    ${dishes.length ? `
      <div class="modal-section-title">Popular Dishes</div>
      <div class="modal-list">${dishChips}</div>
    ` : ''}

    ${cafe.listed_in_type ? `
      <div class="modal-section-title">Listed In</div>
      <div class="modal-list">
        <span class="modal-chip">${cafe.listed_in_type}</span>
        ${cafe.listed_in_city ? `<span class="modal-chip">${cafe.listed_in_city}</span>` : ''}
      </div>
    ` : ''}
  `;

  modalOverlay.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeModal(e) {
  if (e && e.target !== modalOverlay) return;
  modalOverlay.classList.add('hidden');
  document.body.style.overflow = '';
}


document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    modalOverlay.classList.add('hidden');
    document.body.style.overflow = '';
  }
});


function loadAll(page = 1) {
  state.mode = 'all';
  state.currentPage = page;
  showStatus('Loading cafés…', 'loading');

  fetch(`${BASE_URL}/all?page=${page}&per_page=18`)
    .then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then(data => {
      hideStatus();
      renderCafes(data.cafes, data.total, data.page, data.pages);
    })
    .catch(err => {
      showStatus(`Failed to load cafés. Is the backend running? (${err.message})`, 'error');
    });
}


function loadRandom() {
  state.mode = 'random';
  showStatus('Finding a café for you…', 'loading');

  fetch(`${BASE_URL}/random`)
    .then(r => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then(data => {
      hideStatus();
      const cafe = data.cafe;
      if (!cafe) {
        showStatus('No café returned from server.', 'error');
        return;
      }
      hideLanding();
      emptyState.classList.add('hidden');
      resultsMeta.classList.remove('hidden');
      resultsCount.textContent = 'Random pick ✦';
      pagination.style.display = 'none';
      cardsGrid.innerHTML = '';
      cardsGrid.appendChild(buildCard(cafe, 0));
    })
    .catch(err => {
      showStatus(`Failed to fetch random café. (${err.message})`, 'error');
    });
}


function applyFilters() {
  const location = document.getElementById('loc-select').value;
  const minRate  = document.getElementById('rating-select').value;
  const maxCost  = document.getElementById('cost-select').value;
  const online   = document.getElementById('online-select').value;


  const hasFilters = location || minRate || maxCost || online;
  if (!hasFilters) {
    loadAll(1);
    return;
  }

  state.mode = 'search';
  state.lastFilters = { location, minRate, maxCost, online };

  const params = new URLSearchParams();
  if (location) params.append('location', location);
  if (minRate)  params.append('min_rate', minRate);
  if (maxCost)  params.append('max_cost', maxCost);
  if (online)   params.append('online_order', online);

  showStatus('Searching…', 'loading');

  fetch(`${BASE_URL}/search?${params.toString()}`)
    .then(r => {
      if (r.status === 404) return { cafes: [] };
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then(data => {
      hideStatus();
      const cafes = data.cafes || [];
      renderCafes(cafes, cafes.length, 1, 1);
    })
    .catch(err => {
      showStatus(`Search failed. (${err.message})`, 'error');
    });
}


function resetFilters() {
  document.getElementById('loc-select').value    = '';
  document.getElementById('rating-select').value = '';
  document.getElementById('cost-select').value   = '';
  document.getElementById('online-select').value = '';
  loadAll(1);
}

function changePage(direction) {
  const newPage = state.currentPage + direction;
  if (newPage < 1 || newPage > state.totalPages) return;

  if (state.mode === 'all') {
    loadAll(newPage);
  }


  document.getElementById('filter-bar').scrollIntoView({ behavior: 'smooth' });
}
