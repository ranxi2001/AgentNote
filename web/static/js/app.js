/**
 * AgentNote Web UI - Frontend Application
 * Chat-first interface with Notion-inspired design
 */

// === State Management ===
const state = {
  currentView: 'chat',
  currentCategory: null,
  ideas: [],
  recentIdeas: [],
  categories: [],
  messages: [],
  isDarkMode: false
};

// === DOM Elements ===
const elements = {
  sidebar: null,
  sidebarOverlay: null,
  menuToggle: null,
  themeToggle: null,
  viewToggle: null,
  chatView: null,
  ideasView: null,
  chatMessages: null,
  chatInput: null,
  chatSendBtn: null,
  ideasGrid: null,
  categoryNav: null,
  recentList: null,
  modalOverlay: null,
  toastContainer: null
};

// === API Functions ===
const api = {
  async getIdeas(params = {}) {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`/api/ideas?${query}`);
    return res.json();
  },

  async getIdea(id) {
    const res = await fetch(`/api/ideas/${id}`);
    return res.json();
  },

  async addIdea(data) {
    const res = await fetch('/api/ideas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  async updateIdea(id, data) {
    const res = await fetch(`/api/ideas/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return res.json();
  },

  async deleteIdea(id) {
    const res = await fetch(`/api/ideas/${id}`, {
      method: 'DELETE'
    });
    return res.json();
  },

  async getCategories() {
    const res = await fetch('/api/categories');
    return res.json();
  },

  async getRecent(limit = 5) {
    const res = await fetch(`/api/recent?limit=${limit}`);
    return res.json();
  },

  async sendChat(message) {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });
    return res.json();
  }
};

// === UI Functions ===
const ui = {
  init() {
    // Cache DOM elements
    elements.sidebar = document.getElementById('sidebar');
    elements.sidebarOverlay = document.getElementById('sidebar-overlay');
    elements.menuToggle = document.getElementById('menu-toggle');
    elements.themeToggle = document.getElementById('theme-toggle');
    elements.chatView = document.getElementById('chat-view');
    elements.ideasView = document.getElementById('ideas-view');
    elements.chatMessages = document.getElementById('chat-messages');
    elements.chatInput = document.getElementById('chat-input');
    elements.chatSendBtn = document.getElementById('chat-send-btn');
    elements.ideasGrid = document.getElementById('ideas-grid');
    elements.categoryNav = document.getElementById('category-nav');
    elements.recentList = document.getElementById('recent-list');
    elements.modalOverlay = document.getElementById('modal-overlay');
    elements.toastContainer = document.getElementById('toast-container');

    // Bind events
    this.bindEvents();

    // Load initial data
    this.loadInitialData();

    // Check theme preference
    this.loadTheme();
  },

  bindEvents() {
    // Menu toggle
    elements.menuToggle?.addEventListener('click', () => this.toggleSidebar());
    elements.sidebarOverlay?.addEventListener('click', () => this.closeSidebar());

    // Theme toggle
    elements.themeToggle?.addEventListener('click', () => this.toggleTheme());

    // Chat input
    elements.chatInput?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    elements.chatSendBtn?.addEventListener('click', () => this.sendMessage());

    // Auto-resize textarea
    elements.chatInput?.addEventListener('input', () => {
      elements.chatInput.style.height = 'auto';
      elements.chatInput.style.height = elements.chatInput.scrollHeight + 'px';
    });

    // View toggle buttons
    document.querySelectorAll('[data-view]').forEach(btn => {
      btn.addEventListener('click', () => this.switchView(btn.dataset.view));
    });

    // Category nav
    document.querySelectorAll('[data-category]').forEach(btn => {
      btn.addEventListener('click', () => this.filterByCategory(btn.dataset.category));
    });

    // Modal close
    document.querySelectorAll('[data-modal-close]').forEach(btn => {
      btn.addEventListener('click', () => this.closeModal());
    });

    // Chat hints
    document.querySelectorAll('.chat-hint').forEach(hint => {
      hint.addEventListener('click', () => {
        elements.chatInput.value = hint.textContent;
        elements.chatInput.focus();
      });
    });

    // Add idea button
    document.getElementById('add-idea-btn')?.addEventListener('click', () => this.openAddModal());
  },

  async loadInitialData() {
    try {
      // Load categories
      const catRes = await api.getCategories();
      if (catRes.success) {
        state.categories = catRes.data;
        this.renderCategories();
      }

      // Load recent ideas
      const recentRes = await api.getRecent(5);
      if (recentRes.success) {
        state.recentIdeas = recentRes.data;
        this.renderRecentIdeas();
      }

      // Load all ideas for grid view
      const ideasRes = await api.getIdeas({ limit: 50 });
      if (ideasRes.success) {
        state.ideas = ideasRes.data;
        this.renderIdeasGrid();
      }
    } catch (err) {
      console.error('Failed to load initial data:', err);
      this.showToast('Failed to load data', 'error');
    }
  },

  // === Sidebar ===
  toggleSidebar() {
    elements.sidebar?.classList.toggle('open');
    elements.sidebarOverlay?.classList.toggle('active');
  },

  closeSidebar() {
    elements.sidebar?.classList.remove('open');
    elements.sidebarOverlay?.classList.remove('active');
  },

  // === Theme ===
  loadTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.setAttribute('data-theme', 'dark');
      state.isDarkMode = true;
      this.updateThemeIcon();
    }
  },

  toggleTheme() {
    state.isDarkMode = !state.isDarkMode;
    if (state.isDarkMode) {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('theme', 'light');
    }
    this.updateThemeIcon();
  },

  updateThemeIcon() {
    const icon = elements.themeToggle?.querySelector('svg use');
    if (icon) {
      icon.setAttribute('href', `#icon-${state.isDarkMode ? 'sun' : 'moon'}`);
    }
  },

  // === Views ===
  switchView(view) {
    state.currentView = view;

    // Update toggle buttons
    document.querySelectorAll('[data-view]').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.view === view);
    });

    // Show/hide views
    if (view === 'chat') {
      elements.chatView?.classList.add('active');
      elements.ideasView?.classList.remove('active');
    } else {
      elements.chatView?.classList.remove('active');
      elements.ideasView?.classList.add('active');
      this.loadIdeas();
    }

    this.closeSidebar();
  },

  // === Chat ===
  async sendMessage() {
    const message = elements.chatInput?.value.trim();
    if (!message) return;

    // Add user message
    this.addMessage(message, 'user');
    elements.chatInput.value = '';
    elements.chatInput.style.height = 'auto';

    // Disable input while processing
    elements.chatSendBtn.disabled = true;

    try {
      const res = await api.sendChat(message);

      if (res.success) {
        // Handle different response types
        if (res.type === 'search' || res.type === 'list') {
          this.addMessage(res.response, 'assistant');
          if (res.data && res.data.length > 0) {
            this.addIdeaListMessage(res.data);
          }
        } else if (res.type === 'action' && res.action === 'add') {
          this.addMessage(res.response, 'assistant');
          // Refresh data
          this.loadInitialData();
        } else {
          this.addMessage(res.response, 'assistant');
        }
      } else {
        this.addMessage(res.error || 'Something went wrong', 'assistant');
      }
    } catch (err) {
      console.error('Chat error:', err);
      this.addMessage('Failed to process message', 'assistant');
    } finally {
      elements.chatSendBtn.disabled = false;
    }
  },

  addMessage(content, role) {
    const message = { content, role, timestamp: new Date() };
    state.messages.push(message);

    const messageEl = document.createElement('div');
    messageEl.className = `message message-${role}`;
    messageEl.innerHTML = `
      <div class="message-avatar">${role === 'user' ? 'U' : 'A'}</div>
      <div class="message-content">${this.escapeHtml(content).replace(/\n/g, '<br>')}</div>
    `;

    elements.chatMessages?.appendChild(messageEl);
    elements.chatMessages?.scrollTo(0, elements.chatMessages.scrollHeight);
  },

  addIdeaListMessage(ideas) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message message-assistant';

    const ideasHtml = ideas.map(idea => `
      <div class="idea-card" onclick="ui.viewIdea(${idea.id})" style="margin: 8px 0; padding: 12px;">
        <div class="idea-card-title">${this.escapeHtml(idea.title)}</div>
        <div class="idea-card-content">${this.escapeHtml(idea.content?.substring(0, 100) || '')}...</div>
        ${idea.category ? `<span class="idea-card-category">${this.escapeHtml(idea.category)}</span>` : ''}
      </div>
    `).join('');

    messageEl.innerHTML = `
      <div class="message-avatar">A</div>
      <div class="message-content" style="padding: 0; background: none;">
        ${ideasHtml}
      </div>
    `;

    elements.chatMessages?.appendChild(messageEl);
    elements.chatMessages?.scrollTo(0, elements.chatMessages.scrollHeight);
  },

  // === Categories ===
  renderCategories() {
    if (!elements.categoryNav) return;

    const totalCount = state.ideas.length || state.categories.reduce((sum, c) => sum + c.count, 0);

    let html = `
      <div class="nav-item ${!state.currentCategory ? 'active' : ''}" data-category="" onclick="ui.filterByCategory('')">
        <svg class="nav-item-icon"><use href="#icon-inbox"></use></svg>
        <span>All</span>
        <span class="nav-item-count">${totalCount}</span>
      </div>
    `;

    state.categories.forEach(cat => {
      html += `
        <div class="nav-item ${state.currentCategory === cat.category ? 'active' : ''}"
             data-category="${this.escapeHtml(cat.category)}"
             onclick="ui.filterByCategory('${this.escapeHtml(cat.category)}')">
          <svg class="nav-item-icon"><use href="#icon-folder"></use></svg>
          <span>${this.escapeHtml(cat.category)}</span>
          <span class="nav-item-count">${cat.count}</span>
        </div>
      `;
    });

    elements.categoryNav.innerHTML = html;
  },

  async filterByCategory(category) {
    state.currentCategory = category || null;

    // Update active state
    document.querySelectorAll('[data-category]').forEach(el => {
      el.classList.toggle('active', el.dataset.category === category);
    });

    // Load filtered ideas
    await this.loadIdeas();
    this.closeSidebar();
  },

  // === Recent Ideas ===
  renderRecentIdeas() {
    if (!elements.recentList) return;

    if (state.recentIdeas.length === 0) {
      elements.recentList.innerHTML = '<div class="recent-item" style="color: var(--text-muted);">No ideas yet</div>';
      return;
    }

    elements.recentList.innerHTML = state.recentIdeas.map(idea => `
      <div class="recent-item" onclick="ui.viewIdea(${idea.id})">
        ${this.escapeHtml(idea.title)}
      </div>
    `).join('');
  },

  // === Ideas Grid ===
  async loadIdeas() {
    try {
      const params = { limit: 50 };
      if (state.currentCategory) {
        params.category = state.currentCategory;
      }

      const res = await api.getIdeas(params);
      if (res.success) {
        state.ideas = res.data;
        this.renderIdeasGrid();
      }
    } catch (err) {
      console.error('Failed to load ideas:', err);
    }
  },

  renderIdeasGrid() {
    if (!elements.ideasGrid) return;

    if (state.ideas.length === 0) {
      elements.ideasGrid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <div class="empty-state-icon">💡</div>
          <div class="empty-state-title">No ideas yet</div>
          <div class="empty-state-text">Start a conversation to capture your first idea</div>
        </div>
      `;
      return;
    }

    elements.ideasGrid.innerHTML = state.ideas.map(idea => `
      <div class="idea-card" onclick="ui.viewIdea(${idea.id})">
        <div class="idea-card-header">
          <div class="idea-card-title">${this.escapeHtml(idea.title)}</div>
          <button class="header-btn idea-card-menu" onclick="event.stopPropagation(); ui.showIdeaMenu(${idea.id})">
            <svg width="16" height="16"><use href="#icon-more"></use></svg>
          </button>
        </div>
        <div class="idea-card-content">${this.escapeHtml(idea.content || '')}</div>
        <div class="idea-card-footer">
          ${idea.category ? `<span class="idea-card-category">${this.escapeHtml(idea.category)}</span>` : '<span></span>'}
          <span class="idea-card-date">${this.formatDate(idea.created_at)}</span>
        </div>
      </div>
    `).join('');
  },

  // === Modal ===
  async viewIdea(id) {
    try {
      const res = await api.getIdea(id);
      if (!res.success) {
        this.showToast('Idea not found', 'error');
        return;
      }

      const idea = res.data;
      this.openModal('View Idea', `
        <div class="form-group">
          <label class="form-label">Title</label>
          <input type="text" class="form-input" id="modal-title" value="${this.escapeHtml(idea.title)}">
        </div>
        <div class="form-group">
          <label class="form-label">Category</label>
          <input type="text" class="form-input" id="modal-category" value="${this.escapeHtml(idea.category || '')}">
        </div>
        <div class="form-group">
          <label class="form-label">Content</label>
          <textarea class="form-input form-textarea" id="modal-content">${this.escapeHtml(idea.content)}</textarea>
        </div>
        <div class="form-group">
          <label class="form-label">Keywords</label>
          <input type="text" class="form-input" id="modal-keywords" value="${(idea.keywords || []).join(', ')}" placeholder="Comma separated">
        </div>
      `, [
        { label: 'Delete', class: 'btn-secondary', action: () => this.deleteIdea(id) },
        { label: 'Save', class: 'btn-primary', action: () => this.saveIdea(id) }
      ]);
    } catch (err) {
      console.error('Failed to load idea:', err);
      this.showToast('Failed to load idea', 'error');
    }
  },

  openAddModal() {
    this.openModal('Add Idea', `
      <div class="form-group">
        <label class="form-label">Title</label>
        <input type="text" class="form-input" id="modal-title" placeholder="Enter title">
      </div>
      <div class="form-group">
        <label class="form-label">Category</label>
        <input type="text" class="form-input" id="modal-category" placeholder="e.g., Productivity, AI, Coding">
      </div>
      <div class="form-group">
        <label class="form-label">Content</label>
        <textarea class="form-input form-textarea" id="modal-content" placeholder="Describe your idea..."></textarea>
      </div>
      <div class="form-group">
        <label class="form-label">Keywords</label>
        <input type="text" class="form-input" id="modal-keywords" placeholder="Comma separated">
      </div>
    `, [
      { label: 'Cancel', class: 'btn-secondary', action: () => this.closeModal() },
      { label: 'Add', class: 'btn-primary', action: () => this.addNewIdea() }
    ]);
  },

  openModal(title, content, buttons = []) {
    const modal = elements.modalOverlay?.querySelector('.modal');
    if (!modal) return;

    modal.querySelector('.modal-title').textContent = title;
    modal.querySelector('.modal-body').innerHTML = content;

    const footer = modal.querySelector('.modal-footer');
    footer.innerHTML = buttons.map(btn => `
      <button class="btn ${btn.class}" data-action="${btn.label}">${btn.label}</button>
    `).join('');

    buttons.forEach(btn => {
      footer.querySelector(`[data-action="${btn.label}"]`)?.addEventListener('click', btn.action);
    });

    elements.modalOverlay?.classList.add('active');
  },

  closeModal() {
    elements.modalOverlay?.classList.remove('active');
  },

  async saveIdea(id) {
    const data = {
      title: document.getElementById('modal-title')?.value,
      content: document.getElementById('modal-content')?.value,
      category: document.getElementById('modal-category')?.value || null,
      keywords: document.getElementById('modal-keywords')?.value.split(',').map(k => k.trim()).filter(k => k)
    };

    if (!data.title || !data.content) {
      this.showToast('Title and content are required', 'error');
      return;
    }

    try {
      const res = await api.updateIdea(id, data);
      if (res.success) {
        this.showToast('Idea updated', 'success');
        this.closeModal();
        this.loadInitialData();
      } else {
        this.showToast(res.error || 'Failed to update', 'error');
      }
    } catch (err) {
      this.showToast('Failed to update idea', 'error');
    }
  },

  async addNewIdea() {
    const data = {
      title: document.getElementById('modal-title')?.value,
      content: document.getElementById('modal-content')?.value,
      category: document.getElementById('modal-category')?.value || null,
      keywords: document.getElementById('modal-keywords')?.value.split(',').map(k => k.trim()).filter(k => k)
    };

    if (!data.title || !data.content) {
      this.showToast('Title and content are required', 'error');
      return;
    }

    try {
      const res = await api.addIdea(data);
      if (res.success) {
        this.showToast('Idea added', 'success');
        this.closeModal();
        this.loadInitialData();
      } else {
        this.showToast(res.error || 'Failed to add', 'error');
      }
    } catch (err) {
      this.showToast('Failed to add idea', 'error');
    }
  },

  async deleteIdea(id) {
    if (!confirm('Are you sure you want to delete this idea?')) return;

    try {
      const res = await api.deleteIdea(id);
      if (res.success) {
        this.showToast('Idea deleted', 'success');
        this.closeModal();
        this.loadInitialData();
      } else {
        this.showToast(res.error || 'Failed to delete', 'error');
      }
    } catch (err) {
      this.showToast('Failed to delete idea', 'error');
    }
  },

  showIdeaMenu(id) {
    // Simple implementation - could be enhanced with a dropdown menu
    if (confirm('Delete this idea?')) {
      this.deleteIdea(id);
    }
  },

  // === Toast ===
  showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span class="toast-message">${this.escapeHtml(message)}</span>`;

    elements.toastContainer?.appendChild(toast);

    setTimeout(() => {
      toast.remove();
    }, 3000);
  },

  // === Utilities ===
  escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  },

  formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;

    // Today
    if (diff < 86400000 && date.getDate() === now.getDate()) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    // This week
    if (diff < 604800000) {
      return date.toLocaleDateString([], { weekday: 'short' });
    }

    // Older
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
  }
};

// === Initialize on DOM ready ===
document.addEventListener('DOMContentLoaded', () => ui.init());

// Make ui globally accessible for onclick handlers
window.ui = ui;
