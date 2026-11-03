(function () {
  'use strict';

  // ---- Configuration via script tag data-attributes ----
  var currentScript = document.currentScript || (function () {
    var scripts = document.getElementsByTagName('script');
    return scripts[scripts.length - 1];
  })();

  if (!currentScript) {
    console.warn('[NewsBanner] Could not find current <script> element.');
    return;
  }

  var dataset = currentScript.dataset || {};
  var SPACE_ID = dataset.contentfulSpace;
  var ENV_ID = dataset.contentfulEnv || 'master';
  var ACCESS_TOKEN = dataset.contentfulAccessToken;

  if (!SPACE_ID || !ACCESS_TOKEN) {
    console.warn('[NewsBanner] Missing Contentful config.');
    return;
  }

  var STORAGE_KEY = 'newsBannerState';
  var ONE_WEEK_MS = 7 * 24 * 60 * 60 * 1000;

  // ---------------------------------------------------------
  // LocalStorage helpers
  // ---------------------------------------------------------
  function getStoredState() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (_) {
      return null;
    }
  }

  function saveState(state) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (_) {}
  }

  function shouldShowBanner(contentSignature) {
    var state = getStoredState();
    if (!state) return true;

    var lastShown = new Date(state.lastShownAt).getTime();
    if (isNaN(lastShown)) return true;

    // Content changed → show again
    if (state.contentSignature !== contentSignature) return true;

    // Over one week → show again
    if (Date.now() - lastShown > ONE_WEEK_MS) return true;

    return false;
  }

  // ---------------------------------------------------------
  // Markdown parser — safe subset (bold, italics, links)
  // ---------------------------------------------------------
  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function markdownToHtml(md) {
    if (!md) return '';

    var html = escapeHtml(md);

    // Links: [text](url)
    html = html.replace(
      /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer" style="color:#00c0b5;text-decoration:underline;">$1</a>'
    );

    // Bold
    html = html.replace(/(\*\*|__)(.+?)\1/g, '<strong>$2</strong>');

    // Italic
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

    // Newlines → <br>
    html = html.replace(/\n{2,}/g, '<br><br>');
    html = html.replace(/\n/g, '<br>');

    return html;
  }

  // ---------------------------------------------------------
  // Create Banner Element (styled for RF / RoboCon)
  // ---------------------------------------------------------
  function createBanner(messageHtml, onClose) {
    var el = document.createElement('div');
    el.setAttribute('role', 'status');
    el.setAttribute('aria-live', 'polite');
    el.setAttribute('aria-label', 'News announcement');

    // Outer positioning
    el.style.position = 'fixed';
    el.style.left = '16px';
    el.style.right = '16px';
    el.style.bottom = '16px';
    el.style.zIndex = '9999';
    el.style.display = 'flex';
    el.style.justifyContent = 'center';
    el.style.pointerEvents = 'none'; // outer wrapper, inner content handles clicks

    var inner = document.createElement('div');
    inner.style.pointerEvents = 'auto';

    // Inner box
    inner.style.display = 'flex';
    inner.style.alignItems = 'flex-start';
    inner.style.gap = '12px';
    inner.style.width = '100%';
    inner.style.maxWidth = '960px';

    inner.style.padding = '14px 18px';
    inner.style.boxSizing = 'border-box';

    // Dark, slightly transparent background so it sits on top of both light & dark sections
    inner.style.background = 'rgba(15,23,42,0.92)'; // slate-900-ish
    inner.style.border = '1px solid #00c0b5'; // slate-400-ish
    inner.style.color = '#E5E7EB'; // slate-200
    inner.style.boxShadow = '0 18px 45px rgba(0,0,0,0.55)';

    inner.style.fontFamily = 'system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif';
    inner.style.fontSize = '1rem';
    inner.style.lineHeight = '1.5';

    // Slide-in transition
    inner.style.transform = 'translateY(120%)';
    inner.style.opacity = '0';
    inner.style.transition = 'transform .3s ease-out, opacity .3s ease-out';

    // Text
    var text = document.createElement('div');
    text.innerHTML = messageHtml;
    text.style.flex = '1 1 auto';
    text.style.marginRight = '4px';
    text.style.maxHeight = '6.5rem';
    text.style.overflowY = 'auto';

    // Close button
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.setAttribute('aria-label', 'Close announcement');
    btn.innerHTML = '&times;';
    btn.style.flex = '0 0 auto';
    btn.style.fontSize = '24px';
    btn.style.border = 'none';
    btn.style.background = 'transparent';
    btn.style.color = '#9CA3AF';
    btn.style.cursor = 'pointer';
    btn.style.lineHeight = '1';
    btn.style.alignSelf = 'center';

    btn.onmouseenter = function () {
      btn.style.color = '#F9FAFB';
    };
    btn.onmouseleave = function () {
      btn.style.color = '#9CA3AF';
    };

    btn.onclick = function () {
      if (onClose) onClose();

      inner.style.transform = 'translateY(120%)';
      inner.style.opacity = '0';

      inner.addEventListener('transitionend', function () {
        el.remove();
      }, { once: true });

      setTimeout(function () {
        if (el.parentNode) el.parentNode.removeChild(el);
      }, 500);
    };

    inner.appendChild(text);
    inner.appendChild(btn);
    el.appendChild(inner);

    // Mobile tweaks (edge-to-edge bar at bottom)
    function applyResponsive() {
      var isMobile = window.matchMedia && window.matchMedia('(max-width: 640px)').matches;
      if (isMobile) {
        el.style.left = '0';
        el.style.right = '0';
        el.style.bottom = '0';
        inner.style.borderRadius = '0';
        inner.style.maxWidth = '100%';
        inner.style.boxShadow = '0 -8px 25px rgba(0,0,0,0.65)';
      } else {
        el.style.left = '16px';
        el.style.right = '16px';
        el.style.bottom = '16px';
        inner.style.maxWidth = '960px';
        inner.style.boxShadow = '0 18px 45px rgba(0,0,0,0.55)';
      }
    }

    applyResponsive();
    if (window.matchMedia) {
      window.matchMedia('(max-width: 640px)').addEventListener('change', applyResponsive);
    } else {
      window.addEventListener('resize', applyResponsive);
    }

    // Trigger slide-in
    inner.__show = function () {
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          inner.style.transform = 'translateY(0)';
          inner.style.opacity = '1';
        });
      });
    };

    // store reference for later
    el.__inner = inner;
    return el;
  }

  // ---------------------------------------------------------
  // Rendering
  // ---------------------------------------------------------
  function renderBanner(text, contentSignature) {
    if (!shouldShowBanner(contentSignature)) return;

    var html = markdownToHtml(text);
    var el = createBanner(html, function () {
      saveState({
        lastShownAt: new Date().toISOString(),
        contentSignature: contentSignature
      });
    });

    var append = function () {
      document.body.appendChild(el);
      if (el.__inner && typeof el.__inner.__show === 'function') {
        el.__inner.__show();
      }
    };

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', append);
    } else {
      append();
    }
  }

  // ---------------------------------------------------------
  // Fetch from Contentful
  // ---------------------------------------------------------
  var url =
    'https://cdn.contentful.com/spaces/' + SPACE_ID +
    '/environments/' + ENV_ID +
    '/entries?content_type=news-banner&limit=1&order=-sys.updatedAt';

  fetch(url, { headers: { Authorization: 'Bearer ' + ACCESS_TOKEN } })
    .then(function (res) { return res.json(); })
    .then(function (data) {
      if (!data.items || !data.items.length) return;

      var entry = data.items[0];
      var fields = entry.fields || {};
      var textField = fields.text;

      var locale =
        typeof textField === 'string'
          ? null
          : (textField ? Object.keys(textField)[0] : null);

      var text =
        typeof textField === 'string'
          ? textField
          : (textField && textField[locale]) || '';

      if (!text) return;

      var signature = text;
      renderBanner(text, signature);
    })
    .catch(function (err) {
      console.warn('[NewsBanner] Failed to load:', err);
    });

})();