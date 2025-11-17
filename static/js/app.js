// ORION - Sistema de Gestión de Proyectos

// Verificar estado del sistema al cargar
async function checkSystemStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        console.log('Sistema ORION:', status);
    } catch (error) {
        console.error('Error de conexión:', error);
    }
}

// Animaciones de la interfaz
function initializeAnimations() {
    // Animación del título
    const title = document.querySelector('.orion-title');
    if (title) {
        title.style.opacity = '0';
        setTimeout(() => {
            title.style.transition = 'opacity 1s ease-in';
            title.style.opacity = '1';
        }, 300);
    }

    // Animación de las tarjetas estadísticas
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease-in, transform 0.5s ease-in';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * (index + 1));
    });

    // Hover efects para botones de acción
    const actionButtons = document.querySelectorAll('.action-button');
    actionButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// Auto-refresh de estadísticas cada 30 segundos
function startAutoRefresh() {
    setInterval(() => {
        checkSystemStatus();
    }, 30000);
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    initializeAnimations();
    checkSystemStatus();
    startAutoRefresh();
    console.log('ORION - Sistema de Gestión de Proyectos iniciado');
});
