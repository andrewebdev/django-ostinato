
django.jQuery(document).ready(function() {

    django.jQuery('#id_template').change(function() {
        django.jQuery('input[name="_continue"]').click();
    });
    
});
