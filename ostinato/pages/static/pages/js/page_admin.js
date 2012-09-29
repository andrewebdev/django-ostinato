

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

    /*
     *  Detail View Scripts
     *
     */

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


    /*
     * List View Scripts
     *
     */

    // Expand/Collapse Rows
    function toggle_row($el, action) {
        if (action == 'collapse') {
            $el.hide();
        } else if (action == 'expand') {
            $el.show();
        }
    }


    $('a.toggle_children').click(function() {
        var $parent_node = $(this).parent();
        var parent_level = parseInt($parent_node.attr('id').split('_')[1]);
        var is_open = $parent_node.hasClass('open');

        // reset node
        $parent_node.removeClass('open');
        $parent_node.removeClass('closed');

        // Find all the rows below this one, that has a higher level
        $(this).parents('tr').nextAll().each(function(i) {
            var $node = $(this).find('span.tree_node');
            var item_level = parseInt($node.attr('id').split('_')[1]);

            // Expand/Collapse that row
            if (item_level > parent_level) {
                if (is_open) {
                    toggle_row($(this), 'collapse');
                    if ($node.hasClass('open')) {
                        $node.removeClass('open');
                        $node.addClass('closed');
                    }
                } else if (item_level === parent_level + 1) {
                    // When expanding, expand only the immediate children
                    toggle_row($(this), 'expand');
                }
            } else {
                // Stop traversing
                return;
            }
        });


        // update the parent node
        if (is_open) {
            $parent_node.addClass('closed');
            $parent_node.find('.toggle_children').button({
                'icons': {'primary': 'ui-icon-triangle-1-e'},
                'text': false
            });
        }
        else {
            $parent_node.addClass('open');
            $parent_node.find('.toggle_children').button({
                'icons': {'primary': 'ui-icon-triangle-1-s'},
                'text': false
            });
        }

        return false;
    });
    $('.tree_node.closed').each(function() {
        var $parent_node = $(this);
        var parent_level = $parent_node.attr('id').split('_')[1];

        $(this).parents('tr').nextAll().each(function(i) {
            var $node = $(this).find('span.tree_node');
            var item_level = $node.attr('id').split('_')[1];

            // Expand/Collapse that row
            if (item_level > parent_level) {
                toggle_row($(this), 'collapse');
            } else {
                // Stop traversing
                return;
            }
        }); 

       $parent_node.find('.toggle_children').button({
            'icons': {'primary': 'ui-icon-triangle-1-e'},
            'text': false
        }); 
    })


    // Reordering of Pages
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
