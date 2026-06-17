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
// ========================================
// BUSCADOR Y FILTROS DE INVENTARIO
// ========================================

function filtrarInventario() {
    const textoBuscar = document.getElementById('buscar')?.value.toLowerCase() || '';
    const categoriaSeleccionada = document.getElementById('filtro-categoria')?.value.toLowerCase() || '';
    const estadoSeleccionado = document.getElementById('filtro-estado')?.value.toLowerCase() || '';
    const filas = document.querySelectorAll('#tabla-productos tr');

    filas.forEach(fila => {
        const nombre = fila.querySelector('td:nth-child(2)')?.textContent.toLowerCase() || '';
        const categoria = fila.querySelector('td:nth-child(3)')?.textContent.toLowerCase() || '';
        const estado = fila.querySelector('td:nth-child(7)')?.textContent.toLowerCase() || '';

        const coincideTexto     = nombre.includes(textoBuscar);
        const coincideCategoria = categoriaSeleccionada === '' || categoria.includes(categoriaSeleccionada);
        const coincideEstado    = estadoSeleccionado === '' || estado.includes(estadoSeleccionado);

        fila.style.display = (coincideTexto && coincideCategoria && coincideEstado) ? '' : 'none';
    });
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('buscar')?.addEventListener('input', filtrarInventario);
    document.getElementById('filtro-categoria')?.addEventListener('change', filtrarInventario);
    document.getElementById('filtro-estado')?.addEventListener('change', filtrarInventario);
});
// ========================================
// MODAL AJUSTAR STOCK
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[data-id]').forEach(btn => {
        btn.addEventListener('click', function() {
            const id     = this.getAttribute('data-id');
            const nombre = this.getAttribute('data-nombre');
            const stock  = this.getAttribute('data-stock');

            document.getElementById('modal-nombre-producto').textContent = nombre;
            document.getElementById('modal-stock-actual').textContent    = stock;
            document.getElementById('form-ajustar-stock').action         = `/inventario/ajustar-stock/${id}/`;

            M.FormSelect.init(document.querySelectorAll('select'));
        });
    });
});
