@echo off
set PORTA=3000
set DIRETORIO=C:\Users\thiagoqm\Desktop\VBA_Prog\Python\projeto1

:loop
cls
echo Verificando servidor na porta %PORTA%...
netstat -ano | findstr :%PORTA% | findstr LISTENING >nul

if %ERRORLEVEL%==0 (
    echo [%TIME%] Servidor Node.js ja esta RODANDO.
) else (
    echo [%TIME%] Servidor NAO esta rodando. Iniciando...
    cd /d "%DIRETORIO%"
    start "" cmd /k "node server.js"
    timeout /t 3 >nul
    echo [%TIME%] Servidor iniciado com sucesso.
)

echo Aguardando 15 minutos para proxima verificacao...
timeout /t 900 >null
@REM timeout /t 900 
goto loop
