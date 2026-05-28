"""
pdf_engine.py — Motor de geração de certificados do Projeto Grael
Suporta múltiplos tamanhos de página (A3, A4, A5, Carta) em landscape.
Todo o layout é calculado proporcionalmente ao tamanho escolhido.
"""
import os
import io
import pandas as pd
from reportlab.lib.pagesizes import A3, A4, A5, LETTER, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
from pypdf import PdfReader, PdfWriter

import constants

# ── Paleta ───────────────────────────────────────────────────────────────────
COR_NOME  = colors.HexColor('#004b8d')
COR_TEXTO = colors.HexColor('#333333')
COR_TH    = colors.HexColor('#004b8d')

# ── Tamanhos disponíveis ──────────────────────────────────────────────────────
TAMANHOS_DISPONIVEIS = {
    'A3':    A3,
    'A4':    A4,      # padrão atual
    'A5':    A5,
    'Carta': LETTER,
}


# ─────────────────────────────────────────────────────────────────────────────
# Layout proporcional
# ─────────────────────────────────────────────────────────────────────────────

def _layout(W: float, H: float) -> dict:
    """
    Calcula todos os valores de posição e tamanho proporcionalmente
    às dimensões W × H da página (já em landscape).
    Os percentuais foram calibrados no A4 landscape (841.89 × 595.28 pt).
    """
    # Largura útil da tabela (70.1 % da página)
    table_w = W * 0.701
    # Proporção das 3 colunas dentro da tabela
    col_w = [table_w * 0.483, table_w * 0.161, table_w * 0.356]

    # Fonte máxima do nome: proporcional à altura (cap em 48, mín em 15)
    font_nome_max = max(15, min(48, int(H * 0.054)))

    return {
        # Nome do aluno
        'safe_center':   W * 0.570,          # centro horizontal seguro (pós-logo)
        'safe_width':    W * 0.760,          # largura máxima do nome
        'y_nome':        H * 0.773,

        # Texto de conclusão
        'y_txt_start':   H * 0.706,
        'y_txt_step':    H * 0.037,
        'font_corpo':    max(9, int(H * 0.024)),

        # Tabela
        'table_left':    W * 0.202,
        'col_w':         col_w,
        'font_th':       max(8, int(H * 0.021)),
        'font_tc':       max(8, int(H * 0.021)),
        'row_h':         H * 0.097,
        'sig_max_w':     W * 0.107,
        'sig_max_h':     H * 0.054,
        'gap_txt_tab':   H * 0.050,

        # Fonte adaptativa do nome
        'font_nome_max': font_nome_max,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _font_nome(nome: str, max_w: float, font_max: int) -> int:
    """Tamanho de fonte ideal para o nome caber em max_w pontos."""
    for size in range(font_max, 10, -1):
        if stringWidth(nome, 'Helvetica-Bold', size) <= max_w:
            return size
    return 10


def _sig_path(educador: str) -> str:
    """Resolve o caminho da assinatura; tenta Nome_Sobrenome.png e _PNG.png."""
    base = educador.strip().replace(' ', '_')
    for sufixo in ['.png', '_PNG.png']:
        p = os.path.join(constants.PATH_ASSINATURAS, base + sufixo)
        if os.path.exists(p):
            return p
    return ''


def _draw_signature(c: canvas.Canvas, path: str,
                    cx: float, y_top: float,
                    max_w: float, max_h: float):
    """Desenha a assinatura centrada em cx, respeitando proporção e limites."""
    if not path:
        return
    from PIL import Image as PILImage
    iw, ih = PILImage.open(path).size
    ratio = iw / ih
    rw = min(max_w, max_h * ratio)
    rh = rw / ratio
    c.drawImage(path, cx - rw / 2, y_top - rh, width=rw, height=rh, mask='auto')


def _draw_table(c: canvas.Canvas, linhas: list, y_top: float, lyt: dict):
    """Desenha cabeçalho + linhas da tabela a partir de y_top."""
    col_w     = lyt['col_w']
    tbl_left  = lyt['table_left']
    font_th   = lyt['font_th']
    font_tc   = lyt['font_tc']
    row_h     = lyt['row_h']
    sig_max_w = lyt['sig_max_w']
    sig_max_h = lyt['sig_max_h']

    cx = [
        tbl_left + col_w[0] / 2,
        tbl_left + col_w[0] + col_w[1] / 2,
        tbl_left + col_w[0] + col_w[1] + col_w[2] / 2,
    ]
    tbl_right = tbl_left + sum(col_w)

    # ── Cabeçalho ────────────────────────────────────────────────────────────
    c.setFont('Helvetica-Bold', font_th)
    c.setFillColor(COR_TH)
    for txt, x in zip(['Módulos Cursados', 'Carga Horária', 'Instrutor(a)'], cx):
        c.drawCentredString(x, y_top, txt)

    sep = font_th * 0.65          # distância da linha ao texto do cabeçalho
    c.setStrokeColor(COR_TH)
    c.setLineWidth(0.8)
    c.line(tbl_left, y_top - sep, tbl_right, y_top - sep)

    # ── Linhas de dados ───────────────────────────────────────────────────────
    y = y_top - sep
    for modulo, ch, educador in linhas:
        mid = y - row_h / 2

        c.setFont('Helvetica', font_tc)
        c.setFillColor(COR_TEXTO)
        c.drawCentredString(cx[0], mid - font_tc * 0.35, str(modulo))
        c.drawCentredString(cx[1], mid - font_tc * 0.35, str(ch))

        sig = _sig_path(educador)
        sig_top = mid + sig_max_h / 2

        if sig:
            _draw_signature(c, sig, cx[2], sig_top, sig_max_w, sig_max_h)
            c.setFont('Helvetica', max(8, font_tc - 1))
            c.setFillColor(COR_TEXTO)
            c.drawCentredString(cx[2], mid - sig_max_h / 2 + font_tc * 0.35, educador)
        else:
            c.setFont('Helvetica', font_tc)
            c.setFillColor(COR_TEXTO)
            c.drawCentredString(cx[2], mid - font_tc * 0.35, educador)

        y -= row_h


def _coletar_linhas(dados) -> list:
    """Extrai as linhas da tabela dos dados do aluno."""
    linhas = []

    # Profissionalizante
    if (pd.notna(dados.get('DISCIPLINA PROF')) and
            str(dados.get('SITUAÇÃO FNAL PROF', '')).strip().upper() == 'APROVADO'):
        linhas.append((
            str(dados['DISCIPLINA PROF']).replace('-', '').strip(),
            str(dados.get('C.H PROF', '80')).replace('.0', ''),
            str(dados.get('EDUCADOR PROF', '')).strip(),
        ))

    # Esporte
    col_disc = ('DISCIPLNA\nESPORTE' if 'DISCIPLNA\nESPORTE' in dados else 'DISCIPLNA ESPORTE')
    col_sit  = ('SITUAÇÃO\nFINAL ESP' if 'SITUAÇÃO\nFINAL ESP' in dados else 'SITUAÇÃO FINAL ESP')
    if (pd.notna(dados.get(col_disc)) and
            str(dados.get(col_sit, '')).strip().upper() == 'APROVADO'):
        materia = str(dados[col_disc]).replace('-', '').strip()
        nivel   = str(dados.get('NÍVEL', 'Básico')).strip()
        linhas.append((
            f'{materia} - {nivel}',
            str(dados.get('C.H ESP', '80')).replace('.0', ''),
            str(dados.get('EDUCADOR ESP', '')).strip(),
        ))

    return linhas


# ─────────────────────────────────────────────────────────────────────────────
# API pública
# ─────────────────────────────────────────────────────────────────────────────

def criar_certificado_em_memoria(dados_aluno,
                                  tamanho: str = 'A4') -> io.BytesIO:
    """
    Gera o certificado PDF em memória e retorna um BytesIO pronto para leitura.

    Parâmetros
    ----------
    dados_aluno : linha do DataFrame com os dados do aluno.
    tamanho     : chave do dicionário TAMANHOS_DISPONIVEIS ('A3', 'A4', 'A5', 'Carta').
                  Padrão: 'A4'.
    """
    pagesize_base = TAMANHOS_DISPONIVEIS.get(tamanho, A4)
    pagesize = landscape(pagesize_base)
    W, H = pagesize
    lyt  = _layout(W, H)

    # ── Overlay com conteúdo dinâmico ────────────────────────────────────────
    buf_overlay = io.BytesIO()
    c = canvas.Canvas(buf_overlay, pagesize=pagesize)

    # Nome do aluno
    nome      = str(dados_aluno.get('EDUCANDO', 'Aluno')).strip()
    font_size = _font_nome(nome, lyt['safe_width'], lyt['font_nome_max'])
    c.setFont('Helvetica-Bold', font_size)
    c.setFillColor(COR_NOME)
    c.drawCentredString(lyt['safe_center'], lyt['y_nome'], nome)

    # Texto de conclusão
    texto_raw = ''
    if pd.notna(dados_aluno.get('TEXTO PROFISISONALIZANTE')):
        texto_raw = str(dados_aluno['TEXTO PROFISISONALIZANTE'])
    elif pd.notna(dados_aluno.get('TEXTO ESPORTE')):
        texto_raw = str(dados_aluno['TEXTO ESPORTE'])
    else:
        texto_raw = 'concluiu com sucesso as atividades do Projeto Grael.'

    font_corpo = lyt['font_corpo']
    y_txt = lyt['y_txt_start']
    for i, linha in enumerate([l.strip() for l in texto_raw.split('\n') if l.strip()]):
        c.setFont('Helvetica' if i == 0 else 'Helvetica-Bold', font_corpo)
        c.setFillColor(COR_TEXTO)
        c.drawCentredString(lyt['safe_center'], y_txt, linha)
        y_txt -= lyt['y_txt_step']

    # Tabela
    y_tabela = y_txt + lyt['y_txt_step'] - lyt['gap_txt_tab']
    linhas_tabela = _coletar_linhas(dados_aluno)
    if linhas_tabela:
        _draw_table(c, linhas_tabela, y_top=y_tabela, lyt=lyt)

    c.showPage()
    c.save()
    buf_overlay.seek(0)

    # ── Fundo ────────────────────────────────────────────────────────────────
    buf_fundo = io.BytesIO()
    cf = canvas.Canvas(buf_fundo, pagesize=pagesize)
    if os.path.exists(constants.PATH_FUNDO):
        cf.drawImage(constants.PATH_FUNDO, 0, 0, width=W, height=H)
    else:
        cf.setFillColor(colors.white)
        cf.rect(0, 0, W, H, fill=1, stroke=0)
    cf.showPage()
    cf.save()
    buf_fundo.seek(0)

    # ── Mesclagem ────────────────────────────────────────────────────────────
    pg = PdfReader(buf_fundo).pages[0]
    pg.merge_page(PdfReader(buf_overlay).pages[0])

    writer = PdfWriter()
    writer.add_page(pg)
    buf_final = io.BytesIO()
    writer.write(buf_final)
    buf_final.seek(0)
    return buf_final