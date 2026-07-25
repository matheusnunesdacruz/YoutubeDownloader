import customtkinter as ctk
from tkinter import filedialog
from tkinter import messagebox
import threading

from downloader import Downloader
from config import Config


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class Interface(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Youtube Downloader")

        self.geometry("900x650")

        self.resizable(False, False)


        self.downloader = Downloader()

        self.configuracao = Config()

        self.url = ""

        self.formatos = []


        self.criar_interface()



    def criar_interface(self):


        titulo = ctk.CTkLabel(
            self,
            text="YOUTUBE DOWNLOADER",
            font=("Arial",30,"bold")
        )

        titulo.pack(pady=20)



        self.link = ctk.CTkEntry(
            self,
            width=700,
            height=40,
            placeholder_text="Cole o link do YouTube aqui"
        )

        self.link.pack()



        self.botao_buscar = ctk.CTkButton(
            self,
            text="Buscar Vídeo",
            command=self.buscar
        )

        self.botao_buscar.pack(pady=15)



        self.titulo_video = ctk.CTkLabel(
            self,
            text="Título: -",
            font=("Arial",16)
        )

        self.titulo_video.pack()



        self.qualidade = ctk.CTkComboBox(
            self,
            width=250,
            values=[]
        )

        self.qualidade.pack(pady=15)



        frame_pasta = ctk.CTkFrame(self)

        frame_pasta.pack(
            pady=10
        )


        self.pasta = ctk.CTkEntry(
            frame_pasta,
            width=500
        )

        self.pasta.insert(
            0,
            self.configuracao.get_pasta()
        )

        self.pasta.pack(
            side="left",
            padx=10
        )


        escolher = ctk.CTkButton(
            frame_pasta,
            text="Escolher Pasta",
            command=self.escolher_pasta
        )

        escolher.pack(
            side="left"
        )



        self.progress = ctk.CTkProgressBar(
            self,
            width=700
        )

        self.progress.set(0)

        self.progress.pack(
            pady=20
        )



        self.status = ctk.CTkLabel(
            self,
            text="Aguardando..."
        )

        self.status.pack()



        self.botao_download = ctk.CTkButton(
            self,
            text="BAIXAR VÍDEO",
            height=45,
            command=self.iniciar_download
        )

        self.botao_download.pack(
            pady=20
        )



    def buscar(self):

        url = self.link.get()

        if url == "":

            messagebox.showwarning(
                "Aviso",
                "Cole um link primeiro."
            )

            return


        self.status.configure(
            text="Buscando informações..."
        )


        threading.Thread(
            target=self.buscar_thread,
            args=(url,),
            daemon=True
        ).start()



    def buscar_thread(self,url):

        try:

            info = self.downloader.buscar_video(
                url
            )


            self.formatos = (
                self.downloader.qualidades()
            )


            lista = []


            for f in self.formatos:

                lista.append(
                    f["nome"]
                )


            self.qualidade.configure(
                values=lista
            )


            if lista:

                self.qualidade.set(
                    lista[-1]
                )


            self.titulo_video.configure(

                text=
                "Título: "
                +
                info["title"]

            )


            self.status.configure(
                text="Vídeo encontrado!"
            )


            self.url = url



        except Exception as erro:


            messagebox.showerror(
                "Erro",
                str(erro)
            )



    def escolher_pasta(self):

        pasta = filedialog.askdirectory()


        if pasta:

            self.pasta.delete(
                0,
                "end"
            )

            self.pasta.insert(
                0,
                pasta
            )


            self.configuracao.set_pasta(
                pasta
            )



    def iniciar_download(self):


        qualidade = self.qualidade.get()


        if qualidade == "":

            messagebox.showwarning(
                "Aviso",
                "Escolha uma qualidade."
            )

            return



        formato_id = None


        for f in self.formatos:

            if f["nome"] == qualidade:

                formato_id = f["id"]



        if formato_id is None:

            return



        self.status.configure(
            text="Baixando..."
        )


        threading.Thread(

            target=self.download_thread,

            args=(
                formato_id,
            ),

            daemon=True

        ).start()



    def download_thread(self, formato):


        self.downloader.baixar(

            self.url,

            formato,

            self.pasta.get(),

            self.atualizar_progresso

        )


        self.status.configure(
            text="Download concluído!"
        )



    def atualizar_progresso(self,valor):

        self.progress.set(
            valor
        )