const { exec } = require('child_process');
const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 3000;
app.use(cors());
app.use(express.json());

app.post('/executar-python', (req, res) => {
    console.log("🟢 Iniciando execução do script Python...");

    const { valor } = req.body;
    const { campo } = req.body;

    if (!valor) {
        return res.status(400).json({ mensagem: "❌ Nenhum valor numérico foi enviado!" });
    }

    // console.log(`🟢 Valor recebido: ${valor}`);
    // console.log(`🟢 Valor recebido: ${campo}`);

    exec(`python sap_script.py ${valor} ${campo}`, (error, stdout, stderr) => {
        if (error) {
            console.error(`❌ Erro ao executar Python: ${error.message}`);
            console.error(`🔴 stderr:\n${stderr}`);
            console.error(`🟡 stdout:\n${stdout}`);
            return res.status(500).json({ mensagem: "Erro ao executar o script!", detalhe: error.message });
        }
        if (stderr) {
            console.error(`⚠️ Erro no script: ${stderr}`);
            return res.status(500).json({ mensagem: "Erro ao executar o script!", detalhe: stderr });
        }

        console.log("✅ Script Python executado com sucesso!");
        res.json({ mensagem: "Execução concluída!", resultado: stdout.trim() });
    });
});

// app.listen(PORT, () => {
//     console.log(`Servidor rodando em http://localhost:${PORT}`);
// });
app.listen(3000, '0.0.0.0', () => {
    console.log('Servidor rodando em http://10.67.4.122:3000');
  });
  
