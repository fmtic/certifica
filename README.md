# 🎓 Certifica - Sistema de Emissão de Certificados (Projeto Grael)

O **Certifica** é uma ferramenta desenvolvida em Python utilizando **Streamlit** e **ReportLab** para automatizar a geração de certificados em lote a partir de dados consolidados em planilhas Excel (.xlsx). O sistema desenha dinamicamente tabelas de disciplinas cursadas, atribui assinaturas digitais de instrutores e acopla o conteúdo por cima de um modelo de fundo.

---

## 🚀 Funcionalidades Atuais

1. **Gestão Dinâmica de Design**: Upload direto pela barra lateral do Streamlit para atualizar o template de fundo do certificado (`Ventos.png`), eliminando a necessidade de mexer no código.
2. **Seleção de Tamanhos**: Suporte a múltiplos tamanhos de página em modo Paisagem (`A3`, `A4`, `A5`, `Carta`) com rebalanceamento de margens e fontes proporcional de forma automática.
3. **Cruzamento de Dados Inteligente**: Varre a planilha, valida aprovações no esporte e/ou profissionalizante e renderiza o bloco textual de conclusão correto.
4. **Assinaturas Automatizadas**: Se houver um arquivo `.png` com o nome do educador (em letras minúsculas e separado por underline, ex: `joao_silva.png`) dentro de `assinaturas/`, a rubrica é desenhada na tabela automaticamente.
5. **Download Consolidado**: Compactação imediata de todos os certificados gerados num único pacote `.zip`.

---

## 📁 Estrutura de Pastas

```text
📁 certifica/
│── 📄 .gitignore              # Ignora arquivos do sistema e dados sensíveis de homologação
│── 📄 app.py                  # Interface web baseada em Streamlit e lógica de upload
│── 📄 constants.py            # Centralização de caminhos globais (fundo e assinaturas)
│── 📄 pdf_engine.py           # Motor matemático de cálculo e renderização gráfica do PDF
│── 📄 README.md               # Instruções e documentação do projeto
│── 📄 requirements.txt        # Dependências de bibliotecas Python
├── 📁 modelos_certificado/    # Diretório que hospeda o fundo ativo do certificado
│   └── 🖼️ Ventos.png          # Imagem base PNG padrão do certificado
└── 📁 assinaturas/            # Repositório de assinaturas dos instrutores
    └── 🖼️ karoline_faria.png  # Exemplo de assinatura nome_sobrenome.png


🛠️ Instalação e Execução
1. Pré-requisitos
Certifique-se de que possui o Python instalado na sua máquina (versão 3.10 ou superior recomendada).

2. Configurar o Ambiente Virtual (Opcional, mas Recomendado)
Bash
# Criar o ambiente virtual
python -m venv .venv

# Ativar no Windows:
.venv\Scripts\activate

# Ativar no Linux/macOS:
source .venv/bin/activate
3. Instalar Dependências
Instale todos os pacotes necessários que estão mapeados no arquivo requirements.txt:

Bash
pip install -r requirements.txt
4. Executar o Painel
Rode o comando do Streamlit para iniciar a interface web localmente:

Bash
streamlit run app.py
A aplicação abrirá automaticamente no seu navegador padrão pelo endereço http://localhost:8501.

📊 Padrão Esperado da Planilha
Para que a leitura ocorra sem problemas, a planilha carregada deve conter as seguintes colunas obrigatórias:

EDUCANDO (Utilizada para gerar o nome principal e o nome do arquivo individual)

DISCIPLNA ESPORTE (ou com quebra de linha DISCIPLNA\nESPORTE)

SITUAÇÃO FINAL ESP (ou SITUAÇÃO\nFINAL ESP)

C.H ESP, EDUCADOR ESP, TEXTO ESPORTE

DISCIPLINA PROF, SITUAÇÃO FNAL PROF, C.H PROF, EDUCADOR PROF, TEXTO PROFISISONALIZANTE

✒️ Convenção para Imagens de Assinatura
Para que o motor de PDF substitua o nome do instrutor pela sua assinatura em imagem dentro da tabela, certifique-se de que a imagem cumpra os seguintes requisitos:

Formato PNG com fundo transparente.

Nomeado todo em letras minúsculas, sem acentos, mudando espaços por underline (_).

Exemplo: Se o educador na planilha é Karoline Faria, a imagem deve ser karoline_faria.png colocada dentro da pasta assinaturas/.

Se o arquivo não for encontrado, o sistema escreverá apenas o nome textual em Helvetica para evitar quebras.