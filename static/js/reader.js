/**
 * Kinh Thánh Công Giáo - Reading Engine & Interactive Toolbar
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. THEME & FONT INITIALIZATION
  const savedTheme = localStorage.getItem('catholic-bible-theme') || 'sepia';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemePillActive(savedTheme);

  const savedFontSize = localStorage.getItem('catholic-bible-font-size') || '18px';
  document.documentElement.style.setProperty('--font-size-verse', savedFontSize);

  const savedFontFamily = localStorage.getItem('catholic-bible-font-family') || 'serif';
  applyFontFamily(savedFontFamily);

  // 2. THEME CONTROLS
  document.querySelectorAll('.theme-pill').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const theme = e.target.getAttribute('data-set-theme');
      if (theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('catholic-bible-theme', theme);
        updateThemePillActive(theme);
      }
    });
  });

  function updateThemePillActive(theme) {
    document.querySelectorAll('.theme-pill').forEach(btn => {
      if (btn.getAttribute('data-set-theme') === theme) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  // 3. FONT SIZE CONTROLS
  const fontSizes = ['16px', '18px', '21px', '24px'];
  let currentFontIdx = fontSizes.indexOf(savedFontSize);
  if (currentFontIdx === -1) currentFontIdx = 1;

  const btnFontDecrease = document.getElementById('btn-font-decrease');
  const btnFontIncrease = document.getElementById('btn-font-increase');

  if (btnFontDecrease) {
    btnFontDecrease.addEventListener('click', () => {
      if (currentFontIdx > 0) {
        currentFontIdx--;
        const size = fontSizes[currentFontIdx];
        document.documentElement.style.setProperty('--font-size-verse', size);
        localStorage.setItem('catholic-bible-font-size', size);
      }
    });
  }

  if (btnFontIncrease) {
    btnFontIncrease.addEventListener('click', () => {
      if (currentFontIdx < fontSizes.length - 1) {
        currentFontIdx++;
        const size = fontSizes[currentFontIdx];
        document.documentElement.style.setProperty('--font-size-verse', size);
        localStorage.setItem('catholic-bible-font-size', size);
      }
    });
  }

  // Font family toggle
  const btnFontFamily = document.getElementById('btn-font-family');
  if (btnFontFamily) {
    btnFontFamily.addEventListener('click', () => {
      const current = localStorage.getItem('catholic-bible-font-family') || 'serif';
      const next = current === 'serif' ? 'sans' : 'serif';
      applyFontFamily(next);
      localStorage.setItem('catholic-bible-font-family', next);
    });
  }

  function applyFontFamily(fam) {
    if (fam === 'sans') {
      document.documentElement.style.setProperty('--font-body', "var(--font-ui)");
    } else {
      document.documentElement.style.setProperty('--font-body', "'Lora', 'Merriweather', 'Georgia', serif");
    }
  }

  // 4. VERSE INTERACTION & FLOATING MENU
  const actionBar = document.getElementById('verse-action-bar');
  let selectedVerseId = null;
  let selectedVerseElement = null;
  let selectedVerseText = '';
  let selectedVerseRef = '';

  const isAuthenticated = document.body.getAttribute('data-auth') === 'true';

  document.querySelectorAll('.verse-item').forEach(el => {
    el.addEventListener('click', (e) => {
      e.stopPropagation();
      selectedVerseElement = el;
      selectedVerseId = el.getAttribute('data-verse-id');
      selectedVerseText = el.getAttribute('data-verse-text') || el.innerText;
      selectedVerseRef = el.getAttribute('data-verse-ref') || '';

      // Highlight selected verse visually with outline
      document.querySelectorAll('.verse-item').forEach(v => v.style.outline = 'none');
      el.style.outline = '2px dashed var(--accent)';

      // Show action bar
      if (actionBar) {
        actionBar.classList.add('active');
      }
    });
  });

  // Clicking outside deselects
  document.addEventListener('click', (e) => {
    if (actionBar && !actionBar.contains(e.target) && !e.target.classList.contains('verse-item')) {
      actionBar.classList.remove('active');
      if (selectedVerseElement) {
        selectedVerseElement.style.outline = 'none';
      }
      selectedVerseId = null;
      selectedVerseElement = null;
    }
  });

  // Highlight actions
  document.querySelectorAll('.action-color-dot').forEach(dot => {
    dot.addEventListener('click', async () => {
      if (!selectedVerseId) return;
      if (!isAuthenticated) {
        showGuestLoginModal();
        return;
      }
      const color = dot.getAttribute('data-color');
      try {
        const res = await fetch(`/api/highlight/${selectedVerseId}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: `color=${color}`
        });
        const data = await res.json();
        if (data.success) {
          if (color === 'none') {
            selectedVerseElement.removeAttribute('data-highlight');
          } else {
            selectedVerseElement.setAttribute('data-highlight', color);
          }
        }
      } catch (err) {
        console.error(err);
      }
    });
  });

  // Bookmark action
  const btnBookmark = document.getElementById('action-bookmark');
  if (btnBookmark) {
    btnBookmark.addEventListener('click', async () => {
      if (!selectedVerseId) return;
      if (!isAuthenticated) {
        showGuestLoginModal();
        return;
      }
      try {
        const res = await fetch(`/api/bookmark/${selectedVerseId}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCsrfToken(),
          }
        });
        const data = await res.json();
        if (data.success) {
          if (data.saved) {
            selectedVerseElement.classList.add('has-bookmark');
            showToast('Đã thêm vào mục Đánh dấu của bạn!');
          } else {
            selectedVerseElement.classList.remove('has-bookmark');
            showToast('Đã xóa khỏi mục Đánh dấu.');
          }
        }
      } catch (err) {
        console.error(err);
      }
    });
  }

  // Note action
  const btnNote = document.getElementById('action-note');
  const noteModal = document.getElementById('note-modal');
  const noteInput = document.getElementById('note-modal-input');
  const btnSaveNote = document.getElementById('btn-save-note');

  if (btnNote && noteModal) {
    btnNote.addEventListener('click', () => {
      if (!selectedVerseId) return;
      if (!isAuthenticated) {
        showGuestLoginModal();
        return;
      }
      // Prefill note if any
      const existing = selectedVerseElement.getAttribute('data-note') || '';
      if (noteInput) noteInput.value = existing;
      noteModal.classList.add('active');
    });
  }

  if (btnSaveNote && noteInput) {
    btnSaveNote.addEventListener('click', async () => {
      if (!selectedVerseId) return;
      const content = noteInput.value.trim();
      try {
        const res = await fetch(`/api/note/${selectedVerseId}/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: `content=${encodeURIComponent(content)}`
        });
        const data = await res.json();
        if (data.success) {
          if (content) {
            selectedVerseElement.classList.add('has-note');
            selectedVerseElement.setAttribute('data-note', content);
          } else {
            selectedVerseElement.classList.remove('has-note');
            selectedVerseElement.removeAttribute('data-note');
          }
          noteModal.classList.remove('active');
          showToast('Đã lưu ghi chú cá nhân thành công!');
        }
      } catch (err) {
        console.error(err);
      }
    });
  }

  // Share action
  const btnShare = document.getElementById('action-share');
  const shareModal = document.getElementById('share-modal');
  const sharePreviewText = document.getElementById('share-quote-text');
  const sharePreviewRef = document.getElementById('share-quote-ref');

  if (btnShare && shareModal) {
    btnShare.addEventListener('click', () => {
      if (!selectedVerseId) return;
      if (sharePreviewText) sharePreviewText.innerText = `“${selectedVerseText}”`;
      if (sharePreviewRef) sharePreviewRef.innerText = selectedVerseRef;
      shareModal.classList.add('active');
    });
  }

  // Copy quote text to clipboard
  const btnCopyQuote = document.getElementById('btn-copy-quote');
  if (btnCopyQuote) {
    btnCopyQuote.addEventListener('click', () => {
      const fullQuote = `“${selectedVerseText}” (${selectedVerseRef}) - Kinh Thánh Công Giáo (Bản dịch CGKPV)`;
      navigator.clipboard.writeText(fullQuote).then(() => {
        showToast('Đã sao chép câu Lời Chúa vào bộ nhớ đệm!');
      });
    });
  }

  // Modal Closers
  document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
    });
  });

  // Guest Login Modal helper
  window.showGuestLoginModal = function() {
    const m = document.getElementById('guest-limit-modal');
    if (m) m.classList.add('active');
  };

  function showToast(message) {
    let toast = document.getElementById('reader-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'reader-toast';
      toast.style.cssText = 'position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:var(--accent);color:#fff;padding:10px 20px;border-radius:30px;font-size:14px;box-shadow:0 6px 20px rgba(0,0,0,0.2);z-index:9999;transition:opacity 0.3s ease, transform 0.3s ease;font-weight:600;pointer-events:none;';
      document.body.appendChild(toast);
    }
    toast.innerText = message;
    toast.style.opacity = '1';
    toast.style.transform = 'translateX(-50%) translateY(0)';
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(-50%) translateY(10px)';
    }, 2500);
  }

  function getCsrfToken() {
    const meta = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (meta && meta.value) return meta.value;
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
  }
});
