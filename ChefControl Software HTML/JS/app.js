// ========================================
// JAVASCRIPT PERSONALIZADO - CHEFCONTROL
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    
    console.log('ChefControl iniciado correctamente');
    
    var sidenav = document.querySelectorAll('.sidenav');
    M.Sidenav.init(sidenav, { edge: 'left', draggable: true });
    
    var modals = document.querySelectorAll('.modal');
    M.Modal.init(modals, { opacity: 0.5, inDuration: 300, outDuration: 200 });
    
    var selects = document.querySelectorAll('select');
    M.FormSelect.init(selects);
    
    var tooltips = document.querySelectorAll('.tooltipped');
    M.Tooltip.init(tooltips, { position: 'top', delay: 50 });
    
    var dropdowns = document.querySelectorAll('.dropdown-trigger');
    M.Dropdown.init(dropdowns, { coverTrigger: false, constrainWidth: false });
    
    console.log('%c¡Bienvenido a ChefControl!', 'color: #00897b; font-size: 20px; font-weight: bold;');
});

function mostrarNotificacion(mensaje, tipo = 'info') {
    let color = '';
    switch(tipo) {
        case 'success': color = 'green'; break;
        case 'error':   color = 'red';   break;
        case 'warning': color = 'orange'; break;
        default:        color = 'teal';
    }
    M.toast({ html: mensaje, classes: color, displayLength: 4000 });
}
