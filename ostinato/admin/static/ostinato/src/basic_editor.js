import '../node_modules/@editorjs/header/dist/bundle.js';
import '../node_modules/@editorjs/paragraph/dist/bundle.js';
import '../node_modules/@editorjs/list/dist/bundle.js';
import '../node_modules/@editorjs/checklist/dist/bundle.js';
import '../node_modules/@editorjs/quote/dist/bundle.js';
import '../node_modules/@editorjs/warning/dist/bundle.js';
import '../node_modules/@editorjs/marker/dist/bundle.js';
import '../node_modules/@editorjs/code/dist/bundle.js';
import '../node_modules/@editorjs/inline-code/dist/bundle.js';
import '../node_modules/@editorjs/delimiter/dist/bundle.js';
import '../node_modules/@editorjs/embed/dist/bundle.js';
import '../node_modules/@editorjs/table/dist/bundle.js';


export const editorConfig = {
  initialBlock: "paragraph",
  minHeight: "400px",
  autoFocus: true,

  tools: {
    header: {
      class: Header,
      config: {
        placeholder: 'Header Text'
      },
      shortcut: 'CMD+SHIFT+H',
      HTMLGenerator: (data) => `<h${data.level}>${data.text}</h${data.level}>`,
    },

    paragraph: {
      class: Paragraph,
      shortcut: 'CMD+SHIFT+P',
      HTMLGenerator: (data) => `<p>${data.text}</p>`,
    },

    list: {
      class: List,
      inlineToolbar: true,
      shortcut: 'CMD+SHIFT+L',
      HTMLGenerator: (data) => {
        let tagname = data.style.charAt(0) + 'l';
        var renderItem = (item) => { return `<li>${item}</li>`; }
        var items = '';
        data.items.forEach((item) => { items += renderItem(item); });
        return `<${tagname}>${items}</${tagname}>`;
      },
    },

    quote: {
      class: Quote,
      inlineToolbar: true,
      config: {
        quotePlaceholder: 'Enter a quote',
        captionPlaceholder: 'Caption or Author',
      },
      shortcut: 'CMD+SHIFT+O',
      HTMLGenerator: (data) => {
        return `<blockquote style="quote-${data.alignment}">
          <p class="quote-text">${data.text}</p>
          <p class="quote-caption">${data.caption}</p>
        </blockquote>`;
      },
    },

    warning: {
      class: Warning,
      inlineToolbar: true,
      shortcut: 'CMD+SHIFT+W',
      config: {
        titlePlaceholder: 'Warning Title',
        messagePlaceholder: 'Warning Message',
      },
      HTMLGenerator: (data) => {
        return `<div class="warning">
            <p class="warning-title">${data.title}</p>
            <p class="warning-message">${data.message}</p>
          </div>`;
      },
    },

    marker: {
      class:  Marker,
      shortcut: 'CMD+SHIFT+M'
    },

    code: {
      class:  CodeTool,
      shortcut: 'CMD+SHIFT+C',
      HTMLGenerator: (data) => { return `<code>${data.code}</code>`; }
    },

    delimiter: {
      class: Delimiter,
      HTMLGenerator: () => { return `<div class="ce-delimiter"></div>` }
    },

    inlineCode: {
      class: InlineCode,
      shortcut: 'CMD+SHIFT+C'
    },

    table: {
      class: Table,
      inlineToolbar: true,
      shortcut: 'CMD+ALT+T',
      HTMLGenerator: (data) => {
        var rows = '';
        data.content.forEach((row) => {
          var cells = '';
          row.forEach((cell) => { cells += '<td>' + cell + '</td>'; })
          rows += '<tr>' + cells + '</tr>';
        });
        return '<table>' + rows + '</table>';
      }
    },
  },
};
