function get_id(id) { return id.split('_')[2]; }

function getNodeID($node) {
    /* A helper function that returns the tree_id and level for $node */
    var nodeIDList = $node.attr('id').split('_');

    return {
        'treeID': parseInt(nodeIDList[1]),
        'level': parseInt(nodeIDList[2])
    }
}


function move_node(move_data) {
    var $form = $('#ostinato_page_move_form');

    $form.find('input[name="node"]').val(move_data.node);
    $form.find('input[name="target"]').val(move_data['target']);
    $form.find('input[name="position"]').val(move_data.position);

    $form.submit();
}


django.jQuery(document).ready(function() {
    var page_id, selected_template;

    /*  Detail View Scripts */

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


    /* List View Scripts */

    // Expand/Collapse Rows

    $('#result_list td:eq(1)').css('width', '20px');

    function toggleRow($node, action) {
        var $el = $node.parent().parent();
        if (action == 'collapse') {
            $el.hide();
        } else if (action == 'expand') {
            $el.show();
        }
    }


    $('a.toggle_children').click(function() {
        var $parentNode = $(this).parent();
        var parentNodeID = getNodeID($parentNode);
        var is_open = $parentNode.hasClass('open');

        // reset node
        $parentNode.removeClass('open');
        $parentNode.removeClass('closed');

        // Find all the rows of the same tree_id, with a higher level 
        $('span.tree_node[id*="tid_' + parentNodeID.treeID + '_"]').each(function(i) {
            var $node = $(this);
            var nodeID = getNodeID($node);

            // Expand/Collapse that row
            if (nodeID.level > parentNodeID.level) {
                if (is_open) {
                    toggleRow($node, 'collapse');

                    if ($node.hasClass('open')) {
                        $node.removeClass('open');
                        $node.addClass('closed');
                    }
                } else {
                    if (nodeID.level == parentNodeID.level + 1) {
                        toggleRow($node, 'expand');
                    }
                }
            }
        });


        // update the parent node
        if (is_open) {
            $parentNode.addClass('closed').find('.toggle_children')
                .html('<img src="' + STATIC_URL + '/pages/img/tree_closed.png" alt="expand" />');
        }
        else {
            $parentNode.addClass('open').find('.toggle_children')
                .html('<img src="' + STATIC_URL + '/pages/img/tree_open.png" alt="collapse" />');
        }

        return false;
    });


    $('.tree_node.closed').each(function() {
        var $parentNode = $(this);
        var parentNodeID = getNodeID($parentNode);

        $('.tree_node[id*="tid_' + parentNodeID.treeID + '_"]').each(function(i) {
            var $node = $(this);
            var nodeID = getNodeID($node);

            // Expand/Collapse rows of a higher level
            if (nodeID.level > parentNodeID.level) {
                toggleRow($node , 'collapse');
            }
        }); 
    });


    $('.ostinato_page_move').click(function() {
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

    $('._left_of').click(function() {
        var target = get_id($(this).parent().attr('id'));
        move_node({'node': page_id, 'target': target, 'position': 'left'});
    });

    $('._right_of').click(function() {
        var target = get_id($(this).parent().attr('id'));
        move_node({'node': page_id, 'target': target, 'position': 'right'});
    });

    $('._child_of').click(function() {
        var target = get_id($(this).parent().attr('id'));
        move_node({'node': page_id, 'target': target, 'position': 'last-child'});
    });

    $('.ostinato_cancel_move').click(function() {
        $(this).hide();
        $('.ostinato_move_action').hide();
        $('.ostinato_page_move').show();

        page_id = null;
    });

});
