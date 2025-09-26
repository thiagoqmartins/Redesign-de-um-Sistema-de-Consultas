const fs = require('fs');
const selfsigned = require('selfsigned');

// 🔒 Gera certificado autoassinado na hora (válido por 365 dias)
const attrs = [{ name: 'commonName', value: 'localhost' }];
const pems = selfsigned.generate(attrs, { days: 365 });

// Salva os arquivos no disco
fs.writeFileSync('certificado.crt', pems.cert);  // ✅ depois de gerar
fs.writeFileSync('chave.key', pems.private);
