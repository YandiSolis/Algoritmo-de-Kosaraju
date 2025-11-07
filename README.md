# TikTok Network - Análisis de Comunidades

**TikTok Network** es una aplicación de escritorio desarrollada en **Python** con la librería **CustomTkinter**, que simula una red de usuarios de TikTok. Permite crear perfiles, establecer conexiones entre creadores, explorar relaciones y analizar comunidades mediante los algoritmos de **Kosaraju** y **Tarjan** para detectar **componentes fuertemente conexas (SCC)** en grafos dirigidos.

---

## Características principales

- **Gestión de usuarios:**  
  Crea, elimina y administra perfiles de TikTok simulados.

- **Conexiones entre usuarios:**  
  Los perfiles pueden seguirse entre sí, formando un grafo dirigido de relaciones.

- **Visualización interactiva:**  
  Visualiza la red completa de seguidores en tiempo real con **NetworkX** y **Matplotlib**, con zoom y desplazamiento dinámico.

- **Análisis de comunidades:**  
  - **Kosaraju:** Encuentra los conjuntos de usuarios fuertemente conectados.  
  - **Tarjan:** Detecta comunidades mediante un algoritmo más eficiente.

- **Interfaz moderna estilo TikTok:**  
  Diseño oscuro, botones animados y estructura visual limpia usando **CustomTkinter**.

---

## Tecnologías utilizadas

| Tipo | Herramienta |
|------|--------------|
| Lenguaje principal | Python 3.10+ |
| GUI | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) |
| Backend visual | Tkinter |
| Graficación | Matplotlib |
| Modelado de grafos | NetworkX |
| Lógica | Algoritmos de Kosaraju y Tarjan |

---

## Instalación y ejecución

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/tuusuario/tiktok-network.git
   cd tiktok-network
