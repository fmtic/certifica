import io
import os
import zipfile
from datetime import date
import pandas as pd
import streamlit as st

import constants
import pdf_engine

# ── Constantes ────────────────────────────────────────────────────────────────
LIMITE_FUNDO_MB    = 5
LIMITE_FUNDO_BYTES = LIMITE_FUNDO_MB * 1024 * 1024

OPCOES_TAMANHO = list(pdf_engine.TAMANHOS_DISPONIVEIS.keys())  # ['A3','A4','A5','Carta']
TAMANHO_PADRAO = 'A4'

st.set_page_config(
    page_title="Certifica",
    page_icon="🎓",
    layout="centered",
)

st.title("⛵ Sistema de Emissão de Certificados")
st.markdown("---")


# ── 1. FUNDO DO CERTIFICADO ───────────────────────────────────────────────────
st.subheader("🖼️ Modelo de fundo")

nome_fundo_atual = (
    os.path.basename(constants.PATH_FUNDO)
    if os.path.exists(constants.PATH_FUNDO)
    else "⚠️ nenhum arquivo encontrado"
)
st.caption(f"Fundo ativo: **{nome_fundo_atual}**")

fundo_upload = st.file_uploader(
    "Arraste ou selecione uma nova imagem de fundo (.png ou .jpg) para substituir o modelo atual",
    type=["png", "jpg", "jpeg"],
    help=(
        f"Tamanho máximo: {LIMITE_FUNDO_MB} MB. "
        "A imagem deve estar em orientação paisagem (largura > altura). "
        "Recomendado: 2000 × 1414 px ou proporção A4 landscape."
    ),
)

if fundo_upload is not None:
    if fundo_upload.size > LIMITE_FUNDO_BYTES:
        tamanho_mb = fundo_upload.size / (1024 * 1024)
        st.error(
            f"❌ Imagem muito grande: **{tamanho_mb:.1f} MB**. "
            f"O limite é de **{LIMITE_FUNDO_MB} MB**. "
            "Reduza o tamanho ou a resolução e tente novamente."
        )
    else:
        pasta_modelos = os.path.join(constants.BASE_DIR, "modelos_certificado")
        os.makedirs(pasta_modelos, exist_ok=True)
        caminho_novo = os.path.join(pasta_modelos, fundo_upload.name)

        with open(caminho_novo, "wb") as f:
            f.write(fundo_upload.getbuffer())

        constants.PATH_FUNDO = caminho_novo

        col_prev, col_info = st.columns([2, 1])
        with col_prev:
            st.image(
                fundo_upload,
                caption=f"✅ {fundo_upload.name} ({fundo_upload.size / (1024*1024):.1f} MB)",
                use_container_width=True,
            )
        with col_info:
            st.success("Fundo atualizado com sucesso!")
            st.info(
                "Este fundo será usado em todos os certificados desta sessão. "
                "Para torná-lo permanente, atualize `PATH_FUNDO` em `constants.py` "
                "com o nome deste arquivo."
            )

st.markdown("---")


# ── 2. FORMATO DO CERTIFICADO ─────────────────────────────────────────────────
st.subheader("📐 Formato do certificado")

col_fmt, col_fmt_info = st.columns([1, 2])

with col_fmt:
    tamanho_escolhido = st.radio(
        "Tamanho da página",
        options=OPCOES_TAMANHO,
        index=OPCOES_TAMANHO.index(TAMANHO_PADRAO),
        horizontal=False,
    )

with col_fmt_info:
    from reportlab.lib.pagesizes import A3, A4, A5, LETTER, landscape
    info = {
        'A3':    ('420 × 297 mm', '1190 × 841 pt', 'Ideal para exposições e quadros de honra.'),
        'A4':    ('297 × 210 mm', '841 × 595 pt',  'Padrão atual — cabe em qualquer impressora.'),
        'A5':    ('210 × 148 mm', '595 × 420 pt',  'Compacto, ideal para certificados de participação.'),
        'Carta': ('279 × 216 mm', '792 × 612 pt',  'Padrão norte-americano (Letter), comum em impressoras domésticas.'),
    }
    dim_mm, dim_pt, descricao = info[tamanho_escolhido]
    st.markdown(f"**{tamanho_escolhido} landscape**")
    st.markdown(f"- Dimensões: {dim_mm} &nbsp;·&nbsp; {dim_pt}")
    st.markdown(f"- {descricao}")

st.markdown("---")


# ── 3. PLANILHA E GERAÇÃO ────────────────────────────────────────────────────
st.subheader("📊 Planilha de alunos")

arquivo_upload = st.file_uploader(
    "Arraste ou selecione a sua planilha Excel (.xlsx)", type=["xlsx"]
)

if arquivo_upload is not None:
    try:
        df = pd.read_excel(arquivo_upload)
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=['EDUCANDO'])

        st.success(f"📊 Sucesso! {len(df)} registros de alunos encontrados.")

        if st.button("🚀 Gerar PDFs em Lote"):
            barra_progresso = st.progress(0)
            status_texto = st.empty()

            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                total = len(df)
                for index, (_, linha) in enumerate(df.iterrows()):
                    nome_aluno = str(linha['EDUCANDO']).strip()
                    status_texto.text(f"Renderizando ({index+1}/{total}): {nome_aluno}")

                    pdf_gerado = pdf_engine.criar_certificado_em_memoria(
                        linha, tamanho=tamanho_escolhido
                    )

                    nome_zip = f"Certificado_{nome_aluno.replace(' ', '_')}.pdf"
                    zip_file.writestr(nome_zip, pdf_gerado.getvalue())

                    barra_progresso.progress((index + 1) / total)

            status_texto.text("✨ Tudo pronto! O lote de certificados foi processado.")
            barra_progresso.empty()

            st.download_button(
                label="📥 Baixar Arquivo ZIP com Certificados",
                data=zip_buffer.getvalue(),
                file_name=f"certificados_grael_{tamanho_escolhido}.zip",
                mime="application/zip",
            )

    except Exception as e:
        st.error(f"❌ Ocorreu um problema ao rodar a planilha: {e}")


# ── RODAPÉ ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align: center; color: #888; font-size: 0.8rem; padding: 8px 0 4px 0;">
        © {date.today().year} <strong>FMtic Service Desk</strong> — Todos os direitos reservados
    </div>
    """,
    unsafe_allow_html=True,
)