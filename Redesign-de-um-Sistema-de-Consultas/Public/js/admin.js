// ========== Estado Global ==========
const estadoLinhas = new Map();

// Ordem dos campos (colunas com checkbox)
const campos = [
    'resp_ativo',      // Ativo?
    'Turbinas',
    'Redutores',
    'Novos',
    'Servicos',        // Serviços
    'Calculos',
    'Estudos',
    'Seg_Controle',    // Seg. Controle
    'Documentos',
    'Acessorios'       // Acessórios
];

// ========== Funções Auxiliares ==========

function formatarBR(yyyy_mm_dd) {
    const [y, m, d] = (yyyy_mm_dd || '').split('-');
    if (!y || !m || !d) return yyyy_mm_dd || '';
    return `${d.padStart(2, '0')}/${m.padStart(2, '0')}/${y}`;
}

// Helper: hoje ∈ [inicio, fim] (ambos YYYY-MM-DD). Inclui bordas.
function isHojeDentroPeriodo(inicioStr, fimStr) {
    if (!inicioStr || !fimStr) return false;
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);

    const [yi, mi, di] = inicioStr.split('-').map(Number);
    const [yf, mf, df] = fimStr.split('-').map(Number);
    if (!yi || !mi || !di || !yf || !mf || !df) return false;

    const inicio = new Date(yi, mi - 1, di);
    const fim = new Date(yf, mf - 1, df);
    inicio.setHours(0, 0, 0, 0);
    fim.setHours(0, 0, 0, 0);

    return hoje >= inicio && hoje <= fim;
}

// ========== Toast ==========
function showToast(message, type = '') {
    const el = document.getElementById('toast');
    if (!el) return;
    el.textContent = message;
    el.className = `toast ${type}`.trim();
    el.classList.add('show');
    setTimeout(() => el.classList.remove('show'), 2500);
}

// ========== Dialog de Confirmação ==========
function showConfirmDialog({ title = 'Confirmar ação', message = 'Tem certeza?' } = {}) {
    return new Promise((resolve) => {
        const dlg = document.getElementById('confirm-dialog');
        if (!dlg) {
            resolve(false);
            return;
        }
        const titleEl = document.getElementById('confirm-title');
        const msgEl = document.getElementById('confirm-message');

        if (titleEl) titleEl.textContent = title;
        if (msgEl) msgEl.textContent = message;

        dlg.showModal();

        const onClose = () => {
            dlg.removeEventListener('close', onClose);
            resolve(dlg.returnValue === 'ok'); // true se confirmou
        };
        dlg.addEventListener('close', onClose);
    });
}

function showInfoDialog({ title, message }) {
    return showConfirmDialog({ title, message });
}
// ========== Tooltips do Cabeçalho ==========
// Pega THs por data-campo
function getHeaderCellsMap() {
    const map = new Map();
    const thead = document.querySelector('thead #cabecalho') || document.querySelector('thead tr');
    if (!thead) return map;
    thead.querySelectorAll('th[data-campo]').forEach(th => {
        const campo = th.getAttribute('data-campo');
        map.set(campo, th);
    });
    return map;
}

// Calcula os totais por coluna olhando para estadoLinhas
function calcularTotaisPorColuna() {
    const totais = {};
    campos.forEach(campo => {
        totais[campo] = 0;
    });

    estadoLinhas.forEach(estado => {
        campos.forEach(campo => {
            const v = Number(estado.atual?.[campo] || 0);
            if (v === 1) totais[campo] += 1;
        });
    });

    return totais;
}

function aplicarTooltipsCabecalho() {
    const headers = getHeaderCellsMap();
    const totais = calcularTotaisPorColuna();
    headers.forEach((th, campo) => {
        const qtd = totais[campo] || 0;
        th.setAttribute('data-tooltip', `Quantidade: ${qtd}`);
    });
}

function atualizarTooltipCabecalhoIncremental(campo, delta) {
    const headers = getHeaderCellsMap();
    const th = headers.get(campo);
    if (!th) return;

    // ler número atual de data-tooltip
    const current = th.getAttribute('data-tooltip') || '';
    const match = current.match(/(\d+)$/);
    if (match) {
        const atual = parseInt(match[1], 10) || 0;
        const novo = Math.max(0, atual + delta);
        th.setAttribute('data-tooltip', `Quantidade: ${novo}`);
    } else {
        aplicarTooltipsCabecalho();
    }
}

// ========== Popular Combo de Usuários ==========
function popularComboUsuariosFromTable() {
    const select = document.getElementById('usuario-ausencia');
    if (!select) return;

    // Limpa mantendo o placeholder
    const placeholder = select.querySelector('option[value=""]')?.outerHTML || '<option value="">Selecione um usuário...</option>';
    select.innerHTML = placeholder;

    const nomesSet = new Set();

    // Pega nomes do estadoLinhas
    estadoLinhas.forEach((estado, uid) => {
        if (uid) nomesSet.add(uid);
    });

    // Ordena alfabeticamente (pt-BR) e adiciona ao select
    [...nomesSet].sort((a, b) => a.localeCompare(b, 'pt-BR')).forEach(nome => {
        const opt = document.createElement('option');
        opt.value = nome;
        opt.textContent = nome;
        select.appendChild(opt);
    });
}

// ========== Atualizar botão "Redefinir ausência" ==========
function atualizarBotaoRedefinirAusencia() {
    const btnRedef = document.getElementById('btn-redefinir-ausencia');
    const select = document.getElementById('usuario-ausencia');
    if (!btnRedef || !select) return;

    const nome = (select.value || '').trim();
    if (!nome) {
        btnRedef.disabled = true;
        btnRedef.title = 'Selecione um usuário';
        return;
    }

    const estado = estadoLinhas.get(nome);
    const temAusencia = !!(estado?.inicio_aus && estado?.fim_aus);
    btnRedef.disabled = !temAusencia;
    btnRedef.title = temAusencia ? 'Remover ausência do usuário selecionado' : 'Usuário não possui ausência definida';
}

// ========== Carregar Tabela ==========
async function carregarTabela() {
    const tbody = document.getElementById('tabela-body');
    if (!tbody) {
        console.error('Elemento #tabela-body não encontrado.');
        return;
    }

    tbody.innerHTML = '';

    try {
        const resp = await fetch('/dados_responsaveis');
        if (!resp.ok) throw new Error(`Falha ao buscar dados: ${resp.status} ${resp.statusText}`);
        const data = await resp.json();

        data.forEach((item) => {
            const uid = `${item.nome_resp}`;

            const estadoInicial = {
                nome_resp: item.nome_resp || '',
                resp_ativo: item.resp_ativo || 0,
                Turbinas: item.Turbinas || 0,
                Redutores: item.Redutores || 0,
                Novos: item.Novos || 0,
                Servicos: item['Serviços'] || 0,
                Calculos: item.Calculos || 0,
                Estudos: item.Estudos || 0,
                Seg_Controle: item.Seg_Controle || 0,
                Documentos: item.Documentos || 0,
                Acessorios: item.Acessorios || 0,
                seq_exec: item.seq_exec,
                inicio_aus: item.inicio_aus || null,
                fim_aus: item.fim_aus || null
            };

            // Somente considera "ausente" se hoje estiver dentro do período
            const emAusenciaHoje = isHojeDentroPeriodo(estadoInicial.inicio_aus, estadoInicial.fim_aus);

            estadoLinhas.set(uid, {
                ...estadoInicial,
                original: { ...estadoInicial },
                atual: { ...estadoInicial }
            });

            const row = document.createElement('tr');
            row.setAttribute('data-uid', uid);

            // HTML do nome com indicador de ausência (se houver datas definidas)
            let nomeHtml = '';
            if (estadoInicial.inicio_aus && estadoInicial.fim_aus) {
                const inicioBR = formatarBR(estadoInicial.inicio_aus);
                const fimBR = formatarBR(estadoInicial.fim_aus);
                const tooltipTexto = `Ausência: <br> ${inicioBR} a ${fimBR}`;

                nomeHtml = `
                    <span class="usuario-ausente">
                        ${item.nome_resp}
                        <span class="tooltip-ausencia">${tooltipTexto}</span>
                    </span>
                `;
            } else {
                nomeHtml = item.nome_resp;
            }

            // Checkboxes (desabilitar todos se em ausência hoje)
            const checkboxesHtml = campos.map((campo, idx) => {
                const valor = estadoInicial[campo];
                const checkedAttr = valor == 1 ? 'checked' : '';
                const disabledAttr = emAusenciaHoje ? 'disabled' : '';
                return `
                    <td class="checkbox-cell checkbox-cell-${idx + 1}" data-campo="${campo}">
                        <input type="checkbox" 
                               name="chk${idx + 1}" 
                               id="chk${idx + 1}-${uid}" 
                               data-campo="${campo}"
                               ${checkedAttr}
                               ${disabledAttr}>
                    </td>
                `;
            }).join('');

            // Ações: se em ausência hoje, mostra "Ausente" + botão redefinir; senão, salvar/excluir
            let acoesHtml = '';
            if (emAusenciaHoje) {
                const inicioBR = formatarBR(estadoInicial.inicio_aus);
                const fimBR = formatarBR(estadoInicial.fim_aus);
                acoesHtml = `
                    <div class="ausencia-info">
                        <div class="tooltip">
                            <button type="button" class="btn-salvar btn-ausente" id="btn-redefinir-aus-${uid}">
                                Ausente:<br>${inicioBR} a ${fimBR}
                            </button>
                            <span class="tooltip-text">Clique para redefinir</span>
                        </div>
                    </div>
                `;
            } else {
                acoesHtml = `
                    <button type="button" class="btn-salvar" id="btn-salvar-${uid}">
                        Salvar
                    </button>
                    <button type="button" class="btn-excluir" id="btn-excluir-${uid}" title="Excluir usuário">
                        Excluir
                    </button>
                `;
            }

            row.innerHTML = `
                <td>${nomeHtml}</td>
                ${checkboxesHtml}
                <td class="acoes">
                    ${acoesHtml}
                </td>
            `;

            tbody.appendChild(row);

            // Se EM AUSÊNCIA HOJE: apenas handler do "Redefinir ausência" e encerra a linha
            if (emAusenciaHoje) {
                const btnRedef = row.querySelector(`#btn-redefinir-aus-${uid}`);
                if (btnRedef) {
                    btnRedef.addEventListener('click', async () => {
                        const confirmar = await showConfirmDialog({
                            title: 'Redefinir ausência',
                            message: `Remover as datas de ausência de "${uid}"?`
                        });
                        if (confirmar === false) return;

                        try {
                            btnRedef.disabled = true;
                            btnRedef.textContent = 'Atualizando...';

                            const respLimpar = await fetch('/limpar_ausencia', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ nome_resp: uid })
                            });
                            if (!respLimpar.ok) throw new Error('Falha ao redefinir ausência');

                            showToast(`Ausência de "${uid}" foi removida.`, 'success');

                            // Recarrega a tabela para refletir estado e botões
                            await carregarTabela();
                            popularComboUsuariosFromTable();
                            atualizarBotaoRedefinirAusencia();
                        } catch (err) {
                            console.error(err);
                            showToast('Não foi possível redefinir a ausência.', 'error');
                            btnRedef.disabled = false;
                            btnRedef.textContent = 'Redefinir ausência';
                        }
                    });
                }
                return; // não registra handlers normais
            }

            // Fluxo normal (não está em ausência hoje)
            const cbs = row.querySelectorAll('input[type="checkbox"]');
            const cbAtivo = row.querySelector('input[type="checkbox"][data-campo="resp_ativo"]');
            const outrosCbs = Array.from(cbs).filter(cb => cb !== cbAtivo);
            const btnSalvar = row.querySelector(`#btn-salvar-${uid}`);
            const btnExcluir = row.querySelector(`#btn-excluir-${uid}`);

            const aplicarBloqueioPorAtivo = () => {
                const estado = estadoLinhas.get(uid);
                const ativo = !!estado.atual.resp_ativo;
                outrosCbs.forEach(cb => { cb.disabled = !ativo; });
            };

            const atualizarEstadoBotaoSalvar = () => {
                const estado = estadoLinhas.get(uid);
                const houveMudanca = campos.some(campo =>
                    estado.original[campo] !== estado.atual[campo]
                );
                btnSalvar.disabled = !houveMudanca;
            };

            cbs.forEach((cb) => {
                cb.addEventListener('change', (e) => {
                    const campo = e.target.dataset.campo;
                    const estado = estadoLinhas.get(uid);

                    const valorAnterior = Number(estado.atual[campo] || 0);
                    const novoValor = e.target.checked ? 1 : 0;
                    const delta = novoValor - valorAnterior;

                    estado.atual[campo] = novoValor;
                    estadoLinhas.set(uid, estado);

                    if (campo === 'resp_ativo') {
                        aplicarBloqueioPorAtivo();
                    }

                    if (delta !== 0) {
                        atualizarTooltipCabecalhoIncremental(campo, delta);
                    }

                    atualizarEstadoBotaoSalvar();
                });
            });

            aplicarBloqueioPorAtivo();
            atualizarEstadoBotaoSalvar();

            // Salvar
            btnSalvar.addEventListener('click', async () => {
                const estado = estadoLinhas.get(uid);

                // Validações para resp_ativo = 1
                if (estado.atual.resp_ativo === 1) {
                    const temTurbinaOuRedutor = estado.atual.Turbinas === 1 || estado.atual.Redutores === 1;
                    const temNovoOuServico = estado.atual.Novos === 1 || estado.atual.Servicos === 1;
                    const temAtividade = estado.atual.Calculos === 1 ||
                        estado.atual.Estudos === 1 ||
                        estado.atual.Seg_Controle === 1 ||
                        estado.atual.Documentos === 1 ||
                        estado.atual.Acessorios === 1;

                    const erros = [];
                    if (!temTurbinaOuRedutor) erros.push('• Selecione Turbinas ou Redutores');
                    if (!temNovoOuServico) erros.push('• Selecione Novos ou Serviços');
                    if (!temAtividade) erros.push('• Selecione pelo menos uma atividade (Cálculos, Estudos, Seg. Controle, Documentos ou Acessórios)');

                    if (erros.length > 0) {
                        await showConfirmDialog({
                            title: 'Validação',
                            message: 'Para ativar o usuário, é necessário:\n\n' + erros.join('\n')
                        });
                        return;
                    }
                }

                try {
                    btnSalvar.disabled = true;
                    btnSalvar.textContent = 'Salvando...';

                    const dadosParaSalvar = {
                        nome_resp: uid,
                        seq_exec: estado.seq_exec,
                        resp_ativo: estado.atual.resp_ativo,
                        Turbinas: estado.atual.Turbinas,
                        Redutores: estado.atual.Redutores,
                        Novos: estado.atual.Novos,
                        Servicos: estado.atual.Servicos,
                        Calculos: estado.atual.Calculos,
                        Estudos: estado.atual.Estudos,
                        Seg_Controle: estado.atual.Seg_Controle,
                        Documentos: estado.atual.Documentos,
                        Acessorios: estado.atual.Acessorios
                    };

                    const respSalvar = await fetch('/salvar-responsaveis', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(dadosParaSalvar)
                    });

                    if (!respSalvar.ok) throw new Error('Falha ao salvar esta linha');

                    campos.forEach((campo) => {
                        estado.atual[campo] = Number(estado.atual[campo] === 1 ? 1 : 0);
                        estado.original[campo] = estado.atual[campo];
                    });
                    estadoLinhas.set(uid, estado);

                    aplicarBloqueioPorAtivo();
                    atualizarEstadoBotaoSalvar();

                    showToast(`Usuário "${uid}" salvo com sucesso.`, 'success');

                } catch (err) {
                    console.error(err);
                    await showInfoDialog({
                        title: 'Erro',
                        message: 'Não foi possível salvar esta linha. Tente novamente.'
                    });
                    btnSalvar.disabled = false;
                } finally {
                    btnSalvar.textContent = 'Salvar';
                }
            });

            // Excluir
            btnExcluir.addEventListener('click', async () => {
                const confirmar = await showConfirmDialog({
                    title: 'Excluir usuário',
                    message: `Tem certeza que deseja excluir o usuário "${uid}"?`
                });
                if (!confirmar) return;

                try {
                    btnExcluir.disabled = true;
                    btnExcluir.textContent = 'Excluindo...';

                    const respDel = await fetch('/delete_responsavel', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ nome_resp: uid })
                    });

                    if (!respDel.ok) throw new Error('Falha ao excluir usuário');

                    estadoLinhas.delete(uid);
                    row.remove();

                    aplicarTooltipsCabecalho();

                    showToast(`Usuário "${uid}" excluído com sucesso.`, 'success');

                } catch (err) {
                    console.error(err);
                    showToast('Não foi possível excluir o usuário.', 'error');
                } finally {
                    btnExcluir.disabled = false;
                    btnExcluir.textContent = 'Excluir';
                }
            });
        }); // fim forEach

        // Aplica tooltips após renderizar todas as linhas
        aplicarTooltipsCabecalho();

    } catch (error) {
        console.error('Erro ao carregar os dados:', error);
    }

    // Atualiza combo sempre ao final
    popularComboUsuariosFromTable();
    // Atualiza estado do botão "Redefinir ausência" conforme seleção atual
    atualizarBotaoRedefinirAusencia();
}

// ========== Adicionar Novo Usuário ==========
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-adicionar-resp');
    const btn = document.getElementById('btn-add-usuario');

    if (!form || !btn) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const nomeInput = document.getElementById('novo-nome');
        const nome_resp = (nomeInput.value || '').trim();

        // Regex: somente letras (a-z, A-Z) e letras acentuadas comuns; nada de números, espaços ou especiais
        const somenteLetrasRegex = /^[A-Za-zÀ-ÖØ-öø-ÿ]+$/;

        if (!nome_resp) {
            await showConfirmDialog({ title: 'Atenção', message: 'Informe o nome do usuário.' });
            return;
        }

        if (!somenteLetrasRegex.test(nome_resp)) {
            await showConfirmDialog({
                title: 'Nome inválido',
                message: 'O nome deve conter apenas letras, sem espaços, números ou caracteres especiais.'
            });
            return;
        }

        // Todos os flags começam 0
        const payload = {
            nome_resp,
            resp_ativo: 0,
            Turbinas: 0,
            Redutores: 0,
            Novos: 0,
            Servicos: 0,
            Calculos: 0,
            Estudos: 0,
            Seg_Controle: 0,
            Documentos: 0,
            Acessorios: 0
        };

        try {
            btn.disabled = true;
            btn.textContent = 'Adicionando...';

            const resp = await fetch('/add_responsavel', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!resp.ok) {
                const txt = await resp.text().catch(() => '');
                throw new Error(`Erro ao adicionar. ${txt || ''}`);
            }

            showToast(`Usuário "${nome_resp}" adicionado com sucesso.`, 'success');
            form.reset();
            await carregarTabela(); // recarrega a lista

        } catch (err) {
            console.error(err);
            showToast('Não foi possível adicionar o usuário. Tente novamente.', 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Adicionar';
        }
    });
});

// ========== Definir Ausência ==========
document.addEventListener('DOMContentLoaded', () => {
    const btnAusencia = document.getElementById('btn-definir-ausencia');
    if (btnAusencia) {
        btnAusencia.addEventListener('click', definirAusencia);
    }

    // Mudança no combo: atualiza botão e (opcional) preenche datas
    const select = document.getElementById('usuario-ausencia');
    if (select) {
        select.addEventListener('change', () => {
            atualizarBotaoRedefinirAusencia();

            // Preenche datas se houver ausência do usuário selecionado
            const nome = (select.value || '').trim();
            const estado = estadoLinhas.get(nome);
            const inicioEl = document.getElementById('ausencia-inicio');
            const fimEl = document.getElementById('ausencia-fim');
            if (estado?.inicio_aus && estado?.fim_aus) {
                if (inicioEl) inicioEl.value = estado.inicio_aus;
                if (fimEl) fimEl.value = estado.fim_aus;
            } else {
                if (inicioEl) inicioEl.value = '';
                if (fimEl) fimEl.value = '';
            }
        });
    }

    // Clique no botão "Redefinir ausência" (ao lado do "Definir ausência")
    const btnRedef = document.getElementById('btn-redefinir-ausencia');
    if (btnRedef) {
        btnRedef.addEventListener('click', async () => {
            const selectEl = document.getElementById('usuario-ausencia');
            const nome_resp = (selectEl?.value || '').trim();
            if (!nome_resp) return;

            const confirmar = await showConfirmDialog({
                title: 'Redefinir ausência',
                message: `Remover as datas de ausência de "${nome_resp}"?`
            });
            if (!confirmar) return;

            try {
                btnRedef.disabled = true;
                const originalTxt = btnRedef.textContent;
                btnRedef.textContent = 'Atualizando...';

                const resp = await fetch('/limpar_ausencia', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ nome_resp })
                });
                if (!resp.ok) {
                    const msg = await resp.text().catch(() => '');
                    throw new Error(msg || `HTTP ${resp.status}`);
                }

                showToast(`Ausência de "${nome_resp}" removida.`, 'success');

                // Recarrega tabela/estado e atualiza UI
                await carregarTabela();
                popularComboUsuariosFromTable();
                atualizarBotaoRedefinirAusencia();

                // Limpa datas do form
                const inicioEl = document.getElementById('ausencia-inicio');
                const fimEl = document.getElementById('ausencia-fim');
                if (inicioEl) inicioEl.value = '';
                if (fimEl) fimEl.value = '';

            } catch (err) {
                console.error(err);
                showToast('Não foi possível redefinir a ausência.', 'error');
            } finally {
                btnRedef.textContent = 'Redefinir';
                atualizarBotaoRedefinirAusencia();
            }
        });
    }
});

async function definirAusencia() {
    const btn = document.getElementById('btn-definir-ausencia');
    const select = document.getElementById('usuario-ausencia');
    const inicioEl = document.getElementById('ausencia-inicio');
    const fimEl = document.getElementById('ausencia-fim');

    const nome_resp = (select?.value || '').trim();
    const inicio = (inicioEl?.value || '').trim(); // formato YYYY-MM-DD de input[type=date]
    const fim = (fimEl?.value || '').trim();

    // Validações
    if (!nome_resp) {
        showToast('Selecione um usuário.', 'error');
        select?.focus();
        return;
    }
    if (!inicio || !fim) {
        showToast('Informe as datas de início e fim.', 'error');
        (!inicio ? inicioEl : fimEl)?.focus();
        return;
    }
    if (fim < inicio) {
        showToast('A data de fim deve ser maior ou igual à de início.', 'error');
        fimEl?.focus();
        return;
    }

    try {
        btn.disabled = true;
        btn.textContent = 'Salvando...';

        // Envie as chaves que seu backend espera (ajustado para aceitar inicio_aus/fim_aus também no back, mas mantemos assim)
        const payload = {
            nome_resp,           // string
            inicio_aus: inicio,  // 'YYYY-MM-DD'
            fim_aus: fim         // 'YYYY-MM-DD'
        };

        const resp = await fetch('/definir_ausencia', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!resp.ok) {
            const msg = await resp.text().catch(() => '');
            throw new Error(msg || `HTTP ${resp.status}`);
        }

        // Sucesso
        showToast(`Ausência definida para ${nome_resp} (${formatarBR(inicio)} a ${formatarBR(fim)}).`, 'success');

        // Recarrega a tabela para refletir o estado de ausência
        await carregarTabela();

        // Reset UI
        select.value = '';
        inicioEl.value = '';
        fimEl.value = '';

        // Atualiza estado do botão "Redefinir ausência"
        atualizarBotaoRedefinirAusencia();

    } catch (err) {
        console.error('Erro ao definir ausência:', err);
        showToast('Não foi possível definir a ausência. Tente novamente.', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Definir ausência';
    }
}

// ========== Inicialização ==========
document.addEventListener('DOMContentLoaded', () => {
    carregarTabela();
});


// Incluir rotina para alertar quando não houver responsavel para determinada atividade.