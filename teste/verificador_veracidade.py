import streamlit as st
from groq import Groq
import json

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="VerificaFato – Verificador de Veracidade",
    page_icon="🔍",
    layout="centered",
)

# ── CSS personalizado ───────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main-title {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1a73e8, #0f9d58);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        color: #555;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .card {
        background: #f8f9fa;
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        border-left: 6px solid #1a73e8;
    }
    .verdict-verdadeiro  { border-left-color: #0f9d58; background: #e6f4ea; }
    .verdict-falso       { border-left-color: #d93025; background: #fce8e6; }
    .verdict-parcial     { border-left-color: #f9a825; background: #fef9e7; }
    .verdict-incerto     { border-left-color: #9e9e9e; background: #f5f5f5; }

    .badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 0.8rem;
    }
    .badge-verdadeiro { background:#0f9d58; color:white; }
    .badge-falso      { background:#d93025; color:white; }
    .badge-parcial    { background:#f9a825; color:#333; }
    .badge-incerto    { background:#9e9e9e; color:white; }

    .stTextArea textarea { border-radius: 12px !important; }
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(135deg, #1a73e8, #0f9d58);
        color: white;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.6rem;
        border: none;
    }
    .stButton > button:hover { opacity: 0.9; }

    .fonte-item {
        background: white;
        border-radius: 8px;
        padding: 0.5rem 0.8rem;
        margin: 4px 0;
        font-size: 0.88rem;
        color: #1a73e8;
    }
    .democracia-box {
        background: linear-gradient(135deg, #e8f0fe, #e6f4ea);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-top: 1rem;
        font-size: 0.88rem;
        color: #333;
    }
    footer { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Cabeçalho ───────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🔍 VerificaFato</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Verificador de Veracidade com IA · Feira de Ciências 2025<br>'
    '<em>Veracidade e Vivência Democrática</em></div>',
    unsafe_allow_html=True,
)

# ── Inicializar histórico ────────────────────────────────────────────────────
if "historico" not in st.session_state:
    st.session_state.historico = []

# ── Formulário principal ─────────────────────────────────────────────────────
with st.container():
    afirmacao = st.text_area(
        "📝 Digite a afirmação que deseja verificar:",
        placeholder="Ex: A Terra tem aproximadamente 4,5 bilhões de anos.",
        height=120,
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        categoria = st.selectbox(
            "Categoria",
            ["🌍 Ciência", "🏛️ Política", "💊 Saúde", "📰 Notícia", "📚 História", "🔢 Estatística", "Outro"],
        )
    with col2:
        nivel = st.selectbox("Nível de detalhe", ["Resumido", "Detalhado"])

    verificar = st.button("🔎 Verificar Veracidade")

# ── Função de análise via Claude API ─────────────────────────────────────────
def analisar_afirmacao(texto: str, cat: str, detalhe: str) -> dict:
    client = Groq()

    nivel_instrucao = (
        "Seja conciso, máximo 3 parágrafos."
        if detalhe == "Resumido"
        else "Seja detalhado e didático, explique bem cada ponto."
    )

    prompt = f"""Você é um verificador de fatos especializado em educação e democracia.
Analise a seguinte afirmação da categoria '{cat}' e responda APENAS com um JSON válido neste formato exato:

{{
  "veredicto": "VERDADEIRO" | "FALSO" | "PARCIALMENTE VERDADEIRO" | "INCERTO",
  "confianca": <número inteiro de 0 a 100>,
  "resumo": "<explicação clara e acessível>",
  "argumentos_favor": ["<argumento 1>", "<argumento 2>"],
  "argumentos_contra": ["<argumento 1>", "<argumento 2>"],
  "fontes_sugeridas": ["<fonte ou tipo de fonte confiável 1>", "<fonte 2>"],
  "relevancia_democratica": "<como a veracidade desta informação afeta a cidadania e democracia>",
  "dica_verificacao": "<dica prática de como o cidadão pode verificar isso por conta própria>"
}}

{nivel_instrucao}

Afirmação: {texto}

Responda SOMENTE com o JSON, sem texto adicional."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Modelo gratuito e poderoso da Groq
        max_tokens=1500,
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": "Você é um verificador de fatos preciso. Responda SEMPRE e APENAS com JSON válido, sem nenhum texto antes ou depois.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    raw = response.choices[0].message.content.strip()
    # Remove possíveis blocos de código markdown
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ── Cores e emojis por veredicto ─────────────────────────────────────────────
VEREDICTO_CONFIG = {
    "VERDADEIRO":              ("verdadeiro", "✅", "VERDADEIRO"),
    "FALSO":                   ("falso",      "❌", "FALSO"),
    "PARCIALMENTE VERDADEIRO": ("parcial",    "⚠️", "PARCIALMENTE VERDADEIRO"),
    "INCERTO":                 ("incerto",    "❓", "INCERTO"),
}


def render_resultado(res: dict, afirmacao_orig: str):
    verd = res.get("veredicto", "INCERTO").upper()
    cfg = VEREDICTO_CONFIG.get(verd, VEREDICTO_CONFIG["INCERTO"])
    classe, emoji, label = cfg

    st.markdown(f"""
    <div class="card verdict-{classe}">
        <span class="badge badge-{classe}">{emoji} {label}</span>
        <p><strong>Confiança da análise:</strong> {res.get('confianca', '?')}%</p>
        <p>{res.get('resumo', '')}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**✅ Argumentos a favor**")
        for a in res.get("argumentos_favor", []):
            st.markdown(f"- {a}")
    with col2:
        st.markdown("**❌ Argumentos contra**")
        for a in res.get("argumentos_contra", []):
            st.markdown(f"- {a}")

    st.markdown("**📚 Fontes sugeridas para pesquisa**")
    for f in res.get("fontes_sugeridas", []):
        st.markdown(f'<div class="fonte-item">🔗 {f}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="democracia-box">
        🏛️ <strong>Relevância democrática:</strong><br>{res.get('relevancia_democratica', '')}
        <br><br>
        💡 <strong>Como verificar por conta própria:</strong><br>{res.get('dica_verificacao', '')}
    </div>
    """, unsafe_allow_html=True)


# ── Execução da verificação ───────────────────────────────────────────────────
if verificar:
    if not afirmacao.strip():
        st.warning("⚠️ Por favor, digite uma afirmação para verificar.")
    else:
        with st.spinner("🤖 Analisando com IA... aguarde um momento"):
            try:
                resultado = analisar_afirmacao(afirmacao, categoria, nivel)
                render_resultado(resultado, afirmacao)
                # Salva no histórico
                st.session_state.historico.append({
                    "afirmacao": afirmacao,
                    "veredicto": resultado.get("veredicto", "?"),
                    "confianca": resultado.get("confianca", 0),
                })
            except json.JSONDecodeError:
                st.error("Erro ao interpretar a resposta da IA. Tente novamente.")
            except Exception as e:
                st.error(f"Erro na API: {e}")

# ── Histórico da sessão ───────────────────────────────────────────────────────
if st.session_state.historico:
    st.markdown("---")
    st.markdown("### 📋 Histórico desta sessão")
    for i, item in enumerate(reversed(st.session_state.historico), 1):
        verd = item["veredicto"].upper()
        cfg = VEREDICTO_CONFIG.get(verd, VEREDICTO_CONFIG["INCERTO"])
        _, emoji, label = cfg
        st.markdown(
            f"**{i}.** {emoji} `{label}` ({item['confianca']}%) — _{item['afirmacao'][:80]}..._"
            if len(item["afirmacao"]) > 80
            else f"**{i}.** {emoji} `{label}` ({item['confianca']}%) — _{item['afirmacao']}_"
        )

# ── Rodapé ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small>🏫 Feira de Ciências · Veracidade e Vivência Democrática · "
    "Powered by Groq AI (LLaMA 3.3 70B)</small></center>",
    unsafe_allow_html=True,
)
