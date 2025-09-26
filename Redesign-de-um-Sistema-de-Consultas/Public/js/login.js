function mostrarRegistro() {
  document.getElementById("registroOverlay").classList.add("mostrar");
}

function fecharRegistro() {
  document.getElementById("registroOverlay").classList.remove("mostrar");
}

document.addEventListener("DOMContentLoaded", () => {
  // Referência ao formulário de registro
  const form = document.getElementById("formRegistro");
  // Referência ao botão de fechar o formulário
  const btnFechar = document.getElementById("fecharDiv");

  // Associa o evento de clique ao botão de fechar
  btnFechar.addEventListener("click", fecharRegistro);

  // Evento de envio do formulário
  form.addEventListener("submit", async function (e) {
    e.preventDefault(); // Impede o comportamento padrão de envio do formulário

    // Coleta os valores dos campos do formulário
    const nome = document.getElementById("nome").value;
    const usuario = document.getElementById("usuario").value;
    const email = document.getElementById("email").value;
    const senha = document.getElementById("senhaRegistro").value;
    const senha2 = document.getElementById("senhaRegistroConf").value;

    if (senha != senha2) {
      exibirErro("As senhas não coincidem.");
      return;
    }

    // Envia a senha para validação no backend
    const respSenha = await fetch("/validaSenha", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ senha }) // 🔁 importante usar um objeto!
    });

    // Recebe o resultado da validação da senha
    const resultado = await respSenha.json();

    // Verifica se a senha é válida
    if (!resultado.senhaValida) {
      exibirErro("A senha deve conter no mínimo 6 caracteres, com pelo menos 1 letra maiúscula, 1 letra minúscula e 1 caractere especial.");
      document.getElementById("senhaRegistro").value = "";
      document.getElementById("senhaRegistroConf").value = "";
      return; // Interrompe o envio se a senha for inválida
    }

    // Monta o objeto com os dados do formulário
    const dados = { nome, usuario, email, senha };

    try {
      // Envia os dados do usuário para o backend
      const response = await fetch("/regs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados)
      });

      // Lê a resposta do backend
      const data = await response.json();

      // Se a resposta não for OK, lança erro
      if (!response.ok) {
        throw new Error(data.mensagem || "Erro desconhecido.");
      }

      // Limpa o formulário e exibe confirmação
      form.reset();
      exibirOK("Solicitação de Acesso Enviada!");

      // Fecha o formulário após 3 segundos
      setTimeout(() => {
        fecharRegistro();
      }, 3000);

    } catch (error) {
      // Exibe mensagem de erro em caso de falha
      exibirErro(error.message);
    }
  });
});

function exibirErro(mensagem) {
  const div = document.getElementById("exibirMensagem");

  if (div) {
    div.textContent = mensagem;
    div.className = "erroMensagem";
    div.style.display = "block";
  } else {
    alert(mensagem);
  }
}

function exibirOK(mensagem) {
  const div = document.getElementById("exibirMensagem");

  if (div) {
    div.textContent = mensagem;
    div.className = "okMensagem";
    div.style.display = "block";
  } else {
    alert(mensagem);
  }
}

document.getElementById("toggleSenhaRegistroConf").addEventListener("click", (event) => {
  event.preventDefault(); // impede envio do formulário por segurança

  const campoSenha = document.getElementById("senhaRegistroConf");
  const icone = event.currentTarget.querySelector("span");

  const senhaOculta = campoSenha.type === "password";
  campoSenha.type = senhaOculta ? "text" : "password";
  icone.textContent = senhaOculta ? "visibility_off" : "visibility";
});

document.getElementById("toggleSenhaRegistro").addEventListener("click", (event) => {
  event.preventDefault(); // impede envio do formulário por segurança

  const campoSenha = document.getElementById("senhaRegistro");
  const icone = event.currentTarget.querySelector("span");

  const senhaOculta = campoSenha.type === "password";
  campoSenha.type = senhaOculta ? "text" : "password";
  icone.textContent = senhaOculta ? "visibility_off" : "visibility";
});

document.getElementById("toggleSenhaLogin").addEventListener("click", (event) => {
  event.preventDefault(); // impede envio do formulário por segurança

  const campoSenha = document.getElementById("senhaLogin");
  const icone = event.currentTarget.querySelector("span");

  const senhaOculta = campoSenha.type === "password";
  campoSenha.type = senhaOculta ? "text" : "password";
  icone.textContent = senhaOculta ? "visibility_off" : "visibility";
});

document.addEventListener('DOMContentLoaded', () => {
  const usuario = document.getElementById('usuarioLogin');
  const senha = document.getElementById('senhaLogin');
  const mensagemErro = document.getElementById('mensagemErro');
  const mensagemErro1 = document.getElementById('mensagemErro1');

  [usuario, senha].forEach(campo => {
    if (campo) {
      // Faz a mensagem sumir ao clicar no campo (focus)
      campo.addEventListener('focus', () => {
        if (mensagemErro) {
          mensagemErro.style.display = 'none';
        }
      });

      // (Opcional) Também some ao digitar
      campo.addEventListener('input', () => {
        if (mensagemErro) {
          mensagemErro.style.display = 'none';
        }
      });
    }
  });
});
document.addEventListener('keydown', function (e) {
  // F5 (keyCode 116) ou Ctrl+R (Ctrl + 82)
  if (e.key === "F5" || (e.ctrlKey && e.key === 'r')) {
    e.preventDefault();
    console.log('Recarregamento desativado');
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);
  if (params.get('erro') === '1') {
    const erro = document.getElementById('mensagemErro');
    const erro1 = document.getElementById('mensagemErro1');
    if (erro) {
      erro.textContent = 'Usuário ou senha inválidos.';
      erro.style.display = 'block';
      erro1.style.display = "none";

      // Remove ?erro=1 da URL (sem recarregar a página)
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }
});









