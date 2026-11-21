import os
import sys
import shutil
import urllib.parse


class Downloader:
    """
    Motor de download do aplicativo.

    Estratégia:
    - Não força player_client do YouTube.
    - Deixa o yt-dlp escolher os clientes suportados pela versão atual.
    - Usa process=False na busca para evitar falha de seleção de formato.
    - Usa seletores de formato com fallback.
    - Procura automaticamente por ffmpeg.
    - Procura automaticamente por Deno.
    - Funciona com conteúdo público sem cookies ou login.
    """

    def __init__(self):
        self.info = None

    # =========================================================
    # CAMINHOS
    # =========================================================

    def pasta_programa(self):
        if getattr(sys, "frozen", False):
            return os.path.dirname(os.path.abspath(sys.executable))

        return os.path.dirname(os.path.abspath(__file__))

    def caminho_arquivo(self, nome):
        return os.path.join(self.pasta_programa(), nome)

    # =========================================================
    # FFMPEG
    # =========================================================

    def localizar_ffmpeg(self):
        encontrado = shutil.which("ffmpeg")

        if encontrado:
            return os.path.dirname(encontrado)

        candidatos = [
            self.caminho_arquivo("ffmpeg.exe"),
            self.caminho_arquivo(
                os.path.join("ffmpeg", "bin", "ffmpeg.exe")
            ),
        ]

        try:
            for nome in os.listdir(self.pasta_programa()):
                caminho = os.path.join(
                    self.pasta_programa(),
                    nome
                )

                if not os.path.isdir(caminho):
                    continue

                if "ffmpeg" in nome.lower():
                    candidatos.append(
                        os.path.join(
                            caminho,
                            "bin",
                            "ffmpeg.exe"
                        )
                    )

        except OSError:
            pass

        for candidato in candidatos:
            if os.path.isfile(candidato):
                return os.path.dirname(candidato)

        return None

    # =========================================================
    # DENO
    # =========================================================

    def localizar_deno(self):
        encontrado = shutil.which("deno")

        if encontrado:
            return os.path.dirname(encontrado)

        candidatos = [
            self.caminho_arquivo("deno.exe"),
            self.caminho_arquivo(
                os.path.join("deno", "deno.exe")
            ),
        ]

        for candidato in candidatos:
            if os.path.isfile(candidato):
                return os.path.dirname(candidato)

        return None

    def preparar_runtime_js(self):
        """
        Coloca um Deno portátil no PATH se existir
        ao lado do programa.
        """

        deno_dir = self.localizar_deno()

        if deno_dir:
            path_atual = os.environ.get(
                "PATH",
                ""
            )

            partes = path_atual.split(
                os.pathsep
            )

            if deno_dir not in partes:
                os.environ["PATH"] = (
                    deno_dir
                    + os.pathsep
                    + path_atual
                )

            return deno_dir

        return None

    # =========================================================
    # URL
    # =========================================================

    def limpar_url(self, url):
        url = (url or "").strip()

        if not url:
            raise ValueError(
                "O link do YouTube está vazio."
            )

        try:
            parsed = urllib.parse.urlparse(url)

            host = parsed.netloc.lower()

            # youtube.com/watch?v=ID
            if (
                "youtube.com" in host
                and parsed.path == "/watch"
            ):
                query = urllib.parse.parse_qs(
                    parsed.query
                )

                video_id = query.get(
                    "v",
                    [None]
                )[0]

                if video_id:
                    return (
                        "https://www.youtube.com/watch?v="
                        + video_id
                    )

            # youtu.be/ID
            if "youtu.be" in host:
                video_id = (
                    parsed.path
                    .strip("/")
                    .split("/")[0]
                )

                if video_id:
                    return (
                        "https://www.youtube.com/watch?v="
                        + video_id
                    )

        except Exception:
            pass

        return url

    # =========================================================
    # CONFIGURAÇÃO
    # =========================================================

    def configuracao_base(self):

        # Ativa/procura Deno.
        self.preparar_runtime_js()

        opcoes = {

            "quiet": True,

            "no_warnings": True,

            "noplaylist": True,

            "retries": 10,

            "fragment_retries": 10,

            "file_access_retries": 5,

            "socket_timeout": 30,

            "continuedl": True,

            "prefer_ffmpeg": True,

            "merge_output_format": "mp4",

            "no_color": True,

            # Paralelismo moderado.
            "concurrent_fragment_downloads": 3,

            # Cache do yt-dlp.
            "cachedir": self.caminho_arquivo(
                "yt-dlp-cache"
            ),

            "extractor_args": {
                "youtube": {
                    "player_client": [
                        "android",
                        "ios",
                        "web",
                    ]
                }
            },
        }

        ffmpeg_dir = self.localizar_ffmpeg()

        if ffmpeg_dir:
            opcoes["ffmpeg_location"] = (
                ffmpeg_dir
            )

        return opcoes

    # =========================================================
    # BUSCAR VÍDEO
    # =========================================================

    def buscar_video(self, url):
        import yt_dlp

        url_limpa = self.limpar_url(url)

        opcoes = self.configuracao_base()

        try:

            with yt_dlp.YoutubeDL(
                opcoes
            ) as ydl:

                self.info = ydl.extract_info(
                    url_limpa,
                    download=False,
                    process=True
                )

        except Exception as erro:

            mensagem = str(erro)

            if (
                "Requested format is not available"
                in mensagem
            ):

                mensagem += (
                    "\n\nO YouTube não entregou "
                    "formatos utilizáveis para "
                    "esta sessão."
                    "\n\nVerifique o Deno e atualize "
                    "o yt-dlp."
                )

            raise Exception(
                "Não foi possível buscar o vídeo."
                "\n\n"
                + mensagem
            )

        if not self.info:

            raise Exception(
                "O YouTube não retornou informações "
                "do vídeo."
            )

        formatos = self.info.get(
            "formats"
        ) or []

        if not formatos:

            raise Exception(
                "O vídeo foi localizado, mas o "
                "YouTube não retornou formatos."
                "\n\n"
                "Verifique se o Deno está instalado "
                "e se o yt-dlp foi instalado com "
                "[default]."
            )

        return self.info

    # =========================================================
    # QUALIDADES
    # =========================================================

    def qualidades(self):

        lista = []

        alturas = set()

        if not self.info:
            return lista

        for formato in self.info.get(
            "formats",
            []
        ):

            altura = formato.get(
                "height"
            )

            if not altura:
                continue

            if formato.get(
                "vcodec"
            ) == "none":
                continue

            if altura not in alturas:

                alturas.add(altura)

                lista.append({
                    "id": int(altura),
                    "nome": f"{int(altura)}p",
                    "altura": int(altura)
                })

        lista.sort(
            key=lambda item:
            item["altura"],
            reverse=True
        )

        return lista

    # =========================================================
    # FORMATO
    # =========================================================

    def montar_formato(self, formato):

        if formato in (
            None,
            "",
            "Formato automático"
        ):

            return (
                "bestvideo*+bestaudio/best"
            )

        try:

            altura = int(formato)

        except (
            TypeError,
            ValueError
        ):

            return (
                "bestvideo*+bestaudio/best"
            )

        return (
            f"bestvideo[height<={altura}]"
            "+bestaudio/"
            f"best[height<={altura}]/"
            "best"
        )

    # =========================================================
    # DOWNLOAD
    # =========================================================

    def baixar(
        self,
        url,
        formato,
        pasta,
        progresso=None
    ):

        import yt_dlp

        url_limpa = self.limpar_url(
            url
        )

        if not pasta:

            raise Exception(
                "Escolha uma pasta para "
                "salvar o vídeo."
            )

        os.makedirs(
            pasta,
            exist_ok=True
        )

        opcoes = self.configuracao_base()

        opcoes.update({

            "format": self.montar_formato(
                formato
            ),

            "outtmpl": os.path.join(
                pasta,
                "%(title)s [%(id)s].%(ext)s"
            ),

            "windowsfilenames": True,

            "trim_file_name": 240,

            "progress_hooks": [
                lambda dados:
                self.progresso(
                    dados,
                    progresso
                )
            ],
        })

        try:

            with yt_dlp.YoutubeDL(
                opcoes
            ) as ydl:

                info = ydl.extract_info(
                    url_limpa,
                    download=True
                )

                if not info:

                    raise Exception(
                        "O yt-dlp não retornou "
                        "informações após o download."
                    )

                caminho_base = (
                    ydl.prepare_filename(
                        info
                    )
                )

                pasta_saida = (
                    os.path.dirname(
                        caminho_base
                    )
                )

                nome_base = os.path.splitext(
                    os.path.basename(
                        caminho_base
                    )
                )[0]

                candidatos = [

                    os.path.join(
                        pasta_saida,
                        nome_base + ".mp4"
                    ),

                    caminho_base,
                ]

                try:

                    for arquivo in os.listdir(
                        pasta_saida
                    ):

                        caminho = os.path.join(
                            pasta_saida,
                            arquivo
                        )

                        if (
                            os.path.isfile(
                                caminho
                            )
                            and
                            os.path.splitext(
                                arquivo
                            )[0]
                            ==
                            nome_base
                        ):

                            candidatos.insert(
                                0,
                                caminho
                            )

                except OSError:

                    pass

                for candidato in candidatos:

                    if os.path.isfile(
                        candidato
                    ):

                        return os.path.abspath(
                            candidato
                        )

                raise Exception(
                    "O download terminou, mas "
                    "o arquivo final não foi "
                    "encontrado."
                )

        except Exception as erro:

            mensagem = str(
                erro
            )

            # FALLBACK AUTOMÁTICO
            if (
                "Requested format is not available"
                in mensagem
                and
                self.montar_formato(
                    formato
                ) != "best"
            ):

                try:

                    opcoes["format"] = "best"

                    with yt_dlp.YoutubeDL(
                        opcoes
                    ) as ydl:

                        info = ydl.extract_info(
                            url_limpa,
                            download=True
                        )

                        if info:

                            caminho_base = (
                                ydl.prepare_filename(
                                    info
                                )
                            )

                            pasta_saida = (
                                os.path.dirname(
                                    caminho_base
                                )
                            )

                            nome_base = (
                                os.path.splitext(
                                    os.path.basename(
                                        caminho_base
                                    )
                                )[0]
                            )

                            for arquivo in os.listdir(
                                pasta_saida
                            ):

                                caminho = (
                                    os.path.join(
                                        pasta_saida,
                                        arquivo
                                    )
                                )

                                if (
                                    os.path.isfile(
                                        caminho
                                    )
                                    and
                                    os.path.splitext(
                                        arquivo
                                    )[0]
                                    ==
                                    nome_base
                                ):

                                    return os.path.abspath(
                                        caminho
                                    )

                except Exception as erro2:

                    mensagem = str(
                        erro2
                    )

            if (
                "Requested format is not available"
                in mensagem
            ):

                mensagem += (
                    "\n\nNenhum formato compatível "
                    "foi disponibilizado para "
                    "esta sessão."
                    "\n\nConfira o Deno e atualize "
                    "o yt-dlp."
                )

            raise Exception(
                "Erro no download:"
                "\n\n"
                + mensagem
            )

    # =========================================================
    # PROGRESSO
    # =========================================================

    def progresso(
        self,
        dados,
        funcao
    ):

        if not funcao:
            return

        status = dados.get(
            "status"
        )

        if status == "downloading":

            total = (
                dados.get(
                    "total_bytes"
                )
                or
                dados.get(
                    "total_bytes_estimate"
                )
            )

            baixado = dados.get(
                "downloaded_bytes",
                0
            )

            if total:

                percentual = max(
                    0,
                    min(
                        1,
                        baixado / total
                    )
                )

                funcao(
                    percentual
                )

        elif status == "finished":

            funcao(1)