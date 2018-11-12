// DOCUMENT READY
$(document).ready(function() {
    if (!($("#id_description").prop("disabled"))) {
        // Load the editor
        ClassicEditor.create(document.querySelector('#id_description'),
            {
                language: 'it',
                toolbar: [ 'heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', '|', 'undo', 'redo' ],
                plugin: 'Markdown'
            })
            .then(editor => {
            })
            .catch(error => {
                console.error( error );
            });
    }
});
