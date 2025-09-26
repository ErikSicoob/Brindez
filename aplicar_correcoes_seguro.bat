@echo off
echo Aplicando correções de layout...
echo.

:: Criar backup dos arquivos originais
echo Criando backup dos arquivos originais...
if not exist "backup" mkdir backup

:: Fazer backup dos arquivos originais
if exist "src\ui\components\base_form_screen.py" (
    copy "src\ui\components\base_form_screen.py" "backup\base_form_screen.py.bak"
    if %ERRORLEVEL% NEQ 0 (
        echo Erro ao fazer backup de base_form_screen.py
        pause
        exit /b 1
    )
)

if exist "src\app.py" (
    copy "src\app.py" "backup\app.py.bak"
    if %ERRORLEVEL% NEQ 0 (
        echo Erro ao fazer backup de app.py
        pause
        exit /b 1
    )
)

if exist "src\ui\screens\cadastro_brindes.py" (
    copy "src\ui\screens\cadastro_brindes.py" "backup\cadastro_brindes.py.bak"
    if %ERRORLEVEL% NEQ 0 (
        echo Erro ao fazer backup de cadastro_brindes.py
        pause
        exit /b 1
    )
)

:: Copiar arquivos corrigidos
echo.
echo Aplicando correções...

if exist "base_form_screen_corrigido.py" (
    copy /Y "base_form_screen_corrigido.py" "src\ui\components\base_form_screen.py"
    if %ERRORLEVEL% NEQ 0 (
        echo Erro ao copiar base_form_screen_corrigido.py
        pause
        exit /b 1
    )
) else (
    echo Arquivo base_form_screen_corrigido.py não encontrado
    pause
    exit /b 1
)

if exist "app_corrigido.py" (
    copy /Y "app_corrigido.py" "src\app.py"
    if %ERRORLEVEL% NEQ 0 (
        echo Erro ao copiar app_corrigido.py
        pause
        exit /b 1
    )
) else (
    echo Arquivo app_corrigido.py não encontrado
    pause
    exit /b 1
)

if exist "cadastro_brindes_corrigido.py" (
    if not exist "src\ui\screens" mkdir "src\ui\screens"
    copy /Y "cadastro_brindes_corrigido.py" "src\ui\screens\cadastro_brindes.py"
    if %ERRORLEVEL% NEQ 0 (
        echo Erro ao copiar cadastro_brindes_corrigido.py
        pause
        exit /b 1
    )
) else (
    echo Arquivo cadastro_brindes_corrigido.py não encontrado
    pause
    exit /b 1
)

echo.
echo Todas as correções foram aplicadas com sucesso!
echo Backups dos arquivos originais foram salvos na pasta 'backup'.
echo.
echo Por favor, reinicie a aplicação para ver as mudanças.
pause
