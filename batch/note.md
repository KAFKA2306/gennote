# 実践的Windowsタスク自動化ガイド：検索スクリプトの定期実行システム構築

## 実際の開発環境で使用中の完全設定ファイル

### 設定ファイル（config.ini）
```ini
[Paths]
PYTHON_EXE=C:\Users\100ca\AppData\Local\Programs\Python\Python310\python.exe
SCRIPTS_ROOT=M:\ML\ChatGPT\gennote\batch\scripts
LOG_STORE=M:\ML\ChatGPT\gennote\batch\batch_logs
MAX_LOG_DAYS=30

[Execution]
RETRY_COUNT=3
TIMEOUT_MIN=15
```

### 防御的バッチスクリプト（run_script_secure.bat）
```batch
@echo off
setlocal enabledelayedexpansion

REM === 初期化チェック ===
net use M: >nul || (
    echo [CRITICAL] M: drive not mapped
    exit /b 1
)

REM === 設定読込 ===
for /f "tokens=1,* delims==" %%a in (config.ini) do (
    set "%%a=%%b"
    echo Loaded config: %%a=%%b
)

REM === ディレクトリ検証 ===
dir "%SCRIPTS_ROOT%" >nul || (
    echo [ERROR] Invalid scripts directory
    exit /b 1
)

REM === ログ管理 ===
set "log_file=%LOG_STORE%\%date:~-10,4%%date:~-7,2%%date:~-4,2%.log"
if not exist "%log_file%" (
    type nul > "%log_file%"
)

REM === スクリプト実行 ===
for %%f in ("%SCRIPTS_ROOT%\search_*.py") do (
    echo [%time%] EXEC_START: %%~nxf >> "%log_file%"
    
    set "retry=0"
    :retry_loop
    "%PYTHON_EXE%" "%%f" >> "%log_file%" 2>&1
    
    if !errorlevel! neq 0 (
        set /a "retry+=1"
        if !retry! leq %RETRY_COUNT% (
            echo [RETRY !retry!] %%~nxf >> "%log_file%"
            timeout %TIMEOUT_MIN%
            goto retry_loop
        )
        echo [FATAL] MAX_RETRY_EXCEEDED >> "%log_file%"
        exit /b 1
    )
    
    echo [SUCCESS] %%~nxf >> "%log_file%"
)

REM === ログローテーション ===
forfiles /p "%LOG_STORE%" /m *.log /d -%MAX_LOG_DAYS% /c "cmd /c del @path"
```


## 最適化タスクスケジューラ設定手順

### PowerShell管理者コンソールで実行
```powershell
$action = New-ScheduledTaskAction `
    -Execute "M:\ML\ChatGPT\gennote\batch\run_script.bat"

$trigger = @(
    New-ScheduledTaskTrigger -Daily -At 7am -RandomDelay 00:01
    New-ScheduledTaskTrigger -Daily -At 5pm -RandomDelay 00:01
)

$settings = New-ScheduledTaskSettingsSet `
    -MultipleInstances IgnoreNew `
    -RestartCount 1 `
    -RestartInterval (New-TimeSpan -Minutes 10)

Register-ScheduledTask `
    -TaskName "PerplexitySearchScriptsAutoRunner" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -User "NT AUTHORITY\SYSTEM" `
    -RunLevel Highest
```


## 障害対応チェックリスト

| 現象 | 調査コマンド | 対処方法 |
|------|-------------|----------|
| スクリプト未実行 | `Get-ScheduledTaskInfo -TaskName "SearchScriptsAutoRunner"` | タスク状態を確認 |
| パスエラー | `Test-Path M:\ML\ChatGPT\gennote\batch\scripts` | ドライブマウント確認 |
| モジュール不足 | `Import-Module ScheduledTasks -Force` | タスクスケジューラモジュール再読み込み |
| 権限問題 | `icacls M:\ML\ChatGPT\gennote\batch /grant SYSTEM:(OI)(CI)F` | ACL設定変更 |

## 高度な運用テクニック

### 1. パフォーマンスモニタリング
```powershell
Get-Content -Path $logFile -Wait -Tail 50 | 
    Select-String -Pattern "実行開始|終了コード"
```

### 2. 自動エラー通知
```batch
REM エラー検出時にTeams通知
if !errorlevel! NEQ 0 (
    curl.exe -H "Content-Type: application/json" -d "{'text':'エラー発生: %%~nxf'}" https://webhook.office.com/...
)
```

### 3. 実行時間分析
```powershell
$logs = Get-ChildItem M:\ML\ChatGPT\gennote\batch\batch_logs\*.log
$logs | ForEach-Object {
    $content = Get-Content $_.FullName
    $start = $content | Select-String "実行開始" | Select-Object -First 1
    $end = $content | Select-String "終了コード" | Select-Object -Last 1
    [PSCustomObject]@{
        Date = $_.BaseName
        Duration = (New-TimeSpan -Start $start -End $end).TotalMinutes
    }
}
```