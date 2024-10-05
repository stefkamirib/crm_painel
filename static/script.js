const thElements = document.querySelectorAll('th');

thElements.forEach(th => {
    const resizer = document.createElement('div');
    resizer.classList.add('resizer');
    th.appendChild(resizer);

    let isResizing = false;

    resizer.addEventListener('mousedown', (e) => {
        isResizing = true;
        startX = e.pageX; // Armazena a posição inicial do mouse
        startWidth = th.offsetWidth; // Armazena a largura inicial da coluna
        e.preventDefault(); // Previne seleção de texto durante o redimensionamento
    });

    // Adiciona o evento de mousemove no documento
    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;
        const newWidth = startWidth + (e.pageX - startX);
        if (newWidth > 50) { // Define uma largura mínima de 50px
            th.style.width = `${newWidth}px`;
        }
    });

    // Finaliza o redimensionamento
    document.addEventListener('mouseup', () => {
        isResizing = false;
    });
});
