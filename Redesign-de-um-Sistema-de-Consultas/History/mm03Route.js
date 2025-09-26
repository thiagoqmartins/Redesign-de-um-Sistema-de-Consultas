// executarPythonRoute.js
const { exec } = require('child_process');
const express = require('express');
const router = express.Router();

router.post('/executar-python', (req, res) => {
    console.log("🟢 Iniciando execução do script Python...");

    const { valor } = req.body;

    if (!valor) {
        return res.status(400).json({ mensagem: "❌ Nenhum valor numérico foi enviado!" });
    }

    console.log(`🟢 Valor recebido: ${valor}`);

    exec(`python sap_script.py ${valor}`, (error, stdout, stderr) => {
        if (error) {
            console.error(`❌ Erro ao executar Python: ${error.message}`);
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

module.exports = router;
