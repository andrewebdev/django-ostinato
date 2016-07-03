
HTMLTextAreaElement.prototype.insertAtCaret = function (text) {
    text = text || '';
    if (document.selection) {
        // IE
        this.focus();
        var sel = document.selection.createRange();
        sel.text = text;
    } else if (this.selectionStart || this.selectionStart === 0) {
        // Others
        var startPos = this.selectionStart;
        var endPos = this.selectionEnd;
        this.value = this.value.substring(0, startPos) +
        text +
        this.value.substring(endPos, this.value.length);
        this.selectionStart = startPos + text.length;
        this.selectionEnd = startPos + text.length;
    } else {
        this.value += text;
    }
};


function insertIntoEditor(editor, content) {
    tinyMCE.execCommand('mceFocus', false, editor);
    tinymce.activeEditor.execCommand('mceInsertContent', false, content);
}


function cbInsertAction(browser, fieldName, content) {
    // var field = document.querySelector('#id_' + fieldName);
    // field.insertAtCaret(content);
    insertIntoEditor('id_' + fieldName, content);
}

