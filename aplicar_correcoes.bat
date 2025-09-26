@echo off
echo Aplicando correções de layout...

:: Atualizar base_form_screen.py
echo Atualizando base_form_screen.py...
python fix_layout.py

:: Atualizar cadastro_brindes.py
echo Atualizando cadastro_brindes.py...
python fix_cadastro_brindes.py

:: Atualizar app.py
echo Atualizando app.py...
python fix_app.py

echo.
echo Todas as correções foram aplicadas com sucesso!
echo Por favor, reinicie a aplicação para ver as mudanças.
pause
