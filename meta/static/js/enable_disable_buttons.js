$(document).ready(function () {
    var action = $('select[name="action"]').val();
    if (action === 'add') {
        $('button[name="enable_editors"]').show();
        $('button[name="remove_editors"]').hide();
    } else if (action === 'remove') {
        $('button[name="enable_editors"]').hide();
        $('button[name="remove_editors"]').show();
    }
    function updateVisibilityAndButtons() {
        var userType = $('select[name="select_users_type"]').val();

        if (userType === 'editors') {
            $('h3:contains("Escolha uma curadoria")').show();
            $('select[name="selected_curation_id"]').show();
        } else {
            $('h3:contains("Escolha uma curadoria")').hide();
            $('select[name="selected_curation_id"]').hide();
        }
    }

    updateVisibilityAndButtons();
    $('select[name="select_users_type"]').change(updateVisibilityAndButtons);
});