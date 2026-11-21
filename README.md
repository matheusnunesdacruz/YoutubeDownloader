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
- FFmpeg necessário para combinar faixas separadas de vídeo e áudio; alguns
  vídeos em 720p ou superior precisam dessa combinação.
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

## Gerar o executável no Windows

O PyInstaller gera o executável para a mesma plataforma e arquitetura do Python
usado na compilação. Para gerar a versão de Windows, faça o processo em um
computador com Windows.

1. Instale o Python 3.10 ou superior e abra o PowerShell na pasta do projeto,
   onde está o arquivo `main.py`.
2. Crie um ambiente virtual e instale as dependências do aplicativo:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

3. Instale o PyInstaller nesse mesmo ambiente:

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller
```

4. Gere um único arquivo executável:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm --onefile --windowed --name YoutubeDownloader main.py
```

5. Aguarde a compilação. O arquivo estará em
   `dist\YoutubeDownloader.exe`; dê dois cliques nele para abrir o aplicativo.

O FFmpeg e o Deno não são incluídos no executável. Instale o FFmpeg e adicione
`ffmpeg.exe` ao `PATH` do Windows, ou coloque-o ao lado do executável (ou em
`ffmpeg\bin`). Sem ele, alguns vídeos não podem ser baixados em 720p ou em
outras qualidades que exigem combinar áudio e vídeo. O Deno é recomendado para
que o `yt-dlp` consiga obter os formatos disponibilizados pelo YouTube.

Uma opção para instalar o FFmpeg no Windows com o WinGet é:

```powershell
winget install --id Gyan.FFmpeg.Shared --exact
```

Se o aplicativo informar que o FFmpeg não foi encontrado, instale-o e reinicie
o aplicativo e o terminal. Se necessário, reinicie a sessão do Windows para
que os novos processos recebam o `PATH` atualizado.

## Estrutura

- `main.py`: ponto de entrada.
- `interface.py`: interface gráfica.
- `downloader.py`: busca e download.
- `config.py`: configuração local.

## Uso responsável

Use o aplicativo apenas em vídeos que você tem autorização para baixar e respeite
os direitos autorais e os termos da plataforma.
