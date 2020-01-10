import '@editorjs/editorjs/dist/editor.js';
import {LitElement, html, css} from 'lit-element';


const baseGenerators = {
  paragraph: (data) => `<p>${data.text}</p>`,

  header: (data) => `<h${data.level}>${data.text}</h${data.level}>`,

  list: (data) => {
    let tagname = data.style.charAt(0) + 'l';
    var renderItem = (item) => { return `<li>${item}</li>`; }
    var items = '';
    data.items.forEach((item) => { items += renderItem(item); });
    return `<${tagname}>${items}</${tagname}>`;
  },

  quote: (data) => {
    return `<blockquote style="quote-${data.alignment}">
      <p class="quote-text">${data.text}</p>
      <p class="quote-caption">${data.caption}</p>
    </blockquote>`;
  },
};


class HTMLEngine {
  constructor(inputEl, templateSelector, generators) {
    this.inputEl = inputEl;
    this.generators = generators;
  }

  read() {
    let doc = new DOMParser().parseFromString(this.inputEl.value, 'text/html');
    var dataTemplate = doc.querySelector('[data-editor-data]');
    if (dataTemplate) {
      // Fix any escaped quotes in the json before parsing
      var jsonData = dataTemplate.dataset.editorData;
      // var validJson = dataTemplate.innerHTML.replace(/\\"/g, '\\\"');
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
    return this.generators[block.type](block.data) + '\n';
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
    this.engine = new HTMLEngine(
      this.saveToEl,
      '[editorjs-data]',
      baseGenerators);
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
    if (ev.data.editorSaved) {
      this.engine.write(ev.data.editorSaved);
    }
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
        height: auto;
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
