
// When changing the template, we should 'refresh' the Page
django.jQuery(document).ready(function() {
    var selected_template;
    django.jQuery('#id_template').focus(function() {
        selected_template = django.jQuery(this).val();
    }).change(function() {
        var refresh = confirm('Changing the template will save and reload the page. Are you sure you want to do this now?');
        if (refresh) {
            django.jQuery('input[name="_continue"]').click();
        } else {
            django.jQuery(this).val(selected_template);
        }
    });
});

