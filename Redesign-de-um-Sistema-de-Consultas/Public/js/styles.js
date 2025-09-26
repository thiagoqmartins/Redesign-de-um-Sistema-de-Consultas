// Função que atualiza a relação altura/largura da janela e define CSS custom property
function atualizarRelacao() {
  const largura = window.innerWidth;
  const altura = window.innerHeight;
  let relacao = 1; // valor padrão

  if (largura > altura) {
    relacao = altura / largura;
  } else if (altura > largura) {
    relacao = largura / altura;
  }

  // Define a variável CSS no :root
  document.documentElement.style.setProperty('--relacao', relacao);
}

// Executa no carregamento da página
atualizarRelacao();

// Atualiza a relação ao redimensionar a janela
window.addEventListener('resize', atualizarRelacao);

// Seleciona o elemento da tabela que deve existir no DOM
const tabela = document.querySelector('.tabela');

// Função para mostrar o font-size da tabela de forma segura
function mostrarFontSize() {
  if (!tabela) {
    // console.warn('Elemento .tabela não encontrado.');
    return;
  }
  const fontSize = window.getComputedStyle(tabela).fontSize;

  // Exemplo de debug (comentado)
  // document.getElementById('teste5').textContent = 'Font ' + fontSize;
}

// Executa ao carregar a página e ao redimensionar a janela
window.addEventListener('load', mostrarFontSize);
window.addEventListener('resize', mostrarFontSize);

document.querySelectorAll('.tooltip').forEach(tooltip => {
  tooltip.addEventListener('mouseenter', () => {
    const rect = tooltip.getBoundingClientRect();
    const tooltipHeight = 40; // aprox altura do tooltip (ajuste se precisar)

    // Se estiver muito perto do topo da janela, mostra embaixo
    if (rect.top < tooltipHeight + 10) {
      tooltip.classList.add('tooltip-bottom');
    } else {
      tooltip.classList.remove('tooltip-bottom');
    }
  });
});

const tfooter = document.getElementById('footer');
// tfooter.innerHTML = `
//                       <span class="creditos-dev">Desenvolvido por Thiago Martins</span>         
//                       `;
tfooter.innerHTML = `
                      <div class="tooltip">
                        <span class="material-icons icon_html">html</span>
                        <span class="tooltip-text">HTML</span>
                      </div>

                      <div class="tooltip">
                        <span class="material-icons icon_css">css</span>
                        <span class="tooltip-text">CSS</span>
                      </div>

                      <div class="tooltip">
                        <span class="material-icons icon_js">javascript</span>
                        <span class="tooltip-text">JavaScript</span>
                      </div>

                      <span class="creditos-dev">Desenvolvido por Thiago Martins</span>

                      <div class="tooltip">
                        <span class="material-icons icon_json">data_object</span>
                        <span class="tooltip-text">JSON</span>
                      </div>

                      <div class="tooltip">
                        <span class="material-icons icon_python">code</span>
                        <span class="tooltip-text">Python</span>
                      </div>

                      <div class="tooltip">
                        <span class="material-icons icon_sql">storage</span>
                        <span class="tooltip-text">SQL</span>
                      </div>

                      <div class="tooltip">
                        <img src="images/sapico.png" class="icon_sap"/>
                        <span class="tooltip-text">SAP</span>
                      </div>
                      `;




