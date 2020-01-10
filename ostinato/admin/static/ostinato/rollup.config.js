import resolve from 'rollup-plugin-node-resolve';


export default [
  {
    input: 'src/pages-admin.js',
    output: {
      file: 'dist/pages-admin.js',
      format: 'iife',
    },
    plugins: [
      resolve({
        module: true,
      }),
    ],
  },

  {
    input: 'src/ostinato-editor.js',
    output: {
      file: 'dist/ostinato-editor.js',
      format: 'iife',
    },
    plugins: [
      resolve({
        module: true,
      }),
    ],
  },

];
