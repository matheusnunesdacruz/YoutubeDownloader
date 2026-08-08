import os
import sys
import urllib.parse
import yt_dlp


class Downloader:

    def __init__(self):
        self.info = None

    def caminho_arquivo(self, nome):
        if getattr(sys, "frozen", False):
            pasta = os.path.dirname(sys.executable)
        else:
            pasta = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(pasta, nome)

    def limpar_url(self, url):
        """Remove parâmetros desnecessários da URL mantendo apenas o ID do vídeo."""
        try:
            parsed = urllib.parse.urlparse(url)
            if "youtube.com" in parsed.netloc and "watch" in parsed.path:
                query = urllib.parse.parse_qs(parsed.query)
                video_id = query.get("v", [None])[0]
                if video_id:
                    return f"https://www.youtube.com/watch?v={video_id}"
        except Exception:
            pass
        return url

    def configuracao_base(self):
        opcoes = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "prefer_ffmpeg": True,
            "nocheckcertificate": True,
            "ignoreerrors": False,
            "retries": 10,
            "fragment_retries": 10,
            "continuedl": True,
            "merge_output_format": "mp4",
            "no_color": True,
        }

        caminho_cookie = self.caminho_arquivo("cookies.txt")
        if os.path.exists(caminho_cookie):
            opcoes["cookiefile"] = caminho_cookie

        return opcoes

    def buscar_video(self, url):
        url_limpa = self.limpar_url(url)
        opcoes = self.configuracao_base()

        try:
            with yt_dlp.YoutubeDL(opcoes) as ydl:
                self.info = ydl.extract_info(url_limpa, download=False)
        except Exception as erro:
            raise Exception("Não foi possível buscar o vídeo.\n\n" + str(erro))

        return self.info

    def qualidades(self):
        lista = []
        usadas = set()

        if not self.info:
            return lista

        for formato in self.info.get("formats", []):
            altura = formato.get("height")
            if not altura:
                continue

            # Considera apenas vídeos (mesmo os sem áudio nativo, que o ffmpeg vai juntar depois)
            if formato.get("vcodec") == "none":
                continue

            nome = f"{altura}p"

            if nome not in usadas:
                usadas.add(nome)
                lista.append({
                    "id": altura,
                    "nome": nome,
                    "altura": altura
                })

        lista.sort(key=lambda x: x["altura"], reverse=True)
        return lista

    def baixar(self, url, formato, pasta, progresso=None):
        url_limpa = self.limpar_url(url)
        os.makedirs(pasta, exist_ok=True)
        opcoes = self.configuracao_base()

        # Seleciona o vídeo na resolução desejada (ou melhor disponível) + melhor áudio
        formato_download = (
            f"bestvideo[height<={formato}]+bestaudio/"
            f"best[height<={formato}]/"
            "best"
        )

        opcoes.update({
            "format": formato_download,
            "outtmpl": os.path.join(pasta, "%(title)s.%(ext)s"),
            "progress_hooks": [
                lambda dados: self.progresso(dados, progresso)
            ]
        })

        try:
            with yt_dlp.YoutubeDL(opcoes) as ydl:
                info = ydl.extract_info(url_limpa, download=True)
                caminho_gerado = ydl.prepare_filename(info)
                
                base, _ = os.path.splitext(caminho_gerado)
                caminho_mp4 = base + ".mp4"

                if os.path.exists(caminho_mp4):
                    return caminho_mp4
                elif os.path.exists(caminho_gerado):
                    return caminho_gerado
                else:
                    return caminho_gerado

        except Exception as erro:
            raise Exception("Erro no download:\n\n" + str(erro))

    def progresso(self, dados, funcao):
        if not funcao:
            return

        status = dados.get("status")

        if status == "downloading":
            total = dados.get("total_bytes") or dados.get("total_bytes_estimate")
            baixado = dados.get("downloaded_bytes", 0)

            if total:
                funcao(baixado / total)

        elif status == "finished":
            funcao(1)