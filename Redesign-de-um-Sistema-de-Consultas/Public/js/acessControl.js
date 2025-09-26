// Mapas para tradução de nível de acesso e status
const niveisAcessoMap = {
  0: 'User',
  1: 'Moderador',
  2: 'Admin',
  3: 'Super_Admin',
  4: 'Virtual_User'
};

const statusMap = {
  0: 'Inativo',
  1: 'Ativo',
  2: 'Pendente',
  3: 'Suspenso'
};

// Função para carregar usuários e montar a tabela
function carregarUsuarios() {
  fetch('/usuarios')
    .then(res => res.json())
    .then(dados => {
      const container = document.getElementById('tabelaUsuarios');
      if (!container) {
        console.warn('Elemento #tabelaUsuarios não encontrado.');
        return;
      }

      const tabela = document.createElement('table');
      tabela.classList.add('tabela');

      tabela.innerHTML = `
        <thead>
          <tr>
            <th>Nome</th>
            <th>Usuário</th>
            <th>Email</th>
            <th>Nível de Acesso</th>
            <th>Status</th>
            <th>Alterar Nível Acesso</th>
            <th>Alterar Status</th>
            <th>Resetar Senha</th>
            <th>Excluir/Reativar</th>
          </tr>
        </thead>
        <tbody id="tabela-body"></tbody>
      `;

      const tbody = tabela.querySelector('#tabela-body');

      dados.forEach(usuario => {
        // ... seu código para criar as linhas ...
        const nivelTexto = niveisAcessoMap[usuario.nivel_acesso] || usuario.nivel_acesso;
        const statusTexto = statusMap[usuario.status] || usuario.status;
        const ativoStatus = usuario.status === 1 || usuario.status === '1' || usuario.status === 'Ativo';
        let iconeStatus = ativoStatus ? 'toggle_on' : 'toggle_off';

        const statusNormalizado =
          usuario.status === 0 || usuario.status === '0' ? 'Inativo' :
            usuario.status === 1 || usuario.status === '1' || usuario.status === 'Ativo' ? 'Ativo' :
              usuario.status === 2 || usuario.status === '2' || usuario.status === 'Pendente' ? 'Pendente' :
                usuario.status === 3 || usuario.status === '3' || usuario.status === 'Suspenso' ? 'Suspenso' :
                  'Desconhecido';


        switch (statusNormalizado) {
          case 'Ativo':
            iconeStatus = 'toggle_on';
            break;
          case 'Inativo':
            iconeStatus = 'toggle_off';
            break;
          case 'Pendente':
            iconeStatus = 'pending_actions';  // ícone exemplo
            break;
          case 'Suspenso':
            iconeStatus = 'block';            // ícone exemplo
            break;
          default:
            iconeStatus = 'help_outline';     // fallback
        }



        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td data-label="Nome">${usuario.nome}</td>
          <td data-label="Usuário">${usuario.usuario}</td>
          <td data-label="Email">${usuario.email}</td>
          <td data-label="Nível de Acesso" title="${nivelTexto}">${nivelTexto}</td>
          <td data-label="Status" title="${statusTexto}">${statusTexto}</td>
          <td data-label="Alterar Nível">
            <button onclick='alterarNivel(${usuario.id}, ${usuario.status}, ${JSON.stringify(usuario.usuario)})' title="Alterar nível">
              <span class="material-icons">security</span>
            </button>
          </td>
          <td data-label="Alterar Status">
            <button onclick='alterarStatus(${usuario.id}, ${usuario.status}, ${JSON.stringify(usuario.usuario)})' title="Alterar status" class="btn-status ${statusNormalizado.toLowerCase()}"
>
              <span class="material-icons">${iconeStatus}</span>
            </button>
          </td>
          <td data-label="Resetar Senha">
            <button onclick="resetarSenha(${usuario.id})" title="Resetar senha">
              <span class="material-icons">restart_alt</span>
            </button>
          </td>
          <td data-label="Excluir">
            <button onclick="excluirUsuario(${usuario.id})" title="Excluir usuário" class="btn-excluir">
              <span class="material-icons">delete</span>
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });

      container.innerHTML = '';
      container.appendChild(tabela);

      // AQUI: ligar o evento de filtro no campoBusca, AGORA que a tabela está pronta
      const campoBusca = document.getElementById('campoBusca');
      if (campoBusca) {
        campoBusca.addEventListener('input', () => {
          const filtro = campoBusca.value.toLowerCase();
          const linhas = tbody.getElementsByTagName('tr');

          for (let i = 0; i < linhas.length; i++) {
            const linha = linhas[i];
            const textoLinha = linha.textContent.toLowerCase();

            linha.style.display = textoLinha.indexOf(filtro) > -1 ? '' : 'none';
          }
        });
      }
    })
    .catch(err => console.error('Erro ao carregar usuários:', err));
}


// Funções exemplo para as ações — substitua pelas chamadas reais

function resetarSenha(id) {
  if (confirm('Deseja realmente resetar a senha deste usuário?')) {
    fetch(`/usuarios/${id}/resetar`, { method: 'POST' })
      .then(res => res.json())
      .then(resp => alert(resp.mensagem || 'Senha resetada com sucesso.'))
      .catch(err => console.error(err));
  }
}

// ✅ Nova função para excluir usuário
function excluirUsuario(id) {
  if (confirm('Tem certeza que deseja excluir este usuário? Essa ação não poderá ser desfeita.')) {
    fetch(`/usuarios/${id}`, { method: 'DELETE' })
      .then(res => res.json())
      .then(resp => {
        alert(resp.mensagem || 'Usuário excluído com sucesso.');
        carregarUsuarios(); // Atualiza a tabela
      })
      .catch(err => {
        console.error('Erro ao excluir usuário:', err);
        alert('Erro ao excluir o usuário.');
      });
  }
}

// Carrega a tabela quando o DOM estiver pronto
window.addEventListener('DOMContentLoaded', carregarUsuarios);

// Função para criar o modal no DOM uma única vez
// Função para criar o modal no DOM uma única vez
function criarModalAlterarNivel() {
  if (document.getElementById('modalAlterarNivel')) return; // Já existe

  const modal = document.createElement('div');
  modal.id = 'modalAlterarNivel';
  modal.style.display = 'none';
  modal.style.position = 'fixed';
  modal.style.zIndex = '10000';
  modal.style.left = '0';
  modal.style.top = '0';
  modal.style.width = '100%';
  modal.style.height = '100%';
  modal.style.overflow = 'auto';
  modal.style.backgroundColor = 'rgba(0,0,0,0.5)';

  modal.innerHTML = `
    <div style="
      background-color: #fff;
      margin: 15% auto;
      padding: 20px;
      border-radius: 8px;
      width: 300px;
      text-align: center;
      box-shadow: 0 5px 15px rgba(0,0,0,0.3);
      position: relative;
    ">
      <span id="fecharModal" style="
        color: #aaa;
        position: absolute;
        right: 15px;
        top: 10px;
        font-size: 28px;
        font-weight: bold;
        cursor: pointer;
      ">&times;</span>
      <h3>Alterar Nível de Acesso</h3>
      <select id="selectNivel" style="font-size: 16px; padding: 6px; width: 100%; margin-top: 10px;">
        <option value="0">User</option>
        <option value="1">Moderador</option>
        <option value="2">Admin</option>
        <option value="3">Super_Admin</option>
        <option value="4">Virtual_User</option>
      </select>
      <br /><br />
      <button id="btnConfirmarNivel" style="
        padding: 8px 16px;
        font-size: 16px;
        cursor: pointer;
      ">Confirmar</button>
    </div>
  `;

  document.body.appendChild(modal);

  // Fechar modal ao clicar no "x"
  document.getElementById('fecharModal').onclick = () => {
    modal.style.display = 'none';
  };

  // Fechar modal ao clicar fora da área do conteúdo
  window.onclick = (event) => {
    if (event.target === modal) {
      modal.style.display = 'none';
    }
  };
}

let usuarioLogado = null;

// Obter dados do usuário logado
async function carregarUsuarioLogado() {
  try {
    const resposta = await fetch('/usuario-logado');
    if (!resposta.ok) {
      throw new Error('Usuário não autenticado');
    }

    const dados = await resposta.json();
    usuarioLogado = dados.nome;
  } catch (erro) {
    console.error('Erro ao carregar usuário logado:', erro.message);
  }
}

let usuarioSelecionado = null;

// Função chamada ao clicar no botão para alterar nível
async function alterarNivel(id, statusAtual, usuario) {
  usuarioSelecionado = id;
  nomeUsuario = usuario || 'Usuário Desconhecido';

  console.log(id)

  if (usuarioLogado === nomeUsuario) {
    return; // Sai da função
  }

  criarModalAlterarNivel();
  const modal = document.getElementById('modalAlterarNivel');
  modal.style.display = 'block';
}

// Botão confirmar dentro do modal
document.addEventListener('DOMContentLoaded', () => {
  criarModalAlterarNivel();

  document.getElementById('btnConfirmarNivel').onclick = () => {
    const select = document.getElementById('selectNivel');
    const novoNivel = parseInt(select.value, 10);

    if (usuarioSelecionado === null) {
      //   alert('Usuário não selecionado.');
      return;
    }

    // Aqui você coloca a chamada para enviar para backend, por exemplo:
    fetch(`/usuarios/${usuarioSelecionado}/nivel`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nivel_acesso: novoNivel })
    })
      .then(res => {
        if (!res.ok) throw new Error('Erro ao alterar nível');
        return res.json();
      })
      .then(data => {
        //   alert(data.mensagem || 'Nível alterado com sucesso.');
        carregarUsuarios(); // Atualiza a tabela
        document.getElementById('modalAlterarNivel').style.display = 'none';
      })
      .catch(err => {
        console.error(err);
        //   alert('Erro ao alterar o nível do usuário.');
      });
  };
});

function alterarStatus(id, statusAtual, usuario) {
  const novoStatus = statusAtual === 1 ? 0 : 1;
  const nomeUsuario = usuario || 'Usuário Desconhecido';

  console.log(id, statusAtual)

  fetch(`/usuarios/${id}/status`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      status: novoStatus,
      nome: nomeUsuario // nome do usuário que está sendo alterado
    })
  })
    .then(res => {
      if (!res.ok) throw new Error('Erro ao alterar status');
      return res.json();
    })
    .then(() => {
      carregarUsuarios(); // Atualiza a tabela após alteração
    })
    .catch(err => {
      console.error('Erro ao alterar status:', err);
      alert('Erro ao alterar status do usuário.');
    });
}








