import os
import sys
import yt_dlp



class Downloader:


    def __init__(self):

        self.info = None




    def caminho_arquivo(self, nome):


        if getattr(sys, "frozen", False):

            # Quando estiver rodando como EXE

            pasta = os.path.dirname(

                sys.executable

            )


        else:

            # Quando estiver rodando pelo Python

            pasta = os.path.dirname(

                os.path.abspath(__file__)

            )


        return os.path.join(

            pasta,

            nome

        )







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


            "merge_output_format": "mp4"


        }





        # ===========================
        # CARREGAMENTO DO COOKIE
        # ===========================


        caminho_cookie = self.caminho_arquivo(

            "cookies.txt"

        )



        if os.path.exists(caminho_cookie):


            opcoes["cookiefile"] = caminho_cookie



        return opcoes










    def buscar_video(self, url):


        opcoes = self.configuracao_base()



        try:


            with yt_dlp.YoutubeDL(opcoes) as ydl:


                self.info = ydl.extract_info(

                    url,

                    download=False

                )




        except Exception as erro:



            raise Exception(

                "Não foi possível buscar o vídeo.\n\n"

                + str(erro)

            )



        return self.info







    def qualidades(self):


        lista = []


        usadas = set()



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




            nome = f"{altura}p"




            if nome not in usadas:



                usadas.add(nome)



                lista.append({


                    "id": altura,


                    "nome": nome,


                    "altura": altura


                })







        lista.sort(

            key=lambda x:

            x["altura"],

            reverse=True

        )



        return lista











    def baixar(

            self,

            url,

            formato,

            pasta,

            progresso=None):





        os.makedirs(

            pasta,

            exist_ok=True

        )





        opcoes = self.configuracao_base()





        formato_download = (


            f"bestvideo[height<={formato}]"

            "+bestaudio/"

            f"best[height<={formato}]/"

            "best"

        )





        opcoes.update({



            "format":

            formato_download,



            "outtmpl":

            os.path.join(

                pasta,

                "%(title)s.%(ext)s"

            ),



            "progress_hooks":

            [

                lambda dados:

                self.progresso(

                    dados,

                    progresso

                )

            ]

        })






        try:



            with yt_dlp.YoutubeDL(opcoes) as ydl:



                ydl.download(

                    [

                        url

                    ]

                )





        except Exception as erro:



            raise Exception(

                "Erro no download:\n\n"

                + str(erro)

            )









    def progresso(

            self,

            dados,

            funcao):



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



                funcao(

                    baixado / total

                )






        elif status == "finished":



            funcao(1)