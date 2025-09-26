const botoes = document.querySelectorAll('.cont_botoes .btn');
var botaoAtivo = 0
const botaoAtualizar = document.querySelectorAll('.btn.atualizar');

// chama a verificação a cada 1 segundo (1000 ms)
setInterval(verificarUsuario, 1000);

// chama uma vez imediatamente para não esperar 1s
verificarUsuario();

var nClaim = 0;
let usuarioPodeArrastar = false;

document.getElementById("telaErro").addEventListener("click", function (event) {
    event.stopPropagation(); // evita afetar outros elementos
});

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
        <p>Redirecionando para a página de suporte em <span id="tempoErro">5</span> segundos...</p>
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

        carregarTabela(); // chama após saber o nível
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

    fetch('/dados')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('tabela-body');
            tbody.innerHTML = '';

            data.forEach(item => {
                // console.log(item.class_BU);
                if (item.class_BU != null) {
                    return; // pula se for diferente de null
                }
                contador++;

                const row = document.createElement('tr');
                row.setAttribute('data-numero-nota', item.numero_nota);

                row.innerHTML = `
                    <td>${item.seq_exec}</td>
                    <td>${item.tipo_nota}</td>
                    <td>${item.numero_nota}</td>
                    <td>${item.nome_lista}</td>
                    <td>${item.descricao}</td>                
                  `;
                row.addEventListener('click', (event) => {
                    event.stopPropagation();
                    const div = document.getElementById('minhaDiv');
                    const conteudo = document.getElementById('conteudoDiv');

                    div.style.display = 'none';

                    setTimeout(() => {
                        // Verifica se class_BU está vazio ou null
                        // if (!item.class_BU || item.class_BU.trim() === '') {
                        if (!item.class_BU?.trim()) {
                            conteudo.innerHTML = `
                                <div class="block1">
                                    <div class= "blockuniq">
                                        <div class="block2">
                                            <strong>Nota:</strong> ${item.numero_nota}<br>
                                            <strong>Cliente:</strong> ${item.cliente}<br>
                                            <strong>Descrição:</strong> ${item.descricao}<br>
                                            <strong>Notificador:</strong> ${item.notificador}<br><br>
                                        </div>
                                        <div class="descricao">
                                        <strong>Descrição:</strong>
                                        </div>
                                        <div class="block3">                                    
                                            <div class="scrollable-content">
                                            <br> ${item.content || ''}<br>
                                            </div>
                                        </div>                                        
                                    </div>
                                    <div class="block4">
                                        <ul>
                                            <li><strong>#NT</strong> → Novas Turbinas</li>
                                            <li><strong>#NR</strong> → Novos Redutores</li>
                                            <li><strong>#ST</strong> → Serviços Turbinas</li>
                                            <li><strong>#SR</strong> → Serviços Redutores</li>
                                            <li><strong>#GT</strong> → Gestão Projetos Turbinas</li>
                                            <li><strong>#GR</strong> → Gestão Projetos Redutores</li>
                                            <li><strong>#GST</strong> → Gestão Projetos Serviços Turbinas</li>
                                            <li><strong>#GSR</strong> → Gestão Projetos Serviços Redutores</li>
                                            <li><strong>#AT-T</strong> → Assistência Técnica Turbinas</li>
                                            <li><strong>#AT-R</strong> → Assistência Técnica Redutores</li>
                                        </ul>
                                    </div>
                                </div>
                                <div class="blockfinal">                                                                   
                                    <label for="classBUSelect"><strong>Selecionar BU/TAG:</strong></label>
                                    <select id="classBUSelect">
                                        <option value="">-- Escolha uma opção --</option>
                                        <option value="#NT">#NT → Cálculo Turbina > Cálculo Redutor > Segurança e Controle > Acessórios > Estudos > Documentação</option>
                                        <option value="#NR">#NR → Cálculo Redutor > Segurança e Controle > Estudos > Documentação</option>
                                        <option value="#ST">#ST → Cálculo Turbina > Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças</option>
                                        <option value="#SR">#SR → Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças</option>
                                        <option value="#GT">#GT → Cálculo Turbina > Cálculo Redutor > Segurança e Controle > Acessórios > Estudos > Documentação</option>
                                        <option value="#GR">#GR → Cálculo Redutor > Segurança e Controle > Estudos > Documentação</option>
                                        <option value="#GST">#GST → Cálculo Turbina > Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças</option>
                                        <option value="#GSR">#GSR → Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças</option>
                                        <option value="#AT-T">#AT-T → Cálculo Turbina > Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças</option>
                                        <option value="#AT-R">#AT-R → Cálculo Redutor > Segurança e Controle > Estudos > Partes e Peças</option>
                                    </select><br>
                                    <button class="btnSalvar" onclick="salvarBU('${item.numero_nota}')">Salvar</button>                                    
                                </div>
                                
                            `;
                        } else {
                            conteudo.innerHTML = `
                                <strong>Nota:</strong> ${item.numero_nota}<br>
                                <strong>Cliente:</strong> ${item.cliente}<br>
                                <strong>Descrição:</strong> ${item.descricao}<br>
                                <strong>Notificador:</strong> ${item.notificador}<br>
                                <strong>BU/TAG:</strong> ${item.class_BU}
                            `;
                        }

                        div.style.display = 'block';
                    }, 100);
                });

                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Erro ao carregar os dados:', error);
        });
}

function salvarBU(numeroNota) {
    const valorSelect = document.getElementById('classBUSelect').value;
    console.log(numeroNota);
    console.log(valorSelect);
    if (valorSelect == '') {
        document.getElementById("telaErro").style.display = "flex";
    } else {
        fetch('/salvarBU', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                numero_nota: numeroNota,
                class_bu: valorSelect
            })
        })
            .then(response => {
                if (!response.ok) throw new Error('Erro ao salvar');
                return response.json();
            })
            .then(data => {
                const minhaDiv = document.getElementById('minhaDiv');
                if (minhaDiv) {
                    minhaDiv.style.display = 'none';
                }
                carregarTabela()
            })
            .catch(error => {
                console.error(error);
                alert('Erro ao salvar!');
            });
    }
}

var num = "numero"
function limparDados(idStatus) {
    const status = document.getElementById(idStatus);
    status.textContent = "";
    status.className = "";
}

let intervalId; // Variável global para controlar o loop dos pontos

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

function fecharTelaErro() {
    document.getElementById("telaErro").style.display = "none";
}





