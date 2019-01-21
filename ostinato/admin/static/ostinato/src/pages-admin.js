import {LitElement, html, css, svg} from 'lit-element';


const moveIcon = svg`<svg viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet" focusable="false" style="pointer-events: none; display: block; width: 100%; height: 100%;"><g><path d="M10 9h4V6h3l-5-5-5 5h3v3zm-1 1H6V7l-5 5 5 5v-3h3v-4zm14 2l-5-5v3h-3v4h3v3l5-5zm-9 3h-4v3H7l5 5 5-5h-3v-3z"></path></g></svg>`;
const copyIcon = svg`<svg viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet" focusable="false" style="pointer-events: none; display: block; width: 100%; height: 100%;"><g><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"></path></g></svg>`;
const addIcon = svg`<svg viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet" focusable="false" style="pointer-events: none; display: block; width: 100%; height: 100%;"><g><path d="M19 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"></path></g></svg>`;
const cancelIcon = svg`<svg viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet" focusable="false" style="pointer-events: none; display: block; width: 100%; height: 100%;"><g><path d="M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2zm5 13.59L15.59 17 12 13.41 8.41 17 7 15.59 10.59 12 7 8.41 8.41 7 12 10.59 15.59 7 17 8.41 13.41 12 17 15.59z"></path></g></svg>`;
const arrowUpIcon = svg`<svg viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet" focusable="false" style="pointer-events: none; display: block; width: 100%; height: 100%;"><g><path d="M4 12l1.41 1.41L11 7.83V20h2V7.83l5.58 5.59L20 12l-8-8-8 8z"></path></g></svg>`;
const arrowDownIcon = svg`<svg viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet" focusable="false" style="pointer-events: none; display: block; width: 100%; height: 100%;"><g><path d="M20 12l-1.41-1.41L13 16.17V4h-2v12.17l-5.58-5.59L4 12l8 8 8-8z"></path></g></svg>`;
const arrowSubIcon = svg`<svg viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet" focusable="false" style="pointer-events: none; display: block; width: 100%; height: 100%;"><g><path d="M19 15l-6 6-1.42-1.42L15.17 16H4V4h2v10h9.17l-3.59-3.58L13 9l6 6z"></path></g></svg>`;


class OstPagesController extends LitElement {

  static get properties() {
    return {
      csrfToken: { type: String },
      addPageUrl: { type: String },
      moveAction: { type: String },
      copyAction: { type: String },
    };
  }

  constructor() {
    super();

    this.csrfToken = '';
    this.addPageUrl = '';
    this.moveAction = '';
    this.copyAction = '';
    this._node = null;
  }

  render() {
    return html`
      <form id="actionForm" method="post" accept-charset="utf-8">
        <input type="hidden" name="csrfmiddlewaretoken" .value=${this.csrfToken} />
        <input type="hidden" name="node" .value=${this._node} />
        <input type="hidden" name="target" .value=${this._target} />
        <input type="hidden" name="position" .value=${this._position} />
      </form>
    `;
  }

  startAction(action, node) {
    this._node = node;

    switch (action) {
      case 'move':
        this._action = this.moveAction;
        break;

      case 'copy':
        this._action = this.copyAction;
        break;
    }

    this.dispatchEvent(new CustomEvent('action-started', {
      detail: {
        action: action,
        node: node,
      }
    }));
  }

  cancelAction() {
    this._node = null;
    this._action = null;

    this.dispatchEvent(new CustomEvent('action-cancelled'));
  }

  commitAction(targetNode, position) {
    if (this._node && this._action) {
      let nodeEl = document.querySelector(`[nodeId="${this._node}"]`);
      let targetEl = document.querySelector(`[nodeId="${targetNode}"]`);
      let actionForm = this.shadowRoot.getElementById('actionForm');

      let isDescendentOf = (
        (targetEl.left > nodeEl.left) && (targetEl.right < nodeEl.right)
      );

      if (isDescendentOf) {
        alert("Page cannot be made a child or sibling of one of it's descendants");
      }  else {
        actionForm.action = this._action;
        actionForm.querySelector('[name="node"]').value = this._node;
        actionForm.querySelector('[name="target"]').value = targetNode;
        actionForm.querySelector('[name="position"]').value = position;

        actionForm.submit();
      }
      this.dispatchEvent(new CustomEvent('action-finished', {
        detail: {
          action: this._action,
          node: this._node,
          position: position,
          targetNode: targetNode,
        }
      }))
    }
  }
}

customElements.define('ost-pages-controller', OstPagesController);


class OstPageNode extends LitElement {

  static get properties() {
    return {
      editUrl: { type: String },
      nodeId: {
        type: Number,
        reflect: true,
      },
      treeId: { type: Number },
      level: { type: Number },
      left: { type: Number },
      right: { type: Number },
      _currentAction: { type: Object },
    };
  }

  constructor() {
    super();
    this._currentAction = null;
  }

  connectedCallback() {
    super.connectedCallback();

    this._pagesController = document.querySelector('ost-pages-controller');

    if (this.level == 1) {
      this.style.paddingLeft = '0.5em';
    } else if (this.level > 1) {
      this.style.paddingLeft = `calc(1em * ${this.level})`;
    }

    this._pagesController.addEventListener('action-started', (ev) => {
      this._currentAction = ev.detail;
    });

    this._pagesController.addEventListener('action-cancelled', (ev) => {
      this._currentAction = null;
    });
  }

  cancelActionTemplate() {
    if (this._currentAction && this._currentAction.node === this.nodeId) {
      return html`
        <button
          title="Cancel"
          @click=${(ev) => {
            ev.preventDefault();
            this._pagesController.cancelAction();
          }}>
          ${cancelIcon}
        </button>
      `;
    }

    return '';
  }

  moveTargetsTemplate() {
    if (this._currentAction && this._currentAction.node !== this.nodeId) {
      return html`
        <button
          title="Insert above"
          @click=${(ev) => {
            ev.preventDefault();
            this._pagesController.commitAction(this.nodeId, 'left');
          }}>
          ${arrowUpIcon}
        </button>

        <button
          title="Insert below"
          @click=${(ev) => {
            ev.preventDefault();
            this._pagesController.commitAction(this.nodeId, 'right');
          }}>
          ${arrowDownIcon}
        </button>

        <button
          title="Insert as sub-page"
          @click=${(ev) => {
            ev.preventDefault();
            this._pagesController.commitAction(this.nodeId, 'last-child');
          }}>
          ${arrowSubIcon}
        </button>
      `;
    }

    return '';
  }

  actionsTemplate() {
    if (!this._currentAction) {
      return html`
        <button
          title="Move Page"
          @click=${(ev) => {
            ev.preventDefault();
            this._pagesController.startAction('move', this.nodeId);
          }}>
          ${moveIcon}
        </button>

        <button
          title="Create Copy"
          @click=${(ev) => {
            ev.preventDefault();
            this._pagesController.startAction('copy', this.nodeId);
          }}>
          ${copyIcon}
        </button>

        <button
          title="Create Sub Page"
          @click=${(ev) => {
            ev.preventDefault();
            window.location = `${this._pagesController.addPageUrl}?parent=${this.nodeId}`;
          }}>
          ${addIcon}
        </button>
      `;
    }
  }

  branchTemplate() {
    if (this.level > 0) {
      let branch = ''.repeat(this.level);
      return html`┕━&nbsp;`;
    }
    return '';
  }

  render() {
    return html`
      <style>
        :host {
          display: flex;
          flex-direction: row;
          align-items: center;
        }

        .actions button {
          box-sizing: border-box;
          background: transparent;
          border: 0 none;
          padding: 5px;
          width: 30px;
          height: 30px;
          cursor: pointer;
          fill: #417690;
        }

        ::slotted(*) {
          flex: 1;
          flex-basis: 0.000000001px;
        }

        hidden {
          display: none !important;
          visibility: hidden;
        }
      </style>

      ${this.branchTemplate()}

      <slot name="title"></slot>

      <div class="actions">
        ${this.actionsTemplate()}
        ${this.cancelActionTemplate()}
        ${this.moveTargetsTemplate()}
      </div>
    `;
  }

}

customElements.define('ost-page-node', OstPageNode);


(function() {
  document.addEventListener('DOMContentLoaded', () => {

    // Detail view functions and methods
    (function() {
      // When changing the template, we should 'refresh' the Page
      var templateEl = document.getElementById('id_template');

      if (templateEl) {
        const initial_template = templateEl.value;
        templateEl.addEventListener('change', (ev) => {
          const msg = 'Changing the template will save and reload the page. Are you sure you want to do this now?';
          if (confirm(msg)) {
            document.querySelector('input[name="_continue"]').click();
          } else {
            templateEl.value = initial_template;
          }
        });
      }
    })();

  }, false);

})();
