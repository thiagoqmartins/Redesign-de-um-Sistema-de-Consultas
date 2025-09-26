const botoes = document.querySelectorAll('.cont_botoes .btn');
var botaoAtivo = 0
const botaoAtualizar = document.querySelectorAll('.btn.atualizar');

window.addEventListener("beforeunload", function (e) {
    navigator.sendBeacon('/logout');
});

// chama a verificação a cada 1 segundo (1000 ms)
setInterval(verificarUsuario, 1000);

// chama uma vez imediatamente para não esperar 1s
verificarUsuario();
// carregarNoticiasSalvas();

var nClaim = 0;
let usuarioPodeArrastar = false;

document.addEventListener('click', (event) => {
    const div = document.getElementById('minhaDiv');
    if (!div.contains(event.target)) {
        div.style.display = 'none';
    }
});

document.getElementById('fecharDiv').addEventListener('click', () => {
    document.getElementById('minhaDiv').style.display = 'none';
});

document.addEventListener('DOMContentLoaded', () => {
    const campoBusca = document.getElementById('campoBusca');
    const tabelaBody = document.getElementById('tabela-body');

    campoBusca.addEventListener('input', () => {
        const filtro = campoBusca.value.toLowerCase();
        const linhas = tabelaBody.getElementsByTagName('tr');

        for (let i = 0; i < linhas.length; i++) {
            const linha = linhas[i];
            const textoLinha = linha.textContent.toLowerCase();

            if (textoLinha.indexOf(filtro) > -1) {
                linha.style.display = '';
            } else {
                linha.style.display = 'none';
            }
        }
    });
});

function verificarLogin(req, res, next) {
    if (!req.session.usuario) {
        return res.redirect('/aviso'); // ou outra página de login
    }
    next();
}

function verificarUsuario() {
    fetch('/usuario')
        .then(res => {
            if (!res.ok) throw new Error('Não autenticado');
            return res.json();
        })
        .then(data => {
            usuarioPodeArrastar = data.nivel_acesso >= 1;
            if (data.nivel_acesso >= 2) {
                const btnAdmin = document.getElementById('btnAdmin');
                if (btnAdmin) btnAdmin.style.display = 'inline-block';
            } else {
                // Se o nível for menor que 2, esconde o botão
                const btnAdmin = document.getElementById('btnAdmin');
                if (btnAdmin) btnAdmin.style.display = 'none';
            }

        })
        .catch(err => {
            if (err.message === 'Não autenticado') {
                // Mostrar tela de aviso e redirecionar
                mostrarAvisoERedirecionar();
            } else if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
                mostrarAvisoErroConexao();
            }
        });
}

function mostrarAvisoERedirecionar() {
    if (document.getElementById('avisoNaoLogado')) return; // evita duplicar aviso

    const aviso = document.createElement('div');
    aviso.id = 'avisoNaoLogado';
    aviso.style.zIndex = 9999;
    aviso.style.position = 'fixed';
    aviso.style.top = 0;
    aviso.style.left = 0;
    aviso.style.width = '100vw';
    aviso.style.height = '100vh';
    aviso.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    aviso.style.color = 'white';
    aviso.style.display = 'flex';
    aviso.style.justifyContent = 'center';
    aviso.style.alignItems = 'center';
    aviso.style.fontSize = '24px';
    aviso.style.flexDirection = 'column';
    aviso.innerHTML = `
        <p>Você não está logado.</p>
        <p>Redirecionando para a tela de login em <span id="tempo">3</span> segundos...</p>
    `;
    document.body.appendChild(aviso);

    let segundos = 3;
    const intervalo = setInterval(() => {
        segundos--;
        document.getElementById('tempo').textContent = segundos;
        if (segundos <= 0) {
            clearInterval(intervalo);
            window.location.href = '/login';
        }
    }, 1000);
}

function mostrarAvisoErroConexao() {
    if (document.getElementById('avisoErroConexao')) return; // evita duplicar aviso

    const aviso = document.createElement('div');
    aviso.id = 'avisoErroConexao';
    aviso.style.zIndex = 9999;
    aviso.style.position = 'fixed';
    aviso.style.top = 0;
    aviso.style.left = 0;
    aviso.style.width = '100vw';
    aviso.style.height = '100vh';
    aviso.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
    aviso.style.color = 'white';
    aviso.style.display = 'flex';
    aviso.style.justifyContent = 'center';
    aviso.style.alignItems = 'center';
    aviso.style.fontSize = '24px';
    aviso.style.flexDirection = 'column';
    aviso.style.textAlign = 'center';
    aviso.innerHTML = `
        <p>Não foi possível conectar ao servidor.</p>
        <p>Redirecionando em <span id="tempoErro">5</span> segundos...</p>
    `;
    document.body.appendChild(aviso);

    let segundos = 5;
    const intervalo = setInterval(() => {
        segundos--;
        document.getElementById('tempoErro').textContent = segundos;
        if (segundos <= 0) {
            clearInterval(intervalo);
            window.location.href = 'https://weg365.sharepoint.com/teams/BR-WEN-TGM';  // coloque a URL desejada aqui
        }
    }, 1000);
}

fetch('/usuario')
    .then(res => {
        if (!res.ok) throw new Error('Não autenticado');
        return res.json();
    })
    .then(data => {
        usuarioPodeArrastar = data.nivel_acesso >= 1;

        // 👇 Mostrar botão de administração se for nível 2 ou mais
        if (data.nivel_acesso >= 2) {
            const btnAdmin = document.getElementById('btnAdmin');
            if (btnAdmin) btnAdmin.style.display = 'inline-block';
        }
        exibeAdministracao(data.nivel_acesso);
        novosUsuario();
        carregarTabela();

    })
    .catch(err => {
        if (err.message === 'Não autenticado') {
            // Cria uma "tela" sobreposta
            const aviso = document.createElement('div');
            aviso.style.zIndex = 9999;
            aviso.style.position = 'fixed';
            aviso.style.top = 0;
            aviso.style.left = 0;
            aviso.style.width = '100vw';
            aviso.style.height = '100vh';
            aviso.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
            aviso.style.color = 'white';
            aviso.style.display = 'flex';
            aviso.style.justifyContent = 'center';
            aviso.style.alignItems = 'center';
            aviso.style.fontSize = '24px';
            aviso.style.flexDirection = 'column';
            aviso.innerHTML = `
                <p>Você não está logado.</p>
                <p>Redirecionando para a tela de login em <span id="tempo">3</span> segundos...</p>
            `;
            document.body.appendChild(aviso);

            // Contador regressivo
            let segundos = 3;
            const intervalo = setInterval(() => {
                segundos--;
                document.getElementById('tempo').textContent = segundos;
                if (segundos <= 0) {
                    clearInterval(intervalo);
                    window.location.href = '/login';
                }
            }, 1000);
        } else {
            console.warn('Erro ao verificar nível de acesso:', err);
            carregarTabela(); // ainda pode carregar só visualmente
        }
    });

function carregarTabela() {
    let contador = 0;
    let ordemAntes = [];

    fetch('/dados')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('tabela-body');
            tbody.innerHTML = '';

            data.forEach(item => {
                // contador++;
                let bu = item.class_BU
                if (!bu) {
                    contador++;
                } else {

                    const row = document.createElement('tr');
                    row.setAttribute('data-numero-nota', item.numero_nota);


                    if (usuarioPodeArrastar) {
                        row.setAttribute('draggable', true);
                    }

                    row.innerHTML = `
                    <td>${item.seq_exec}</td>
                    <td>${item.tipo_nota}</td>
                    <td>${item.numero_nota}</td>
                    <td>${item.nome_lista}</td>
                    <td>${item.descricao}</td>
                    <td>${item.notificador}</td>
                    <td>${item.data_criacao ? item.data_criacao.replace(/\./g, "/") : ''}</td>
                `;

                    // document.getElementById('teste').textContent = contador;

                    // Clique para abrir detalhes
                    row.addEventListener('click', (event) => {
                        event.stopPropagation();
                        const div = document.getElementById('minhaDiv');
                        const conteudo = document.getElementById('conteudoDiv');

                        div.style.display = 'none';
                        div.style.height = 'auto';
                        setTimeout(() => {
                            let porcentagem = item["numero_ordem"];
                            if (porcentagem > 100) porcentagem = 100;

                            conteudo.innerHTML = `
                            <strong style="font-size: 14px">Nota:</strong> <span style="font-size: 12px">${item.numero_nota}</span><br>
                            <strong style="font-size: 14px">Cliente:</strong> <span style="font-size: 12px">${item.cliente}</span><br>
                            <strong style="font-size: 14px">Descrição:</strong> <span style="font-size: 12px">${item.descricao}</span><br>
                            <strong style="font-size: 14px">Notificador:</strong> <span style="font-size: 12px">${item.notificador}</span><br>
                            <span style="font-size: 12px;"> ${item.content}</span>                        
                            <label>Progresso:</label>
                            <div class="barra-container">
                                <div class="barra-progresso" style="width: ${porcentagem}%;">${porcentagem}%</div>
                            </div>
                        `;
                            document.documentElement.style.setProperty('--largura-barra', porcentagem);
                            div.style.display = 'block';
                        }, 100);
                    });

                    if (usuarioPodeArrastar) {
                        // Eventos de arrastar
                        row.addEventListener('dragstart', () => {
                            row.classList.add('dragging');

                            // Captura a ordem ANTES de arrastar
                            ordemAntes = Array.from(document.querySelectorAll('#tabela-body tr')).map(linha => ({
                                numero_nota: linha.getAttribute('data-numero-nota')
                            }));
                        });

                        row.addEventListener('dragend', () => {
                            row.classList.remove('dragging');
                            atualizarOrdemNoServidor();
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
                    }

                    tbody.appendChild(row);
                }
            });
            const nTotal = document.getElementById('nTotal');
            if (contador > 0) {
                nTotal.style.display = '';
                nTotal.innerHTML = ` ${contador}`
            } else {
                nTotal.style.display = 'none';
            }

        })

        .catch(error => {
            console.error('Erro ao carregar os dados:', error);
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
    function atualizarOrdemNoServidor() {
        const linhas = document.querySelectorAll('#tabela-body tr');
        const novaOrdem = [];

        linhas.forEach((linha, index) => {
            const numeroNota = linha.getAttribute('data-numero-nota');
            novaOrdem.push({
                numero_nota: numeroNota,
                cliente: linha.cells[3].textContent,
                nova_seq_exec: index + 1
            });
        });

        // Gera resumo das mudanças comparando "antes" e "depois"
        const mudancas = novaOrdem.map((nova, index) => {
            const antes = ordemAntes.find(item => item.numero_nota === nova.numero_nota);
            const posicaoAntiga = ordemAntes.findIndex(item => item.numero_nota === nova.numero_nota) + 1;
            const posicaoNova = index + 1;

            //     if (posicaoAntiga !== posicaoNova) {
            //         return `${nova.numero_nota} - ${nova.cliente} | Para ${posicaoNova}`;
            //         // return `${nova.numero_nota} - ${nova.cliente}: De ${posicaoAntiga} Para ${posicaoNova}`;
            //     } else {
            //         return null; // posição não mudou
            //     }
            // }).filter(m => m !== null);

            if (posicaoAntiga !== posicaoNova) {
                return {
                    numero_nota: nova.numero_nota,
                    cliente: nova.cliente,
                    anterior: posicaoAntiga,
                    novo: posicaoNova
                };
            } else {
                return null;
            }
        }).filter(m => m !== null);
        // Se não houve mudanças reais, não faz nada
        if (mudancas.length === 0) {
            Swal.fire('Sem mudanças', 'A ordem das notas não foi alterada.', 'info');
            return;
        }

        // Diálogo com visual das mudanças
        Swal.fire({
            title: 'Confirmar alteração de ordem?',
            // html: `<div style="text-align:left;max-height:200px;overflow:auto; font-size: 1rem;">
            //     <strong>As seguintes alterações serão feitas:</strong><br><br>
            //     ${mudancas.map(m => `${m}`).join('<br>')}
            //    </div>`,
            html: `<div style="text-align:left; max-height:200px; font-size: 1rem;">
                <strong>As seguintes alterações serão feitas:</strong><br><br>
                <span style="font-weight: bold; color: #333;">Total de mudanças: ${mudancas.length}</span><br><br> 
                <div style ="overflow:auto;">               
                <table style="width:100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th style="text-align:left; border-bottom: 1px solid #ccc; padding: 4px; font-size: 0.9rem;">Claim</th>
                            <th style="text-align:left; border-bottom: 1px solid #ccc; padding: 4px; font-size: 0.9rem;">Cliente</th>
                            <th style="text-align:left; border-bottom: 1px solid #ccc; padding: 4px; font-size: 0.9rem;">Nova Posição</th>                            
                        </tr>
                    </thead>
                    <tbody>
                        ${mudancas.map(m => `
                            <tr>
                                <td style="padding: 4px; border-bottom: 1px solid #eee; font-size: 0.8rem;">${m.numero_nota}</td>
                                <td style="padding: 4px; border-bottom: 1px solid #eee; text-align:left; font-size: 0.8rem;">${m.cliente}</td>
                                <td style="padding: 4px; border-bottom: 1px solid #eee; font-size: 0.8rem;">${m.novo}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
                <div>
            </div>`,
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: 'Sim, atualizar',
            cancelButtonText: 'Cancelar',
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            // customClass: {
            //     icon: 'icone-tamanho',
            // }
        }).then((result) => {
            if (result.isConfirmed) {
                fetch('/atualizar-ordem', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        antes: ordemAntes,
                        depois: novaOrdem
                    })
                })
                    .then(res => res.json())
                    .then(json => {
                        Swal.fire('Sucesso!', 'A ordem foi atualizada.', 'success');
                        carregarTabela();
                    })
                    .catch(err => {
                        console.error('Erro ao atualizar ordem:', err);
                        Swal.fire('Erro', 'Não foi possível atualizar a ordem.', 'error');
                    });
            } else {
                carregarTabela(); // Reverte visualmente
            }
        });
    }
}


function novosUsuario() {
    fetch("/usuarios")
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector('tbody');
            tbody.innerHTML = '';

            let contador = 0;
            const uTotal = document.getElementById('uTotal');

            // Contar quantos têm status === "2"
            data.forEach(usuario => {
                if (usuario.status === "2" || usuario.status === 2) {
                    contador++;
                }
            });

            // Atualizar visualização
            if (contador > 0) {
                uTotal.style.display = '';
                uTotal.innerHTML = `${contador}`;
            } else {
                uTotal.style.display = 'none';
            }
        })
        .catch(erro => {
            console.error('Erro ao carregar usuários:', erro);
        });
}

// var num = "numero"
function limparDados(idStatus) {
    const status = document.getElementById(idStatus);
    status.textContent = "";
    status.className = "";
}

let intervalId; // Variável global para controlar o loop dos pontos

function mostrarLoading() {
    const loading = document.getElementById('loading');
    const texto = document.getElementById('loading-text');
    const spinner = document.getElementById('spinner');

    texto.innerHTML = "Processando.<br>Por favor, aguarde!<br>.";

    spinner.style.display = "block";
    loading.style.display = 'flex';

    let pontos = '.';

    // Limpa qualquer intervalo anterior
    clearInterval(intervalId);

    intervalId = setInterval(() => {
        pontos = pontos.length < 50 ? pontos + '.' : '.';
        texto.innerHTML = `Processando.<br>Por favor, aguarde!<br>${pontos}`;
    }, 500);

}

function esconderLoading(mensagem) {
    // const erro = document.getElementById('mensagem-erro');
    const loading = document.getElementById('loading');
    const texto = document.getElementById('loading-text');
    const spinner = document.getElementById('spinner');
    clearInterval(intervalId);

    if (mensagem && mensagem.trim() === "Concluído com sucesso") {
        spinner.style.display = 'none';
        texto.innerHTML = `✅ ${mensagem}`;
        console.log('✅ Mensagem1:', mensagem);
        setTimeout(() => {
            loading.style.display = 'none';
            spinner.style.display = 'none';
            texto.innerHTML = ''; // Limpa o texto de erro   
            location.reload();
        }, 1000);
    } else {
        spinner.style.display = 'none';
        texto.innerHTML = `✅ ${mensagem}`;
        console.log('✅ Mensagem2:', mensagem);
        setTimeout(() => {
            loading.style.display = 'none';
            spinner.style.display = 'none';
            texto.innerHTML = ''; // Limpa o texto de erro   
        }, 500);
    }

    // spinner.style.display = 'none';
    // texto.innerHTML = `✅ ${mensagem}`;
    // console.log('✅ Mensagem:', mensagem);
    // setTimeout(() => {
    //     loading.style.display = 'none';
    //     spinner.style.display = 'none';
    //     texto.innerHTML = ''; // Limpa o texto de erro   
    //     if (mensagem && mensagem.trim() !== "Concluído com sucesso") {
    //         location.reload();
    //         console.log('🔄 Recarregando a página após concluir a operação.');
    //     }

    // }, 1000);

}

function exibirErro(mensagem) {
    // const erro = document.getElementById('mensagem-erro');
    const loading = document.getElementById('loading');
    const texto = document.getElementById('loading-text');
    const spinner = document.getElementById('spinner');
    clearInterval(intervalId);

    spinner.style.display = 'none';
    texto.innerHTML = `⚠️ ${mensagem}`;

    setTimeout(() => {
        loading.style.display = 'none';
        spinner.style.display = 'none';
        texto.innerHTML = ''; // Limpa o texto de erro
        // Interrompe o loop dos pontos quando fecha o loading

    }, 1000);

}

function atualizarDados(transaction) {
    transaction = transaction || "IQS9"; // Define um valor padrão se não for passado    
    mostrarLoading(); // 👉 Mostra a tela de loading
    fetch('/executar-python-iqs9', {

        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            campo: transaction,
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log('📦 Dados recebidos:', data);

            if (!data || !data.resultado || data.resultado !== 'Concluído') {
                throw new Error('Dados inválidos ou operação não concluída.');
            } else {
                console.log('✅ Operação concluída com sucesso:', data);
                esconderLoading('Concluído com sucesso:'); // 👉 Esconde o loading quando finalizar
            }
        })
        .catch(error => {
            console.error('❌ Erro ao atualizar os dados:', error);
            exibirErro('Ocorreu um erro ao processar os dados.');
        });


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

    if (!numero || numero.length !== 8) {
        elementId.textContent = "❌ insira um número.";
        elementId.className = "erro";
        elementId.id = oldElementId;

        return;
    }

    elementId.textContent = "⏳ Executando...";
    elementId.className = "executando";
    mostrarLoading(); // 👉 Mostra a tela de loading

    fetch('/executar-python', {

        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            valor: numero,
            campo: idCampo,
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log('🔵 Resposta do backend:', data);
            esconderLoading(); // 👉 Esconde o loading quando finalizar  
            elementId.textContent = data.resultadoJson;
            elementId.className = "sucesso";
            elementId.id = oldElementId;
        })
        .catch(error => {
            esconderLoading(); // 👉 Esconde o loading quando finalizar  
            elementId.textContent = ("❌ " + error.message);
            elementId.className = "erro";
            elementId.id = oldElementId;
        });
}

function executarPython2(nClaim) {
    const numero = nClaim
    mostrarLoading(); // 👉 Mostra a tela de loading

    fetch('/executar-python', {

        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            valor: numero,
            campo: "clm3",
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log('📦 Dados recebidos:', data);

            if (!data || !data.resultadoJson || data.resultadoJson !== 'Concluído') {
                throw new Error('Dados inválidos ou operação não concluída.');
            } else {
                console.log('✅ Operação concluída com sucesso1:', data);
                esconderLoading("Claim visualizada no SAP"); // 👉 Esconde o loading quando finalizar
            }
        })
        .catch(error => {
            console.error('❌ Erro');
            console.error('❌ Erro ao atualizar os dados:', error);
            exibirErro('Ocorreu um erro ao processar os dados.');
        });
}
// Chama a função para carregar as notícias salvas
// function carregarNoticiasSalvas() {
//     fetch("/noticias")
//         .then(res => res.json())
//         .then(data => {
//             const banner = document.getElementById("noticiasBanner");

//             if (!data || !data.length) {
//                 banner.innerText = "Nenhuma notícia disponível.";
//                 return;
//             }

//             banner.innerHTML = "";

//             data.forEach(noticia => {
//                 const item = document.createElement("span");
//                 item.innerHTML = `<a href="${noticia.url}" target="_blank" style="color:#fff; text-decoration:none;"><strong>${noticia.title}</strong></a>`;
//                 banner.appendChild(item);
//             });

//             // Clone opcional para rolagem contínua
//             // const clone = banner.cloneNode(true);
//             // banner.appendChild(clone);
//         })
//         .catch(error => {
//             document.getElementById("noticiasBanner").innerText = "Erro ao carregar notícias.";
//             console.error("Erro:", error);
//         });
// }

function chamarAtualizar() {
    fetch('/atualizar', {
        method: 'POST'
    })
        .then(res => res.json())
        .then(data => {
            console.log(data);
            // alert('Atualizado com sucesso!');
            location.reload(); // Atualiza a página atual

        })
        .catch(err => console.error('Erro:', err));
}

function criarZZ() {
    console.log("Criando ZZ...");
    fetch('/criarZZ', {
        method: 'POST'
    })
        .then(res => res.json())
        .then(data => {
            console.log(data);
            // alert('Atualizado com sucesso!');
            // location.reload(); // Atualiza a página atual

        })
        .catch(err => console.error('Erro:', err));
}

async function carregarNoticias() {
    try {
        const resposta = await fetch('/noticias.json');
        const noticias = await resposta.json();

        const noticiasBanner = document.getElementById("noticiasBanner");

        // Use o título com link para montar as notícias
        const conteudo = noticias.map(n => `
      <span>
        <a href="${n.url}" target="_blank" rel="noopener noreferrer" style="color: inherit; text-decoration: none;">
          ${n.title}
        </a>
      </span>
    `).join('');

        noticiasBanner.innerHTML = conteudo + conteudo; // duplicar para scroll contínuo

        requestAnimationFrame(() => {
            const larguraTotal = noticiasBanner.scrollWidth / 2;
            const velocidade = 80; // px/s
            const duracao = larguraTotal / velocidade;

            noticiasBanner.style.animation = `deslizamento ${duracao}s linear infinite`;
        });

    } catch (erro) {
        console.error("Erro ao carregar as notícias:", erro);
    }
}

carregarNoticias()

function exibeAdministracao(nivel) {

    const barraAdm = document.getElementById("container-botoes");

    if (nivel >= 2) {
        barraAdm.style.display = ''
    } else {
        barraAdm.style.display = 'none'
    }

    // if (nivel === 2) {
    if (nivel === 2) {
        barraAdm.innerHTML += `
        <div class="tooltip">
            <div class="divTriagem">
                <div class="nTotal" id="nTotal">
                </div>
                <button id="btnTriagem" class="admin-button" onclick="window.location.href='/triagem'">
                    <span class="material-icons">grading</span>
                </button>
            </div>
            <span class="tooltip-text">Triagem</span>
        </div>
        <div class="tooltip">
            <button id="btnAtualizar" class="admin-button" onclick="chamarAtualizar()">
                <span class="material-icons">sync</span>
            </button>
            <span class="tooltip-text">Atualizar</span>
        </div>
            `;
    }

    if (nivel >= 3) {
        barraAdm.innerHTML += `
        <div class="tooltip">
            <div class="divTriagem">
                <div class="adm" id="adm" style="display: none;">
                </div>
                <button id="btnBD" class="admin-button" >
                    <span class="material-icons">storage</span>
                </button>
                <span class="tooltip-text">Banco de Dados</span>
        </div>
        </div>
        <div class="tooltip">
            <div class="divTriagem">
                <div class="adm" id="adm" style="display: none;">
                </div>
                <button id="btnAdm" class="admin-button" onclick="window.location.href='/admin'">
                    <span class="material-icons">settings</span>
                </button>
                <span class="tooltip-text">Administração</span>
            </div>
        </div>
        <div class="tooltip">
            <div class="divTriagem">
                <div class="nTotal" id="uTotal" style="display: none;">
                </div>
                <button id="btnAdmin" class="admin-button" onclick="window.location.href='/acessControl'">
                    <span class="material-icons">person</span>
                </button>
                <span class="tooltip-text">Controle de Acessos</span>
            </div>
        </div>
    <div class="tooltip">
        <div class="divTriagem">
            <div class="nTotal" id="nTotal">
            </div>
            <button id="btnTriagem" class="admin-button" onclick="window.location.href='/triagem'">
                <span class="material-icons">grading</span>
            </button>
        </div>
        <span class="tooltip-text">Triagem</span>
    </div>
    <div class="tooltip">
        <button id="btnAtualizar" class="admin-button" onclick="chamarAtualizar()">
            <span class="material-icons">sync</span>
        </button>
        <span class="tooltip-text">Atualizar</span>
    </div>
        <div class="tooltip">
        <button id="btnCriarZZ" class="admin-button" onclick="criarZZ()">
            <span class="material-icons">add_circle</span>
        </button>
        <span class="tooltip-text">Criar ZZ</span>
    </div>
            `;
    }
}

document.addEventListener("click", (e) => {
    if (e.target.closest("#btnBD")) {
        fetch("/abrir-sqlite")
            .then(() => {
                window.open("http://127.0.0.1:8080", "_blank");
            })
            .catch(err => console.error("Erro:", err));
    }
});




