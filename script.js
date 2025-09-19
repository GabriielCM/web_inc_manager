// Q-Manager - Sistema de Gerenciamento da Qualidade
// JavaScript para funcionalidades interativas

class QManager {
    constructor() {
        this.currentPage = 'dashboard';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupSidebarToggle();
        this.loadPage('dashboard');
    }

    setupEventListeners() {
        // Event listeners para itens do menu
        const menuItems = document.querySelectorAll('.menu-item');
        menuItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const page = e.currentTarget.getAttribute('data-page');
                this.loadPage(page);
                this.updateActiveMenuItem(e.currentTarget);
            });
        });
    }

    setupSidebarToggle() {
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebar = document.querySelector('.sidebar');
        const mainContent = document.querySelector('.main-content');

        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');
        });

        // Fechar sidebar em telas pequenas ao clicar fora
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                    sidebar.classList.remove('open');
                }
            }
        });
    }

    updateActiveMenuItem(activeItem) {
        // Remove active class de todos os itens
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Adiciona active class ao item clicado
        activeItem.classList.add('active');
    }

    loadPage(pageName) {
        this.currentPage = pageName;
        this.updatePageTitle(pageName);
        this.updatePageContent(pageName);
    }

    updatePageTitle(pageName) {
        const pageTitles = {
            'dashboard': {
                title: 'Dashboard',
                description: 'Visão geral do sistema de gestão da qualidade'
            },
            'audits': {
                title: 'Auditorias',
                description: 'Gerenciamento de auditorias internas e externas'
            },
            'non-conformities': {
                title: 'Não Conformidades',
                description: 'Controle e acompanhamento de não conformidades'
            },
            'corrective-actions': {
                title: 'Ações Corretivas',
                description: 'Planejamento e execução de ações corretivas'
            },
            'preventive-actions': {
                title: 'Ações Preventivas',
                description: 'Implementação de ações preventivas'
            },
            'procedures': {
                title: 'Procedimentos',
                description: 'Gestão de procedimentos da qualidade'
            },
            'work-instructions': {
                title: 'Instruções de Trabalho',
                description: 'Controle de instruções de trabalho'
            },
            'forms': {
                title: 'Formulários',
                description: 'Formulários e documentos da qualidade'
            },
            'reports': {
                title: 'Relatórios',
                description: 'Geração de relatórios e indicadores'
            },
            'analytics': {
                title: 'Análises',
                description: 'Análises estatísticas e tendências'
            },
            'users': {
                title: 'Usuários',
                description: 'Gestão de usuários e permissões'
            },
            'settings': {
                title: 'Configurações',
                description: 'Configurações do sistema'
            }
        };

        const pageInfo = pageTitles[pageName] || pageTitles['dashboard'];
        
        document.getElementById('pageTitle').textContent = pageInfo.title;
        document.getElementById('pageDescription').textContent = pageInfo.description;
    }

    updatePageContent(pageName) {
        const contentArea = document.getElementById('pageContent');
        
        // Conteúdo específico para cada página
        const pageContents = {
            'dashboard': this.getDashboardContent(),
            'audits': this.getAuditsContent(),
            'non-conformities': this.getNonConformitiesContent(),
            'corrective-actions': this.getCorrectiveActionsContent(),
            'preventive-actions': this.getPreventiveActionsContent(),
            'procedures': this.getProceduresContent(),
            'work-instructions': this.getWorkInstructionsContent(),
            'forms': this.getFormsContent(),
            'reports': this.getReportsContent(),
            'analytics': this.getAnalyticsContent(),
            'users': this.getUsersContent(),
            'settings': this.getSettingsContent()
        };

        contentArea.innerHTML = pageContents[pageName] || pageContents['dashboard'];
        
        // Adiciona animação de fade in
        contentArea.style.opacity = '0';
        setTimeout(() => {
            contentArea.style.opacity = '1';
        }, 100);
    }

    getDashboardContent() {
        return `
            <div class="dashboard-grid">
                <div class="dashboard-card">
                    <div class="card-icon">
                        <i class="fas fa-clipboard-check"></i>
                    </div>
                    <div class="card-content">
                        <h3>Auditorias</h3>
                        <p class="card-number">12</p>
                        <p class="card-description">Auditorias realizadas este mês</p>
                    </div>
                </div>
                
                <div class="dashboard-card">
                    <div class="card-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <div class="card-content">
                        <h3>Não Conformidades</h3>
                        <p class="card-number">5</p>
                        <p class="card-description">Pendentes de resolução</p>
                    </div>
                </div>
                
                <div class="dashboard-card">
                    <div class="card-icon">
                        <i class="fas fa-tools"></i>
                    </div>
                    <div class="card-content">
                        <h3>Ações Corretivas</h3>
                        <p class="card-number">8</p>
                        <p class="card-description">Em andamento</p>
                    </div>
                </div>
                
                <div class="dashboard-card">
                    <div class="card-icon">
                        <i class="fas fa-shield-alt"></i>
                    </div>
                    <div class="card-content">
                        <h3>Ações Preventivas</h3>
                        <p class="card-number">3</p>
                        <p class="card-description">Implementadas</p>
                    </div>
                </div>
            </div>
            
            <div class="recent-activities">
                <h2>Atividades Recentes</h2>
                <div class="activity-list">
                    <div class="activity-item">
                        <div class="activity-icon">
                            <i class="fas fa-plus-circle"></i>
                        </div>
                        <div class="activity-content">
                            <p>Nova não conformidade registrada</p>
                            <span class="activity-time">Há 2 horas</span>
                        </div>
                    </div>
                    <div class="activity-item">
                        <div class="activity-icon">
                            <i class="fas fa-check-circle"></i>
                        </div>
                        <div class="activity-content">
                            <p>Auditoria concluída com sucesso</p>
                            <span class="activity-time">Há 4 horas</span>
                        </div>
                    </div>
                    <div class="activity-item">
                        <div class="activity-icon">
                            <i class="fas fa-file-alt"></i>
                        </div>
                        <div class="activity-content">
                            <p>Novo procedimento aprovado</p>
                            <span class="activity-time">Ontem</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getAuditsContent() {
        return `
            <div class="page-placeholder">
                <div class="placeholder-icon">
                    <i class="fas fa-clipboard-check"></i>
                </div>
                <h2>Módulo de Auditorias</h2>
                <p>Funcionalidade em desenvolvimento. Aqui você poderá:</p>
                <ul>
                    <li>Agendar auditorias</li>
                    <li>Registrar resultados</li>
                    <li>Acompanhar cronograma</li>
                    <li>Gerar relatórios</li>
                </ul>
            </div>
        `;
    }

    getNonConformitiesContent() {
        return `
            <div class="page-placeholder">
                <div class="placeholder-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h2>Módulo de Não Conformidades</h2>
                <p>Funcionalidade em desenvolvimento. Aqui você poderá:</p>
                <ul>
                    <li>Registrar não conformidades</li>
                    <li>Classificar por severidade</li>
                    <li>Acompanhar resolução</li>
                    <li>Análise de tendências</li>
                </ul>
            </div>
        `;
    }

    getCorrectiveActionsContent() {
        return `
            <div class="page-placeholder">
                <div class="placeholder-icon">
                    <i class="fas fa-tools"></i>
                </div>
                <h2>Módulo de Ações Corretivas</h2>
                <p>Funcionalidade em desenvolvimento. Aqui você poderá:</p>
                <ul>
                    <li>Planejar ações corretivas</li>
                    <li>Definir responsáveis</li>
                    <li>Acompanhar prazos</li>
                    <li>Verificar eficácia</li>
                </ul>
            </div>
        `;
    }

    getPreventiveActionsContent() {
        return `
            <div class="page-placeholder">
                <div class="placeholder-icon">
                    <i class="fas fa-shield-alt"></i>
                </div>
                <h2>Módulo de Ações Preventivas</h2>
                <p>Funcionalidade em desenvolvimento. Aqui você poderá:</p>
                <ul>
                    <li>Identificar riscos</li>
                    <li>Planejar ações preventivas</li>
                    <li>Monitorar implementação</li>
                    <li>Avaliar efetividade</li>
                </ul>
            </div>
        `;
    }

    getProceduresContent() {
        return `
            <div class="page-placeholder">
                <div class="placeholder-icon">
                    <i class="fas fa-file-alt"></i>
                </div>
                <h2>Módulo de Procedimentos</h2>
                <p>Funcionalidade em desenvolvimento. Aqui você poderá:</p>
                <ul>
                    <li>Gerenciar procedimentos</li>
                    <li>Controle de versões</li>
                    <li>Aprovação de documentos</li>
                    <li>Distribuição eletrônica</li>
                </ul>
            </div>
        `;
    }

    getWorkInstructionsContent() {
        return `
            <div class="page-placeholder">
                <div class="placeholder-icon">
                    <i class="fas fa-list-ol"></i>
                </div>
                <h2>Módulo de Instruções de Trabalho</h2>
                <p>Funcionalidade em desenvolvimento. Aqui você poderá:</p>
                <ul>
                    <li>Criar instruções detalhadas</li>
                    <li>Atualizar procedimentos</li>
                    <li>Treinamento de equipe</li>
                    <li>Controle de acesso</li>
                </ul>
            </div>
        `;
    }

    getFormsContent() {
        return `
            <div class="page-placeholder">
                <div class="placeholder-icon">
                    <i class="fas fa-file-signature"></i>
                </div>
                <h2>Módulo de Formulários</h2>
                <p>Funcionalidade em desenvolvimento. Aqui você poderá:</p>
                <ul>
                    <li>Criar formulários personalizados</li>
                    <li>Coletar dados</li>
                    <li>Análise de respostas</li>
                    <li>Exportação de dados</li>
                </ul>
            </div>
        `;
    }

    getReportsContent() {
        return `
            <div class="page-placeholder">
                <div class="placeholder-icon">
                    <i class="fas fa-chart-bar"></i>
                </div>
                <h2>Módulo de Relatórios</h2>
                <p>Funcionalidade em desenvolvimento. Aqui você poderá:</p>
                <ul>
                    <li>Gerar relatórios automáticos</li>
                    <li>Personalizar visualizações</li>
                    <li>Agendar envios</li>
                    <li>Exportar em diversos formatos</li>
                </ul>
            </div>
        `;
    }

    getAnalyticsContent() {
        return `
            <div class="page-placeholder">
                <div class="placeholder-icon">
                    <i class="fas fa-chart-pie"></i>
                </div>
                <h2>Módulo de Análises</h2>
                <p>Funcionalidade em desenvolvimento. Aqui você poderá:</p>
                <ul>
                    <li>Análise estatística</li>
                    <li>Identificação de tendências</li>
                    <li>Dashboards interativos</li>
                    <li>Previsões e projeções</li>
                </ul>
            </div>
        `;
    }

    getUsersContent() {
        return `
            <div class="page-placeholder">
                <div class="placeholder-icon">
                    <i class="fas fa-users"></i>
                </div>
                <h2>Módulo de Usuários</h2>
                <p>Funcionalidade em desenvolvimento. Aqui você poderá:</p>
                <ul>
                    <li>Gerenciar usuários</li>
                    <li>Definir permissões</li>
                    <li>Controle de acesso</li>
                    <li>Histórico de atividades</li>
                </ul>
            </div>
        `;
    }

    getSettingsContent() {
        return `
            <div class="page-placeholder">
                <div class="placeholder-icon">
                    <i class="fas fa-cog"></i>
                </div>
                <h2>Módulo de Configurações</h2>
                <p>Funcionalidade em desenvolvimento. Aqui você poderá:</p>
                <ul>
                    <li>Configurar sistema</li>
                    <li>Personalizar interface</li>
                    <li>Gerenciar integrações</li>
                    <li>Backup e restauração</li>
                </ul>
            </div>
        `;
    }
}

// Estilos adicionais para placeholders
const additionalStyles = `
    .page-placeholder {
        background: white;
        border-radius: 12px;
        padding: 3rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e1e5e9;
    }
    
    .placeholder-icon {
        width: 80px;
        height: 80px;
        margin: 0 auto 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        color: white;
    }
    
    .page-placeholder h2 {
        color: #2c3e50;
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }
    
    .page-placeholder p {
        color: #7f8c8d;
        margin-bottom: 1.5rem;
        font-size: 1.1rem;
    }
    
    .page-placeholder ul {
        text-align: left;
        max-width: 400px;
        margin: 0 auto;
        color: #5a6c7d;
    }
    
    .page-placeholder li {
        margin-bottom: 0.5rem;
        padding-left: 1rem;
        position: relative;
    }
    
    .page-placeholder li:before {
        content: "✓";
        position: absolute;
        left: 0;
        color: #667eea;
        font-weight: bold;
    }
`;

// Adiciona estilos adicionais
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Inicializa a aplicação quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    new QManager();
});

// Adiciona funcionalidade de responsividade
window.addEventListener('resize', () => {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (window.innerWidth <= 768) {
        sidebar.classList.add('collapsed');
        mainContent.classList.add('expanded');
    } else {
        sidebar.classList.remove('collapsed');
        mainContent.classList.remove('expanded');
    }
});