$ErrorActionPreference = "Stop"

$projectRoot = $PSScriptRoot
$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"

Push-Location $projectRoot
try {
    if (-not (Test-Path $venvPython)) {
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao criar o ambiente virtual."
        }
    }

    & $venvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao atualizar o pip."
    }

    & $venvPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao instalar as dependências do projeto."
    }

    & $venvPython -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao instalar o PyInstaller."
    }

    & $venvPython -m PyInstaller --clean --noconfirm --onefile --windowed --name YoutubeDownloader main.py
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao gerar o executável."
    }

    Write-Host "Executável gerado em: $(Join-Path $projectRoot 'dist\YoutubeDownloader.exe')"
}
finally {
    Pop-Location
}
