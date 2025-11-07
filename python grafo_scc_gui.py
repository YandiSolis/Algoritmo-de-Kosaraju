#!/usr/bin/env python3
import sys, time, math
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sys.setrecursionlimit(10000)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

TIKTOK_BG = "#000000"
TIKTOK_CARD = "#121212"
TIKTOK_ACCENT = "#FE2C55"
TIKTOK_SECONDARY = "#20D5EC"
TIKTOK_TEXT = "#FFFFFF"
TIKTOK_TEXT_SECONDARY = "#A0A0A0"

def centrar_ventana(parent, popup, w, h):
    parent.update_idletasks()
    pantalla_w = parent.winfo_screenwidth()
    pantalla_h = parent.winfo_screenheight()
    x = int((pantalla_w / 2) - (w / 2))
    y = int((pantalla_h / 2) - (h / 2))
    popup.geometry(f"{w}x{h}+{x}+{y}")
    popup.transient(parent)
    popup.grab_set()

class Grafo:
    def __init__(self):
        self.adyacencia = defaultdict(list)
    
    def agregar_nodo(self, nombre):
        if nombre not in self.adyacencia:
            self.adyacencia[nombre] = []
    
    def agregar_arista(self, u, v):
        if u not in self.adyacencia:
            self.adyacencia[u] = []
        if v not in self.adyacencia:
            self.adyacencia[v] = []
        if v not in self.adyacencia[u]:
            self.adyacencia[u].append(v)
    
    def eliminar_nodo(self, nombre):
        if nombre in self.adyacencia:
            del self.adyacencia[nombre]
        for u in list(self.adyacencia.keys()):
            if nombre in self.adyacencia[u]:
                self.adyacencia[u].remove(nombre)
    
    def eliminar_arista(self, u, v):
        if u in self.adyacencia and v in self.adyacencia[u]:
            self.adyacencia[u].remove(v)
    
    def nodos(self):
        return list(self.adyacencia.keys())
    
    def aristas(self):
        aristas = []
        for u, vecinos in self.adyacencia.items():
            for v in vecinos:
                aristas.append((u, v))
        return aristas
    
    def kosaraju_scc(self):
        visitado = set()
        pila = []
        
        def dfs_primera(u):
            visitado.add(u)
            for v in self.adyacencia[u]:
                if v not in visitado:
                    dfs_primera(v)
            pila.append(u)
        
        for u in self.adyacencia:
            if u not in visitado:
                dfs_primera(u)
        
        grafo_transpuesto = defaultdict(list)
        for u in self.adyacencia:
            for v in self.adyacencia[u]:
                grafo_transpuesto[v].append(u)
        
        for u in self.adyacencia:
            grafo_transpuesto.setdefault(u, [])
        
        visitado.clear()
        componentes = []
        
        def dfs_segunda(u, comp):
            visitado.add(u)
            comp.append(u)
            for v in grafo_transpuesto[u]:
                if v not in visitado:
                    dfs_segunda(v, comp)
        
        while pila:
            u = pila.pop()
            if u not in visitado:
                comp = []
                dfs_segunda(u, comp)
                componentes.append(comp)
        
        return componentes
    
    def tarjan_scc(self):
        indice = 0
        indices = {}
        low = {}
        en_pila = set()
        pila = []
        componentes = []
        
        def conexion_fuerte(v):
            nonlocal indice
            indices[v] = indice
            low[v] = indice
            indice += 1
            pila.append(v)
            en_pila.add(v)
            
            for w in self.adyacencia[v]:
                if w not in indices:
                    conexion_fuerte(w)
                    low[v] = min(low[v], low[w])
                elif w in en_pila:
                    low[v] = min(low[v], indices[w])
            
            if low[v] == indices[v]:
                comp = []
                while True:
                    w = pila.pop()
                    en_pila.remove(w)
                    comp.append(w)
                    if w == v:
                        break
                componentes.append(comp)
        
        for v in self.adyacencia:
            if v not in indices:
                conexion_fuerte(v)
        
        return componentes

class AppTikTok(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TikTok Network - Análisis de Comunidades")
        self.geometry("1400x900")
        self.configure(fg_color=TIKTOK_BG)
        self.grafo = Grafo()
        self.posiciones = {}
        self.arrastrando = False
        self.ultimo_raton = None
        self.ventana_perfil_actual = None
        
        plt.style.use('dark_background')
        
        self.crear_header()
        self.crear_layout_principal()

    def crear_header(self):
        header = ctk.CTkFrame(self, fg_color=TIKTOK_BG, height=80)
        header.pack(fill="x", padx=0, pady=0)
        
        logo_frame = ctk.CTkFrame(header, fg_color="transparent")
        logo_frame.pack(side="left", padx=20, pady=15)
        
        ctk.CTkLabel(logo_frame, text="📱", font=("Segoe UI", 24)).pack(side="left")
        ctk.CTkLabel(logo_frame, text="TikTok Network", 
                    font=("Segoe UI", 20, "bold"), 
                    text_color=TIKTOK_TEXT).pack(side="left", padx=(10,0))
        
        frame_botones = ctk.CTkFrame(header, fg_color="transparent")
        frame_botones.pack(side="right", padx=20, pady=15)
        
        botones = [
            ("👤 Crear Perfil", self.abrir_crear_perfil, TIKTOK_SECONDARY),
            ("🔍 Explorar", self.abrir_explorar, TIKTOK_ACCENT),
            ("🗑️ Administrar", self.abrir_administrar, "#FF4444"),
            ("⚡ Kosaraju", self.ejecutar_kosaraju, "#25F4EE"),
            ("🔍 Tarjan", self.ejecutar_tarjan, "#FE2C55"),
            ("🔄 Reiniciar", self.limpiar_grafo, "#696969")
        ]
        
        for texto, comando, color in botones:
            ctk.CTkButton(frame_botones, 
                         text=texto,
                         command=comando,
                         fg_color=color,
                         hover_color=self.ajustar_brillo(color, 0.8),
                         text_color=TIKTOK_BG if color != "#696969" else TIKTOK_TEXT,
                         font=("Segoe UI", 12, "bold"),
                         width=120,
                         height=35).pack(side="left", padx=5)

    def ajustar_brillo(self, color, factor):
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(min(255, int(c * factor)) for c in rgb)
        return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'

    def crear_layout_principal(self):
        main = ctk.CTkFrame(self, fg_color=TIKTOK_BG)
        main.pack(fill="both", expand=True, padx=15, pady=(0,15))
        
        panel_izquierdo = ctk.CTkFrame(main, fg_color=TIKTOK_CARD, width=300, corner_radius=15)
        panel_izquierdo.pack(side="left", fill="y", padx=(0,10))
        panel_izquierdo.pack_propagate(False)
        
        panel_central = ctk.CTkFrame(main, fg_color=TIKTOK_CARD, corner_radius=15)
        panel_central.pack(side="left", fill="both", expand=True, padx=10)
        
        panel_derecho = ctk.CTkFrame(main, fg_color=TIKTOK_CARD, width=350, corner_radius=15)
        panel_derecho.pack(side="right", fill="y", padx=(10,0))
        panel_derecho.pack_propagate(False)
        
        self.crear_panel_izquierdo(panel_izquierdo)
        self.crear_panel_central(panel_central)
        self.crear_panel_derecho(panel_derecho)

    def crear_panel_izquierdo(self, parent):
        titulo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        titulo_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(titulo_frame, 
                    text="👥 Creadores",
                    font=("Segoe UI", 18, "bold"),
                    text_color=TIKTOK_TEXT).pack(anchor="w")
        
        ctk.CTkLabel(titulo_frame,
                    text="Todos los perfiles en la red",
                    font=("Segoe UI", 12),
                    text_color=TIKTOK_TEXT_SECONDARY).pack(anchor="w")
        
        stats_frame = ctk.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=10)
        stats_frame.pack(fill="x", padx=15, pady=(0,15))
        
        self.etiqueta_stats = ctk.CTkLabel(stats_frame,
                                      text="📊 Estadísticas:\n• 0 creadores\n• 0 conexiones",
                                      font=("Segoe UI", 11),
                                      text_color=TIKTOK_TEXT_SECONDARY,
                                      justify="left")
        self.etiqueta_stats.pack(padx=15, pady=10)
        
        frame_lista = ctk.CTkFrame(parent, fg_color="transparent")
        frame_lista.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.lista_nodos = tk.Listbox(frame_lista,
                                      bg="#1E1E1E",
                                      fg=TIKTOK_TEXT,
                                      selectbackground=TIKTOK_ACCENT,
                                      selectforeground=TIKTOK_TEXT,
                                      font=("Segoe UI", 11),
                                      borderwidth=0,
                                      highlightthickness=0)
        
        scrollbar = ctk.CTkScrollbar(frame_lista, command=self.lista_nodos.yview)
        self.lista_nodos.configure(yscrollcommand=scrollbar.set)
        
        self.lista_nodos.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.lista_nodos.bind('<Double-1>', self.al_doble_click_lista)

    def al_doble_click_lista(self, event):
        seleccion = self.lista_nodos.curselection()
        if seleccion:
            usuario = self.lista_nodos.get(seleccion[0]).replace('@', '')
            self.mostrar_perfil_tiktok(usuario)

    def crear_panel_central(self, parent):
        titulo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        titulo_frame.pack(fill="x", padx=25, pady=20)
        
        ctk.CTkLabel(titulo_frame,
                    text="🌐 Red de Seguidores",
                    font=("Segoe UI", 18, "bold"),
                    text_color=TIKTOK_TEXT).pack(anchor="w")
        
        ctk.CTkLabel(titulo_frame,
                    text="Visualiza las comunidades y conexiones",
                    font=("Segoe UI", 12),
                    text_color=TIKTOK_TEXT_SECONDARY).pack(anchor="w")
        
        frame_grafico = ctk.CTkFrame(parent, fg_color="transparent")
        frame_grafico.pack(fill="both", expand=True, padx=20, pady=(0,20))
        
        self.figura, self.ejes = plt.subplots(figsize=(10, 8), facecolor=TIKTOK_CARD)
        self.figura.patch.set_alpha(0.0)
        self.lienzo = FigureCanvasTkAgg(self.figura, master=frame_grafico)
        self.widget_lienzo = self.lienzo.get_tk_widget()
        self.widget_lienzo.configure(bg=TIKTOK_CARD)
        self.widget_lienzo.pack(fill="both", expand=True)
        
        self.lienzo.mpl_connect('scroll_event', self.al_scroll)
        self.lienzo.mpl_connect('button_press_event', self.al_presionar_boton)
        self.lienzo.mpl_connect('button_release_event', self.al_soltar_boton)
        self.lienzo.mpl_connect('motion_notify_event', self.al_mover_raton)

    def crear_panel_derecho(self, parent):
        titulo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        titulo_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(titulo_frame,
                    text="📈 Resultados",
                    font=("Segoe UI", 18, "bold"),
                    text_color=TIKTOK_TEXT).pack(anchor="w")
        
        ctk.CTkLabel(titulo_frame,
                    text="Análisis de comunidades",
                    font=("Segoe UI", 12),
                    text_color=TIKTOK_TEXT_SECONDARY).pack(anchor="w")
        
        frame_texto = ctk.CTkFrame(parent, fg_color="transparent")
        frame_texto.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.texto_salida = ScrolledText(frame_texto,
                                      bg="#1E1E1E",
                                      fg=TIKTOK_TEXT,
                                      insertbackground=TIKTOK_TEXT,
                                      selectbackground=TIKTOK_ACCENT,
                                      font=("Consolas", 10),
                                      borderwidth=0,
                                      relief="flat",
                                      wrap="word")
        self.texto_salida.pack(fill="both", expand=True)

    def al_scroll(self, event):
        if event.inaxes is None: return
        escala_base = 1.25
        ax = event.inaxes
        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None: return
        
        xlim_actual = ax.get_xlim()
        ylim_actual = ax.get_ylim()
        factor_escala = escala_base if event.button == "up" else 1/escala_base
        
        nuevo_ancho = (xlim_actual[1] - xlim_actual[0]) * factor_escala
        nuevo_alto = (ylim_actual[1] - ylim_actual[0]) * factor_escala
        
        relx = (xdata - xlim_actual[0]) / (xlim_actual[1] - xlim_actual[0])
        rely = (ydata - ylim_actual[0]) / (ylim_actual[1] - ylim_actual[0])
        
        ax.set_xlim([xdata - nuevo_ancho * relx, xdata + nuevo_ancho * (1 - relx)])
        ax.set_ylim([ydata - nuevo_alto * rely, ydata + nuevo_alto * (1 - rely)])
        self.lienzo.draw_idle()

    def al_presionar_boton(self, event):
        if event.dblclick and event.button == 1 and event.inaxes:
            self.al_doble_click(event)
            return
        if event.button == 1 and event.inaxes:
            self.arrastrando = True
            self.ultimo_raton = (event.xdata, event.ydata)

    def al_soltar_boton(self, event):
        if event.button == 1:
            self.arrastrando = False
            self.ultimo_raton = None

    def al_mover_raton(self, event):
        if not self.arrastrando or event.inaxes is None or event.xdata is None or event.ydata is None:
            return
        
        ax = event.inaxes
        ultimo = self.ultimo_raton
        if ultimo is None:
            self.ultimo_raton = (event.xdata, event.ydata)
            return
        
        dx = ultimo[0] - event.xdata
        dy = ultimo[1] - event.ydata
        
        xlim_actual = ax.get_xlim()
        ylim_actual = ax.get_ylim()
        
        ax.set_xlim(xlim_actual[0] + dx, xlim_actual[1] + dx)
        ax.set_ylim(ylim_actual[0] + dy, ylim_actual[1] + dy)
        
        self.ultimo_raton = (event.xdata, event.ydata)
        self.lienzo.draw_idle()

    def al_doble_click(self, event):
        if event.inaxes is None or not self.posiciones:
            return
        
        x, y = event.xdata, event.ydata
        mas_cercano = None
        distancia_min = float('inf')
        
        for nodo, (nxp, nyp) in self.posiciones.items():
            dist = math.hypot(x - nxp, y - nyp)
            if dist < distancia_min:
                distancia_min = dist
                mas_cercano = nodo
        
        xlim = event.inaxes.get_xlim()
        ylim = event.inaxes.get_ylim()
        diagonal = math.hypot(xlim[1] - xlim[0], ylim[1] - ylim[0])
        
        if mas_cercano is not None and distancia_min <= diagonal * 0.05:
            self.mostrar_perfil_tiktok(mas_cercano)

    def mostrar_perfil_tiktok(self, usuario):
        if self.ventana_perfil_actual and self.ventana_perfil_actual.winfo_exists():
            self.ventana_perfil_actual.destroy()
        
        self.ventana_perfil_actual = ctk.CTkToplevel(self)
        popup = self.ventana_perfil_actual
        popup.title(f"@{usuario} - Perfil TikTok")
        popup.configure(fg_color=TIKTOK_BG)
        centrar_ventana(self, popup, 500, 700)
        
        header = ctk.CTkFrame(popup, fg_color=TIKTOK_CARD, corner_radius=15)
        header.pack(fill="x", padx=20, pady=20)
        
        frame_avatar = ctk.CTkFrame(header, fg_color="transparent")
        frame_avatar.pack(padx=20, pady=20)
        
        ctk.CTkLabel(frame_avatar, text="👤", font=("Segoe UI", 40)).pack()
        ctk.CTkLabel(frame_avatar, text=f"@{usuario}", 
                    font=("Segoe UI", 18, "bold"),
                    text_color=TIKTOK_TEXT).pack(pady=(10,5))
        ctk.CTkLabel(frame_avatar, text="Creador de contenido",
                    font=("Segoe UI", 12),
                    text_color=TIKTOK_TEXT_SECONDARY).pack()
        
        seguidores = [u for u, vecinos in self.grafo.adyacencia.items() if usuario in vecinos]
        siguiendo = list(self.grafo.adyacencia.get(usuario, []))
        
        stats_frame = ctk.CTkFrame(header, fg_color="#1E1E1E", corner_radius=10)
        stats_frame.pack(fill="x", padx=20, pady=(0,20))
        
        texto_stats = f"📊 Estadísticas del perfil\n\n"
        texto_stats += f"👀 Seguidores: {len(seguidores)}\n"
        texto_stats += f"❤️  Siguiendo: {len(siguiendo)}\n"
        texto_stats += f"🔗 Total: {len(seguidores) + len(siguiendo)}"
        
        ctk.CTkLabel(stats_frame, text=texto_stats,
                    font=("Segoe UI", 12),
                    text_color=TIKTOK_TEXT,
                    justify="left").pack(padx=15, pady=15)
        
        frame_eliminar = ctk.CTkFrame(header, fg_color="transparent")
        frame_eliminar.pack(fill="x", padx=20, pady=(0,10))
        
        ctk.CTkButton(frame_eliminar, text="🗑️ Eliminar Perfil",
                     fg_color="#FF4444",
                     hover_color="#CC0000",
                     text_color=TIKTOK_TEXT,
                     command=lambda: self.eliminar_perfil_usuario(usuario, popup)).pack(fill="x")
        
        cuerpo = ctk.CTkFrame(popup, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=20, pady=10)
        
        pestañas = ctk.CTkTabview(cuerpo, fg_color=TIKTOK_CARD)
        pestañas.pack(fill="both", expand=True)
        
        pestaña1 = pestañas.add("👥 Seguidores")
        pestaña2 = pestañas.add("❤️  Siguiendo")
        pestaña3 = pestañas.add("🔍 Explorar")
        
        self.configurar_pestaña_seguidores(pestaña1, seguidores, usuario)
        self.configurar_pestaña_siguiendo(pestaña2, siguiendo, usuario)
        self.configurar_pestaña_explorar(pestaña3, usuario)
        
        ctk.CTkButton(popup, text="Cerrar Perfil", 
                     command=popup.destroy,
                     fg_color=TIKTOK_TEXT_SECONDARY,
                     hover_color="#696969",
                     height=40).pack(pady=20)

    def configurar_pestaña_seguidores(self, pestaña, seguidores, usuario_actual):
        pestaña.configure(fg_color=TIKTOK_CARD)
        
        if not seguidores:
            ctk.CTkLabel(pestaña, text="No tiene seguidores aún",
                        text_color=TIKTOK_TEXT_SECONDARY).pack(expand=True)
            return
            
        frame_scroll = ctk.CTkScrollableFrame(pestaña, fg_color=TIKTOK_CARD)
        frame_scroll.pack(fill="both", expand=True)
        
        for usuario in seguidores:
            frame_usuario = ctk.CTkFrame(frame_scroll, fg_color="#1E1E1E", corner_radius=8)
            frame_usuario.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(frame_usuario, text=f"@{usuario}",
                        font=("Segoe UI", 11),
                        text_color=TIKTOK_TEXT).pack(side="left", padx=10, pady=8)
            
            if usuario in self.grafo.adyacencia.get(usuario_actual, []):
                ctk.CTkButton(frame_usuario, text="Dejar de seguir",
                             fg_color="#FF4444",
                             hover_color="#CC0000",
                             text_color=TIKTOK_TEXT,
                             width=120,
                             command=lambda u=usuario: self.dejar_de_seguir(usuario_actual, u)).pack(side="right", padx=10, pady=5)
            else:
                ctk.CTkButton(frame_usuario, text="Seguir",
                             fg_color=TIKTOK_ACCENT,
                             hover_color=self.ajustar_brillo(TIKTOK_ACCENT, 0.8),
                             text_color=TIKTOK_TEXT,
                             width=120,
                             command=lambda u=usuario: self.seguir_usuario(usuario_actual, u)).pack(side="right", padx=10, pady=5)

    def configurar_pestaña_siguiendo(self, pestaña, siguiendo, usuario_actual):
        pestaña.configure(fg_color=TIKTOK_CARD)
        
        if not siguiendo:
            ctk.CTkLabel(pestaña, text="No sigue a nadie aún",
                        text_color=TIKTOK_TEXT_SECONDARY).pack(expand=True)
            return
            
        frame_scroll = ctk.CTkScrollableFrame(pestaña, fg_color=TIKTOK_CARD)
        frame_scroll.pack(fill="both", expand=True)
        
        for usuario in siguiendo:
            frame_usuario = ctk.CTkFrame(frame_scroll, fg_color="#1E1E1E", corner_radius=8)
            frame_usuario.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(frame_usuario, text=f"@{usuario}",
                        font=("Segoe UI", 11),
                        text_color=TIKTOK_TEXT).pack(side="left", padx=10, pady=8)
            
            ctk.CTkButton(frame_usuario, text="Dejar de seguir",
                         fg_color="#FF4444",
                         hover_color="#CC0000",
                         text_color=TIKTOK_TEXT,
                         width=120,
                         command=lambda u=usuario: self.dejar_de_seguir(usuario_actual, u)).pack(side="right", padx=10, pady=5)

    def configurar_pestaña_explorar(self, pestaña, usuario_actual):
        pestaña.configure(fg_color=TIKTOK_CARD)
        frame_scroll = ctk.CTkScrollableFrame(pestaña, fg_color=TIKTOK_CARD)
        frame_scroll.pack(fill="both", expand=True)
        
        otros_usuarios = [u for u in self.grafo.nodos() if u != usuario_actual]
        
        if not otros_usuarios:
            ctk.CTkLabel(frame_scroll, text="No hay otros usuarios para seguir",
                        text_color=TIKTOK_TEXT_SECONDARY).pack(expand=True)
            return
            
        frame_busqueda = ctk.CTkFrame(frame_scroll, fg_color="transparent")
        frame_busqueda.pack(fill="x", pady=(0,10))
        
        entrada_busqueda = ctk.CTkEntry(frame_busqueda, placeholder_text="Buscar usuarios...")
        entrada_busqueda.pack(fill="x", padx=5)
        
        frame_usuarios = ctk.CTkFrame(frame_scroll, fg_color="transparent")
        frame_usuarios.pack(fill="both", expand=True)
        
        def filtrar_usuarios(*args):
            consulta = entrada_busqueda.get().lower()
            for widget in frame_usuarios.winfo_children():
                widget.destroy()
            usuarios_mostrar = [u for u in otros_usuarios if consulta in u.lower()] if consulta else otros_usuarios
            self.llenar_lista_usuarios(frame_usuarios, usuarios_mostrar, usuario_actual)
        
        entrada_busqueda.bind('<KeyRelease>', filtrar_usuarios)
        self.llenar_lista_usuarios(frame_usuarios, otros_usuarios, usuario_actual)

    def llenar_lista_usuarios(self, parent, usuarios, usuario_actual):
        for usuario in usuarios:
            frame_usuario = ctk.CTkFrame(parent, fg_color="#1E1E1E", corner_radius=8)
            frame_usuario.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(frame_usuario, text=f"@{usuario}",
                        font=("Segoe UI", 11),
                        text_color=TIKTOK_TEXT).pack(side="left", padx=10, pady=8)
            
            if usuario in self.grafo.adyacencia.get(usuario_actual, []):
                ctk.CTkButton(frame_usuario, text="Siguiendo ✓",
                             fg_color=TIKTOK_SECONDARY,
                             hover_color=self.ajustar_brillo(TIKTOK_SECONDARY, 0.8),
                             text_color=TIKTOK_BG,
                             width=120,
                             command=lambda u=usuario: self.dejar_de_seguir(usuario_actual, u)).pack(side="right", padx=10, pady=5)
            else:
                ctk.CTkButton(frame_usuario, text="Seguir",
                             fg_color=TIKTOK_ACCENT,
                             hover_color=self.ajustar_brillo(TIKTOK_ACCENT, 0.8),
                             text_color=TIKTOK_TEXT,
                             width=120,
                             command=lambda u=usuario: self.seguir_usuario(usuario_actual, u)).pack(side="right", padx=10, pady=5)

    def seguir_usuario(self, origen, destino):
        self.grafo.agregar_arista(origen, destino)
        self.actualizar_ui()
        if self.ventana_perfil_actual and self.ventana_perfil_actual.winfo_exists():
            self.ventana_perfil_actual.destroy()
            self.mostrar_perfil_tiktok(origen)

    def dejar_de_seguir(self, origen, destino):
        self.grafo.eliminar_arista(origen, destino)
        self.actualizar_ui()
        if self.ventana_perfil_actual and self.ventana_perfil_actual.winfo_exists():
            self.ventana_perfil_actual.destroy()
            self.mostrar_perfil_tiktok(origen)

    def eliminar_perfil_usuario(self, usuario, popup):
        if not messagebox.askyesno("Confirmar Eliminación", 
                                 f"¿Estás seguro de que quieres eliminar el perfil @{usuario}?\n\nEsta acción no se puede deshacer."):
            return
        
        popup.destroy()
        if self.ventana_perfil_actual and self.ventana_perfil_actual.winfo_exists():
            self.ventana_perfil_actual.destroy()
        
        self.grafo.eliminar_nodo(usuario)
        self.actualizar_ui()
        messagebox.showinfo("Perfil Eliminado", f"El perfil @{usuario} ha sido eliminado.")

    def abrir_administrar(self):
        if not self.grafo.adyacencia: 
            messagebox.showinfo("Info", "No hay perfiles para administrar")
            return
        
        popup = ctk.CTkToplevel(self)
        popup.title("🗑️ Administrar Perfiles")
        popup.configure(fg_color=TIKTOK_BG)
        centrar_ventana(self, popup, 600, 700)
        
        ctk.CTkLabel(popup, text="🗑️ Administrar Perfiles",
                    font=("Segoe UI", 18, "bold"),
                    text_color=TIKTOK_TEXT).pack(pady=20)
        
        frame_scroll = ctk.CTkScrollableFrame(popup, fg_color=TIKTOK_CARD)
        frame_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        for usuario in sorted(self.grafo.nodos()):
            frame_perfil = ctk.CTkFrame(frame_scroll, fg_color="#1E1E1E", corner_radius=10)
            frame_perfil.pack(fill="x", pady=5, padx=5)
            
            frame_info = ctk.CTkFrame(frame_perfil, fg_color="transparent")
            frame_info.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(frame_info, text=f"👤 @{usuario}",
                        font=("Segoe UI", 14, "bold"),
                        text_color=TIKTOK_TEXT).pack(anchor="w")
            
            seguidores = [u for u, vecinos in self.grafo.adyacencia.items() if usuario in vecinos]
            siguiendo = list(self.grafo.adyacencia.get(usuario, []))
            
            texto_stats = f"Seguidores: {len(seguidores)} | Siguiendo: {len(siguiendo)}"
            ctk.CTkLabel(frame_info, text=texto_stats,
                        font=("Segoe UI", 11),
                        text_color=TIKTOK_TEXT_SECONDARY).pack(anchor="w")
            
            frame_acciones = ctk.CTkFrame(frame_perfil, fg_color="transparent")
            frame_acciones.pack(fill="x", padx=15, pady=(0,10))
            
            ctk.CTkButton(frame_acciones, text="Ver Perfil",
                         fg_color=TIKTOK_SECONDARY,
                         hover_color=self.ajustar_brillo(TIKTOK_SECONDARY, 0.8),
                         text_color=TIKTOK_BG,
                         width=120,
                         command=lambda u=usuario: self.mostrar_perfil_desde_administrar(u, popup)).pack(side="left", padx=5)
            
            ctk.CTkButton(frame_acciones, text="Eliminar Perfil",
                         fg_color="#FF4444",
                         hover_color="#CC0000",
                         text_color=TIKTOK_TEXT,
                         width=120,
                         command=lambda u=usuario: self.eliminar_desde_administrar(u, popup)).pack(side="right", padx=5)
        
        ctk.CTkButton(popup, text="Cerrar",
                     command=popup.destroy,
                     fg_color=TIKTOK_TEXT_SECONDARY,
                     hover_color="#696969",
                     height=40).pack(pady=20)

    def mostrar_perfil_desde_administrar(self, usuario, popup_administrar):
        popup_administrar.destroy()
        self.mostrar_perfil_tiktok(usuario)

    def eliminar_desde_administrar(self, usuario, popup_administrar):
        if not messagebox.askyesno("Confirmar Eliminación", 
                                 f"¿Estás seguro de que quieres eliminar el perfil @{usuario}?"):
            return
        
        self.grafo.eliminar_nodo(usuario)
        self.actualizar_ui()
        
        if self.ventana_perfil_actual and self.ventana_perfil_actual.winfo_exists():
            self.ventana_perfil_actual.destroy()
        
        popup_administrar.destroy()
        self.abrir_administrar()
        messagebox.showinfo("Perfil Eliminado", f"El perfil @{usuario} ha sido eliminado.")

    def abrir_explorar(self):
        if not self.grafo.adyacencia: 
            messagebox.showinfo("Info", "Primero crea algunos perfiles")
            return
        
        popup = ctk.CTkToplevel(self)
        popup.title("🔍 Explorar Usuarios")
        popup.configure(fg_color=TIKTOK_BG)
        centrar_ventana(self, popup, 500, 600)
        
        ctk.CTkLabel(popup, text="🔍 Explorar Todos los Usuarios",
                    font=("Segoe UI", 16, "bold"),
                    text_color=TIKTOK_TEXT).pack(pady=20)
        
        frame_origen = ctk.CTkFrame(popup, fg_color=TIKTOK_CARD, corner_radius=10)
        frame_origen.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(frame_origen, text="Selecciona tu perfil:",
                    text_color=TIKTOK_TEXT).pack(pady=10)
        
        variable_origen = ctk.StringVar()
        combo_origen = ctk.CTkComboBox(frame_origen, 
                                     values=self.grafo.nodos(),
                                     variable=variable_origen,
                                     state="readonly")
        combo_origen.pack(fill="x", padx=20, pady=(0,10))
        
        frame_lista = ctk.CTkFrame(popup, fg_color="transparent")
        frame_lista.pack(fill="both", expand=True, padx=20, pady=10)
        
        def actualizar_lista_usuarios(*args):
            origen_actual = variable_origen.get()
            if not origen_actual:
                return
            
            for widget in frame_lista.winfo_children():
                widget.destroy()
            
            frame_scroll = ctk.CTkScrollableFrame(frame_lista, fg_color=TIKTOK_CARD)
            frame_scroll.pack(fill="both", expand=True)
            
            otros_usuarios = [u for u in self.grafo.nodos() if u != origen_actual]
            
            for usuario in otros_usuarios:
                frame_usuario = ctk.CTkFrame(frame_scroll, fg_color="#1E1E1E", corner_radius=8)
                frame_usuario.pack(fill="x", pady=2, padx=5)
                
                ctk.CTkLabel(frame_usuario, text=f"@{usuario}",
                            font=("Segoe UI", 11),
                            text_color=TIKTOK_TEXT).pack(side="left", padx=10, pady=8)
                
                if usuario in self.grafo.adyacencia.get(origen_actual, []):
                    ctk.CTkButton(frame_usuario, text="Dejar de seguir",
                                 fg_color="#FF4444",
                                 hover_color="#CC0000",
                                 text_color=TIKTOK_TEXT,
                                 width=120,
                                 command=lambda u=usuario: self.dejar_de_seguir(origen_actual, u)).pack(side="right", padx=10, pady=5)
                else:
                    ctk.CTkButton(frame_usuario, text="Seguir",
                                 fg_color=TIKTOK_ACCENT,
                                 hover_color=self.ajustar_brillo(TIKTOK_ACCENT, 0.8),
                                 text_color=TIKTOK_TEXT,
                                 width=120,
                                 command=lambda u=usuario: self.seguir_usuario(origen_actual, u)).pack(side="right", padx=10, pady=5)
        
        variable_origen.trace('w', actualizar_lista_usuarios)
        combo_origen.set(self.grafo.nodos()[0] if self.grafo.nodos() else "")

    def abrir_crear_perfil(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Crear Perfil TikTok")
        popup.configure(fg_color=TIKTOK_BG)
        centrar_ventana(self, popup, 400, 250)
        
        ctk.CTkLabel(popup, text="👤 Crear Nuevo Perfil",
                    font=("Segoe UI", 16, "bold"),
                    text_color=TIKTOK_TEXT).pack(pady=20)
        
        frame_entrada = ctk.CTkFrame(popup, fg_color="transparent")
        frame_entrada.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(frame_entrada, text="Nombre de usuario:",
                    text_color=TIKTOK_TEXT).pack(anchor="w")
        
        entrada = ctk.CTkEntry(frame_entrada, 
                           placeholder_text="@usuario",
                           height=40,
                           font=("Segoe UI", 12))
        entrada.pack(fill="x", pady=10)
        
        def crear():
            nombre = entrada.get().strip()
            if nombre.startswith("@"):
                nombre = nombre[1:]
            if not nombre: 
                messagebox.showwarning("Advertencia", "Ingresa un nombre válido")
                return
            if nombre in self.grafo.adyacencia: 
                messagebox.showwarning("Advertencia", "El usuario ya existe")
                return
            self.grafo.agregar_nodo(nombre)
            self.actualizar_ui()
            popup.destroy()
            messagebox.showinfo("¡Éxito!", f"🎉 Perfil @{nombre} creado")
        
        ctk.CTkButton(popup, text="Crear Perfil",
                     command=crear,
                     fg_color=TIKTOK_ACCENT,
                     hover_color=self.ajustar_brillo(TIKTOK_ACCENT, 0.8),
                     height=40).pack(pady=20)

    def ejecutar_kosaraju(self):
        if not self.grafo.adyacencia: 
            messagebox.showinfo("Info","No hay perfiles en la red")
            return
        inicio = time.perf_counter()
        componentes = self.grafo.kosaraju_scc()
        fin = time.perf_counter()
        self.mostrar_resultados("⚡ Kosaraju", componentes, fin - inicio)

    def ejecutar_tarjan(self):
        if not self.grafo.adyacencia: 
            messagebox.showinfo("Info","No hay perfiles en la red")
            return
        inicio = time.perf_counter()
        componentes = self.grafo.tarjan_scc()
        fin = time.perf_counter()
        self.mostrar_resultados("🔍 Tarjan", componentes, fin - inicio)

    def mostrar_resultados(self, nombre_algoritmo, componentes, tiempo_ejecucion):
        self.texto_salida.delete(1.0, tk.END)
        self.texto_salida.insert(tk.END, f"🎯 {nombre_algoritmo}\n\n")
        self.texto_salida.insert(tk.END, "🏆 Comunidades encontradas:\n\n")
        
        componentes_ordenados = sorted(componentes, key=lambda c: -len(c))
        for i, comp in enumerate(componentes_ordenados, 1):
            emoji = "👑" if len(comp) == max(len(c) for c in componentes_ordenados) else "👥"
            self.texto_salida.insert(tk.END, f"{emoji} Comunidad {i} (tamaño={len(comp)}): {comp}\n")
        
        self.texto_salida.insert(tk.END, f"\n⏱️  Tiempo: {tiempo_ejecucion:.6f} segundos\n")
        self.texto_salida.insert(tk.END, f"📊 Total comunidades: {len(componentes)}\n")
        
        self.dibujar_grafo(componentes)

    def limpiar_grafo(self):
        if messagebox.askyesno("Confirmar","¿Eliminar todos los perfiles y conexiones?"):
            self.grafo = Grafo()
            self.actualizar_ui()
            self.texto_salida.delete(1.0, tk.END)
            if self.ventana_perfil_actual and self.ventana_perfil_actual.winfo_exists():
                self.ventana_perfil_actual.destroy()
            messagebox.showinfo("Listo", "Red reiniciada")

    def actualizar_ui(self):
        self.actualizar_lista_nodos()
        self.actualizar_estadisticas()
        self.dibujar_grafo([])

    def actualizar_lista_nodos(self):
        self.lista_nodos.delete(0, tk.END)
        for nodo in sorted(self.grafo.nodos()): 
            self.lista_nodos.insert(tk.END, f"@{nodo}")

    def actualizar_estadisticas(self):
        num_nodos = len(self.grafo.nodos())
        num_aristas = len(self.grafo.aristas())
        self.etiqueta_stats.configure(
            text=f"📊 Estadísticas:\n• {num_nodos} creadores\n• {num_aristas} conexiones"
        )

    def dibujar_grafo(self, componentes):
        self.ejes.clear()
        G = nx.DiGraph()
        G.add_nodes_from(self.grafo.nodos())
        G.add_edges_from(self.grafo.aristas())
        
        paleta_colores = ['#FE2C55', '#25F4EE', '#FFFFFF', '#FFD600', '#69C9D0', '#EE1D52', '#20D5EC']
        mapa_colores = {}
        
        for i, comp in enumerate(componentes):
            for nodo in comp: 
                mapa_colores[nodo] = paleta_colores[i % len(paleta_colores)]
        
        colores = [mapa_colores.get(n, "#A0A0A0") for n in G.nodes()]
        
        if len(G.nodes()) == 0:
            self.ejes.text(0.5, 0.5, "Bienvenido a TikTok Network\n\nCrea tu primer perfil\npara empezar a conectar",
                        horizontalalignment='center', verticalalignment='center', 
                        fontsize=14, color=TIKTOK_TEXT, transform=self.ejes.transAxes)
            self.ejes.set_facecolor(TIKTOK_CARD)
            self.lienzo.draw_idle()
            return
        
        self.posiciones = nx.spring_layout(G, seed=42)
        
        nx.draw_networkx_edges(G, self.posiciones, ax=self.ejes, 
                              arrowstyle='-|>', arrowsize=20, width=2.0,
                              connectionstyle='arc3,rad=0.1', 
                              edge_color=TIKTOK_TEXT_SECONDARY, alpha=0.6)
        
        nx.draw_networkx_nodes(G, self.posiciones, ax=self.ejes, 
                              node_color=colores, node_size=1500,
                              edgecolors=TIKTOK_TEXT, linewidths=2.0,
                              alpha=0.9)
        
        nx.draw_networkx_labels(G, self.posiciones, ax=self.ejes, 
                               font_size=10, font_weight='bold',
                               font_family='Segoe UI',
                               bbox=dict(boxstyle="round,pad=0.3", facecolor=TIKTOK_CARD, 
                                        edgecolor='none', alpha=0.8))
        
        self.ejes.set_title("Red de TikTok - Comunidades de Seguidores", 
                         fontsize=16, color=TIKTOK_TEXT, pad=20)
        self.ejes.set_facecolor(TIKTOK_CARD)
        self.ejes.axis("off")
        self.lienzo.draw_idle()

if __name__ == "__main__":
    app = AppTikTok()
    app.mainloop()