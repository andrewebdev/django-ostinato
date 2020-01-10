import '../node_modules/@editorjs/header/dist/bundle.js';
import '../node_modules/@editorjs/list/dist/bundle.js';
import '../node_modules/@editorjs/checklist/dist/bundle.js';
import '../node_modules/@editorjs/quote/dist/bundle.js';
import '../node_modules/@editorjs/warning/dist/bundle.js';
import '../node_modules/@editorjs/marker/dist/bundle.js';
import '../node_modules/@editorjs/code/dist/bundle.js';
import '../node_modules/@editorjs/inline-code/dist/bundle.js';
import '../node_modules/@editorjs/delimiter/dist/bundle.js';
import '../node_modules/@editorjs/link/dist/bundle.js';
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
    },

    list: {
      class: List,
      inlineToolbar: true,
      shortcut: 'CMD+SHIFT+L'
    },

    quote: {
      class: Quote,
      inlineToolbar: true,
      config: {
        quotePlaceholder: 'Enter a quote',
        captionPlaceholder: 'Caption or Author',
      },
      shortcut: 'CMD+SHIFT+O'
    },

    warning: Warning,

    marker: {
      class:  Marker,
      shortcut: 'CMD+SHIFT+M'
    },

    code: {
      class:  CodeTool,
      shortcut: 'CMD+SHIFT+C'
    },

    delimiter: Delimiter,

    inlineCode: {
      class: InlineCode,
      shortcut: 'CMD+SHIFT+C'
    },

    linkTool: LinkTool,

    embed: Embed,

    table: {
      class: Table,
      inlineToolbar: true,
      shortcut: 'CMD+ALT+T'
    },
  },
};
