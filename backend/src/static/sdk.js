const STYLES = `#sateraito-ai-iframe-panel {
  position: fixed;
  z-index: 10000;
  top: 45px;
  right: 45px;
  min-width: 400px;
  width: 40vw;
  height: 0px;
  border: none;
  overflow: hidden;
  transition: 0.25s all;
  pointer-events: none;
  background-color: var(--search-box-bg-color, #ffffff);
  font-family: var(--theme-font-family-box-search, Arial, sans-serif);
  font-size: var(--search-box-font-size, 16px);
}
#sateraito-ai-iframe-panel.show {
  height: 90vh;
  pointer-events: auto;
  box-shadow: var(--search-box-box-shadow, 0 2px 8px rgba(0, 0, 0, 0.15));
  border: var(--search-box-border-size) solid rgba(0, 0, 0, 0.1);
  border-radius: var(--search-box-border-radius, 10px);
}
#sateraito-ai-iframe-panel.show[data-layout=fullscreen], #sateraito-ai-iframe-panel.show[data-layout=fullscreen_blur] {
  opacity: 1;
  pointer-events: all;
  z-index: 10000;
}
#sateraito-ai-iframe-panel[data-layout=fullscreen], #sateraito-ai-iframe-panel[data-layout=fullscreen_blur] {
  position: absolute;
  max-width: none;
  height: calc(100vh);
  width: calc(100vw - 2px);
  opacity: 0;
  pointer-events: none;
  z-index: -1;
  border-radius: 0;
  top: calc(50% - 1px);
  left: 50%;
  transform: translate(-50%, -50%);
}
#sateraito-ai-iframe-panel[data-layout=fullscreen_blur] {
  -webkit-backdrop-filter: blur(20px);
          backdrop-filter: blur(20px);
  background-color: rgba(255, 255, 255, 0.25);
}
#sateraito-ai-iframe-panel[data-layout=fullscreen_blur] .result-search-container {
  padding: 0 10px;
}

#sateraito-ai-button-panel {
  cursor: pointer;
  z-index: 10001;
  align-items: center;
  justify-content: center;
  border: none;
  overflow: hidden;
  transition: 0.25s all;
  font-size: 18px;
  position: absolute;
  right: calc(20px + var(--search-box-padding, 0px));
  top: calc(20px + var(--search-box-padding, 0px));
  background-color: var(--search-button-bg-color, #fff);
  border-radius: var(--search-button-border-radius);
  color: var(--search-button-color-text, #000);
  fill: var(--search-button-color-text, #000);
}
#sateraito-ai-button-panel img {
  width: 20px;
  height: 20px;
}
#sateraito-ai-button-panel .icon-open,
#sateraito-ai-button-panel .icon-close {
  transition: 0.25s all;
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
#sateraito-ai-button-panel .icon-open {
  opacity: 1;
}
#sateraito-ai-button-panel .icon-close {
  opacity: 0;
}
#sateraito-ai-button-panel::before {
  content: "";
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  background-color: #fff;
  opacity: 0;
  border-radius: inherit;
  z-index: -1;
  transition: 0.25s all;
}
#sateraito-ai-button-panel:hover::before {
  opacity: 0.5;
  z-index: 2;
}
#sateraito-ai-button-panel.show {
  width: 40px;
  height: 40px;
}
#sateraito-ai-button-panel.show-icon-close {
  transform: rotate(-180deg);
}
#sateraito-ai-button-panel.show-icon-close .icon-open {
  opacity: 0;
}
#sateraito-ai-button-panel.show-icon-close .icon-close {
  opacity: 1;
}`;

const CONFIG = {
  // BASE_URL: 'http://localhost:8080',
  // SERVER_URL: 'http://localhost:3000',
  BASE_URL: 'https://aisearch-dot-vn-sateraito-apps-timecard2.appspot.com',
  SERVER_URL: 'https://aisearch-dot-vn-sateraito-apps-timecard2.appspot.com',
  ID_ROOT: 'sateraito-ai-root',
  ID_IFRAME_PANEL: 'sateraito-ai-iframe-panel',
  ID_BUTTON_PANEL: 'sateraito-ai-button-panel',
  DEFAULT_BUTTON_STYLE: {
    // transform: 'scale(0)',
    // opacity: '0',
  }
};

const MyRedis = {
  get: function (key) {
    return localStorage.getItem(key);
  },
  set: function (key, value) {
    localStorage.setItem(key, value);
  },
  remove: function (key) {
    localStorage.removeItem(key);
  }
};

const SateraitoAI = {
  _boxSearchConfig: null,
  _shadowRoot: null,
  _iframePanel: null,

  init: function (config) {
    if (!config || !config.tenant || !config.appId) {
      throw new Error('Missing required config: tenant and appId');
    }
    this._boxSearchConfig = null;
    const cachedConfig = MyRedis.get('box_search_config');
    if (cachedConfig) {
      try {
        this._boxSearchConfig = JSON.parse(cachedConfig);
      } catch (e) {
        this._boxSearchConfig = null;
      }
    }
    this.initShadowRoot();
    this.getStyle(`${CONFIG.BASE_URL}/static/@mdi/font/css/materialdesignicons.min.css`);
    // this.getStyle(`${CONFIG.BASE_URL}/static/box-search-ai/style.css`);
    this.initStyle(STYLES);
    this.initButtonPanel();
    this.initIFramePanel(config);
    this.refreshUI();

    this.initEvents();
  },

  initShadowRoot: function () {
    const rootEl = document.getElementById(CONFIG.ID_ROOT) || document.body;
    this._shadowRoot = rootEl.shadowRoot || rootEl.attachShadow({ mode: 'open' });
  },

  initStyle: function (cssText) {
    if (!this._shadowRoot) {
      this.initShadowRoot();
    }
    const style = document.createElement('style');
    style.textContent = cssText;
    this._shadowRoot.appendChild(style);
  },

  getStyle: function (url) {
    if (!this._shadowRoot) {
      this.initShadowRoot();
    }
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.type = 'text/css';
    link.href = url;
    this._shadowRoot.appendChild(link);
  },

  initIFramePanel: function (config) {
    if (!this._shadowRoot) {
      this.initShadowRoot();
    }
    if (!this._iframePanel) {
      const iframeEl = document.createElement('iframe');
      iframeEl.id = CONFIG.ID_IFRAME_PANEL;
      iframeEl.src = `${CONFIG.SERVER_URL}/${config.tenant}/${config.appId}/box_search`;
      iframeEl.allow = 'clipboard-read; clipboard-write; microphone; camera; autoplay; encrypted-media; fullscreen; display-capture';
      iframeEl.allowFullscreen = true;
      iframeEl.sandbox = 'allow-scripts allow-same-origin allow-forms allow-popups allow-modals';
      this._shadowRoot.appendChild(iframeEl);
      this._iframePanel = iframeEl;
    }
  },

  initButtonPanel: function () {
    if (!this._shadowRoot) {
      this.initShadowRoot();
    }
    let buttonEl = this._shadowRoot.getElementById(CONFIG.ID_BUTTON_PANEL);
    if (!buttonEl) {
      buttonEl = document.createElement('button');
      buttonEl.id = CONFIG.ID_BUTTON_PANEL;
      Object.assign(buttonEl.style, CONFIG.DEFAULT_BUTTON_STYLE);
      this._shadowRoot.appendChild(buttonEl);
    }
  },

  sendMessageToIFrame: function (message) {
    if (this._iframePanel && this._iframePanel.contentWindow) {
      this._iframePanel.contentWindow.postMessage(message, '*');
    } else {
      throw new Error('IFrame panel is not initialized.');
    }
  },

  setLayoutBoxSearch: function (layout) {
    if (!this._iframePanel) {
      throw new Error('IFrame panel is not initialized.');
    }

    // Set attribute 'data-layout' on iframe panel
    this._iframePanel.setAttribute('data-layout', layout);
  },

  setIconButton: function (icon) {
    if (!this._shadowRoot) {
      this.initShadowRoot();
    }
    const buttonEl = this._shadowRoot.getElementById(CONFIG.ID_BUTTON_PANEL);
    if (buttonEl) {
      let vHtml = '';
      if (icon.startsWith('http://') || icon.startsWith('https://')) {
        vHtml = `<img class="icon-open" src="${icon}" alt="Button Icon" />`;
      } else if (icon.trim().startsWith('<svg')) {
        vHtml = `<div class="icon-open">${icon}</div>`;
      } else if (icon.startsWith('mdi')) {
        vHtml = `<span class="icon-open mdi ${icon}"></span>`;
      } else {
        throw new Error('Invalid icon format. Please provide a valid URL, SVG string, or mdi class name.');
      }

      vHtml += '<span class="icon-close mdi mdi-close"></span>';

      buttonEl.classList.add('show');
      buttonEl.innerHTML = vHtml;
    }
  },

  setGlobalVariableCss: function (variable, value) {
    const rootEl = document.getElementById(CONFIG.ID_ROOT) || document.body;
    rootEl.style.setProperty(variable, value);
  },

  refreshUI: function () {
    if (!this._boxSearchConfig) return;
    const { search_box, search_button, theme } = this._boxSearchConfig;
    if (search_box) {
      this.setLayoutBoxSearch(search_box.type);
      this.setGlobalVariableCss('--search-box-bg-color', search_box.options.background_color);
      this.setGlobalVariableCss('--search-box-border-radius', `${search_box.options.border_radius}px`);
      this.setGlobalVariableCss('--search-box-border-size', search_box.options.shadow ? `0px` : '1px');
      this.setGlobalVariableCss('--search-box-padding', `${search_box.options.padding}px`);
      this.setGlobalVariableCss('--search-box-box-shadow', search_box.options.shadow ? '0 2px 8px rgba(0,0,0,0.15)' : 'none');
      this.setGlobalVariableCss('--search-box-font-size', `${search_box.options['font-size'] || 16}px`);
    }
    if (theme) {
      this.setGlobalVariableCss('--theme-color-text-box-search', theme.color);
      this.setGlobalVariableCss('--theme-color-background-box-search', theme.background_color);
      this.setGlobalVariableCss('--theme-font-family-box-search', theme.font);
    }
    if (search_button) {
      this.setGlobalVariableCss('--search-button-color-text', search_button.color);
      this.setGlobalVariableCss('--search-button-bg-color', search_button.background_color);
      this.setGlobalVariableCss('--search-button-border-radius', `${search_button.border_radius}px`);
      this.setIconButton(search_button.icon);
    }
  },

  initEvents: function () {
    if (!this._shadowRoot) {
      this.initShadowRoot();
    }

    const buttonEl = this._shadowRoot.getElementById(CONFIG.ID_BUTTON_PANEL);
    if (buttonEl) {
      buttonEl.addEventListener('click', () => {
        let isShow = this._iframePanel.classList.contains('show');

        // Toggle class name 'show' on iframe panel
        this._iframePanel.classList.toggle('show', !isShow);
        
        buttonEl.classList.toggle('show-icon-close', !isShow);

        this.sendMessageToIFrame({ type: 'toggle_panel', data: { show: !isShow }});
      });
    }
  }
};

// Expose SateraitoAI to the global window object
window.SateraitoAI = SateraitoAI;
if (window.SateraitoAIAsyncInit) {
  window.SateraitoAIAsyncInit();
  window.addEventListener('message', function (event) {
    if (!event.data || !event.data.type) return;
    const { type, data } = event.data;
    switch (type) {
      case 'request_client_web_site': {
        const { origin, href } = window.location;
        try {
          SateraitoAI.sendMessageToIFrame({
            type: 'response_client_web_site',
            data: { origin, href }
          });
        } catch (err) {
          console.error(err);
        }
        break;
      }
      case 'box_search_config': {
        if (!data) return;
        SateraitoAI._boxSearchConfig = data;
        MyRedis.set('box_search_config', JSON.stringify(data));
        SateraitoAI.refreshUI();
        break;
      }
      default:
        break;
    }
  }, false);
}