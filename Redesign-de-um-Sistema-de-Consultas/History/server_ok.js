const { exec } = require('child_process');
const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 3000;
app.use(cors());

app.get('/executar-python', (req, res) => {
    console.log("🟢 Iniciando execução do script Python...");
    
    exec('python sap_script.py', (error, stdout, stderr) => {
        if (error) {
            console.error(`❌ Erro ao executar Python: ${error.message}`);
            return res.json({ mensagem: "Erro ao executar o script!" });
        }
        if (stderr) {
            console.error(`⚠️ Erro no script: ${stderr}`);
            return res.json({ mensagem: "Erro durante a execução do script!" });
        }

        console.log("✅ Script Python executado com sucesso!");
        res.json({ mensagem: "Execução concluída!" });
    });
});

app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});


// app.get('/executar-python', (req, res) => {
//     exec('python sap_script.py', (error, stdout, stderr) => {
//         if (error) {
//             console.error(`Erro: ${error.message}`);
//             return res.json({ mensagem: "Erro ao executar o script SAP." });
//         }
//         if (stderr) {
//             console.error(`Stderr: ${stderr}`);
//             return res.json({ mensagem: "Erro na execução do SAP." });
//         }
//         console.log(`Resultado: ${stdout}`);
//         // return res.json({ mensagem: "Script SAP executado com sucesso!" });
//     });
// });

// app.listen(3000, () => console.log("Servidor rodando em http://localhost:3000"));
