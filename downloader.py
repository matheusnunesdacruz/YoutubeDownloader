import yt_dlp


class Downloader:

    def __init__(self):
        self.info = None


    def buscar_video(self, url):

        opcoes = {
            "quiet": True,
            "no_warnings": True
        }

        with yt_dlp.YoutubeDL(opcoes) as ydl:
            self.info = ydl.extract_info(
                url,
                download=False
            )

        return self.info



    def qualidades(self):

        lista = []

        usados = set()


        for formato in self.info["formats"]:

            altura = formato.get("height")

            if altura is None:
                continue


            if formato.get("vcodec") == "none":
                continue


            qualidade = f"{altura}p"


            if qualidade not in usados:

                usados.add(qualidade)

                lista.append({
                    "nome": qualidade,
                    "id": formato["format_id"]
                })


        lista.sort(
            key=lambda x:
            int(x["nome"].replace("p",""))
        )


        return lista



    def baixar(
            self,
            url,
            formato,
            pasta,
            progresso=None):


        opcoes = {

            "format":
            f"{formato}+bestaudio/best",

            "merge_output_format":
            "mp4",

            "outtmpl":
            f"{pasta}/%(title)s.%(ext)s",


            "progress_hooks":
            [
                lambda dados:
                self.progresso(
                    dados,
                    progresso
                )
            ]
        }


        with yt_dlp.YoutubeDL(opcoes) as ydl:

            ydl.download([url])



    def progresso(self, dados, funcao):

        if funcao:

            if dados["status"] == "downloading":

                total = dados.get(
                    "total_bytes"
                ) or dados.get(
                    "total_bytes_estimate"
                )


                baixado = dados.get(
                    "downloaded_bytes",
                    0
                )


                if total:

                    porcentagem = (
                        baixado / total
                    )

                    funcao(
                        porcentagem
                    )