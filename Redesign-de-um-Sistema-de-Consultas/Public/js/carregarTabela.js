function carregarTabela(botaoAtivo) {
    let unid = botaoAtivo;
    let contador = 0;
    console.log('Unidade selecionada:', unid);

    // Conversões dos nomes
    if (unid === "Serviços Redutores") {
        unid = "Service TR";
    } else if (unid === "Serviços Turbinas") {
        unid = "Service TU";
    } else if (unid === "Modificação de Projeto") {
        unid = "Gestão de Projetos";
    }

    fetch(`/api/dados?unidade=${encodeURIComponent(unid)}`)
        .then(response => {
            if (!response.ok) throw new Error('Erro na resposta da API');
            return response.json();
        })
        .then(data => {
            if (!Array.isArray(data)) {
                console.error('Resposta inesperada da API:', data);
                return;
            }

            const tbody = document.getElementById('tabela-body');
            tbody.innerHTML = '';
            contador = 0;

            data.forEach(item => {
                if (item.status === "FILA" && item.nome_lista === unid) {
                    contador++;

                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${contador}</td>
                        <td>${item.tipo_nota}</td>
                        <td>${item.numero_nota}</td>
                        <td>${item.cliente}</td>
                        <td>${item.descricao}</td>
                        <td>${item.notificador}</td>
                        <td>${item.data_criacao ? item.data_criacao.replace(/\./g, "/") : ''}</td>
                    `;

                    document.getElementById('teste').textContent = contador;

                    // Evento de duplo clique
                    row.addEventListener('dblclick', () => {
                        let nClaim = item.numero_nota;
                        executarPython2(nClaim);
                    });

                    // Configuração para drag & drop
                    row.setAttribute('draggable', true);

                    row.addEventListener('dragstart', () => {
                        row.classList.add('dragging');
                    });

                    row.addEventListener('dragend', () => {
                        row.classList.remove('dragging');
                    });

                    row.addEventListener('dragover', (e) => {
                        e.preventDefault();
                        const draggingRow = document.querySelector('.dragging');
                        const afterElement = getDragAfterElement(tbody, e.clientY);
                        if (afterElement == null) {
                            tbody.appendChild(draggingRow);
                        } else {
                            tbody.insertBefore(draggingRow, afterElement);
                        }
                    });

                    tbody.appendChild(row);
                }
            });

            // Se nenhum item foi carregado
            if (contador === 0) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;">Nenhum dado encontrado para "${unid}" com status FILA.</td></tr>`;
                document.getElementById('teste').textContent = '0';
            }
        })
        .catch(error => {
            console.error('Erro ao carregar os dados do banco:', error);
            alert('Não foi possível carregar os dados. Tente novamente mais tarde.');
        });

    // Função auxiliar para drag & drop
    function getDragAfterElement(container, y) {
        const rows = [...container.querySelectorAll('tr:not(.dragging)')];
        return rows.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }
}
