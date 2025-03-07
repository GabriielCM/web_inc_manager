<!-- Remova o fetch e use submissão normal -->
{% for registro in registros %}
<tr>
    <td>{{ registro.item }}</td>
    <td>{{ registro.descricao }}</td>
    <td>{{ registro.qtd_recebida }}</td>
    <td class="status-cell" data-inspecionado="{{ registro.inspecionado|lower }}" data-adiado="{{ registro.adiado|lower }}">
        {% if registro.inspecionado %}
            Inspecionado
        {% elif registro.adiado %}
            Adiado
        {% else %}
            Pendente
        {% endif %}
    </td>
    <td>
        <button type="button" class="btn btn-primary btn-sm" onclick="openCRMLink('{{ registro.item }}')">Acessar Desenho</button>
        <form method="POST" action="{{ url_for('visualizar_registros_inspecao') }}" style="display:inline;">
            <input type="hidden" name="item_index" value="{{ loop.index0 }}">
            <input type="hidden" name="action" value="inspecionar">
            <button type="submit" class="btn btn-success btn-sm">Inspecionar</button>
        </form>
        <form method="POST" action="{{ url_for('visualizar_registros_inspecao') }}" style="display:inline;">
            <input type="hidden" name="item_index" value="{{ loop.index0 }}">
            <input type="hidden" name="action" value="adiar">
            <button type="submit" class="btn btn-secondary btn-sm">Adiar</button>
        </form>
    </td>
</tr>
{% endfor %}

<!-- Atualize o script -->
<script>
function openCRMLink(item) {
    const token = "{{ session.get('inspecao_crm_token', '') }}";
    if (!token) {
        alert('Token CRM não disponível');
        return;
    }
    const baseUrl = "http://192.168.1.47/crm/index.php?route=engenharia/produto/update";
    const encodedItem = encodeURIComponent(item);
    const link = `${baseUrl}&token=${token}&cod_item=${encodedItem}&filter_cod=${item.toLowerCase()}`;
    window.open(link, '_blank');
}

function updateSaveButton() {
    const statusCells = document.querySelectorAll('.status-cell');
    let allProcessed = true;
    
    statusCells.forEach(cell => {
        const inspecionado = cell.getAttribute('data-inspecionado') === 'true';
        const adiado = cell.getAttribute('data-adiado') === 'true';
        if (!inspecionado && !adiado) {
            allProcessed = false;
        }
    });
    
    const saveButton = document.getElementById('saveButton');
    saveButton.disabled = !allProcessed;
}

document.addEventListener('DOMContentLoaded', updateSaveButton);
</script>