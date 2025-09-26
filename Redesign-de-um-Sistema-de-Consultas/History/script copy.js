const botoes = document.querySelectorAll('.cont_botoes .btn');
var botaoAtivo = 0

botoes.forEach(botao => {
    botao.addEventListener('click', () => {
        // Remove a classe 'ativo' de todos os botões
        botoes.forEach(btn => btn.classList.remove('ativo'));

        // Adiciona a classe 'ativo' ao botão clicado
        botao.classList.add('ativo');

        // Se quiser fazer algo com o texto ou índice:
        // console.log(`Botão ativo: ${botao.textContent}`);
        // Ou usar um data-atributo: botao.dataset.tipo, por exemplo

        botaoAtivo = document.querySelector('.cont_botoes .btn.ativo');        
        carregarTabela(botaoAtivo.textContent);

    });
});

var nClaim = 0;
function carregarTabela(botaoAtivo) {
    var unid = botaoAtivo;
    var contador = 0
    console.log(unid);


    if (unid === "Serviços Redutores") {
        unid = "Service TR";
    }else if(unid === "Serviços Turbinas") {
        unid = "Service TU";
    }else if(unid === "Modificação de Projeto") {
        unid = "Gestão de Projetos";
    }



    fetch('teste2.json')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('tabela-body');
            tbody.innerHTML = ''; // Limpa qualquer conteúdo anterior

            data.forEach(item => {
                
                if (item["Campo15"] === unid) {
                  console.log(item["Campo15"]);
                }
                           
                

                if (item["Campo17"] === "Fila" && item["Campo15"] === unid) {
                    contador++;
                    const row = document.createElement('tr');
                    row.innerHTML = `
                <td>${item.ID}</td>
                <td>${item.Tipo}</td>
                <td>${item["Número Nota"]}</td>
                <td>${item.Cliente}</td>
                <td>${item.Descrição}</td>
                <td>${item.Solicitante}</td>
                <td>${item["Data Criação"].replace(/\./g, "/")}</td>
            `;                      

                    // Adiciona o evento de clique na própria linha
                    row.addEventListener('dblclick', () => {
                        // alert(`Número da Claim: ${item["Número Nota"]}`);
                        nClaim = item["Número Nota"];
                        executarPython2(nClaim);
                    });
                    // row.addEventListener('click', () => {
                    //     // Remove a classe 'selected' de todas as linhas
                    //     const rows = document.querySelectorAll('#tabela-body tr');
                    //     rows.forEach(r => r.classList.remove('selected'));

                    //     // Adiciona a classe 'selected' apenas na linha clicada
                    //     row.classList.add('selected');
                    // });

                    //new
                    row.setAttribute('draggable', true); // permite arrastar

                    // Quando começa a arrastar
                    row.addEventListener('dragstart', (e) => {
                        row.classList.add('dragging');
                    });

                    // Quando termina o arrasto
                    row.addEventListener('dragend', () => {
                        row.classList.remove('dragging');
                    });

                    // Durante o arrasto, detectar onde soltar
                    row.addEventListener('dragover', (e) => {
                        e.preventDefault(); // necessário para permitir o drop
                        const draggingRow = document.querySelector('.dragging');
                        const tbody = document.getElementById('tabela-body');
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
            // alert("Número de Claims: " + contador); 
        })
        .catch(error => {
            console.error('Erro ao carregar os dados do JSON:', error);
        });

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
// Adiciona o evento de clique no botão "Executar"
document.getElementById("executar").addEventListener("click", () => { executarPython("MM03"); });
document.getElementById("executar1").addEventListener("click", () => { executarPython("MM02"); });
document.getElementById("MM03").addEventListener("focus", () => { limparDados("status"); });
document.getElementById("MM02").addEventListener("focus", () => { limparDados("status1"); });


document.getElementById("MM03").addEventListener("input", () => {
    const input = document.getElementById("MM03");
    if (input.value.trim() === "") {
        limparDados("status")
        // aqui você pode mostrar uma mensagem ou alterar o estilo, por exemplo
    }
});

document.getElementById("MM02").addEventListener("input", () => {
    const input = document.getElementById("MM02");
    if (input.value.trim() === "") {
        limparDados("status1")
        // aqui você pode mostrar uma mensagem ou alterar o estilo, por exemplo
    }
});

document.getElementById("MM03").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault(); // impede comportamento padrão (tipo enviar formulário)
        document.getElementById("executar").click(); // simula clique no botão
    }
});

document.getElementById("MM02").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        document.getElementById("executar1").click();
    }
});

var num = "numero"
function limparDados(idStatus) {
    const status = document.getElementById(idStatus);
    status.textContent = "";
    status.className = "";
}

function executarPython(idCampo) {
    const numero = document.getElementById(idCampo).value;

    let elementId
    let oldElementId

    if (idCampo === "MM02") {
        elementId = document.getElementById("status1");
        oldElementId = elementId.id
        elementId.id = "status";
    } else if (idCampo === "MM03") {
        elementId = document.getElementById("status");
        oldElementId = elementId.id
        elementId.id = "status";
    }

    // const status = document.getElementById("status");

    if (!numero || numero.length !== 8) {
        elementId.textContent = "❌ insira um número.";
        elementId.className = "erro";
        elementId.id = oldElementId;
        // alert("Por favor, insira um número antes de executar.");
        return;
    }

    elementId.textContent = "⏳ Executando...";
    elementId.className = "executando";

    fetch('http://localhost:3000/executar-python', {

        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            valor: numero,
            campo: idCampo,
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na resposta do servidor.');
                ;
            }
            return response.json();
        })
        .then(data => {
            elementId.textContent = "✅ Concluído!";
            elementId.className = "sucesso";
            elementId.id = oldElementId;
        })
        .catch(error => {
            elementId.textContent = ("❌ " + error.message);
            elementId.className = "erro";
            elementId.id = oldElementId;
        });
}

function executarPython2(nClaim) {
    const numero = nClaim


    fetch('http://localhost:3000/executar-python', {

        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            valor: numero,
            campo: "MM03",
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na resposta do servidor.');
                ;
            }
            return response.json();
        })
        .then(data => {
            // elementId.textContent = "✅ Concluído!";
            // elementId.className = "sucesso";
            // elementId.id = oldElementId;
        })
        .catch(error => {
            // elementId.textContent = ("❌ " + error.message);
            // elementId.className = "erro";
            // elementId.id = oldElementId;
        });
}
