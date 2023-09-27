$(document).ready(function () {
    // Função para atualizar a visibilidade dos elementos com base na seleção do usuário
    function updateVisibilityAndButtons() {
        console.log("entrou");
        var userType = $('select[name="select_users_type"]').val();
        var action = $('select[name="action"]').val();

        // Esconder ou mostrar a seção de curadoria com base na seleção de "especialistas"
        if (userType === 'specialists') {
            $('h3:contains("Escolha uma curadoria")').show();
            $('select[name="selected_curation_id"]').show();
        } else {
            $('h3:contains("Escolha uma curadoria")').hide();
            $('select[name="selected_curation_id"]').hide();
        }

        // Esconder ou mostrar os botões com base na seleção de "adicionar" ou "remover"
        if (action === 'add') {
            $('button[name="enable_specialists"]').show();
            $('button[name="remove_specialists"]').hide();
        } else if (action === 'remove') {
            $('button[name="enable_specialists"]').hide();
            $('button[name="remove_specialists"]').show();
        }
    }

    updateVisibilityAndButtons();
    $('select[name="select_users_type"], select[name="action"]').change(updateVisibilityAndButtons);
});