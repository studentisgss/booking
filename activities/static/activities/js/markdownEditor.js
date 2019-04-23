// DOCUMENT READY
$(document).ready(function() {
    if (!($("#id_description").prop("disabled"))) {
/*
INSTALLATION INSTRUCTION FOR CKEDITOR

You need a custom build of CKEditor to integrate the MArkdown plugin.
Follow the instruction in the section 'Adding a plugin to a build' at the following link to compile the build with the plugin:

https://ckeditor.com/docs/ckeditor5/latest/builds/guides/integration/installing-plugins.html

To install the Markdown plugin you can find the detail at https://ckeditor.com/docs/ckeditor5/latest/features/markdown.html
(Use the install command, for the code to load the plugin read the following text.)

When you arrive in the first guide at the step to edit 'src/ckeditor.js'
add the import and the Markdown function as in the second link
then add in the plugins list 'Markdown' (same name as the function),
you should **not** add 'GFMDataProcessor' in the plugins list.
*/

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
