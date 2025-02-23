@echo off
setlocal enabledelayedexpansion

REM ========== 基本設定 ==========
set "CONDA_PATH=C:\Users\100ca\anaconda3"
set "ENV_NAME=base"
set "SCRIPTS_DIR=M:\ML\ChatGPT\gennote\batch\scripts"
set "LOGS_DIR=M:\ML\ChatGPT\gennote\batch\batch_logs"
set "PYTHON_EXE=%CONDA_PATH%\python.exe"
set "MAX_LOGS=30"

REM ========== 事前チェック ==========
if not exist "%CONDA_PATH%" (
    echo [ERROR] Conda path not found: %CONDA_PATH%
    exit /b 1
)

if not exist "%SCRIPTS_DIR%\" (
    echo [ERROR] Scripts directory not found: %SCRIPTS_DIR%
    exit /b 1
)

REM ========== ログ管理 ==========
if not exist "%LOGS_DIR%\" (
    mkdir "%LOGS_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to create logs directory
        exit /b 1
    )
)

REM 古いログ削除（最新30件を保持）
for /f "skip=%MAX_LOGS% eol=: delims=" %%F in ('dir /b /o-d "%LOGS_DIR%\*.log"') do (
    del "%LOGS_DIR%\%%F"
)

REM ========== Conda環境設定 ==========
call "%CONDA_PATH%\condabin\conda.bat" activate %ENV_NAME%
if errorlevel 1 (
    echo [ERROR] Conda activation failed
    exit /b 1
)

REM ========== スクリプト実行 ==========
set "timestamp=%date:/=-%_%time::=-%"
set "log=%LOGS_DIR%\%timestamp:.=%.log"

for %%f in ("%SCRIPTS_DIR%\search_*.py") do (
    echo [%time%] START: %%~nxf >> "%log%"
    
    "%PYTHON_EXE%" "%%f" >> "%log%" 2>&1
    
    if errorlevel 1 (
        echo [ERROR] FAILED: %%~nxf >> "%log%"
    ) else (
        echo [SUCCESS] COMPLETED: %%~nxf >> "%log%"
    )
)

REM ========== 後処理 ==========
call "%CONDA_PATH%\condabin\conda.bat" deactivate
echo All processes completed. Log: %log%

endlocal
