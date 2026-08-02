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

        self.title("DOWNLOAD YOUTUBE IASD JD. das Oliveiras")
        self.geometry("900x720")
        self.resizable(False, False)

        self.downloader = Downloader()
        self.configuracao = Config()

        self.url = ""
        self.titulo_atual = ""
        self.formatos = []

        self.criar_interface()

    def criar_interface(self):
        # Título principal
        titulo = ctk.CTkLabel(
            self,
            text="DOWNLOAD YOUTUBE IASD JD. das Oliveiras",
            font=("Arial", 26, "bold")
        )
        titulo.pack(pady=(15, 10))

        # --- FRAME DE URL (Entrada + Botão Colar + Botão Buscar) ---
        frame_url = ctk.CTkFrame(self, fg_color="transparent")
        frame_url.pack(pady=10)

        self.link = ctk.CTkEntry(
            frame_url,
            width=500,
            height=40,
            placeholder_text="Cole o link do YouTube aqui..."
        )
        self.link.pack(side="left", padx=(0, 5))

        self.botao_colar = ctk.CTkButton(
            frame_url,
            text="📋 Colar",
            width=80,
            height=40,
            command=self.colar_link
        )
        self.botao_colar.pack(side="left", padx=5)

        self.botao_buscar = ctk.CTkButton(
            frame_url,
            text="Buscar Vídeo",
            width=110,
            height=40,
            command=self.buscar
        )
        self.botao_buscar.pack(side="left", padx=(5, 0))

        # --- INFORMAÇÕES DO VÍDEO ---
        self.titulo_video = ctk.CTkLabel(
            self,
            text="Título: -",
            font=("Arial", 15),
            wraplength=700
        )
        self.titulo_video.pack(pady=5)

        self.qualidade = ctk.CTkComboBox(
            self,
            width=250,
            values=["Aguardando vídeo..."]
        )
        self.qualidade.pack(pady=10)

        # --- SELEÇÃO DE PASTA ---
        frame_pasta = ctk.CTkFrame(self)
        frame_pasta.pack(pady=10)

        self.pasta = ctk.CTkEntry(frame_pasta, width=500)
        self.pasta.insert(0, self.configuracao.get_pasta())
        self.pasta.pack(side="left", padx=10)

        escolher = ctk.CTkButton(
            frame_pasta,
            text="Escolher Pasta",
            command=self.escolher_pasta
        )
        escolher.pack(side="left")

        # --- BARRA DE PROGRESSO E STATUS ---
        self.progress = ctk.CTkProgressBar(self, width=700)
        self.progress.set(0)
        self.progress.pack(pady=15)

        self.status = ctk.CTkLabel(self, text="Aguardando...")
        self.status.pack()

        self.botao_download = ctk.CTkButton(
            self,
            text="BAIXAR VÍDEO",
            height=40,
            font=("Arial", 14, "bold"),
            command=self.iniciar_download
        )
        self.botao_download.pack(pady=15)

        # --- HISTÓRICO CLICÁVEL DE VÍDEOS BAIXADOS ---
        lbl_historico = ctk.CTkLabel(
            self,
            text="Vídeos Baixados nesta Sessão (clique para abrir):",
            font=("Arial", 14, "bold")
        )
        lbl_historico.pack(pady=(10, 2), anchor="w", padx=100)

        # Frame rolável onde cada vídeo será inserido como um link clicável
        self.lista_downloads = ctk.CTkScrollableFrame(
            self,
            width=680,
            height=120
        )
        self.lista_downloads.pack(pady=(0, 15))

    # --- MÉTODOS DE AÇÃO E UTILITÁRIOS ---

    def colar_link(self):
        """Lê a área de transferência e cola no campo de link."""
        try:
            conteudo = self.clipboard_get().strip()
            if conteudo:
                self.link.delete(0, "end")
                self.link.insert(0, conteudo)
            else:
                messagebox.showwarning("Aviso", "A área de transferência está vazia.")
        except Exception:
            messagebox.showwarning("Aviso", "Não foi possível ler a área de transferência.")

    def abrir_arquivo(self, caminho):
        """Abre o arquivo no reprodutor padrão do sistema operacional."""
        try:
            if os.path.exists(caminho):
                if sys.platform == "win32":
                    os.startfile(caminho)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", caminho])
                else:
                    subprocess.Popen(["xdg-open", caminho])
            else:
                # Caso o nome do arquivo tenha mudado, abre a pasta do download
                pasta = os.path.dirname(caminho)
                if os.path.exists(pasta):
                    if sys.platform == "win32":
                        os.startfile(pasta)
                    elif sys.platform == "darwin":
                        subprocess.Popen(["open", pasta])
                    else:
                        subprocess.Popen(["xdg-open", pasta])
                else:
                    messagebox.showerror("Erro", "O arquivo ou pasta não foi encontrado.")
        except Exception as e:
            messagebox.showerror("Erro ao abrir", str(e))

    def adicionar_ao_historico(self, titulo, pasta):
        """Adiciona um item clicável à lista de vídeos baixados."""
        # Caminho onde o yt-dlp provavelmente salvou o vídeo em MP4
        caminho_provavel = os.path.join(pasta, f"{titulo}.mp4")

        # Se não achar exatamente .mp4, procura por qualquer arquivo na pasta contendo o título
        caminho_final = caminho_provavel
        if not os.path.exists(caminho_provavel) and os.path.exists(pasta):
            for arq in os.listdir(pasta):
                if arq.startswith(titulo[:20]):  # Compara os primeiros caracteres do título
                    caminho_final = os.path.join(pasta, arq)
                    break

        # Cria o item clicável (estilo link)
        btn_item = ctk.CTkButton(
            self.lista_downloads,
            text=f"🎬  {titulo}",
            anchor="w",
            fg_color="transparent",
            text_color="#3B82F6",  # Azul estilo hyperlink
            hover_color="#2A2D32",
            height=30,
            font=("Arial", 13, "underline"),
            command=lambda path=caminho_final: self.abrir_arquivo(path)
        )
        btn_item.pack(fill="x", padx=5, pady=2)

    def buscar(self):
        url = self.link.get().strip()

        if not url:
            messagebox.showwarning("Aviso", "Cole um link primeiro.")
            return

        self.status.configure(text="Buscando informações...")

        threading.Thread(
            target=self.buscar_thread,
            args=(url,),
            daemon=True
        ).start()

    def buscar_thread(self, url):
        try:
            info = self.downloader.buscar_video(url)
            self.formatos = self.downloader.qualidades()

            lista = [f["nome"] for f in self.formatos]
            lista = list(dict.fromkeys(lista))

            lista.sort(
                key=lambda x: int(x.replace("p", "")) if x.replace("p", "").isdigit() else 0,
                reverse=True
            )

            if lista:
                self.qualidade.configure(values=lista)
                self.qualidade.set(lista[0])
            else:
                self.qualidade.configure(values=["Formato automático"])
                self.qualidade.set("Formato automático")

            self.titulo_atual = info.get("title", "Sem título")
            self.titulo_video.configure(text="Título: " + self.titulo_atual)
            self.status.configure(text="Vídeo encontrado!")
            self.url = url

        except Exception as erro:
            messagebox.showerror("Erro", str(erro))

    def escolher_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta.delete(0, "end")
            self.pasta.insert(0, pasta)
            self.configuracao.set_pasta(pasta)

    def iniciar_download(self):
        qualidade = self.qualidade.get()

        if qualidade in ["", "Aguardando vídeo..."]:
            messagebox.showwarning("Aviso", "Escolha uma qualidade.")
            return

        formato_id = None
        for f in self.formatos:
            if f["nome"] == qualidade:
                formato_id = f["id"]
                break

        if formato_id is None and qualidade != "Formato automático":
            messagebox.showwarning("Aviso", "Qualidade inválida. Faça a busca novamente.")
            return

        self.botao_download.configure(state="disabled")
        self.status.configure(text="Baixando...")
        self.progress.set(0)

        threading.Thread(
            target=self.download_thread,
            args=(formato_id,),
            daemon=True
        ).start()

    def download_thread(self, formato):
        try:
            self.downloader.baixar(
                self.url,
                formato,
                self.pasta.get(),
                self.atualizar_progresso
            )

            self.status.configure(text="Download concluído!")

            # Adiciona o link na interface de forma segura para a thread principal
            pasta_destino = self.pasta.get()
            self.after(0, lambda: self.adicionar_ao_historico(self.titulo_atual, pasta_destino))

        except Exception as erro:
            messagebox.showerror("Erro", str(erro))

        finally:
            self.botao_download.configure(state="normal")

    def atualizar_progresso(self, valor):
        self.progress.set(valor)