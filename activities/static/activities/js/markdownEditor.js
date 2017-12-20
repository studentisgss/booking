// DOCUMENT READY
$(document).ready(function() {
    if (!($("#id_description").prop("disabled"))) {
        var simplemde = new SimpleMDE({ element: $("#id_description")[0],
                                        forceSync: true,
                                        toolbar: ["bold", "italic", "strikethrough", "|",
                                                    "heading-2", "heading-3", "|",
                                                    "quote", "unordered-list", "ordered-list", "|",
                                                    "link", "table", "horizontal-rule", "|",
                                                    "preview", "|", "guide"]});
    }
});
