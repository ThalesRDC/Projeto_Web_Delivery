#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
Gerador de Imagens a partir de Diagramas Mermaid
Projeto: Plataforma Unificada de Gestão de Delivery (PUGD)
===============================================================================

Este script varre os arquivos Markdown presentes na pasta 'arquivos.md/diagramas'
(ou qualquer outro arquivo/pasta especificado), extrai os blocos de código
Mermaid (```mermaid ... ```) e gera:

  1. Imagens PNG (alta resolução, com fator de escala configurável)
  2. Imagens vetoriais SVG (escaláveis sem perda de qualidade)
  3. Arquivos de código Mermaid (.mmd)
  4. Páginas HTML interativas para visualização no navegador
  5. Uma página galeria 'index.html' consolidando todos os diagramas

Motores de Renderização Suportados:
  - 'api' (padrão): Serviço oficial Mermaid (mermaid.ink via compressão Pako/zlib).
                    Rápido, sem necessidade de instalar Node/Puppeteer.
  - 'cli' (--cli):  Executa o mermaid-cli (mmdc / npx @mermaid-js/mermaid-cli) localmente.
  - 'edge' (--edge): Captura screenshots usando o Microsoft Edge headless local.

Uso:
  python gerar_diagramas.py                     # Gera todos os diagramas em PNG e SVG
  python gerar_diagramas.py --format png        # Apenas PNG
  python gerar_diagramas.py --format svg        # Apenas SVG
  python gerar_diagramas.py --scale 3           # PNG em altíssima resolução (3x)
  python gerar_diagramas.py --theme dark        # Tema escuro do Mermaid
  python gerar_diagramas.py --output Diagramas  # Pasta de destino
===============================================================================
"""

import os
import re
import sys
import json
import zlib
import base64
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple

try:
    import requests
except ImportError:
    print("[ERRO] A biblioteca 'requests' é necessária. Instale com: pip install requests")
    sys.exit(1)


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# =============================================================================
# CORES E FORMATAÇÃO DE TERMINAL
# =============================================================================
class Cor:
    RESET = "\033[0m"
    NEGRITO = "\033[1m"
    VERDE = "\033[92m"
    AZUL = "\033[94m"
    CIANO = "\033[96m"
    AMARELO = "\033[93m"
    VERMELHO = "\033[91m"
    CINZA = "\033[90m"


def print_info(msg: str) -> None:
    print(f"{Cor.AZUL}[INFO] {msg}{Cor.RESET}")


def print_ok(msg: str) -> None:
    print(f"{Cor.VERDE}[OK] {msg}{Cor.RESET}")


def print_aviso(msg: str) -> None:
    print(f"{Cor.AMARELO}[AVISO] {msg}{Cor.RESET}")


def print_erro(msg: str) -> None:
    print(f"{Cor.VERMELHO}[ERRO] {msg}{Cor.RESET}")


# =============================================================================
# ESTRUTURA DE DADOS PARA DIAGRAMA
# =============================================================================
class Diagrama:
    def __init__(
        self,
        arquivo_origem: str,
        titulo: str,
        slug: str,
        codigo_mermaid: str,
        indice: int,
    ):
        self.arquivo_origem = arquivo_origem
        self.titulo = titulo
        self.slug = slug
        self.codigo_mermaid = codigo_mermaid.strip()
        self.indice = indice

    def __repr__(self) -> str:
        return f"<Diagrama '{self.slug}' ({self.titulo})>"


# =============================================================================
# FUNÇÕES DE EXTRAÇÃO E PROCESSAMENTO
# =============================================================================
def sanitizar_nome_arquivo(texto: str) -> str:
    """Converte um título ou nome em um slug limpo para nome de arquivo."""
    # Remover prefixos numéricos de markdown seções (ex: "8.1 ")
    # Manter o número no início se for numeração de diagrama (ex: "8.1_")
    texto = texto.strip()

    # Normalizar caracteres acentuados comuns em PT-BR
    substituicoes = {
        "á": "a", "à": "a", "ã": "a", "â": "a", "ä": "a",
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "í": "i", "ì": "i", "î": "i", "ï": "i",
        "ó": "o", "ò": "o", "õ": "o", "ô": "o", "ö": "o",
        "ú": "u", "ù": "u", "û": "u", "ü": "u",
        "ç": "c", "ñ": "n",
        "Á": "A", "À": "A", "Ã": "A", "Â": "A", "Ä": "A",
        "É": "E", "È": "E", "Ê": "E", "Ë": "E",
        "Í": "I", "Ì": "I", "Î": "I", "Ï": "I",
        "Ó": "O", "Ò": "O", "Õ": "O", "Ô": "O", "Ö": "O",
        "Ú": "U", "Ù": "U", "Û": "U", "Ü": "U",
        "Ç": "C", "Ñ": "N",
    }
    for orig, dest in substituicoes.items():
        texto = texto.replace(orig, dest)

    # Tratar pontuações especiais
    texto = re.sub(r"[^\w\s\.-]", "", texto)
    texto = re.sub(r"[\s\t]+", "_", texto)
    texto = re.sub(r"_+", "_", texto)
    texto = texto.strip("_")
    return texto.lower()


def extrair_diagramas_de_arquivo(caminho_md: Path) -> List[Diagrama]:
    """Lê um arquivo Markdown e extrai todos os blocos ```mermaid."""
    diagramas: List[Diagrama] = []
    nome_base = caminho_md.stem

    try:
        with open(caminho_md, "r", encoding="utf-8") as f:
            conteudo = f.read()
    except Exception as e:
        print_erro(f"Não foi possível ler {caminho_md}: {e}")
        return []

    linhas = conteudo.splitlines()
    in_mermaid = False
    bloco_atual: List[str] = []
    ultimo_titulo = ""
    indice = 0

    for linha in linhas:
        linha_strip = linha.strip()

        # Rastrear o cabeçalho mais recente (título da seção)
        if linha_strip.startswith("#") and not in_mermaid:
            # Remove marcadores '#' e limpa
            ultimo_titulo = re.sub(r"^#+\s*", "", linha_strip).strip()

        # Início de bloco mermaid
        elif linha_strip.startswith("```mermaid"):
            in_mermaid = True
            bloco_atual = []

        # Fim de bloco mermaid
        elif in_mermaid and linha_strip.startswith("```"):
            in_mermaid = False
            indice += 1
            codigo = "\n".join(bloco_atual).strip()

            if codigo:
                # Determinar o título
                titulo = ultimo_titulo if ultimo_titulo else f"{nome_base} - Diagrama {indice}"
                
                # Gerar slug para nome de arquivo
                slug_titulo = sanitizar_nome_arquivo(titulo)
                slug_arquivo = sanitizar_nome_arquivo(nome_base)

                if slug_titulo and len(slug_titulo) > 2:
                    slug = slug_titulo
                else:
                    slug = f"{slug_arquivo}_{indice}"

                diagramas.append(
                    Diagrama(
                        arquivo_origem=caminho_md.name,
                        titulo=titulo,
                        slug=slug,
                        codigo_mermaid=codigo,
                        indice=indice,
                    )
                )
            bloco_atual = []

        # Linhas dentro do bloco mermaid
        elif in_mermaid:
            bloco_atual.append(linha)

    # Se o arquivo terminou sem fechar o bloco ```
    if in_mermaid and bloco_atual:
        indice += 1
        codigo = "\n".join(bloco_atual).strip()
        if codigo:
            titulo = ultimo_titulo if ultimo_titulo else f"{nome_base} - Diagrama {indice}"
            slug = sanitizar_nome_arquivo(titulo) or f"{sanitizar_nome_arquivo(nome_base)}_{indice}"
            diagramas.append(
                Diagrama(
                    arquivo_origem=caminho_md.name,
                    titulo=titulo,
                    slug=slug,
                    codigo_mermaid=codigo,
                    indice=indice,
                )
            )

    return diagramas


# =============================================================================
# ENGINES DE RENDERIZAÇÃO
# =============================================================================
class RenderizadorMermaid:
    def __init__(
        self,
        output_dir: Path,
        tema: str = "default",
        escala: int = 2,
        formato: str = "all",
    ):
        self.output_dir = output_dir
        self.tema = tema
        self.escala = escala
        self.formato = formato  # 'all', 'png', 'svg'
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        }

    def _codificar_pako(self, codigo_mermaid: str) -> str:
        """Compacta o código Mermaid com zlib e converte para base64 URL-safe."""
        estado = {
            "code": codigo_mermaid,
            "mermaid": {
                "theme": self.tema,
            },
        }
        json_bytes = json.dumps(estado).encode("utf-8")
        comprimido = zlib.compress(json_bytes, level=9)
        return base64.urlsafe_b64encode(comprimido).decode("ascii")

    def renderizar_via_api(
        self, diag: Diagrama
    ) -> Tuple[Optional[Path], Optional[Path]]:
        """Renderiza o diagrama utilizando a API pública oficial mermaid.ink."""
        pako_str = self._codificar_pako(diag.codigo_mermaid)
        png_path: Optional[Path] = None
        svg_path: Optional[Path] = None

        # 1. Gerar SVG se solicitado
        if self.formato in ("all", "svg"):
            url_svg = f"https://mermaid.ink/svg/pako:{pako_str}"
            try:
                resp = requests.get(url_svg, headers=self.headers, timeout=25)
                if resp.status_code == 200 and resp.text.startswith("<svg"):
                    svg_dest = self.output_dir / f"{diag.slug}.svg"
                    with open(svg_dest, "w", encoding="utf-8") as f:
                        f.write(resp.text)
                    svg_path = svg_dest
                else:
                    print_aviso(
                        f"Falha ao gerar SVG para '{diag.slug}': HTTP {resp.status_code}"
                    )
            except Exception as e:
                print_aviso(f"Erro de rede ao baixar SVG de '{diag.slug}': {e}")

        # 2. Gerar PNG se solicitado
        if self.formato in ("all", "png"):
            url_png = (
                f"https://mermaid.ink/img/pako:{pako_str}?type=png&scale={self.escala}"
            )
            try:
                resp = requests.get(url_png, headers=self.headers, timeout=30)
                if resp.status_code == 200 and resp.content[:8] == b"\x89PNG\r\n\x1a\n":
                    png_dest = self.output_dir / f"{diag.slug}.png"
                    with open(png_dest, "wb") as f:
                        f.write(resp.content)
                    png_path = png_dest
                else:
                    print_aviso(
                        f"Falha ao gerar PNG para '{diag.slug}': HTTP {resp.status_code}"
                    )
            except Exception as e:
                print_aviso(f"Erro de rede ao baixar PNG de '{diag.slug}': {e}")

        return png_path, svg_path

    def renderizar_via_cli(
        self, diag: Diagrama, mmd_path: Path
    ) -> Tuple[Optional[Path], Optional[Path]]:
        """Renderiza usando mermaid-cli (mmdc) local."""
        png_path: Optional[Path] = None
        svg_path: Optional[Path] = None

        # Verificar comando disponível (mmdc ou npx @mermaid-js/mermaid-cli)
        cmd_base = ["mmdc"] if shutil.which("mmdc") else ["npx", "-y", "@mermaid-js/mermaid-cli"]

        if self.formato in ("all", "png"):
            dest_png = self.output_dir / f"{diag.slug}.png"
            cmd = cmd_base + [
                "-i", str(mmd_path),
                "-o", str(dest_png),
                "-s", str(self.escala),
                "-t", self.tema,
            ]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if res.returncode == 0 and dest_png.exists():
                    png_path = dest_png
                else:
                    print_aviso(f"mmdc falhou para PNG de '{diag.slug}': {res.stderr[:200]}")
            except Exception as e:
                print_aviso(f"Erro ao executar mmdc: {e}")

        if self.formato in ("all", "svg"):
            dest_svg = self.output_dir / f"{diag.slug}.svg"
            cmd = cmd_base + [
                "-i", str(mmd_path),
                "-o", str(dest_svg),
                "-t", self.tema,
            ]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if res.returncode == 0 and dest_svg.exists():
                    svg_path = dest_svg
                else:
                    print_aviso(f"mmdc falhou para SVG de '{diag.slug}': {res.stderr[:200]}")
            except Exception as e:
                print_aviso(f"Erro ao executar mmdc: {e}")

        return png_path, svg_path

    def salvar_mmd(self, diag: Diagrama) -> Path:
        """Salva o código Mermaid original em um arquivo .mmd."""
        caminho = self.output_dir / f"{diag.slug}.mmd"
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(diag.codigo_mermaid + "\n")
        return caminho

    def salvar_html(self, diag: Diagrama) -> Path:
        """Gera uma página HTML interativa individual com renderização Mermaid."""
        caminho = self.output_dir / f"{diag.slug}.html"
        html_conteudo = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{diag.titulo} - PUGD</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 24px;
      background: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #1e293b;
    }}
    .header {{
      text-align: center;
      margin-bottom: 24px;
    }}
    h1 {{
      margin: 0 0 8px 0;
      color: #0f172a;
      font-size: 22px;
      font-weight: 700;
    }}
    .meta {{
      color: #64748b;
      font-size: 13px;
    }}
    .actions {{
      margin-top: 14px;
      display: flex;
      justify-content: center;
      gap: 10px;
    }}
    .btn {{
      display: inline-block;
      padding: 7px 14px;
      background: #2563eb;
      color: white;
      text-decoration: none;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      transition: background 0.2s;
    }}
    .btn:hover {{ background: #1d4ed8; }}
    .btn-secondary {{ background: #64748b; }}
    .btn-secondary:hover {{ background: #475569; }}
    .diagram-container {{
      background: white;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 30px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 400px;
      overflow: auto;
    }}
    .footer {{
      text-align: center;
      margin-top: 24px;
      color: #94a3b8;
      font-size: 12px;
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>{diag.titulo}</h1>
    <div class="meta">Origem: <code>arquivos.md/diagramas/{diag.arquivo_origem}</code></div>
    <div class="actions">
      <a class="btn" href="{diag.slug}.png" download>Baixar PNG</a>
      <a class="btn btn-secondary" href="{diag.slug}.svg" download>Baixar SVG</a>
      <a class="btn btn-secondary" href="{diag.slug}.mmd" download>Código Mermaid (.mmd)</a>
      <a class="btn btn-secondary" href="index.html">← Voltar à Galeria</a>
    </div>
  </div>

  <div class="diagram-container">
    <pre class="mermaid">
{diag.codigo_mermaid}
    </pre>
  </div>

  <div class="footer">
    Plataforma Unificada de Gestão de Delivery (PUGD) • Renderizado via Mermaid.js
  </div>

  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    mermaid.initialize({{
      startOnLoad: true,
      theme: '{self.tema}',
      flowchart: {{ useMaxWidth: true, htmlLabels: true }},
      er: {{ useMaxWidth: true }},
      sequence: {{ useMaxWidth: true }}
    }});
  </script>
</body>
</html>"""
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(html_conteudo)
        return caminho


# =============================================================================
# GERADOR DA GALERIA HTML INDEX
# =============================================================================
def gerar_galeria_html(output_dir: Path, itens: List[Dict]) -> Path:
    """Gera um arquivo index.html navegável com todos os diagramas gerados."""
    caminho_index = output_dir / "index.html"

    cards_html = []
    for item in itens:
        slug = item["slug"]
        titulo = item["titulo"]
        origem = item["origem"]
        tem_png = item["png"] is not None
        tem_svg = item["svg"] is not None

        preview_img = f"{slug}.png" if tem_png else (f"{slug}.svg" if tem_svg else "")

        img_tag = (
            f'<img src="{preview_img}" alt="{titulo}" loading="lazy" />'
            if preview_img
            else '<div class="no-preview">Sem imagem disponível</div>'
        )

        botoes = []
        if tem_png:
            botoes.append(f'<a class="tag-btn png" href="{slug}.png" target="_blank">PNG</a>')
        if tem_svg:
            botoes.append(f'<a class="tag-btn svg" href="{slug}.svg" target="_blank">SVG</a>')
        botoes.append(f'<a class="tag-btn html" href="{slug}.html">Ver Interativo</a>')
        botoes.append(f'<a class="tag-btn mmd" href="{slug}.mmd" target="_blank">.MMD</a>')

        card = f"""
    <div class="card">
      <div class="card-preview">
        <a href="{slug}.html">
          {img_tag}
        </a>
      </div>
      <div class="card-body">
        <h3 class="card-title" title="{titulo}">{titulo}</h3>
        <div class="card-origin">Fonte: <code>{origem}</code></div>
        <div class="card-links">
          {' '.join(botoes)}
        </div>
      </div>
    </div>"""
        cards_html.append(card)

    cards_str = "\n".join(cards_html)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Galeria de Diagramas Técnicos - PUGD</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 0;
      background: #0f172a;
      color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    header {{
      background: #1e293b;
      border-bottom: 1px solid #334155;
      padding: 30px 40px;
    }}
    .header-content {{
      max-width: 1400px;
      margin: 0 auto;
    }}
    h1 {{
      margin: 0 0 10px 0;
      font-size: 26px;
      font-weight: 700;
      color: #f8fafc;
    }}
    p.lead {{
      margin: 0;
      color: #94a3b8;
      font-size: 15px;
    }}
    .stats {{
      margin-top: 15px;
      display: flex;
      gap: 20px;
      font-size: 13px;
      color: #38bdf8;
    }}
    main {{
      max-width: 1400px;
      margin: 30px auto;
      padding: 0 40px 60px 40px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
      gap: 24px;
    }}
    .card {{
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 12px 24px -6px rgba(0, 0, 0, 0.4);
      border-color: #38bdf8;
    }}
    .card-preview {{
      background: #ffffff;
      height: 240px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 16px;
      overflow: hidden;
    }}
    .card-preview a {{
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 100%;
    }}
    .card-preview img {{
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }}
    .no-preview {{
      color: #64748b;
      font-size: 13px;
    }}
    .card-body {{
      padding: 18px;
      display: flex;
      flex-direction: column;
      flex-grow: 1;
    }}
    .card-title {{
      margin: 0 0 6px 0;
      font-size: 16px;
      color: #f1f5f9;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .card-origin {{
      font-size: 12px;
      color: #94a3b8;
      margin-bottom: 16px;
    }}
    .card-origin code {{
      color: #38bdf8;
      background: #0f172a;
      padding: 2px 6px;
      border-radius: 4px;
    }}
    .card-links {{
      margin-top: auto;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .tag-btn {{
      font-size: 11px;
      font-weight: 600;
      padding: 5px 10px;
      border-radius: 6px;
      text-decoration: none;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      transition: opacity 0.2s;
    }}
    .tag-btn:hover {{ opacity: 0.85; }}
    .tag-btn.png {{ background: #10b981; color: white; }}
    .tag-btn.svg {{ background: #8b5cf6; color: white; }}
    .tag-btn.html {{ background: #0284c7; color: white; }}
    .tag-btn.mmd {{ background: #475569; color: white; }}
    footer {{
      text-align: center;
      padding: 30px;
      border-top: 1px solid #334155;
      color: #64748b;
      font-size: 13px;
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-content">
      <h1>Plataforma Unificada de Gestão de Delivery (PUGD)</h1>
      <p class="lead">Galeria de Diagramas Técnicos e de Arquitetura de Software</p>
      <div class="stats">
        <span>Total de diagramas: <strong>{len(itens)}</strong></span>
        <span>Origem: <code>arquivos.md/diagramas/</code></span>
        <span>Status: <strong>Atualizado</strong></span>
      </div>
    </div>
  </header>

  <main>
    <div class="grid">
{cards_str}
    </div>
  </main>

  <footer>
    PUGD • Diagramas gerados automaticamente com Mermaid Engine
  </footer>
</body>
</html>"""

    with open(caminho_index, "w", encoding="utf-8") as f:
        f.write(html)
    return caminho_index


# =============================================================================
# FLUXO PRINCIPAL DE EXECUÇÃO
# =============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Gera imagens (PNG, SVG, HTML) a partir de diagramas Mermaid em arquivos.md/diagramas."
    )
    parser.add_argument(
        "--input",
        "-i",
        default="arquivos.md/diagramas",
        help="Diretório ou arquivo Markdown de entrada (padrão: arquivos.md/diagramas)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="Diagramas",
        help="Diretório de saída para imagens geradas (padrão: Diagramas)",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["all", "png", "svg"],
        default="all",
        help="Formatos de imagem a serem gerados: png, svg ou all (padrão: all)",
    )
    parser.add_argument(
        "--theme",
        "-t",
        choices=["default", "neutral", "dark", "forest", "base"],
        default="default",
        help="Tema do Mermaid (padrão: default)",
    )
    parser.add_argument(
        "--scale",
        "-s",
        type=int,
        default=2,
        help="Fator de escala para qualidade do PNG (padrão: 2 para Retina)",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Força uso do mermaid-cli (mmdc) local em vez da API mermaid.ink",
    )

    args = parser.parse_args()

    # Resolver caminhos
    caminho_input = Path(args.input)
    caminho_output = Path(args.output)
    caminho_output.mkdir(parents=True, exist_ok=True)

    print(f"\n{Cor.NEGRITO}{Cor.CIANO}====================================================================")
    print("  GERADOR DE IMAGENS MERMAID - PROJETO WEB DELIVERY")
    print(f"===================================================================={Cor.RESET}\n")
    print_info(f"Pasta de Entrada : {caminho_input}")
    print_info(f"Pasta de Saída   : {caminho_output}")
    print_info(f"Formato          : {args.format.upper()}")
    print_info(f"Tema Mermaid     : {args.theme}")
    print_info(f"Escala PNG       : {args.scale}x")
    print_info(f"Modo de Render   : {'Local CLI (mmdc)' if args.cli else 'API Mermaid Oficial (mermaid.ink)'}\n")

    # Identificar arquivos .md para leitura
    arquivos_md: List[Path] = []
    if caminho_input.is_file() and caminho_input.suffix.lower() == ".md":
        arquivos_md.append(caminho_input)
    elif caminho_input.is_dir():
        arquivos_md = sorted(list(caminho_input.glob("*.md")))
    else:
        print_erro(f"O caminho de entrada '{caminho_input}' não foi encontrado.")
        sys.exit(1)

    if not arquivos_md:
        print_aviso(f"Nenhum arquivo Markdown encontrado em '{caminho_input}'.")
        sys.exit(0)

    # Extrair todos os diagramas
    todos_diagramas: List[Diagrama] = []
    slugs_vistos = set()

    for arq in arquivos_md:
        diags = extrair_diagramas_de_arquivo(arq)
        for d in diags:
            # Evitar colisão de nomes
            slug_original = d.slug
            contador = 1
            while d.slug in slugs_vistos:
                contador += 1
                d.slug = f"{slug_original}_{contador}"
            slugs_vistos.add(d.slug)
            todos_diagramas.append(d)

    total_diags = len(todos_diagramas)
    print_info(f"Total de arquivos .md analisados: {len(arquivos_md)}")
    print_info(f"Total de diagramas Mermaid encontrados: {total_diags}\n")

    if total_diags == 0:
        print_aviso("Nenhum bloco ```mermaid encontrado.")
        sys.exit(0)

    # Inicializar renderizador
    renderizador = RenderizadorMermaid(
        output_dir=caminho_output,
        tema=args.theme,
        escala=args.scale,
        formato=args.format,
    )

    resultados = []
    sucessos = 0

    print(f"{Cor.NEGRITO}Iniciando a geração das imagens...{Cor.RESET}\n")

    for i, diag in enumerate(todos_diagramas, start=1):
        print(f"{Cor.CINZA}[{i:02d}/{total_diags:02d}]{Cor.RESET} Processando: {Cor.NEGRITO}{diag.titulo}{Cor.RESET}")
        print(f"       Arquivo: {diag.arquivo_origem} | Identificador: {diag.slug}")

        # Salvar código .mmd e .html
        mmd_file = renderizador.salvar_mmd(diag)
        html_file = renderizador.salvar_html(diag)

        png_path: Optional[Path] = None
        svg_path: Optional[Path] = None

        if args.cli:
            png_path, svg_path = renderizador.renderizar_via_cli(diag, mmd_file)
        else:
            png_path, svg_path = renderizador.renderizar_via_api(diag)

        status_partes = []
        if png_path and png_path.exists():
            status_partes.append(f"{Cor.VERDE}PNG ({png_path.stat().st_size // 1024} KB){Cor.RESET}")
        if svg_path and svg_path.exists():
            status_partes.append(f"{Cor.VERDE}SVG ({svg_path.stat().st_size // 1024} KB){Cor.RESET}")
        status_partes.append(f"{Cor.AZUL}HTML{Cor.RESET}")
        status_partes.append(f"{Cor.CINZA}MMD{Cor.RESET}")

        if (args.format == "all" and (png_path or svg_path)) or \
           (args.format == "png" and png_path) or \
           (args.format == "svg" and svg_path):
            sucessos += 1
            print(f"       {Cor.VERDE}[OK] Concluído:{Cor.RESET} {' | '.join(status_partes)}\n")
        else:
            print(f"       {Cor.AMARELO}[AVISO] HTML e MMD salvos, mas houve falha na renderização de imagem.{Cor.RESET}\n")

        resultados.append({
            "titulo": diag.titulo,
            "slug": diag.slug,
            "origem": diag.arquivo_origem,
            "png": png_path,
            "svg": svg_path,
            "html": html_file,
            "mmd": mmd_file,
        })

    # Gerar galeria HTML index.html
    index_path = gerar_galeria_html(caminho_output, resultados)

    # Resumo final
    print(f"\n{Cor.NEGRITO}{Cor.CIANO}====================================================================")
    print("  RESUMO DA GERAÇÃO")
    print(f"===================================================================={Cor.RESET}")
    print_ok(f"Diagramas processados com sucesso : {sucessos} de {total_diags}")
    print_ok(f"Pasta de destino                  : {caminho_output.resolve()}")
    print_ok(f"Painel / Galeria HTML             : {index_path.resolve()}")
    print(f"{Cor.CIANO}===================================================================={Cor.RESET}\n")

    print(f"{Cor.NEGRITO}Você pode abrir os arquivos gerados diretamente no navegador:{Cor.RESET}")
    print(f"  {Cor.AZUL}start {index_path}{Cor.RESET} (no Windows/PowerShell)\n")


if __name__ == "__main__":
    main()
