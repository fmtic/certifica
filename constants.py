import os

# ── Caminhos ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Imagem de fundo do certificado (troque o arquivo em modelos_certificado/)
PATH_FUNDO = os.path.join(BASE_DIR, 'modelos_certificado', 'Ventos.png')

# Pasta com as imagens de assinatura dos instrutores (Nome_Sobrenome.png)
PATH_ASSINATURAS = os.path.join(BASE_DIR, 'assinaturas')