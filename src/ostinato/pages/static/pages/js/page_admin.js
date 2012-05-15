

function get_id(id) { return id.split('_')[2]; }

function move_node(move_data) {
    var $form = $('#ostinato_page_move_form');

    $form.find('input[name="node"]').val(move_data.node);
    $form.find('input[name="target"]').val(move_data['target']);
    $form.find('input[name="position"]').val(move_data.position);

    $form.submit();
}


django.jQuery(document).ready(function() {

    var page_id, selected_template;

    // When changing the template, we should 'refresh' the Page
    django.jQuery('#id_template').focus(function() {
        selected_template = $(this).val();
    }).change(function() {
        var refresh = confirm('Changing the template will save and reload the page. Are you sure you want to do this now?');
        if (refresh) {
            django.jQuery('input[name="_continue"]').click();
        } else {
            $(this).val(selected_template);
        }
    });

    $('.ostinato_page_move').button({
        'icons': {'primary': 'ui-icon-arrow-4'},
        'text': false

    }).click(function() {
        /*
            Show the movement actions for the selected page
            make sure that the page being moved does not have it's actions
            visible
        */
        $('.ostinato_page_move').hide();
        $('.ostinato_move_action').show();
        $(this).siblings('.ostinato_move_action').hide();
        $(this).siblings('.ostinato_cancel_move').show();

        page_id = get_id($(this).parent().attr('id'));

    }).each(function() {
        $(this).parent().parent().css('text-align', 'center');

    });

    $('.ostinato_move_action, .ostinato_cancel_move').css('display', 'none');

    $('._left_of').button({
        'icons': {'primary': 'ui-icon-arrowthickstop-1-n'},
        'text': false
    }).click(function() {
        var target = get_id($(this).parent().attr('id'));
        move_node({'node': page_id, 'target': target, 'position': 'left'});
    });

    $('._right_of').button({
        'icons': {'primary': 'ui-icon-arrowthickstop-1-s'},
        'text': false
    }).click(function() {
        var target = get_id($(this).parent().attr('id'));
        move_node({'node': page_id, 'target': target, 'position': 'right'});
    });

    $('._child_of').button({
        'icons': {'primary': 'ui-icon-arrowreturnthick-1-e'},
        'text': false
    }).click(function() {
        var target = get_id($(this).parent().attr('id'));
        move_node({'node': page_id, 'target': target, 'position': 'last-child'});
    });

    $('.ostinato_cancel_move').button({
        'icons': {'primary': 'ui-icon-close'}
    }).click(function() {
        $(this).hide();
        $('.ostinato_move_action').hide();
        $('.ostinato_page_move').show();

        page_id = null;
    });

});
