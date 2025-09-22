"""
Script para criar executável standalone do Sistema de Controle de Brindes
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_executable():
    """Cria executável usando PyInstaller"""
    
    print("🚀 Iniciando processo de build do executável...")
    
    # Verificar se PyInstaller está instalado
    try:
        import PyInstaller
        print("✅ PyInstaller encontrado")
    except ImportError:
        print("❌ PyInstaller não encontrado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller instalado")
    
    # Limpar builds anteriores
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        print("🧹 Limpeza de builds anteriores concluída")
    
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Comando PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",                    # Arquivo único
        "--windowed",                   # Sem console (GUI)
        "--name=BrindeSystem",          # Nome do executável
        "--icon=assets/icon.ico",       # Ícone (se existir)
        "--add-data=src;src",          # Incluir código fonte
        "--hidden-import=customtkinter", # Imports necessários
        "--hidden-import=PIL",
        "--hidden-import=packaging",
        "--hidden-import=sqlite3",
        "--hidden-import=psutil",
        "--clean",                      # Limpeza antes do build
        "main.py"
    ]
    
    # Criar ícone padrão se não existir
    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    if not os.path.exists("assets/icon.ico"):
        print("⚠️  Ícone não encontrado, usando padrão")
        cmd.remove("--icon=assets/icon.ico")
    
    print("🔨 Executando PyInstaller...")
    print(f"Comando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build concluído com sucesso!")
        
        # Verificar se o executável foi criado
        exe_path = Path("dist/BrindeSystem.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Executável criado: {exe_path}")
            print(f"📏 Tamanho: {size_mb:.1f} MB")
            
            # Criar pasta de distribuição
            dist_folder = Path("distribuicao")
            if dist_folder.exists():
                shutil.rmtree(dist_folder)
            
            dist_folder.mkdir()
            
            # Copiar executável
            shutil.copy2(exe_path, dist_folder / "BrindeSystem.exe")
            
            # Criar README
            create_readme(dist_folder)
            
            # Criar script de instalação
            create_install_script(dist_folder)
            
            print(f"📁 Pasta de distribuição criada: {dist_folder.absolute()}")
            
        else:
            print("❌ Executável não foi criado")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no build: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False
    
    return True

def create_readme(dist_folder: Path):
    """Cria arquivo README para distribuição"""
    
    readme_content = """# Sistema de Controle de Brindes

## Descrição
Sistema completo para controle de estoque de brindes corporativos com:
- Gestão de brindes (cadastro, edição, exclusão)
- Controle de estoque (entrada, saída, transferências)
- Relatórios e dashboards
- Sistema de auditoria
- Gestão de usuários e filiais

## Requisitos do Sistema
- Windows 10 ou superior
- 4GB de RAM (recomendado)
- 100MB de espaço livre em disco

## Instalação

### Instalação Simples
1. Execute o arquivo `instalar.bat` como administrador
2. Siga as instruções na tela
3. O sistema será instalado em `C:\\Program Files\\BrindeSystem`

### Instalação Manual
1. Copie o arquivo `BrindeSystem.exe` para uma pasta de sua escolha
2. Execute o arquivo como administrador na primeira vez
3. O banco de dados será criado automaticamente

## Primeiro Uso
1. Execute o sistema
2. O login será feito automaticamente com seu usuário Windows
3. Na primeira execução, você será cadastrado como Administrador
4. Configure as filiais, categorias e unidades de medida
5. Comece a cadastrar seus brindes

## Funcionalidades Principais

### Dashboard
- Indicadores de estoque
- Gráficos de movimentação
- Alertas de estoque baixo

### Gestão de Brindes
- Cadastro completo com código automático
- Controle de quantidade e valor
- Categorização e filiais

### Movimentações
- Entrada de estoque
- Saída com justificativa
- Transferências entre filiais
- Histórico completo

### Configurações
- Gestão de usuários
- Cadastro de filiais
- Categorias e unidades
- Configurações gerais

### Relatórios
- Relatório de estoque
- Movimentações por período
- Itens com estoque baixo
- Auditoria do sistema

## Backup e Segurança
- Backup automático do banco de dados
- Sistema de logs completo
- Auditoria de todas as operações
- Controle de acesso por usuário

## Suporte
Para suporte técnico, entre em contato com a equipe de TI.

## Versão
Sistema de Controle de Brindes v1.0
Desenvolvido com Python e CustomTkinter
"""
    
    with open(dist_folder / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)

def create_install_script(dist_folder: Path):
    """Cria script de instalação"""
    
    install_script = """@echo off
echo ========================================
echo  Sistema de Controle de Brindes v1.0
echo  Script de Instalacao
echo ========================================
echo.

REM Verificar se esta executando como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Executando como administrador...
) else (
    echo ERRO: Execute este script como administrador!
    echo Clique com botao direito e selecione "Executar como administrador"
    pause
    exit /b 1
)

echo.
echo Criando diretorio de instalacao...
if not exist "C:\\Program Files\\BrindeSystem" (
    mkdir "C:\\Program Files\\BrindeSystem"
)

echo Copiando arquivos...
copy "BrindeSystem.exe" "C:\\Program Files\\BrindeSystem\\"
copy "README.txt" "C:\\Program Files\\BrindeSystem\\"

echo.
echo Criando atalho na area de trabalho...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Sistema de Brindes.lnk'); $Shortcut.TargetPath = 'C:\\Program Files\\BrindeSystem\\BrindeSystem.exe'; $Shortcut.Save()"

echo.
echo Criando entrada no menu iniciar...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\BrindeSystem" (
    mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\BrindeSystem"
)
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\BrindeSystem\\Sistema de Brindes.lnk'); $Shortcut.TargetPath = 'C:\\Program Files\\BrindeSystem\\BrindeSystem.exe'; $Shortcut.Save()"

echo.
echo ========================================
echo  INSTALACAO CONCLUIDA COM SUCESSO!
echo ========================================
echo.
echo O sistema foi instalado em:
echo C:\\Program Files\\BrindeSystem
echo.
echo Atalhos criados:
echo - Area de trabalho
echo - Menu iniciar
echo.
echo Pressione qualquer tecla para executar o sistema...
pause >nul

start "" "C:\\Program Files\\BrindeSystem\\BrindeSystem.exe"
"""
    
    with open(dist_folder / "instalar.bat", "w", encoding="cp1252") as f:
        f.write(install_script)

def create_spec_file():
    """Cria arquivo .spec personalizado para PyInstaller"""
    
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src')],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'packaging',
        'sqlite3',
        'psutil',
        'tkinter',
        'tkinter.messagebox',
        'tkinter.filedialog'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BrindeSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    with open("BrindeSystem.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)

if __name__ == "__main__":
    print("🎯 Sistema de Build - Controle de Brindes")
    print("=" * 50)
    
    if create_executable():
        print("\n🎉 Build concluído com sucesso!")
        print("📦 Arquivos de distribuição prontos na pasta 'distribuicao'")
        print("\n📋 Próximos passos:")
        print("1. Teste o executável")
        print("2. Distribua a pasta 'distribuicao' para os usuários")
        print("3. Execute 'instalar.bat' como administrador nos computadores de destino")
    else:
        print("\n❌ Falha no build")
        sys.exit(1)
