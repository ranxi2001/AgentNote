/**
 * AgentNote Blog Viewer
 * Markdown document display frontend
 */

// State
const state = {
  docs: [],
  categories: [],
  tags: [],
  currentDoc: null,
  filter: {
    category: null,
    tag: null,
    keyword: ''
  },
  isDark: false
};

// DOM
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// API
const api = {
  async getDocs(params = {}) {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`/api/docs?${query}`);
    return res.json();
  },
  async getDoc(id) {
    const res = await fetch(`/api/docs/${id}`);
    return res.json();
  },
  async getCategories() {
    const res = await fetch('/api/categories');
    return res.json();
  },
  async getTags() {
    const res = await fetch('/api/tags');
    return res.json();
  }
};

// Markdown Parser (simple implementation)
const md = {
  parse(text) {
    if (!text) return '';

    let html = text
      // Escape HTML
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')

      // Code blocks (must be before other replacements)
      .replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) =>
        `<pre><code class="language-${lang}">${code.trim()}</code></pre>`)

      // Inline code
      .replace(/`([^`]+)`/g, '<code>$1</code>')

      // Headers
      .replace(/^#### (.+)$/gm, '<h4>$1</h4>')
      .replace(/^### (.+)$/gm, '<h3>$1</h3>')
      .replace(/^## (.+)$/gm, '<h2>$1</h2>')
      .replace(/^# (.+)$/gm, '<h1>$1</h1>')

      // Bold and italic
      .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')

      // Links and images
      .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')

      // Blockquotes
      .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')

      // Horizontal rule
      .replace(/^---$/gm, '<hr>')

      // Unordered lists
      .replace(/^- (.+)$/gm, '<li>$1</li>')

      // Ordered lists
      .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')

      // Paragraphs (lines that aren't already wrapped)
      .replace(/^(?!<[hpuolbic]|<\/|<hr|<pre|<block)(.+)$/gm, '<p>$1</p>')

      // Clean up consecutive blockquotes
      .replace(/<\/blockquote>\n<blockquote>/g, '\n')

      // Wrap lists
      .replace(/(<li>.*<\/li>\n?)+/g, match => {
        if (match.includes('1.')) return `<ol>${match}</ol>`;
        return `<ul>${match}</ul>`;
      })

      // Line breaks
      .replace(/\n\n/g, '\n');

    return html;
  }
};

// UI Functions
const ui = {
  init() {
    this.bindEvents();
    this.loadTheme();
    this.loadData();
  },

  bindEvents() {
    // Menu toggle
    $('#menu-btn')?.addEventListener('click', () => this.toggleSidebar());
    $('#overlay')?.addEventListener('click', () => this.closeSidebar());

    // Theme toggle
    $('#theme-btn')?.addEventListener('click', () => this.toggleTheme());

    // Search
    $('#search-input')?.addEventListener('input', debounce((e) => {
      state.filter.keyword = e.target.value;
      this.loadDocs();
    }, 300));

    // Back button
    $('#doc-back')?.addEventListener('click', () => this.showList());
  },

  async loadData() {
    try {
      // Load categories and tags
      const [catRes, tagRes] = await Promise.all([
        api.getCategories(),
        api.getTags()
      ]);

      if (catRes.success) {
        state.categories = catRes.data;
        this.renderCategories();
      }

      if (tagRes.success) {
        state.tags = tagRes.data;
        this.renderTags();
      }

      // Load documents
      await this.loadDocs();
    } catch (err) {
      console.error('Failed to load data:', err);
    }
  },

  async loadDocs() {
    const params = { limit: 50 };
    if (state.filter.category) params.category = state.filter.category;
    if (state.filter.tag) params.tag = state.filter.tag;
    if (state.filter.keyword) params.keyword = state.filter.keyword;

    try {
      const res = await api.getDocs(params);
      if (res.success) {
        state.docs = res.data;
        this.renderDocs();
      }
    } catch (err) {
      console.error('Failed to load docs:', err);
    }
  },

  renderCategories() {
    const container = $('#category-list');
    if (!container) return;

    const total = state.docs.length || state.categories.reduce((s, c) => s + c.count, 0);

    let html = `
      <li class="nav-item ${!state.filter.category ? 'active' : ''}"
          onclick="ui.filterCategory(null)">
        <span>All Documents</span>
        <span class="count">${total}</span>
      </li>
    `;

    state.categories.forEach(cat => {
      html += `
        <li class="nav-item ${state.filter.category === cat.category ? 'active' : ''}"
            onclick="ui.filterCategory('${escapeHtml(cat.category)}')">
          <span>${escapeHtml(cat.category)}</span>
          <span class="count">${cat.count}</span>
        </li>
      `;
    });

    container.innerHTML = html;
  },

  renderTags() {
    const container = $('#tag-cloud');
    if (!container) return;

    if (state.tags.length === 0) {
      container.innerHTML = '<span class="tag" style="opacity:0.5">No tags yet</span>';
      return;
    }

    container.innerHTML = state.tags.map(t => `
      <span class="tag ${state.filter.tag === t.name ? 'active' : ''}"
            onclick="ui.filterTag('${escapeHtml(t.name)}')">${escapeHtml(t.name)}</span>
    `).join('');
  },

  renderDocs() {
    const container = $('#doc-list');
    if (!container) return;

    if (state.docs.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">📄</div>
          <div class="empty-title">No documents yet</div>
          <div class="empty-text">Use Claude to format and save your notes</div>
        </div>
      `;
      return;
    }

    container.innerHTML = state.docs.map(doc => `
      <div class="doc-card" onclick="ui.viewDoc(${doc.id})">
        <div class="doc-card-header">
          <div class="doc-card-title">${escapeHtml(doc.title)}</div>
          ${doc.category ? `<span class="doc-card-category">${escapeHtml(doc.category)}</span>` : ''}
        </div>
        <div class="doc-card-summary">${escapeHtml(doc.summary || '')}</div>
        <div class="doc-card-meta">
          <span>${formatDate(doc.created_at)}</span>
          ${doc.tags && doc.tags.length > 0 ? `
            <div class="doc-card-tags">
              ${doc.tags.slice(0, 3).map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('')}
            </div>
          ` : ''}
        </div>
      </div>
    `).join('');
  },

  async viewDoc(id) {
    try {
      const res = await api.getDoc(id);
      if (!res.success) return;

      state.currentDoc = res.data;

      // Update view
      $('#doc-view-title').textContent = state.currentDoc.title;
      $('#doc-view-category').textContent = state.currentDoc.category || 'Uncategorized';
      $('#doc-view-date').textContent = formatDate(state.currentDoc.created_at);
      $('#doc-view-content').innerHTML = md.parse(state.currentDoc.content);

      // Update tags
      const tagsContainer = $('#doc-view-tags');
      if (state.currentDoc.tags && state.currentDoc.tags.length > 0) {
        tagsContainer.innerHTML = state.currentDoc.tags.map(t =>
          `<span class="tag">${escapeHtml(t)}</span>`
        ).join('');
        tagsContainer.parentElement.style.display = 'flex';
      } else {
        tagsContainer.parentElement.style.display = 'none';
      }

      // Show doc view
      $('#list-view').classList.add('hidden');
      $('#doc-view').classList.add('active');

      window.scrollTo(0, 0);
    } catch (err) {
      console.error('Failed to load doc:', err);
    }
  },

  showList() {
    $('#doc-view').classList.remove('active');
    $('#list-view').classList.remove('hidden');
    state.currentDoc = null;
  },

  filterCategory(category) {
    state.filter.category = category;
    state.filter.tag = null;
    this.renderCategories();
    this.renderTags();
    this.loadDocs();
    this.closeSidebar();
  },

  filterTag(tag) {
    state.filter.tag = state.filter.tag === tag ? null : tag;
    state.filter.category = null;
    this.renderCategories();
    this.renderTags();
    this.loadDocs();
    this.closeSidebar();
  },

  // Sidebar
  toggleSidebar() {
    $('#sidebar')?.classList.toggle('open');
    $('#overlay')?.classList.toggle('active');
  },

  closeSidebar() {
    $('#sidebar')?.classList.remove('open');
    $('#overlay')?.classList.remove('active');
  },

  // Theme
  loadTheme() {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.setAttribute('data-theme', 'dark');
      state.isDark = true;
    }
    this.updateThemeIcon();
  },

  toggleTheme() {
    state.isDark = !state.isDark;
    if (state.isDark) {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('theme', 'light');
    }
    this.updateThemeIcon();
  },

  updateThemeIcon() {
    const btn = $('#theme-btn');
    if (btn) {
      btn.innerHTML = state.isDark
        ? '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
        : '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    }
  }
};

// Utilities
function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

// Initialize
document.addEventListener('DOMContentLoaded', () => ui.init());

// Global access
window.ui = ui;
