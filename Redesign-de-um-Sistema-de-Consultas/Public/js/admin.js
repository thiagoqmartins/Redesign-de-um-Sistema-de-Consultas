document.addEventListener("click", function (e) {
    if (e.target.closest(".btn-editar")) {
        let linha = e.target.closest("tr");
        let celulaAcoes = linha.querySelector(".acoes");

        celulaAcoes.innerHTML = `
            <button class="btn btn-sm btn-success btn-salvar"><i class="bi bi-check-lg"></i></button>
            <button class="btn btn-sm btn-secondary btn-cancelar"><i class="bi bi-x-lg"></i></button>
        `;
    }

    if (e.target.closest(".btn-cancelar") || e.target.closest(".btn-salvar")) {
        let linha = e.target.closest("tr");
        let celulaAcoes = linha.querySelector(".acoes");

        celulaAcoes.innerHTML = `
            <button class="btn btn-sm btn-primary btn-editar"><i class="bi bi-pencil-square"></i></button>
            <button class="btn btn-sm btn-danger btn-excluir"><i class="bi bi-trash"></i></button>
        `;
    }
});