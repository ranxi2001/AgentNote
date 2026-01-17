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
  isDark: false,
  // Document cache for preloading
  docCache: new Map(),
  preloadQueue: new Set()
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
  async getDoc(id, useCache = true) {
    // Check cache first
    if (useCache && state.docCache.has(id)) {
      return { success: true, data: state.docCache.get(id), fromCache: true };
    }
    const res = await fetch(`/api/docs/${id}`);
    const data = await res.json();
    // Cache successful responses
    if (data.success) {
      state.docCache.set(id, data.data);
    }
    return data;
  },
  async deleteDoc(id) {
    const res = await fetch(`/api/docs/${id}`, { method: 'DELETE' });
    // Clear from cache
    state.docCache.delete(id);
    return res.json();
  },
  async getCategories() {
    const res = await fetch('/api/categories');
    return res.json();
  },
  async getTags() {
    const res = await fetch('/api/tags');
    return res.json();
  },
  // Preload document in background
  preload(id) {
    if (state.docCache.has(id) || state.preloadQueue.has(id)) return;
    state.preloadQueue.add(id);
    // Use requestIdleCallback for non-blocking preload
    const load = () => {
      fetch(`/api/docs/${id}`)
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            state.docCache.set(id, data.data);
          }
        })
        .catch(() => {})
        .finally(() => state.preloadQueue.delete(id));
    };
    if ('requestIdleCallback' in window) {
      requestIdleCallback(load, { timeout: 2000 });
    } else {
      setTimeout(load, 100);
    }
  }
};

// Markdown Parser (simple implementation)
const md = {
  // Store extracted headings for TOC
  headings: [],

  parse(text, options = {}) {
    if (!text) return '';

    // Reset headings
    this.headings = [];

    // Remove first H1 if it matches the title (avoid duplicate)
    if (options.title) {
      const firstH1Match = text.match(/^# (.+)$/m);
      if (firstH1Match) {
        const h1Text = firstH1Match[1].trim();
        const titleNormalized = options.title.trim();
        // Remove if similar (exact match or very close)
        if (h1Text === titleNormalized ||
            h1Text.replace(/[（）()]/g, '') === titleNormalized.replace(/[（）()]/g, '')) {
          text = text.replace(/^# .+\n+/, '');
        }
      }
    }

    // Extract headings for TOC and add IDs
    let headingId = 0;
    const addHeading = (level, title) => {
      const id = `heading-${headingId++}`;
      this.headings.push({ level, title, id });
      return id;
    };

    // Parse tables first and store them with placeholders
    const tables = [];
    text = text.replace(/^\|(.+)\|\s*\n\|[-:\s|]+\|\s*\n((?:\|.+\|\s*\n?)+)/gm, (match) => {
      const placeholder = `__TABLE_${tables.length}__`;
      tables.push(this.parseTable(match));
      return placeholder;
    });

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

      // Headers with IDs for TOC
      .replace(/^#### (.+)$/gm, (_, title) => {
        const id = addHeading(4, title);
        return `<h4 id="${id}">${title}</h4>`;
      })
      .replace(/^### (.+)$/gm, (_, title) => {
        const id = addHeading(3, title);
        return `<h3 id="${id}">${title}</h3>`;
      })
      .replace(/^## (.+)$/gm, (_, title) => {
        const id = addHeading(2, title);
        return `<h2 id="${id}">${title}</h2>`;
      })
      .replace(/^# (.+)$/gm, (_, title) => {
        const id = addHeading(1, title);
        return `<h1 id="${id}">${title}</h1>`;
      })

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

    // Restore tables
    tables.forEach((tableHtml, i) => {
      html = html.replace(`__TABLE_${i}__`, tableHtml);
    });

    return html;
  },

  // Generate TOC HTML from extracted headings
  generateTOC() {
    if (this.headings.length === 0) return '';

    // Only include H2 and H3 for cleaner TOC
    const tocItems = this.headings.filter(h => h.level === 2 || h.level === 3);
    if (tocItems.length < 2) return ''; // No TOC if less than 2 headings

    let html = '<nav class="toc"><div class="toc-title">目录</div><ul class="toc-list">';
    tocItems.forEach(h => {
      const indent = h.level === 3 ? ' toc-indent' : '';
      // Clean the title (remove HTML entities that were escaped)
      const cleanTitle = h.title
        .replace(/&lt;/g, '<')
        .replace(/&gt;/g, '>')
        .replace(/&amp;/g, '&')
        .replace(/<[^>]+>/g, ''); // Remove any HTML tags
      html += `<li class="toc-item${indent}"><a href="#${h.id}">${cleanTitle}</a></li>`;
    });
    html += '</ul></nav>';
    return html;
  },

  // Parse a single markdown table
  parseTable(tableText) {
    const lines = tableText.trim().split('\n');
    if (lines.length < 3) return tableText; // Need at least header, separator, and one row

    // Parse header (first line)
    const headers = lines[0].split('|').map(h => h.trim()).filter(h => h);

    // Skip separator line (second line)
    // Parse body rows (remaining lines)
    const rows = lines.slice(2).map(row => {
      return row.split('|').map(cell => cell.trim()).filter(cell => cell !== '');
    });

    // Build HTML table
    let html = '<table>\n<thead>\n<tr>\n';
    headers.forEach(h => {
      html += `<th>${h}</th>\n`;
    });
    html += '</tr>\n</thead>\n<tbody>\n';

    rows.forEach(row => {
      html += '<tr>\n';
      row.forEach(cell => {
        html += `<td>${cell}</td>\n`;
      });
      html += '</tr>\n';
    });

    html += '</tbody>\n</table>';
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

    // Delete button
    $('#doc-delete')?.addEventListener('click', () => this.deleteDoc());
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
      <div class="doc-card" onclick="ui.viewDoc(${doc.id})" onmouseenter="api.preload(${doc.id})">
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

    // Preload first 3 documents immediately for faster initial navigation
    state.docs.slice(0, 3).forEach(doc => api.preload(doc.id));
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

      // Parse markdown with title to remove duplicate H1
      const contentHtml = md.parse(state.currentDoc.content, { title: state.currentDoc.title });
      const tocHtml = md.generateTOC();

      // Render content
      $('#doc-view-content').innerHTML = contentHtml;

      // Render TOC to sidebar (if element exists)
      const tocEl = $('#doc-toc');
      if (tocEl) {
        tocEl.innerHTML = tocHtml;
      }

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

  async deleteDoc() {
    if (!state.currentDoc) return;

    const confirmed = confirm(`确定要删除「${state.currentDoc.title}」吗？\n\n此操作不可撤销。`);
    if (!confirmed) return;

    try {
      const res = await api.deleteDoc(state.currentDoc.id);
      if (res.success) {
        this.showList();
        this.loadData(); // Refresh list
      } else {
        alert('删除失败: ' + (res.error || 'Unknown error'));
      }
    } catch (err) {
      console.error('Failed to delete doc:', err);
      alert('删除失败: ' + err.message);
    }
  },

  filterCategory(category) {
    state.filter.category = category;
    state.filter.tag = null;
    this.showList();
    this.renderCategories();
    this.renderTags();
    this.loadDocs();
    this.closeSidebar();
  },

  filterTag(tag) {
    state.filter.tag = state.filter.tag === tag ? null : tag;
    state.filter.category = null;
    this.showList();
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
