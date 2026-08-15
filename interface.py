import os
import sys
import subprocess
import threading

import customtkinter as ctk
from tkinter import filedialog, messagebox

from downloader import Downloader
from config import Config


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class Interface(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title(
            "DOWNLOAD YOUTUBE IASD JD. das Oliveiras"
        )

        self.geometry(
            "900x720"
        )

        self.resizable(
            False,
            False
        )

        self.downloader = Downloader()

        self.configuracao = Config()

        self.url = ""

        self.titulo_atual = ""

        self.formatos = []

        self.criando_busca = False

        self.criando_download = False

        self.criar_interface()

    # =====================================================
    # INTERFACE
    # =====================================================

    def criar_interface(self):

        titulo = ctk.CTkLabel(
            self,
            text=(
                "DOWNLOAD YOUTUBE "
                "IASD JD. das Oliveiras"
            ),
            font=(
                "Arial",
                26,
                "bold"
            )
        )

        titulo.pack(
            pady=(
                15,
                10
            )
        )

        frame_url = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        frame_url.pack(
            pady=10
        )

        self.link = ctk.CTkEntry(
            frame_url,
            width=500,
            height=40,
            placeholder_text=(
                "Cole o link do YouTube aqui..."
            )
        )

        self.link.pack(
            side="left",
            padx=(
                0,
                5
            )
        )

        self.botao_colar = ctk.CTkButton(
            frame_url,
            text="📋 Colar",
            width=80,
            height=40,
            command=self.colar_link
        )

        self.botao_colar.pack(
            side="left",
            padx=5
        )

        self.botao_buscar = ctk.CTkButton(
            frame_url,
            text="Buscar Vídeo",
            width=110,
            height=40,
            command=self.buscar
        )

        self.botao_buscar.pack(
            side="left",
            padx=(
                5,
                0
            )
        )

        self.titulo_video = ctk.CTkLabel(
            self,
            text="Título: -",
            font=(
                "Arial",
                15
            ),
            wraplength=700
        )

        self.titulo_video.pack(
            pady=5
        )

        self.qualidade = ctk.CTkComboBox(
            self,
            width=250,
            values=[
                "Aguardando vídeo..."
            ]
        )

        self.qualidade.pack(
            pady=10
        )

        frame_pasta = ctk.CTkFrame(
            self
        )

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
            pady=15
        )

        self.status = ctk.CTkLabel(
            self,
            text="Aguardando..."
        )

        self.status.pack()

        self.botao_download = ctk.CTkButton(
            self,
            text="BAIXAR VÍDEO",
            height=40,
            font=(
                "Arial",
                14,
                "bold"
            ),
            command=self.iniciar_download
        )

        self.botao_download.pack(
            pady=15
        )

        lbl_historico = ctk.CTkLabel(
            self,
            text=(
                "Vídeos Baixados nesta Sessão "
                "(clique para abrir):"
            ),
            font=(
                "Arial",
                14,
                "bold"
            )
        )

        lbl_historico.pack(
            pady=(
                10,
                2
            ),
            anchor="w",
            padx=100
        )

        self.lista_downloads = (
            ctk.CTkScrollableFrame(
                self,
                width=680,
                height=120
            )
        )

        self.lista_downloads.pack(
            pady=(
                0,
                15
            )
        )

    # =====================================================
    # THREAD -> UI
    # =====================================================

    def ui(self, funcao):

        try:

            self.after(
                0,
                funcao
            )

        except Exception:

            pass

    def mostrar_erro(
        self,
        titulo,
        mensagem
    ):

        self.ui(
            lambda:
            messagebox.showerror(
                titulo,
                mensagem
            )
        )

    # =====================================================
    # COLAR
    # =====================================================

    def colar_link(self):

        try:

            conteudo = (
                self.clipboard_get()
                .strip()
            )

            if conteudo:

                self.link.delete(
                    0,
                    "end"
                )

                self.link.insert(
                    0,
                    conteudo
                )

            else:

                messagebox.showwarning(
                    "Aviso",
                    "A área de transferência "
                    "está vazia."
                )

        except Exception:

            messagebox.showwarning(
                "Aviso",
                "Não foi possível ler "
                "a área de transferência."
            )

    # =====================================================
    # ABRIR ARQUIVO
    # =====================================================

    def abrir_arquivo(
        self,
        caminho
    ):

        try:

            if os.path.exists(caminho):

                if sys.platform == "win32":

                    os.startfile(
                        caminho
                    )

                elif sys.platform == "darwin":

                    subprocess.Popen([
                        "open",
                        caminho
                    ])

                else:

                    subprocess.Popen([
                        "xdg-open",
                        caminho
                    ])

                return

            pasta = os.path.dirname(
                caminho
            )

            if os.path.exists(pasta):

                if sys.platform == "win32":

                    os.startfile(
                        pasta
                    )

                elif sys.platform == "darwin":

                    subprocess.Popen([
                        "open",
                        pasta
                    ])

                else:

                    subprocess.Popen([
                        "xdg-open",
                        pasta
                    ])

                return

            messagebox.showerror(
                "Erro",
                "O arquivo ou pasta "
                "não foi encontrado."
            )

        except Exception as erro:

            messagebox.showerror(
                "Erro ao abrir",
                str(erro)
            )

    # =====================================================
    # HISTÓRICO
    # =====================================================

    def adicionar_ao_historico(
        self,
        titulo,
        caminho_exato
    ):

        btn_item = ctk.CTkButton(
            self.lista_downloads,
            text=f"🎬  {titulo}",
            anchor="w",
            fg_color="transparent",
            text_color="#3B82F6",
            hover_color="#2A2D32",
            height=30,
            font=(
                "Arial",
                13,
                "underline"
            ),
            command=lambda path=caminho_exato:
                self.abrir_arquivo(path)
        )

        btn_item.pack(
            fill="x",
            padx=5,
            pady=2
        )

    # =====================================================
    # BUSCA
    # =====================================================

    def buscar(self):

        url = (
            self.link.get()
            .strip()
        )

        if not url:

            messagebox.showwarning(
                "Aviso",
                "Cole um link primeiro."
            )

            return

        if (
            self.criando_busca
            or
            self.criando_download
        ):

            return

        self.criando_busca = True

        self.botao_buscar.configure(
            state="disabled"
        )

        self.botao_download.configure(
            state="disabled"
        )

        self.status.configure(
            text="Buscando informações..."
        )

        self.titulo_video.configure(
            text="Título: -"
        )

        self.qualidade.configure(
            values=[
                "Buscando..."
            ]
        )

        self.qualidade.set(
            "Buscando..."
        )

        threading.Thread(
            target=self.buscar_thread,
            args=(url,),
            daemon=True
        ).start()

    def buscar_thread(
        self,
        url
    ):

        try:

            info = (
                self.downloader
                .buscar_video(url)
            )

            formatos = (
                self.downloader
                .qualidades()
            )

            lista = [
                f["nome"]
                for f in formatos
            ]

            if lista:

                lista = list(
                    dict.fromkeys(
                        lista
                    )
                )

                lista.sort(
                    key=lambda valor:
                    int(
                        valor
                        .replace(
                            "p",
                            ""
                        )
                    ),
                    reverse=True
                )

                primeira = lista[0]

                self.ui(
                    lambda:
                    self.qualidade.configure(
                        values=lista
                    )
                )

                self.ui(
                    lambda:
                    self.qualidade.set(
                        primeira
                    )
                )

            else:

                self.ui(
                    lambda:
                    self.qualidade.configure(
                        values=[
                            "Formato automático"
                        ]
                    )
                )

                self.ui(
                    lambda:
                    self.qualidade.set(
                        "Formato automático"
                    )
                )

            self.titulo_atual = (
                info.get(
                    "title",
                    "Sem título"
                )
            )

            self.url = url

            self.formatos = formatos

            self.ui(
                lambda:
                self.titulo_video.configure(
                    text=(
                        "Título: "
                        + self.titulo_atual
                    )
                )
            )

            self.ui(
                lambda:
                self.status.configure(
                    text="Vídeo encontrado!"
                )
            )

        except Exception as erro:

            self.mostrar_erro(
                "Erro",
                str(erro)
            )

            self.ui(
                lambda:
                self.status.configure(
                    text="Falha ao buscar vídeo."
                )
            )

        finally:

            self.criando_busca = False

            self.ui(
                lambda:
                self.botao_buscar.configure(
                    state="normal"
                )
            )

            self.ui(
                lambda:
                self.botao_download.configure(
                    state="normal"
                )
            )

    # =====================================================
    # PASTA
    # =====================================================

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

    # =====================================================
    # DOWNLOAD
    # =====================================================

    def iniciar_download(self):

        qualidade = (
            self.qualidade.get()
        )

        if qualidade in [
            "",
            "Aguardando vídeo...",
            "Buscando..."
        ]:

            messagebox.showwarning(
                "Aviso",
                "Faça a busca do vídeo primeiro."
            )

            return

        if not self.url:

            messagebox.showwarning(
                "Aviso",
                "Faça a busca do vídeo primeiro."
            )

            return

        formato_id = None

        for formato in self.formatos:

            if formato["nome"] == qualidade:

                formato_id = (
                    formato["id"]
                )

                break

        if (
            formato_id is None
            and
            qualidade != "Formato automático"
        ):

            messagebox.showwarning(
                "Aviso",
                "Qualidade inválida."
            )

            return

        if self.criando_download:

            return

        self.criando_download = True

        self.botao_download.configure(
            state="disabled"
        )

        self.botao_buscar.configure(
            state="disabled"
        )

        self.status.configure(
            text="Baixando..."
        )

        self.progress.set(0)

        pasta = (
            self.pasta.get()
            .strip()
        )

        threading.Thread(
            target=self.download_thread,
            args=(
                formato_id,
                pasta
            ),
            daemon=True
        ).start()

    def download_thread(
        self,
        formato,
        pasta
    ):

        try:

            caminho_arquivo = (
                self.downloader.baixar(
                    self.url,
                    formato,
                    pasta,
                    self.atualizar_progresso
                )
            )

            self.ui(
                lambda:
                self.status.configure(
                    text="Download concluído!"
                )
            )

            self.ui(
                lambda:
                self.adicionar_ao_historico(
                    self.titulo_atual,
                    caminho_arquivo
                )
            )

        except Exception as erro:

            self.mostrar_erro(
                "Erro",
                str(erro)
            )

            self.ui(
                lambda:
                self.status.configure(
                    text="Falha no download."
                )
            )

        finally:

            self.criando_download = False

            self.ui(
                lambda:
                self.botao_download.configure(
                    state="normal"
                )
            )

            self.ui(
                lambda:
                self.botao_buscar.configure(
                    state="normal"
                )
            )

    # =====================================================
    # PROGRESSO
    # =====================================================

    def atualizar_progresso(
        self,
        valor
    ):

        self.ui(
            lambda:
            self.progress.set(
                max(
                    0,
                    min(
                        1,
                        valor
                    )
                )
            )
        )