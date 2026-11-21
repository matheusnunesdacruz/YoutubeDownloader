# YouTube Downloader IASD JD. das Oliveiras

Aplicativo desktop para Windows que permite buscar vídeos públicos do YouTube,
escolher a qualidade disponível e salvar o conteúdo em uma pasta local.

## Funcionalidades

- Interface gráfica em CustomTkinter.
- Download com `yt-dlp`.
- Seleção automática de qualidade.
- Download em segundo plano sem bloquear a interface.
- Localização automática de FFmpeg e Deno.
- Não exige `cookies.txt`, conta ou login.

## Requisitos

- Windows 10 ou superior.
- Python 3.10 ou superior.
- FFmpeg recomendado no `PATH` ou na raiz do projeto.
- Deno recomendado no `PATH` ou na raiz do projeto.

## Instalação

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Execução

```powershell
python main.py
```

## Configuração opcional

O aplicativo cria `config.json` automaticamente com a pasta padrão de download.
O arquivo `cookies.txt` não é necessário e não é carregado pelo programa.

## Compilar o executável

```powershell
python -m pip install pyinstaller
pyinstaller --noconsole --onedir --windowed main.py
```

O executável será gerado em `dist\main\`.

## Estrutura

- `main.py`: ponto de entrada.
- `interface.py`: interface gráfica.
- `downloader.py`: busca e download.
- `config.py`: configuração local.

## Uso responsável

Use o aplicativo apenas em vídeos que você tem autorização para baixar e respeite
os direitos autorais e os termos da plataforma.
