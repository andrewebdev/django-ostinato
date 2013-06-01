function get_id(id) { return id.split('_')[2]; }

function getNodeID($node) {
    /* A helper function that returns the tree_id and level for $node */
    var nodeIDList = $node.attr('id').split('_');

    return {
        'treeID': parseInt(nodeIDList[1]),
        'level': parseInt(nodeIDList[2]),
        'lft': parseInt(nodeIDList[3]),
        'rght': parseInt(nodeIDList[4])
    }
}

function page_action(data, action) {
    var $form = django.jQuery('#ostinato_page_action_form');

    $form.find('input[name="node"]').val(data.node);
    $form.find('input[name="target"]').val(data['target']);
    $form.find('input[name="position"]').val(data.position);

    $form.attr('action', page_action_urls[action]);
    $form.submit();
}


django.jQuery(document).ready(function() {
    var page_id, selected_template, current_action;

    /*  Detail View Scripts */

    // When changing the template, we should 'refresh' the Page
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


    /* List View Scripts */

    // Expand/Collapse Rows

    django.jQuery('#result_list td:eq(1)').css('width', '20px');

    function toggleRow($node, action) {
        var $el = $node.parent().parent();
        if (action == 'collapse') {
            $el.hide();
        } else if (action == 'expand') {
            $el.show();
        }
    }


    django.jQuery('a.toggle_children').click(function() {
        var $parentNode = django.jQuery(this).parent();
        var parentNodeID = getNodeID($parentNode);
        var is_open = $parentNode.hasClass('open');

        // reset node
        $parentNode.removeClass('open');
        $parentNode.removeClass('closed');

        // Find all the rows of the same treeID
        query = 'span.tree_node[id*="tid_' + parentNodeID.treeID + '_"]';
        django.jQuery(query).each(function(i) {
            var $node = django.jQuery(this);
            var nodeID = getNodeID($node);

            // Expand/Collapse the row
            if ((nodeID.lft > parentNodeID.lft) && (nodeID.rght < parentNodeID.rght)) {
                if (is_open) {
                    toggleRow($node, 'collapse');

                    // All child nodes must be fully collapsed as well
                    if ($node.hasClass('open')) {
                        $node.removeClass('open');
                        $node.addClass('closed');
                        $node.find('.toggle_children')
                            .html('<img src="' + STATIC_URL +
                                  '/pages/img/tree_closed.png" alt="expand" />');
                    }
                } else if (nodeID.level == parentNodeID.level + 1) {
                    // only expand immediate children
                    toggleRow($node, 'expand');
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


    django.jQuery('.tree_node.closed').each(function() {
        var $parentNode = django.jQuery(this);
        var parentNodeID = getNodeID($parentNode);

        django.jQuery('.tree_node[id*="tid_' + parentNodeID.treeID + '_"]').each(function(i) {
            var $node = django.jQuery(this);
            var nodeID = getNodeID($node);

            // Expand/Collapse rows of a higher level
            if (nodeID.level > parentNodeID.level) {
                toggleRow($node , 'collapse');
            }
        }); 
    });


    // Set up the movement and duplicate actions
    django.jQuery('.ostinato_page_move, .ostinato_page_duplicate').click(function() {
        /*
            Show the movement actions for the selected page
            make sure that the page being moved does not have it's actions
            visible.

            Also when the current_action is 'move', do NOT show the
            moveto location links for chile pages, since a parent cannot be a
            child of it's children.
        */
        var query = 'span.tree_node[id*="tid_"]';
        var $parentNode = django.jQuery(this).parents('tr').find(query);
        var parentNodeID = getNodeID($parentNode);

        if (django.jQuery(this).hasClass('ostinato_page_move')) { current_action = 'move'; }
        if (django.jQuery(this).hasClass('ostinato_page_duplicate')) { current_action = 'duplicate'; }

        django.jQuery('.ostinato_page_move, .ostinato_page_duplicate, .ostinato_new_child').hide();
        django.jQuery('.ostinato_move_action').each(function() {
            // Only show the move actions if the target to be moved is not a
            // parent of this node.
            if (current_action == 'move') {
                var $node = django.jQuery(this).parents('tr').find(query);
                var nodeID = getNodeID($node);

                if ((nodeID.lft > parentNodeID.lft) && (nodeID.rght < parentNodeID.rght)) {
                    // We are a child of the node being moved, dont show anything
                } else {
                    // We are not a child of the node being moved
                    django.jQuery(this).show();
                }
            } else {
                django.jQuery(this).show();
            }
        });
        django.jQuery(this).siblings('.ostinato_move_action').hide();
        django.jQuery(this).siblings('.ostinato_cancel_move').show();

        page_id = get_id(django.jQuery(this).parent().attr('id'));
    }).each(function() {
        django.jQuery(this).parent().parent().css('text-align', 'center');
    });

    django.jQuery('.ostinato_move_action, .ostinato_cancel_move').css('display', 'none');

    django.jQuery('._left_of').click(function() {
        var target = get_id(django.jQuery(this).parent().attr('id'));
        page_action({'node': page_id, 'target': target, 'position': 'left'}, current_action);
    });

    django.jQuery('._right_of').click(function() {
        var target = get_id(django.jQuery(this).parent().attr('id'));
        page_action({'node': page_id, 'target': target, 'position': 'right'}, current_action);
    });

    django.jQuery('._child_of').click(function() {
        var target = get_id(django.jQuery(this).parent().attr('id'));
        page_action({'node': page_id, 'target': target, 'position': 'last-child'}, current_action);
    });

    django.jQuery('.ostinato_cancel_move').click(function() {
        django.jQuery(this).hide();
        django.jQuery('.ostinato_move_action').hide();
        django.jQuery('.ostinato_page_move, .ostinato_page_duplicate, .ostinato_new_child').show();

        page_id = null;
        current_action = null;
    });

});
