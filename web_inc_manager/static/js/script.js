// ===== Funções para manipulação de CRM =====
function openCRMLink(item, token) {
    if (!token) {
        alert('Token CRM não disponível');
        return;
    }
    
    const baseUrlElement = document.getElementById('crm-base-url');
    if (!baseUrlElement) {
        alert('Configuração do CRM não disponível');
        return;
    }
    
    const baseUrl = baseUrlElement.dataset.url;
    const encodedItem = encodeURIComponent(item);
    const link = `${baseUrl}&token=${token}&cod_item=${encodedItem}&filter_cod=${item.toLowerCase()}`;
    window.open(link, '_blank');
}

// ===== Funções para a rotina de inspeção =====
function saveScrollPosition() {
    const scrollPosition = window.scrollY || window.pageYOffset;
    document.querySelectorAll('input[name="scroll_position"]').forEach(input => {
        input.value = scrollPosition;
    });
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
    if (saveButton) {
        saveButton.disabled = !allProcessed;
    }
}

// ===== Funções gerais da interface =====
document.addEventListener('DOMContentLoaded', function() {
    // Inicialização de elementos especiais
    const toggleNightMode = document.getElementById('toggleNightMode');
    if (toggleNightMode) {
        toggleNightMode.addEventListener('click', function() {
            document.body.classList.toggle('night-mode');
            
            // Opcional: salvar preferência em localStorage
            if (document.body.classList.contains('night-mode')) {
                localStorage.setItem('nightMode', 'true');
            } else {
                localStorage.setItem('nightMode', 'false');
            }
        });
        
        // Carregar preferência salva, se houver
        if (localStorage.getItem('nightMode') === 'true') {
            document.body.classList.add('night-mode');
        }
    }
    
    // Formatadores de dados
    document.querySelectorAll('.format-date').forEach(function(element) {
        const date = element.textContent.trim();
        if (date && date.match(/^\d{2}-\d{2}-\d{4}$/)) {
            const parts = date.split('-');
            element.title = `${parts[0]}/${parts[1]}/${parts[2]}`;
        }
    });
    
    // Inicializar tooltips Bootstrap, se disponível
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Verificar botões de salvar para rotinas de inspeção
    updateSaveButton();
});