// npm init -y
// npm install express
// npm install cors
// npm install selfsigned
// npm install axios
// npm install sqlite3
// npm install express-session
// npm install bcrypt
// npm install body-parser

// Framework para criar servidor web e APIs
const express = require('express'); // >>> precisa instalar: npm install express

// Middleware para habilitar CORS (Cross-Origin Resource Sharing)
const cors = require('cors');  // >>> precisa instalar: npm install cors

// Módulo para executar comandos e scripts externos (child processes)
const { exec } = require('child_process');

const { execSync } = require("child_process");

// Módulo HTTPS nativo do Node.js para fazer requisições seguras
const https = require('https');

// Biblioteca para gerar certificados SSL autoassinados (instalar com npm install selfsigned)
const selfsigned = require('selfsigned'); // >>> precisa instalar: npm install selfsigned

// Módulo para manipulação de arquivos e diretórios
const fs = require('fs');

// Módulo para manipulação de caminhos de arquivos
const path = require('path');

// Biblioteca SQLite3 com modo verbose para logs detalhados
const sqlite3 = require('sqlite3').verbose(); // >>> precisa instalar: npm install sqlite3

// Inicializa a aplicação Express
const app = express();

// Biblioteca para fazer requisições HTTP, usada aqui para APIs externas
const axios = require('axios'); // >>> precisa instalar: npm install axios

// Configura agente HTTPS para aceitar certificados autoassinados (útil em ambientes de desenvolvimento)
const httpsAgent = new https.Agent({ rejectUnauthorized: false });

// Módulo para acessar informações do sistema operacional (CPU, memória, etc)
const os = require('os')

// Middleware para controle de sessões (login, autenticação)
const session = require('express-session'); // >>> precisa instalar: npm install express-session

// Importa objeto 'error' do console (não muito comum, provavelmente para logging)
const { error } = require('console');

// Importa stdout e stderr do processo atual (para manipulação de entrada/saída)
const { stdout, stderr } = require('process');

// Biblioteca bcrypt para comparar senhas hashed (segurança)
const { compareSync } = require('bcrypt'); // >>> precisa instalar: npm install bcrypt
// (alternativa mais fácil de instalar: bcryptjs)

// Módulo para criar processos filhos com mais controle (spawn)
const { spawn } = require('child_process');

// Middleware para interpretar corpos de requisições (JSON, urlencoded)
const bodyParser = require('body-parser');

const PORT = 3000;
const PORT2 = 3000;

// 🔒 Gera certificado autoassinado na hora (válido por 365 dias)
const attrs = [{ name: 'commonName', value: '10.67.4.122' }];
//const attrs = [{ name: 'commonName', value: '192.168.0.99' }];
const pems = selfsigned.generate(attrs, { days: 365 });

// Salva o certificado e a chave em arquivos locais
fs.writeFileSync('certificado.crt', pems.cert); // Certificado
fs.writeFileSync('chave.key', pems.private);   // Chave privada (opcional)

let contador = 1;

// Configurações para o servidor HTTPS com certificados SSL/TLS
const options = {
    // Leitura da chave privada do certificado (arquivo .key)
    key: fs.readFileSync(path.join(__dirname, '10.67.4.122+1-key.pem')),

    // Leitura do certificado público (arquivo .pem)
    cert: fs.readFileSync(path.join(__dirname, '10.67.4.122+1.pem'))
};

//novo bloco

// Middleware para interpretar dados enviados via formulário (application/x-www-form-urlencoded)
// A opção 'extended: true' permite analisar objetos aninhados no corpo da requisição
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
// ⚠️ Middleware para servir arquivos estáticos da pasta 'public'
// Deve ser colocado DEPOIS das rotas acima para que as rotas personalizadas tenham prioridade
app.use(express.static(path.join(__dirname, 'public')));

// Configuração do middleware de sessão para o Express
// app.use(session({
//     secret: 'segredo',           // Chave secreta usada para assinar o ID da sessão (mantenha em segredo!)
//     resave: false,               // Evita salvar sessão no armazenamento se não houve modificações
//     saveUninitialized: true      // Salva sessões novas mesmo que não modificadas (útil para login, cookies)
// }));

app.use(session({
    secret: 'segredo',
    resave: false,
    saveUninitialized: false,
    // cookie: {
    //     maxAge: 30 * 60 * 1000  // 30 minutos em milissegundos

    // }
}));

// Rota principal ('/')
// Se o usuário estiver autenticado (sessão válida), serve a página principal (index.html)
// Caso contrário, redireciona para a página de login
app.get('/', (req, res) => {
    if (req.session && req.session.usuario) {
        // Usuário autenticado: envia o arquivo index.html da pasta 'public'
        res.sendFile(path.join(__dirname, 'public', 'index.html'));
    } else {
        // Usuário não autenticado: redireciona para a rota '/login'
        res.redirect('/login');
    }
});

// Rota GET para exibir a página de login
app.get('/login', (req, res) => {
    // Envia o arquivo 'login.html' da pasta 'public' como resposta
    res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

// Rota POST para processar o login do usuário
app.post('/login', (req, res) => {
    // Extrai username e password do corpo da requisição
    const { username, password } = req.body;

    // Caminho completo do script Python que fará a validação
    const scriptPath = path.join(__dirname, 'scripts', 'registro.py');

    // Monta o comando para executar o script Python com argumentos
    const comando = `python "${scriptPath}" validar "${username}" "${password}"`;

    // Executa o comando do script Python
    exec(comando, (error, stdout, stderr) => {
        if (error) {
            // Em caso de erro na execução do script, loga e retorna erro 500
            console.error('Erro ao executar script:', error);
            return res.status(500).send('Erro interno no servidor.');
        }
        try {
            // Tenta interpretar a saída do script Python como JSON
            const resposta = JSON.parse(stdout);
            if (resposta.success) {
                // Se login válido, cria a sessão com o nome do usuário e redireciona para página principal
                req.session.usuario = {
                    nome: username,
                    nivel_acesso: resposta.nivel_acesso
                };
                const agora = new Date();
                console.log(`[${agora.toLocaleString('pt-BR')}] Usuário ${username.toUpperCase()} logado com sucesso.`);
                res.redirect('/');
            } else {
                // Se login inválido, lê o arquivo HTML da página de login
                const loginPath = path.join(__dirname, 'public', 'login.html');
                fs.readFile(loginPath, 'utf-8', (err, data) => {
                    if (err)
                        return res.status(500).send('Erro ao carregar página');

                    // Obtém a mensagem de erro enviada pelo script, ou usa uma genérica
                    const erroTexto = resposta.error || 'Erro desconhecido.';

                    // Substitui no HTML a div de mensagem de erro para torná-la visível e mostrar o texto
                    const paginaComErro = data.replace(
                        /<div\s+id="mensagemErro"\s+style="[^"]*">.*?<\/div>/s,
                        `<div id="mensagemErro" style="display: block; color: #e63946; margin-top: 5px;">${erroTexto}</div>`
                    );

                    // Envia a página com a mensagem de erro exibida
                    res.send(paginaComErro);
                });
            }
        } catch (e) {
            // Caso falhe interpretar o JSON retornado pelo script, loga o erro e retorna erro 500
            console.error('Erro ao interpretar saída do Python:', stdout);
            res.status(500).send('Erro na resposta do servidor.');
        }
    });
});

app.get('/logout', (req, res) => {
    req.session.destroy(err => {
        if (err) {
            console.error('Erro ao destruir sessão:', err);
            return res.status(500).send('Erro ao fazer logout.');
        } else {
            console.log("Desconectado")
        }

        res.clearCookie('connect.sid');
        console.log("Usuário deslogado com sucesso!");
        res.redirect('/login');
    });
});

app.get("/abrir-sqlite", (req, res) => {
    const dbPath = "C:\\Users\\thiagoqm\\Desktop\\VBA_Prog\\Python\\Projeto1\\BD\\banco_dados.db";
    const comando = `python -m sqlite_web "${dbPath}"`;
    console.log(dbPath);
    console.log(comando);

    exec(comando, (error, stdout, stderr) => {
        if (error) {
            console.error(`Erro: ${error.message}`);
            return res.status(500).send("Erro ao abrir o SQLite Web");
        }
        console.log(`SQLite Web iniciado`);
        res.send("OK");
    });
});

// Middleware para evitar cache de páginas protegidas
app.use((req, res, next) => {
    res.set('Cache-Control', 'no-store, no-cache, must-revalidate, private');
    res.set('Pragma', 'no-cache');
    res.set('Expires', '0');
    next();
});

app.get('/usuarios', (req, res) => {
    // console.log("🔴 Rota /usuarios acessada");
    const dbPath = path.join(__dirname, 'BD/banco_dados.db');

    const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
        if (err) {
            console.error('Erro ao abrir o banco:', err.message);
            return res.status(500).json({ erro: 'Erro ao abrir o banco.' });
        }
    });

    const sql = `SELECT id, nome, usuario, email, nivel_acesso, status FROM usuarios`;

    db.all(sql, [], (err, rows) => {
        if (err) {
            console.error('Erro na consulta:', err.message);
            return res.status(500).json({ erro: 'Erro ao consultar usuários.' });
        }

        res.json(rows);

        db.close((err) => {
            if (err) {
                console.error('Erro ao fechar o banco:', err.message);
            }
        });
    });
});

app.get('/usuario-logado', (req, res) => {
    if (req.session && req.session.usuario) {
        res.json({
            id: req.session.usuario.id,       // precisa garantir que salvou o id na sessão no login
            nome: req.session.usuario.nome,
            nivel_acesso: req.session.usuario.nivel_acesso
        });
    } else {
        res.status(401).json({ mensagem: 'Não autenticado' });
    }
});

app.put('/usuarios/:id/nivel', (req, res) => {
    const id = parseInt(req.params.id, 10);

    // Se o usuário logado tentar alterar seu próprio nível
    if (req.session.usuario && req.session.usuario.id === id) {
        return res.status(403).json({ mensagem: 'Você não pode alterar seu próprio nível.' });
    }

    const { nivel_acesso } = req.body;
    // Validação básica do nível
    if (![0, 1, 2, 3, 4].includes(nivel_acesso)) {
        return res.status(400).json({ mensagem: 'Nível de acesso inválido.' });
    }

    const dbPath = path.join(__dirname, 'BD/banco_dados.db');
    const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READWRITE, (err) => {
        if (err) {
            console.error('Erro ao abrir o banco:', err.message);
            return res.status(500).json({ erro: 'Erro ao abrir o banco.' });
        }
    });

    const sql = `UPDATE usuarios SET nivel_acesso = ? WHERE id = ?`;

    db.run(sql, [nivel_acesso, id], function (err) {
        if (err) {
            console.error('Erro ao atualizar usuário:', err.message);
            db.close();
            return res.status(500).json({ erro: 'Erro ao atualizar usuário.' });
        }

        if (this.changes === 0) { // nenhuma linha alterada (usuário não encontrado)
            db.close();
            return res.status(404).json({ mensagem: 'Usuário não encontrado.' });
        }

        db.close((err) => {
            if (err) {
                console.error('Erro ao fechar o banco:', err.message);
            }
        });

        res.json({ mensagem: `Nível do usuário atualizado para ${nivel_acesso}.` });
    });
});

app.put('/usuarios/:id/status', (req, res) => {
    const id = parseInt(req.params.id, 10);
    const nomeUsuario = req.body.nome; // ← aqui está o nome vindo do body

    const usuarioLogadoNome = req.session.usuario.nome;

    if (nomeUsuario === usuarioLogadoNome) {
        return res.json({ erro: 'Você não pode alterar seu próprio status.' });
    }

    const dbPath = path.join(__dirname, 'BD/banco_dados.db');
    const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READWRITE, (err) => {
        if (err) {
            console.error('Erro ao abrir o banco:', err.message);
            return res.status(500).json({ erro: 'Erro ao abrir o banco.' });
        }
    });

    // Primeiro, buscar o status atual do usuário
    const sqlSelect = `SELECT status FROM usuarios WHERE id = ?`;
    db.get(sqlSelect, [id], (err, row) => {
        if (err) {
            console.error('Erro ao consultar status:', err.message);
            db.close();
            return res.status(500).json({ erro: 'Erro ao consultar usuário.' });
        }

        if (!row) {
            db.close();
            return res.status(404).json({ mensagem: 'Usuário não encontrado.' });
        }

        // Inverter status se for 0 ou 1 (senão mantém)
        let novoStatus;
        if (row.status === 0 || row.status === 2) novoStatus = 1;
        else if (row.status === 1) novoStatus = 0;
        else novoStatus = row.status; // outros status permanecem

        // Atualizar o status invertido
        const sqlUpdate = `UPDATE usuarios SET status = ? WHERE id = ?`;
        db.run(sqlUpdate, [novoStatus, id], function (err) {
            db.close();

            if (err) {
                console.error('Erro ao atualizar status:', err.message);
                return res.status(500).json({ erro: 'Erro ao atualizar status.' });
            }

            if (this.changes === 0) {
                return res.status(404).json({ mensagem: 'Usuário não encontrado.' });
            }

            return res.json({ mensagem: `Status do usuário alterado para ${novoStatus}.`, status: novoStatus });
        });
    });
});

app.delete('/usuarios/:id', (req, res) => {
    const id = parseInt(req.params.id, 10);

    if (isNaN(id)) {
        return res.status(400).json({ erro: 'ID inválido.' });
    }

    const dbPath = path.join(__dirname, 'BD/banco_dados.db');
    const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READWRITE, (err) => {
        if (err) {
            console.error('Erro ao abrir o banco:', err.message);
            return res.status(500).json({ erro: 'Erro ao abrir o banco.' });
        }
    });

    // Verificar se o usuário existe
    const sqlSelect = `SELECT nome, status FROM usuarios WHERE id = ?`;
    db.get(sqlSelect, [id], (err, row) => {
        if (err) {
            console.error('Erro ao consultar usuário:', err.message);
            db.close();
            return res.status(500).json({ erro: 'Erro ao consultar usuário.' });
        }

        if (!row) {
            db.close();
            return res.status(404).json({ mensagem: 'Usuário não encontrado.' });
        }

        // Atualizar status para 3 (excluído lógico)
        const sqlUpdate = `UPDATE usuarios SET status = 3 WHERE id = ?`;
        db.run(sqlUpdate, [id], function (err) {
            db.close();

            if (err) {
                console.error('Erro ao atualizar status:', err.message);
                return res.status(500).json({ erro: 'Erro ao deletar (atualizar status).' });
            }

            if (this.changes === 0) {
                return res.status(404).json({ mensagem: 'Usuário não encontrado para exclusão.' });
            }

            return res.json({
                mensagem: `Usuário '${row.nome}' marcado como excluído (status = 3).`,
                status: 3
            });
        });
    });
});

app.get('/acessControl', (req, res) => {
    if (!req.session.usuario || req.session.usuario.nivel_acesso < 2) {
        return res.status(403).send('Acesso negado.');
    }
    res.sendFile(path.join(__dirname, 'public/acessControl.html'));
});

app.get('/admin', (req, res) => {
    if (!req.session.usuario || req.session.usuario.nivel_acesso < 2) {
        return res.status(403).send('Acesso negado.');
    }
    res.sendFile(path.join(__dirname, 'public/admin.html'));
});

app.get('/triagem', (req, res) => {
    if (!req.session.usuario || req.session.usuario.nivel_acesso < 2) {
        return res.status(403).send('Acesso negado.');
    }
    res.sendFile(path.join(__dirname, 'public/triagem.html'));
});

// 🔍 Rota GET para retornar dados da tabela 'consultas_iqs9' do banco SQLite
app.get('/dados', (req, res) => {
    // Define o caminho para o arquivo do banco de dados SQLite (ajuste conforme seu projeto)
    const dbPath = path.join(__dirname, 'BD/banco_dados.db');

    // Abre uma conexão somente leitura com o banco de dados
    const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
        if (err) {
            // Em caso de erro ao abrir o banco, loga no console e retorna erro 500
            console.error('Erro ao abrir o banco:', err.message);
            return res.status(500).json({ erro: 'Erro ao abrir o banco.' });
        }
    });

    // SQL para selecionar todos os registros da tabela, ordenados pela coluna 'seq_exec' ascendente
    const sql = `SELECT * FROM consultas_iqs9 ORDER BY seq_exec ASC`;

    // Executa a consulta SQL para obter todos os dados
    db.all(sql, [], (err, rows) => {
        if (err) {
            // Em caso de erro na consulta, loga e retorna erro 500
            console.error('Erro na consulta:', err.message);
            return res.status(500).json({ erro: 'Erro ao consultar dados.' });
        }

        // Se sucesso, retorna os dados encontrados em formato JSON
        res.json(rows);
    });

    // Fecha a conexão com o banco de dados (importante para liberar recursos)
    db.close();
});

// Middleware para permitir requisições Cross-Origin (CORS)
app.use(cors());

// Middleware para interpretar o corpo das requisições como JSON automaticamente
app.use(express.json());



app.post('/createZZ', (req, res) => {
    // Caminho absoluto do script
    const scriptPath = path.join(__dirname, 'scripts', 'createZZ.py');

    // Detecta o comando Python (ajuste para 'py' se sua máquina exigir)
    const PY = process.platform === 'win32' ? 'python' : 'python3';
    const comando = `${PY} "${scriptPath}"`;

    // Timeout evita travar; maxBuffer evita erro por saída grande
    const child = exec(
        comando,
        { timeout: 120000, maxBuffer: 10 * 1024 * 1024 },
        (error, stdout, stderr) => {
            const out = (stdout || '').toString().trim();
            const err = (stderr || '').toString().trim();

            if (error) {
                // → Erro de execução (exit code != 0, timeout, python não encontrado, etc.)
                console.error('❌ /createZZ: erro na execução:', error.message);
                if (err) console.error('↳ stderr:', err);
                if (out) console.error('↳ stdout:', out);
                return res.status(500).json({
                    ok: false,
                    etapa: 'createZZ',
                    erro: error.message,
                    stderr: err,
                    stdout: out
                });
            }

            if (err) {
                // Avisos do script (mantemos como warning sem quebrar a resposta)
                console.warn('⚠️ /createZZ: stderr:', err);
            }

            // Tenta interpretar JSON; se não for JSON, devolve texto bruto
            let data = null;
            try { data = out ? JSON.parse(out) : null; } catch (_) { }

            // Se o script já sinalizou falha lógica ({ ok:false }), preserve como erro de negócio
            if (data && typeof data === 'object' && data.ok === false) {
                return res.status(400).json(data);
            }

            return res.json({
                ok: true,
                etapa: 'createZZ',
                resultado: data ?? out ?? 'ZZ criados com sucesso'
            });
        }
    );

    // Falha ao iniciar o processo (antes mesmo do callback do exec)
    child.on('error', (err) => {
        console.error('❌ /createZZ: falha no spawn/exec:', err.message);
    });
});

// Rota principal
app.post('/executar-python', (req, res) => {
    const { valor, campo } = req.body;
    console.log("🔴 Valor:", valor);
    console.log("🟣 Campo:", campo);

    if (!valor) {
        return res.status(400).json({ mensagem: "❌ Nenhum valor numérico foi enviado!" });
    }

    const comando = `python sap_script.py "${campo}" "${valor}"`;

    exec(comando, (error, stdout, stderr) => {
        if (error) {
            console.error(`❌ Erro ao executar o script Python:\n${error.message}`);
            return res.status(500).json({
                mensagem: "Erro ao executar o script!",
                detalhe: error.message
            });
        }

        if (stderr) {
            console.warn(`⚠️ Aviso do script Python:\n${stderr}`);
        }
        console.log("✅ Resultado do Python:", stderr.trim());
        console.log("✅ Resultado do Python:", stdout.trim());
        console.log("✅ Script Python executado com sucesso!");

        if (stdout) {
            try {
                const resultadoJson = JSON.parse(stdout.trim());

                if (!resultadoJson || Object.keys(resultadoJson).length === 0) {
                    return res.status(404).json({
                        mensagem: "Nenhum dado encontrado na saída do Python.",
                        detalhe: "O script não retornou informações válidas.",
                        retornoBruto: stdout.trim()
                    });
                }

                res.json({ resultadoJson });

            } catch (e) {
                res.status(500).json({
                    mensagem: "❌ Erro ao interpretar a saída do Python.",
                    detalhe: e.message,
                    retornoBruto: stdout.trim()
                });
            }
        } else {
            res.status(500).json({
                mensagem: "❌ Nenhum retorno do script Python.",
                detalhe: "stdout vazio ou nulo"
            });
        }

    });

});

// Rota POST para executar o script Python passando o valor do campo IQS9
app.post('/executar-python-iqs9', (req, res) => {

    // Extrai o campo 'campo' do corpo da requisição
    const { campo } = req.body;

    // Valida se o campo foi enviado; se não, retorna erro 400 (bad request)
    if (!campo) {
        return res.status(400).json({ mensagem: "❌ Nenhum valor numérico foi enviado!" });
    }

    // Monta o comando para executar o script Python com o argumento passado
    const comando = `python sap_script.py "${campo}"`;

    // Executa o comando no shell
    exec(comando, (error, stdout, stderr) => {
        if (error) {
            // Caso haja erro na execução do script, loga e retorna erro 500
            console.error(`❌ Erro ao executar o script Python:\n${error.message}`);
            // SAP GUI For Windowns 770
            return res.status(500).json({
                mensagem: "Erro ao executar o script!",
                detalhe: error.message
            });
        }

        if (stderr) {
            // Se o script Python enviou avisos para stderr, loga como warning
            console.warn(`⚠️ Aviso do script Python:\n${stderr}`);
        }

        try {
            // Tenta interpretar a saída do script Python como JSON
            const resultadoJson = JSON.parse(stdout.trim());
            // Retorna resultado com mensagem de sucesso
            res.json({
                mensagem: "Execução concluída!",
                resultado: resultadoJson
            });
        } catch (e) {
            // Se falhar ao interpretar o JSON, loga o campo enviado e retorna erro 500 com detalhes
            console.log("🟣 Campo:", campo);
            res.status(500).json({
                mensagem: "Erro ao interpretar saída do Python",
                detalhe: e.message,
                retornoBruto: stdout.trim()
            });
        }
    });
});

app.post('/updateContent', (req, res) => {

    // Caminho absoluto do script
    const scriptPath = path.join(__dirname, 'scripts', 'content_claim.py');

    // Chame o Python explicitamente (no Windows pode ser "py" ou "python")
    const comando = `python "${scriptPath}"`;

    // Timeout evita pendurar indefinidamente
    const child = exec(comando, { timeout: 120000 }, (error, stdout, stderr) => {
        if (error) {
            return res.status(500).json({
                ok: false,
                etapa: 'updateContent',
                erro: error.message
            });
        }

        if (stderr && stderr.trim()) {
            // warnings/prints do Python em stderr
            console.warn("⚠️ /updateContent: stderr:", stderr.trim());
        }

        // Se seu script imprime JSON, tente parsear; senão, devolva texto
        let payload = stdout && stdout.trim();
        let data = null;
        try {
            data = payload ? JSON.parse(payload) : null;
        } catch (_) {
            // se não for JSON, seguimos com texto
        }
        return res.json({
            ok: true,
            etapa: 'updateContent',
            resultado: data ?? payload ?? 'Descrições Atualizadas'
        });
    });

    // (opcional) logs quando o processo excede buffer/tempo
    child.on('error', (err) => {
        console.error('❌ /updateContent: falha no spawn/exec:', err.message);
    });
});

setInterval(() => {
    const campo = 'IQS9';



    // Verifica se o campo foi enviado;
    if (!campo) {
        return res.status(400).json({ mensagem: "❌ Nenhum valor numérico foi enviado!" });
    }

    // Comando para executar o script Python com o campo IQS9
    const comando = `python sap_script.py "${campo}"`;

    // console.log(`🚀 Requisição enviada com campo: ${campo}`); 

    // exec(comando, (error, stdout, stderr) => {
    //     if (error) {
    //         console.error(`❌ Erro ao executar o script Python:\n${error.message}`);
    //     }

    //     if (stderr) {

    //         console.warn(`⚠️ Aviso do script Python:\n${stderr}`);
    //     }
    //     console.log("✅ Script Python executado com sucesso!");
    // });
    // axios.post('https://10.67.4.122:3000/createZZ', {}, { httpsAgent })
    // axios.post('https://10.67.4.122:3000/executar-python-iqs9', { campo }, { httpsAgent })  

    // console.log(`🚀 Requisição enviada com campo: ${campo}`);  
    // console.log(`🔄 Contador: ${contador}`);
    // contador++;
}, 15000);

async function executarSequencialmente() {
    console.log("⚠️ Iniciando a sequência de requisições...");
    campo = 'IQS9';
    try {
        console.log("⏳ Atualizando Base de Claims");
        let inicio = Date.now();
        // Primeira requisição
        await axios.post('https://brszon110730.weg.net:3000/executar-python-iqs9', { campo }, { httpsAgent });
        let fim = Date.now();
        console.log(`✅ Base de Claims Atualizada (tempo: ${(fim - inicio) / 1000}s)`);

        console.log("⏳ Atualizando Descrições");
        inicio = Date.now();
        // Segunda requisição
        await axios.post('https://brszon110730.weg.net:3000/updateContent', {}, { httpsAgent });
        fim = Date.now();
        console.log(`✅ Descrições Atualizadas (tempo: ${(fim - inicio) / 1000}s)`);

        // console.log("⏳ Criando ZZs");
        // inicio = Date.now();
        // // Terceira requisição
        // await axios.post('https://brszon110730.weg.net:3000/createZZ', {}, { httpsAgent });
        // fim = Date.now();
        // console.log(`✅ ZZs Criados (tempo: ${(fim - inicio) / 1000}s)`);

        console.log("✔️ Sequenciamento Concluído");
        return "Concluído"
    } catch (error) {
        console.log("❌ Erro na sequência de requisições:");
        console.error('Erro:', error.message);
    }
}

// Chama a função
// setInterval(executarSequencialmente, 15000);
setTimeout(() => {
    executarSequencialmente();
}, 5000);

app.post('/atualizar', (req, res) => {
    console.log(executarSequencialmente());
    res.json({ status: 'ok' });

});

// Rota POST para validar a senha recebida no corpo da requisição
app.post("/validaSenha", (req, res) => {
    // Extrai o campo 'senha' do corpo da requisição
    const { senha } = req.body;

    // Expressão regular para validar a senha:
    // - Pelo menos uma letra minúscula
    // - Pelo menos uma letra maiúscula
    // - Pelo menos um caractere especial (não letra ou dígito)
    // - Comprimento mínimo de 6 caracteres
    const senhaValida = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z\d])(?=.{6,})/.test(senha);

    // Retorna JSON informando se a senha é válida ou não
    res.json({ senhaValida });
});

// Rota POST para "/regs", que recebe dados de registro e executa um script Python para processá-los
app.post('/regs', (req, res) => {
    // Extrai os dados enviados pelo corpo da requisição
    const { nome, usuario, email, senha } = req.body;

    // Monta o caminho completo até o script Python
    const scriptPath = path.join(__dirname, 'scripts', 'registro.py');

    // Monta o comando que será executado no terminal, passando os dados como argumentos
    const comando = `python "${scriptPath}" executar "${nome}" "${usuario}" "${email}" "${senha}"`;

    const datahora = new Date().toLocaleString();

    console.log(`[${datahora}] Registro Novo Usuário: ${usuario}`);

    // Executa o script Python usando o comando montado
    exec(comando, (error, stdout, stderr) => {
        // Se houver erro ao executar o comando (por exemplo, Python não encontrado)
        if (error) {
            console.error('Erro ao executar o script:', error);
            return res.status(500).json({ erro: 'Erro ao executar o script.' });
        }

        // Se o script Python rodar, mas gerar erros (via stderr)
        if (stderr) {
            console.error('Erro no script:', stderr);
            return res.status(500).json({ erro: 'Erro no script Python.' });
        }

        // Captura e limpa a saída padrão retornada pelo script
        const resultadoBruto = stdout.trim();
        console.log("Usuário ou e-mail Existente")
        // console.log('Resultado do script:', JSON.parse(resultadoBruto));

        let resultadoArray;
        try {
            // Tenta converter a saída para JSON
            resultadoArray = JSON.parse(resultadoBruto);
        } catch (e) {
            // Se falhar, responde com erro de interpretação
            return res.status(500).json({
                status: "erro",
                mensagem: "Erro ao interpretar resposta do script"
            });
        }

        // Verifica se a resposta do script contém "ok"
        if (Array.isArray(resultadoArray) && resultadoArray.includes("ok")) {
            // Sucesso: retorna status "ok"
            return res.json({ status: "ok" });
        } else {
            // Erro: usuário ou email já existe (assumido pelo script)
            return res.status(400).json({
                status: "erro",
                mensagem: "Usuário ou e-mail já existe"
            });
        }
    });
});

// Executa a função newsAPI uma única vez assim que o script é carregado
newsAPI();

let timeNews = 60 * 60 * 1000 // 1 hora
// Agenda para executar a função newsAPI periodicamente
setInterval(newsAPI, timeNews / 2); //atualizando a cada meia hora

// Função que executa um script Python para obter as palavras-chave de forma assíncrona
function palavraChave() {
    // Define o caminho completo do script Python 'keyWord.py' dentro da pasta 'scripts'
    const scriptPath = path.join(__dirname, "scripts", "keyWord.py");

    // Retorna uma Promise para lidar com a execução assíncrona do script
    return new Promise((resolve, reject) => {
        // Executa o script Python usando o comando 'python' e o caminho do script
        exec(`python "${scriptPath}"`, (error, stdout, stderr) => {
            // Se ocorreu um erro ao executar o comando, rejeita a Promise com o erro
            if (error) return reject(error);

            // Se o script Python enviou algo no stderr, também rejeita com esse erro
            if (stderr) return reject(new Error(stderr));

            try {
                // Tenta interpretar a saída do script como JSON (remove espaços em branco)
                const resultado = JSON.parse(stdout.trim());
                // Se der certo, resolve a Promise com o resultado (palavras-chave)
                resolve(resultado);
            } catch (e) {
                // Se a saída não for JSON válido, rejeita com uma mensagem de erro customizada
                reject(new Error("❌ Erro ao interpretar JSON do Python: " + e.message));
            }
        });
    });
}

// Função assíncrona para buscar notícias usando a API da GNews
async function newsAPI() {
    try {
        // Define as duas chaves da API para tentativa em ordem
        const apiKey1 = '755a9719bc5b945d8727fbd01eb006f6';
        const apiKey2 = '44c230cdf28879544d745b59d082d4d3';

        // Função auxiliar para fazer a requisição com uma determinada chave
        const buscarNoticias = (key, palavrasChave) => {
            console.log(`🔑 Tentando chave da API: ${palavrasChave}`);
            const url = `https://gnews.io/api/v4/top-headlines?lang=pt&country=br&q=${palavrasChave}&token=${key}`;
            return axios.get(url, { httpsAgent });
        };

        // Obtém as palavras-chave para busca
        let palavrasChave = await palavraChave();
        palavrasChave = palavrasChave.join(" OR ");

        try {
            resposta = await buscarNoticias(apiKey1, palavrasChave);
        } catch (erroApi1) {
            console.warn("Chave API 1 falhou, tentando chave alternativa...");
            // Se apiKey1 falhar, tenta com apiKey2
            resposta = await buscarNoticias(apiKey2, palavrasChave);
        }
        // Caso alguma das requisições tenha funcionado, processa o resultado
        const noticias = resposta.data;
        const datahora = new Date().toLocaleString();

        // Caminho para salvar arquivo JSON com notícias
        const caminho = path.join(__dirname, "public", "noticias.json");

        // Salva os artigos em arquivo JSON formatado
        fs.writeFile(caminho, JSON.stringify(noticias.articles, null, 2), err => {
            if (err) {
                console.error("Erro ao salvar o arquivo:", err.message);
            } else {
                console.log(`📰 Arquivo de notícias atualizado com sucesso! : [${datahora}]`);
            }
        });

    } catch (err) {
        // Erro geral caso ambas as tentativas falhem ou erro interno
        console.error("❌ Erro ao buscar notícias:", err.message);
    }
}

// Rota GET para servir o arquivo JSON com notícias
app.get("/noticias", (req, res) => {
    // Envia o arquivo 'noticias.json' da pasta 'public' como resposta
    res.sendFile(__dirname + "/public/noticias.json");
});

// Middleware para interpretar o corpo das requisições com conteúdo JSON
app.use(bodyParser.json());

// Torna a pasta 'public' acessível como arquivos estáticos (HTML, CSS, JS, imagens etc. do frontend)
app.use(express.static('public')); // frontend

// Rota POST para atualizar a ordem (drag and drop)
app.post('/atualizar-ordem', (req, res) => {
    if (!req.session.usuario || req.session.usuario.nivel_acesso < 1) {
        return res.status(403).json({ erro: 'Acesso negado.' });
    }

    const dadosParaPython = {
        novaOrdem: req.body.depois  // só o array que importa para atualizar o banco
    };

    // Converte o corpo da requisição em JSON string
    const inputJSON = JSON.stringify(dadosParaPython);

    console.log("✅ Teste arrastar......")

    // Cria um processo filho para executar o script Python
    const python = spawn('python', ['scripts/atualizar_ordem.py']);

    // Variáveis para armazenar a saída e erro do script Python
    let output = '';
    let error = '';

    // Captura os dados que o script Python enviar para stdout
    python.stdout.on('data', (data) => {
        output += data.toString();
        // console.log(output)
    });

    // Captura os erros que o script Python enviar para stderr
    python.stderr.on('data', (data) => {
        error += data.toString();
        // console.log(error)
    });

    // Evento disparado quando o script Python finaliza a execução
    python.on('close', (code) => {
        if (code === 0) {
            // Se o script finalizou com sucesso, tenta interpretar o JSON retornado
            try {
                const dbPath = path.join(__dirname, 'BD/banco_dados.db');
                const db = new sqlite3.Database(dbPath);

                const usuario = req.session.usuario.nome || req.session.usuario.login || 'desconhecido';
                const tipoEvento = 'reordenacao';
                const origem = 'tabela_claims';
                const descricao = `Usuário ${usuario} alterou a ordem dos registros via arrastar`;
                const dadosAntes = JSON.stringify(req.body.antes || []);  // você deve garantir que envie isso do frontend
                const dadosDepois = JSON.stringify(req.body.depois || []);
                const ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
                const dataHora = new Date().toISOString();

                const sql = `INSERT INTO logs_sistema 
    (usuario, data_hora, tipo_evento, descricao, dados_antes, dados_depois, origem, ip)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)`;

                db.run(sql, [usuario, dataHora, tipoEvento, descricao, dadosAntes, dadosDepois, origem, ip], function (err) {
                    db.close();
                    if (err) {
                        console.error("❌ Erro ao salvar log:", err.message);
                        // continua o fluxo mesmo se não salvar o log
                    }
                });
                res.json(JSON.parse(output));
            } catch (err) {
                // Caso ocorra erro ao interpretar, retorna erro 500
                res.status(500).json({ erro: 'Erro ao interpretar saída do Python' });
            }
        } else {
            // Se o script retornou erro, responde com erro 500 e detalhes
            res.status(500).json({ erro: 'Falha ao executar Python', detalhes: error || output });
        }
    });

    console.log("✅ Concluído arrastar")

    // Envia os dados para o script Python via stdin
    python.stdin.write(inputJSON);
    python.stdin.end();
});

app.get('/usuario', (req, res) => {
    if (!req.session.usuario) {
        return res.status(401).json({ erro: 'Usuário não autenticado' });
    }

    // Retorna só os dados que interessam
    res.json({
        nome: req.session.usuario.nome,
        nivel_acesso: req.session.usuario.nivel_acesso
    });
});

app.post('/salvarBU', (req, res) => {


    // #TAG       → Identificardor
    // #NT        → 1 
    // #NR        → 2 
    // #ST        → 3 
    // #SR        → 4 
    // #GT        → 5 
    // #GR        → 6 
    // #GST       → 7 
    // #GSR       → 8 
    // #AT-T      → 9 
    // #AT-R      → 10 

    let { numero_nota, class_bu } = req.body;

    if (!numero_nota || class_bu === undefined || class_bu === '') {
        return res.status(400).json({ success: false, message: 'Dados inválidos' });
    }

    const mapTags = {
        "#NT": 1,
        "#NR": 2,
        "#ST": 3,
        "#SR": 4,
        "#GT": 5,
        "#GR": 6,
        "#GST": 7,
        "#GSR": 8,
        "#AT-T": 9,
        "#AT-R": 10
    };

    class_bu = mapTags[class_bu] || class_bu;

    console.log(class_bu);
    console.log(numero_nota);
    // Exemplo com SQLite (adapte conforme seu banco):
    const sqlite3 = require('sqlite3').verbose();
    const db = new sqlite3.Database('BD/banco_dados.db'); // Altere o caminho se necessário

    const sql = `UPDATE consultas_iqs9 SET class_BU = ? WHERE numero_nota = ?`;

    db.run(sql, [class_bu, numero_nota], function (err) {
        if (err) {
            console.error('Erro ao atualizar o banco:', err);
            return res.status(500).json({ success: false, message: 'Erro ao salvar no banco' });
        }

        if (this.changes === 0) {
            return res.status(404).json({ success: false, message: 'Nota não encontrada' });
        }

        return res.json({ success: true, message: 'Salvo com sucesso' });
    });

    db.close();
});

// Cria um servidor HTTPS utilizando as opções (certificado SSL) e o app (Express ou similar)
https.createServer(options, app).listen(PORT, '0.0.0.0', () => {

    // Obtém as interfaces de rede disponíveis no sistema
    const interfaces = os.networkInterfaces();
    let localIp = 'localhost';

    // Percorre todas as interfaces de rede
    for (const name of Object.keys(interfaces)) {
        for (const iface of interfaces[name]) {
            // Verifica se a interface é IPv4 e não é interna (não é o localhost)
            if (iface.family === 'IPv4' && !iface.internal) {
                localIp = iface.address; // Armazena o IP externo
                break; // Sai do loop interno
            }
        }
        if (localIp !== 'localhost') break; // Se já encontrou o IP externo, sai do loop externo
    }

    // Exibe no console o endereço onde o servidor HTTPS está rodando
    console.log(`🚀 Servidor HTTPS rodando em https://${localIp}:${PORT}`);
});

//# =========CÓDIGOS FUNCIONAIS===================

//# ============================

// app.post('/regs', (req, res) => {
//     const { nome, usuario, email, senha } = req.body;

//     const scriptPath = path.join(__dirname, 'scripts', 'registro.py');

//     const comando = `python "${scriptPath}" "${nome}" "${usuario}" "${email}" "${senha}"`;

//     exec(comando, (error, stdout, stderr) => {
//         if (error) {
//             console.error('Erro ao executar o script:', error);
//             return res.status(500).json({ erro: 'Erro ao executar o script.' });
//         }

//         if (stderr) {
//             console.error('Erro no script:', stderr);
//             return res.status(500).json({ erro: 'Erro no script Python.' });
//         }

//         const resultadoBruto = stdout.trim();
//         // console.log('Resultado do script:', resultadoBruto);

//         let resultadoArray;
//         try {
//             resultadoArray = JSON.parse(resultadoBruto);
//         } catch (e) {
//             return res.status(500).json({
//                 status: "erro",
//                 mensagem: "Erro ao interpretar resposta do script"
//             });
//         }

//         // Agora, resultadoArray deve ser ["ok"] ou ["erro"]
//         if (Array.isArray(resultadoArray) && resultadoArray.includes("ok")) {
//             return res.json({ status: "ok" });
//         } else {
//             return res.status(400).json({
//                 status: "erro",
//                 mensagem: "Usuário ou e-mail já existe"
//             });
//         }

//     });
// });