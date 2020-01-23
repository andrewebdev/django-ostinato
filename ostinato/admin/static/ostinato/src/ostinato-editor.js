import {LitElement, html, css} from 'lit-element';


class HTMLEngine {
  constructor(inputEl, templateSelector, editorConfig) {
    this.inputEl = inputEl;
    this.editorConfig = editorConfig;
  }

  read() {
    let doc = new DOMParser().parseFromString(this.inputEl.value, 'text/html');
    var dataTemplate = doc.querySelector('[data-editor-data]');
    if (dataTemplate) {
      var jsonData = dataTemplate.dataset.editorData;
      return JSON.parse(jsonData);
    }
    return null;
  }

  write(outputData) {
    var editorData = JSON.stringify(outputData);
    var renderedBlocks = '';
    outputData.blocks.forEach((block) => {
      renderedBlocks += this.renderBlock(block);
    });
    this.inputEl.value = `<template data-editor-data='${editorData}'></template>
      ${renderedBlocks}`;
  }

  renderBlock(block) {
    return this.editorConfig.tools[block.type].HTMLGenerator(block.data) + '\n';
  }
}


class OstinatoEditorWidget extends LitElement {
  static get properties() {
    return {
      saveTo: { type: String },
      editorConfig: { type: String },
      editorFramePath: { type: String },
    }
  }

  constructor() {
    super();
    this.saveTo = '';
    this.editorConfig = '';
    this.editorFramePath = '';
  }

  connectedCallback() {
    super.connectedCallback();
    this.saveToEl = document.querySelector(this.saveTo);
    // Now import our editor config.
    import(this.editorConfig).then((m) => {
      this.config = m.editorConfig;
      this.engine = new HTMLEngine(
        this.saveToEl,
        '[editorjs-data]',
        this.config);
    });
  }

  loadData() {
    this.editorFrame.contentWindow.postMessage({
      editor: {
        configPath: this.editorConfig,
        data: this.engine.read(),
      },
    });

    window.addEventListener(
      'message',
      this._handleEditorMessages.bind(this));
  }

  _handleEditorMessages(ev) {
    // TODO - SECURITY! Make sure we verify domain here
    if (ev.data.editorSaved) {
      this.engine.write(ev.data.editorSaved);
    }

    if (ev.data.editorReady || ev.data.editorSaved) {
      this.updateFrameHeight();
    }
  }

  updateFrameHeight() {
    var editorContent = this.editorFrame.contentWindow.document;
    var height = Math.max(
      editorContent.body.scrollHeight,
      editorContent.body.offsetHeight,
      editorContent.documentElement.clientHeight,
      editorContent.documentElement.scrollHeight,
      editorContent.documentElement.offsetHeight
    );
    this.editorFrame.style.height = height + 4 + "px";
  }

  _handleFrameLoaded() {
    this.loadData();
  }

  firstUpdated() {
    this.editorFrame = this.shadowRoot.getElementById('editorFrame');
  }

  static get styles() {
    return css`
      :host {
        display: block;
        width: 100%;
      }

      iframe {
        width: 100%;
        min-height: 400px;
        box-shadow: 0 0 1px 2px #e3e3e3;
      }
    `;
  }

  render() {
    return html`
      <iframe
        id="editorFrame"
        @load=${this._handleFrameLoaded}
        src="${this.editorFramePath}"
        frameborder="0">
      </iframe>
    `;
  }
}

customElements.define('ostinato-editor-widget', OstinatoEditorWidget);
