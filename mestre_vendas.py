import streamlit as st
from groq import Groq
from datetime import datetime
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="MESTRE DE VENDAS FÍSICAS", layout="wide")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500;600&display=swap');

    .stApp { background-color: #FFFFFF; color: #000000; font-family: 'DM Sans', sans-serif; }
    [data-testid="stSidebar"] { display: none; }

    .stTextInput>div>div>input,
    .stTextArea>div>textarea,
    .stSelectbox>div>div>div {
        background-color: #FFF8F0 !important;
        color: #000000 !important;
        border: 1px solid #F97316 !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(135deg, #C2410C, #EA580C) !important;
        color: white !important; font-weight: 600; border: none;
        box-shadow: 2px 2px 8px rgba(194,65,12,0.3);
        font-family: 'DM Sans', sans-serif !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover { background: linear-gradient(135deg, #9A3412, #C2410C) !important; transform: translateY(-1px); }

    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #1A1A2E !important; }
    p, span, label, div { color: #1A1A2E !important; font-family: 'DM Sans', sans-serif; }

    .card {
        background: linear-gradient(135deg, #FFF8F0 0%, #FFEDD5 100%);
        padding: 22px; border-radius: 16px;
        border: 1px solid #F97316; margin-bottom: 15px;
        color: #1A1A2E; box-shadow: 0 2px 12px rgba(194,65,12,0.08);
        white-space: pre-wrap;
    }
    .card-dark {
        background: linear-gradient(135deg, #1C0800 0%, #2D1000 100%);
        padding: 22px; border-radius: 16px;
        border: 1px solid #EA580C; margin-bottom: 15px;
        white-space: pre-wrap;
    }
    .card-dark, .card-dark * { color: #FED7AA !important; }
    .card-blue {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        padding: 22px; border-radius: 16px;
        border: 1px solid #93C5FD; margin-bottom: 15px;
        white-space: pre-wrap;
    }
    .card-green {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        padding: 22px; border-radius: 16px;
        border: 1px solid #86EFAC; margin-bottom: 15px;
        white-space: pre-wrap;
    }
    .card-purple {
        background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%);
        padding: 22px; border-radius: 16px;
        border: 1px solid #C4B5FD; margin-bottom: 15px;
        white-space: pre-wrap;
    }
    .card-red {
        background: linear-gradient(135deg, #FFF5F5 0%, #FEE2E2 100%);
        padding: 22px; border-radius: 16px;
        border: 1px solid #FCA5A5; margin-bottom: 15px;
        white-space: pre-wrap;
    }
    .card-yellow {
        background: linear-gradient(135deg, #FEFCE8 0%, #FEF9C3 100%);
        padding: 22px; border-radius: 16px;
        border: 1px solid #FDE047; margin-bottom: 15px;
        white-space: pre-wrap;
    }
    .card-teal {
        background: linear-gradient(135deg, #F0FDFA 0%, #CCFBF1 100%);
        padding: 22px; border-radius: 16px;
        border: 1px solid #5EEAD4; margin-bottom: 15px;
        white-space: pre-wrap;
    }

    .badge         { background: #C2410C; color: white !important; padding: 4px 14px; border-radius: 20px; font-size: 0.78em; font-weight: 600; display: inline-block; margin: 2px; }
    .badge-verde   { background: #059669; color: white !important; padding: 4px 14px; border-radius: 20px; font-size: 0.78em; font-weight: 600; display: inline-block; margin: 2px; }
    .badge-azul    { background: #1D4ED8; color: white !important; padding: 4px 14px; border-radius: 20px; font-size: 0.78em; font-weight: 600; display: inline-block; margin: 2px; }
    .badge-roxo    { background: #7C3AED; color: white !important; padding: 4px 14px; border-radius: 20px; font-size: 0.78em; font-weight: 600; display: inline-block; margin: 2px; }
    .badge-yellow  { background: #CA8A04; color: white !important; padding: 4px 14px; border-radius: 20px; font-size: 0.78em; font-weight: 600; display: inline-block; margin: 2px; }

    .stat-box { background: #FFF8F0; border-radius: 12px; padding: 18px; text-align: center; border: 1px solid #F97316; }
    .stat-numero { font-size: 2em; font-weight: 700; color: #C2410C !important; font-family: 'Playfair Display', serif; }

    .hist-item { background: #FFF8F0; border-radius: 10px; padding: 12px 16px; margin-bottom: 8px; border-left: 4px solid #EA580C; }

    .perfil-btn>button {
        background: linear-gradient(135deg, #C2410C, #EA580C) !important;
        color: white !important; font-weight: 700 !important;
        border-radius: 12px !important; height: 3em !important;
    }

    .divider { border: none; height: 1px; background: linear-gradient(to right, transparent, #F97316, transparent); margin: 20px 0; }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CACHE
# ─────────────────────────────────────────────
@st.cache_resource
def get_cache_vendas():
    return {"perfis": {}}

_cache = get_cache_vendas()

# ─────────────────────────────────────────────
# PERSISTÊNCIA LOCAL (JSON)
# ─────────────────────────────────────────────
CHAVES_SALVAR = [
    'usuario', 'historico_analises', 'materiais_salvos',
    'produto_padrao', 'nicho_padrao', 'preco_custo',
    'preco_venda', 'canal_padrao', 'chat_mentor',
]

def gerar_json_sessao() -> str:
    dados = {k: st.session_state.get(k) for k in CHAVES_SALVAR}
    dados['salvo_em'] = datetime.now().strftime('%d/%m/%Y %H:%M')
    return json.dumps(dados, ensure_ascii=False, indent=2, default=str)

def carregar_json_sessao(dados: dict):
    for k in CHAVES_SALVAR:
        if k in dados:
            st.session_state[k] = dados[k]

def salvar_perfil_cache(usuario: str):
    _cache["perfis"][usuario] = {k: st.session_state.get(k) for k in CHAVES_SALVAR}

def perfis_salvos() -> list:
    return list(_cache["perfis"].keys())

def carregar_perfil_cache(usuario: str) -> dict | None:
    return _cache["perfis"].get(usuario)

def salvar_analise(tipo: str, produto: str, conteudo: str):
    st.session_state.historico_analises.append({
        'data':     datetime.now().strftime('%d/%m %H:%M'),
        'tipo':     tipo,
        'produto':  produto,
        'conteudo': conteudo,
    })

# --- INICIALIZAÇÃO DE ESTADO ---
defaults = {
    'etapa':              "Login",
    'usuario':            "",
    'api_key':            "",
    'pagina':             "Home",
    'historico_analises': [],
    'materiais_salvos':   [],
    'produto_padrao':     "",
    'nicho_padrao':       "",
    'preco_custo':        0.0,
    'preco_venda':        0.0,
    'canal_padrao':       "WhatsApp",
    'chat_mentor':        [],
    'chat_key':           0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- MOTOR DE IA ---
def vendas_ia(prompt: str, system_extra: str = "") -> str:
    try:
        client = Groq(api_key=st.session_state.api_key)
        system = f"""Você é um especialista em vendas de produtos físicos no Brasil com 15 anos de experiência.
Usuário: {st.session_state.usuario}.
Produto foco: {st.session_state.produto_padrao or 'não informado'}.
Nicho: {st.session_state.nicho_padrao or 'não informado'}.
Canal principal: {st.session_state.canal_padrao}.
{system_extra}
PRINCÍPIOS:
- Respostas diretas, práticas e aplicáveis HOJE
- Foco em resultado real, não teoria
- Linguagem de vendedor experiente, não de professor
- Sempre inclua exemplos práticos do mercado brasileiro
- Escreva em português brasileiro natural"""
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Erro na API: {e}"

# --- BARRA DE SALVAR ---
def barra_salvar():
    salvar_perfil_cache(st.session_state.usuario)
    nome_usuario = st.session_state.usuario.lower().replace(' ', '_') or 'minha_sessao'
    total  = len(st.session_state.historico_analises)
    salvos = len(st.session_state.materiais_salvos)

    col_info, col_btn = st.columns([4, 2])
    with col_info:
        st.markdown(
            f"<div style='background:#FFF8F0;border:1px solid #F97316;border-radius:10px;"
            f"padding:10px 14px;font-size:0.84em;color:#1A1A2E;line-height:1.6;'>"
            f"💾 <strong>Antes de sair, salve seus dados no computador.</strong><br>"
            f"<span style='color:#888;font-size:0.88em;'>{total} análises geradas · {salvos} materiais salvos</span>"
            f"</div>",
            unsafe_allow_html=True
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="💾 SALVAR MEUS DADOS (.json)",
            data=gerar_json_sessao(),
            file_name=f"mestre_vendas_{nome_usuario}.json",
            mime="application/json",
            use_container_width=True,
        )
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ============================================================
# TELA: LOGIN
# ============================================================
if st.session_state.etapa == "Login":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("📦 MESTRE DE VENDAS FÍSICAS")
        st.markdown("**O canivete suíço completo para quem vende produto físico — do diagnóstico à escala**")

        st.markdown("""<div style="background:#FFF8F0;border:1px solid #F97316;border-radius:10px;
        padding:10px 16px;margin:10px 0 16px 0;font-size:0.88em;color:#1A1A2E;line-height:1.6;">
        🔒 <strong>ACESSO RESTRITO A CLIENTES DO QUIZ COM PRÊMIOS</strong><br>
        🔗 <a href="https://quizcompremios.com.br/" target="_blank"
        style="color:#C2410C;font-weight:600;text-decoration:none;">quizcompremios.com.br</a>
        </div>""", unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        perfis = perfis_salvos()
        if perfis:
            st.markdown("#### 📦 Mestre de Vendas — clique para acessar seus dados")
            st.caption("Seus materiais estão no servidor. Um clique e você entra.")
            chave_rapida = st.text_input("🔑 Sua Chave API da Groq:", type="password", key="chave_rapida")
            for nome_p in perfis:
                dados_p   = carregar_perfil_cache(nome_p)
                total_p   = len(dados_p.get('historico_analises', [])) if dados_p else 0
                produto_p = dados_p.get('produto_padrao', '') if dados_p else ''
                st.markdown('<div class="perfil-btn">', unsafe_allow_html=True)
                if st.button(
                    f"📦 {nome_p}  —  {total_p} análises  {('· ' + produto_p[:30]) if produto_p else ''}",
                    key=f"perfil_{nome_p}", use_container_width=True
                ):
                    if not chave_rapida.strip():
                        st.warning("Cole sua chave API acima antes de entrar.")
                    else:
                        st.session_state.usuario = nome_p
                        st.session_state.api_key = chave_rapida
                        carregar_json_sessao(dados_p)
                        st.session_state.etapa = "App"
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<hr class='divider'>", unsafe_allow_html=True)
            st.markdown("**Ou entre com outro nome:**")

        nome  = st.text_input("Seu Nome:", key="text_input_Seu_Nome__L276")
        chave = st.text_input("Sua Chave API da Groq:", type="password", key="chave_nova")

        if not perfis:
            st.markdown("""<div style="background:#FFF8F0;border:1px solid #F97316;border-radius:10px;
            padding:12px 16px;font-size:0.86em;color:#1A1A2E;line-height:1.7;margin:10px 0;">
            📥 <strong>Seus dados sumiram?</strong> Isso acontece quando o servidor reinicia.<br>
            Selecione abaixo o arquivo <strong>.json</strong> que você salvou antes — tudo volta como era.
            </div>""", unsafe_allow_html=True)
            arq_login = st.file_uploader("Carregar meus dados salvos (.json):", type=["json"], key="upload_login")
        else:
            arq_login = None

        dados_login = None
        if arq_login is not None:
            try:
                dados_login = json.load(arq_login)
                st.success(f"✅ Dados de **{dados_login.get('usuario','')}** reconhecidos!")
            except Exception:
                st.error("Arquivo inválido.")
                dados_login = None

        if st.button("✨ ENTRAR E VENDER MAIS"):
            if nome and chave:
                st.session_state.usuario = nome
                st.session_state.api_key = chave
                if dados_login:
                    carregar_json_sessao(dados_login)
                st.session_state.etapa = "App"
                st.rerun()
            else:
                st.warning("Preencha nome e chave API.")

        st.markdown("🔑 Não tem chave Groq? Crie grátis em <a href='https://console.groq.com/keys' target='_blank' style='color:#C2410C;font-weight:600;'>console.groq.com/keys</a>", unsafe_allow_html=True)

# ============================================================
# TELA: APP
# ============================================================
elif st.session_state.etapa == "App":

    barra_salvar()

    # NAVBAR — 2 linhas de abas
    st.markdown("**Módulos:**")
    cols1 = st.columns(10)
    paginas1 = [
        ("🏠","Home"),("🧠","Diagnostico"),("🎯","ModeloVenda"),("🛒","Oferta"),
        ("💰","Precificacao"),("👤","Avatar"),("✍️","Copy"),("📱","Conteudo"),
        ("🎥","Criativos"),("💬","Fechamento"),
    ]
    for i,(icone,pag) in enumerate(paginas1):
        labels = {
            "Home":"Painel","Diagnostico":"Diagnóstico","ModeloVenda":"Modelo de Venda",
            "Oferta":"Estratégia de Oferta","Precificacao":"Precificação",
            "Avatar":"Avatar do Cliente","Copy":"Copy","Conteudo":"Conteúdo",
            "Criativos":"Criativos","Fechamento":"Fechamento",
        }
        if cols1[i].button(icone, key=f"nav1_{pag}", help=labels[pag]):
            st.session_state.pagina = pag
            st.rerun()

    cols2 = st.columns(10)
    paginas2 = [
        ("🤖","Atendimento"),("🛍️","Marketplace"),("🌐","Loja"),("📢","Trafego"),
        ("📍","Local"),("📈","Escala"),("🧪","Validacao"),("📊","Auditoria"),
        ("📦","Estoque"),("💎","Branding"),
    ]
    for i,(icone,pag) in enumerate(paginas2):
        labels2 = {
            "Atendimento":"Atendimento Auto","Marketplace":"Marketplace",
            "Loja":"Loja Virtual","Trafego":"Tráfego Pago","Local":"Vendas Locais",
            "Escala":"Escala","Validacao":"Validação","Auditoria":"Auditoria",
            "Estoque":"Estoque","Branding":"Branding",
        }
        if cols2[i].button(icone, key=f"nav2_{pag}", help=labels2[pag]):
            st.session_state.pagina = pag
            st.rerun()

    # Mentor sempre visível
    col_mentor = st.columns([8,2])
    with col_mentor[1]:
        if st.button("🧠 MENTOR 24H", key="nav_mentor", help="Mentor Estratégico"):
            st.session_state.pagina = "Mentor"
            st.rerun()

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── PERFIL DO PRODUTO ─────────────────────────────────────
    with st.expander("⚙️ Seu produto (clique para configurar)", expanded=(not st.session_state.produto_padrao)):
        col_pa, col_pb, col_pc, col_pd = st.columns(4)
        with col_pa:
            st.session_state.produto_padrao = st.text_input("📦 Seu produto:", value=st.session_state.produto_padrao, placeholder="ex: creme para cabelo cacheado", key="text_input___Seu_produto__L367")
            st.session_state.nicho_padrao   = st.text_input("🎯 Nicho:", value=st.session_state.nicho_padrao, placeholder="ex: beleza, fitness, pet...", key="text_input___Nicho__L368")
        with col_pb:
            st.session_state.preco_custo  = st.number_input("💸 Custo do produto (R$):", min_value=0.0, value=float(st.session_state.preco_custo), step=0.5, key="number_input___Custo_do_produto__R____L370")
            st.session_state.preco_venda  = st.number_input("💰 Preço de venda (R$):", min_value=0.0, value=float(st.session_state.preco_venda), step=0.5, key="number_input___Pre_o_de_venda__R____L371")
        with col_pc:
            st.session_state.canal_padrao = st.selectbox("📲 Canal principal:", [
                "WhatsApp","Instagram","Mercado Livre","Shopee","Loja própria","TikTok Shop","Físico/loja","Múltiplos canais"
            ], index=["WhatsApp","Instagram","Mercado Livre","Shopee","Loja própria","TikTok Shop","Físico/loja","Múltiplos canais"].index(
                st.session_state.canal_padrao) if st.session_state.canal_padrao in
                ["WhatsApp","Instagram","Mercado Livre","Shopee","Loja própria","TikTok Shop","Físico/loja","Múltiplos canais"] else 0, key="widget_multi_1")
        with col_pd:
            if st.session_state.preco_custo > 0 and st.session_state.preco_venda > 0:
                margem = round((st.session_state.preco_venda - st.session_state.preco_custo) / st.session_state.preco_venda * 100, 1)
                lucro  = round(st.session_state.preco_venda - st.session_state.preco_custo, 2)
                cor    = "#059669" if margem >= 40 else ("#F59E0B" if margem >= 20 else "#EF4444")
                st.markdown(f"""<div style='background:#FFF8F0;border:2px solid {cor};border-radius:12px;padding:14px;text-align:center;'>
                <div style='font-size:1.8em;font-weight:700;color:{cor};'>R${lucro:.2f}</div>
                <div style='font-size:0.85em;'>lucro por venda</div>
                <div style='font-size:1.2em;font-weight:700;color:{cor};'>{margem}% margem</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ========================
    # HOME
    # ========================
    if st.session_state.pagina == "Home":
        col_u, col_r = st.columns([3, 1])
        with col_u:
            st.title(f"Bora vender mais, {st.session_state.usuario}! 📦")
            st.markdown("<span class='badge'>Mestre de Vendas</span>", unsafe_allow_html=True)
        with col_r:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪 Sair"):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()

        if len(st.session_state.historico_analises) == 0 and len(st.session_state.materiais_salvos) == 0:
            st.markdown("""<div style="background:#FEF3C7;border:2px solid #F59E0B;border-radius:12px;
            padding:12px 18px;margin-bottom:4px;color:#000;font-size:0.9em;font-weight:600;">
            ⚠️ Seus dados não estão mais no servidor.
            </div>""", unsafe_allow_html=True)
            arq_home = st.file_uploader("Carregar meus dados salvos (.json):", type=["json"], key="upload_home")
            if arq_home is not None:
                try:
                    dados_home = json.load(arq_home)
                    carregar_json_sessao(dados_home)
                    salvar_perfil_cache(st.session_state.usuario)
                    st.success("✅ Dados recuperados!")
                    st.rerun()
                except Exception:
                    st.error("Arquivo inválido.")

        tipos = {}
        for a in st.session_state.historico_analises:
            tipos[a['tipo']] = tipos.get(a['tipo'], 0) + 1

        c1,c2,c3,c4 = st.columns(4)
        c1.markdown(f"<div class='stat-box'><div class='stat-numero'>{len(st.session_state.historico_analises)}</div><div>Análises geradas</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stat-box'><div class='stat-numero'>{len(st.session_state.materiais_salvos)}</div><div>Materiais salvos</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='stat-box'><div class='stat-numero'>{tipos.get('Copy',0)}</div><div>Copies gerados</div></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='stat-box'><div class='stat-numero'>{tipos.get('Fechamento',0)}</div><div>Scripts de fechamento</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='card'>💡 <em>'Produto bom que ninguém sabe que existe não vende. Produto mediano com copy excelente vende muito. A diferença está na estratégia.'</em></div>", unsafe_allow_html=True)

        st.markdown("### 🗺️ O que cada módulo faz")
        guia = {
            "🧠 Diagnóstico":        "Análise completa do produto, nicho, concorrência e posicionamento",
            "🎯 Modelo de Venda":    "Define o melhor canal e modelo — estoque, dropshipping, revenda, marca própria",
            "🛒 Estratégia de Oferta":"Cria kits, combos, order bump, upsell, brindes e escassez inteligente",
            "💰 Precificação":       "Cálculo de margem, CAC, ROI, ponto de equilíbrio e projeção de faturamento",
            "👤 Avatar":             "Perfil profundo do cliente ideal — dores, medos, gatilhos e linguagem",
            "✍️ Copy":               "Títulos, descrições, bullet points, storytelling e CTA para produto físico",
            "📱 Conteúdo":           "Posts, reels, stories, TikTok, calendário editorial e ganchos virais",
            "🎥 Criativos":          "Scripts UGC, ângulos de anúncio, headlines e estrutura de criativo vencedor",
            "💬 Fechamento":         "Scripts para WhatsApp/Instagram + quebra de objeções prontas",
            "🤖 Atendimento":        "FAQ, respostas automáticas, recuperação de frios e pós-venda",
            "🛍️ Marketplace":        "SEO e estratégia para Mercado Livre, Shopee, Amazon e Magalu",
            "🌐 Loja Virtual":       "Otimização de página, checkout e conversão para Shopify/Nuvemshop",
            "📢 Tráfego Pago":       "Estratégia completa para Meta Ads, Google Ads e TikTok Ads",
            "📍 Vendas Locais":      "Bairro, delivery, catálogo WhatsApp, Google Maps e parcerias",
            "📈 Escala":             "Como contratar, automatizar, aumentar ticket e criar recorrência",
            "🧪 Validação":          "Antes de investir — vale a pena? Mercado saturado? Tendência ou moda?",
            "📊 Auditoria":          "Por que não vende? Analisa produto, oferta, tráfego, copy e atendimento",
            "📦 Estoque":            "Giro, produto parado, previsão de compra e organização",
            "💎 Branding":           "Nome, slogan, posicionamento e identidade da comunicação",
            "🧠 Mentor 24h":         "Modo conversa — tire dúvidas estratégicas como se fosse um consultor ao vivo",
        }
        for modulo, desc in guia.items():
            st.markdown(f"**{modulo}** — {desc}")

        if st.session_state.historico_analises:
            st.markdown("### 🕐 Últimas Análises")
            for item in reversed(st.session_state.historico_analises[-4:]):
                st.markdown(
                    f"<div class='hist-item'><span class='badge'>{item['tipo']}</span> "
                    f"<span class='badge-azul'>{item['produto'][:30]}</span> "
                    f"<small style='color:#888'>{item['data']}</small></div>",
                    unsafe_allow_html=True
                )

    # ========================
    # DIAGNÓSTICO
    # ========================
    elif st.session_state.pagina == "Diagnostico":
        st.header("🧠 Diagnóstico Inteligente do Negócio")
        st.markdown("Análise completa do seu produto, nicho e potencial de mercado.")

        col1, col2 = st.columns(2)
        with col1:
            produto   = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, placeholder="ex: creme para cabelo cacheado", key="text_input___Produto__L480")
            descricao = st.text_area("📝 Descreva o produto:", height=80, placeholder="ex: creme leave-in para cachos, 300ml, vegano, sem sulfato...", key="text_area___Descreva_o_produto__L481")
            concorrentes = st.text_input("🏆 Principais concorrentes:", placeholder="ex: Salon Line, Cachos e Afins, marcas do Mercado Livre...", key="text_input___Principais_concorrentes_L482")
        with col2:
            nicho     = st.text_input("🎯 Nicho:", value=st.session_state.nicho_padrao, placeholder="ex: beleza, saúde, pet, casa...", key="text_input___Nicho__L484")
            custo     = st.number_input("💸 Custo do produto (R$):", min_value=0.0, value=float(st.session_state.preco_custo), step=0.5, key="number_input___Custo_do_produto__R____L485")
            preco     = st.number_input("💰 Preço de venda pretendido (R$):", min_value=0.0, value=float(st.session_state.preco_venda), step=0.5, key="number_input___Pre_o_de_venda_pretendi_L486")
            canal     = st.text_input("📲 Canal de venda atual:", value=st.session_state.canal_padrao, key="text_input___Canal_de_venda_atual__L487")

        if st.button("🧠 GERAR DIAGNÓSTICO COMPLETO"):
            if produto.strip():
                with st.spinner("Analisando seu negócio..."):
                    margem = round((preco-custo)/preco*100,1) if preco > 0 else 0
                    prompt = (
                        f"Faça um diagnóstico completo do negócio de produto físico.\n"
                        f"Produto: {produto}. Descrição: {descricao}.\n"
                        f"Nicho: {nicho}. Custo: R${custo}. Preço: R${preco}. Margem: {margem}%.\n"
                        f"Canal: {canal}. Concorrentes: {concorrentes or 'não informado'}.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"🧠 DIAGNÓSTICO — {produto.upper()}\n\n"
                        f"📊 ANÁLISE DO PRODUTO:\n"
                        f"• Potencial de mercado: [Alto/Médio/Baixo] — justificativa\n"
                        f"• Diferencial percebido: [o que tem de único]\n"
                        f"• Ciclo de vida do produto: [lançamento/crescimento/maturidade/declínio]\n\n"
                        f"🎯 ANÁLISE DO NICHO:\n"
                        f"• Tamanho do mercado: [estimativa]\n"
                        f"• Nível de concorrência: [Alto/Médio/Baixo]\n"
                        f"• Tendência: [crescendo/estável/caindo]\n\n"
                        f"🏆 ANÁLISE DA CONCORRÊNCIA:\n"
                        f"• Pontos fracos deles que você pode explorar\n"
                        f"• O que eles fazem bem que você precisa fazer também\n"
                        f"• Gap de mercado (o que ninguém está fazendo)\n\n"
                        f"👤 PÚBLICO IDEAL:\n"
                        f"• Quem é (perfil detalhado)\n"
                        f"• Onde está (canais que frequenta)\n"
                        f"• Por que compra esse tipo de produto\n\n"
                        f"💰 ANÁLISE DE MARGEM:\n"
                        f"• Margem atual: {margem}% — {'✅ saudável' if margem >= 40 else '⚠️ apertada' if margem >= 20 else '🚨 perigosa'}\n"
                        f"• Margem ideal para esse nicho: [X%]\n"
                        f"• Sugestão de preço ideal: R$[X]\n\n"
                        f"✅ PONTOS FORTES:\n[Lista com justificativas]\n\n"
                        f"⚠️ PONTOS FRACOS:\n[Lista com como resolver]\n\n"
                        f"🎯 POSICIONAMENTO SUGERIDO:\n"
                        f"[Como se posicionar para se diferenciar — frase de posicionamento]\n\n"
                        f"⚡ TOP 3 AÇÕES IMEDIATAS:\n"
                        f"[O que fazer HOJE para melhorar o negócio]"
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Diagnóstico", produto, res)
                    st.session_state['diag_temp'] = res
                    st.markdown(f"<div class='card'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('diag_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar diagnóstico (.txt)", data=st.session_state['diag_temp'],
                    file_name="diagnostico.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Diagnóstico','produto':produto if 'produto' in dir() else '','conteudo':st.session_state['diag_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # MODELO DE VENDA
    # ========================
    elif st.session_state.pagina == "ModeloVenda":
        st.header("🎯 Escolha do Melhor Modelo de Venda")
        st.markdown("A IA define o melhor caminho para o seu produto e situação.")

        col1, col2 = st.columns(2)
        with col1:
            produto_m  = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, key="text_input___Produto__L553")
            capital    = st.text_input("💰 Capital disponível para investir:", placeholder="ex: R$500, R$2.000, R$10.000...", key="text_input___Capital_dispon_vel_para_L554")
            experiencia= st.selectbox("📊 Sua experiência em vendas:", ["Nunca vendi nada","Já vendi mas pouco","Tenho experiência","Sou vendedor experiente"], key="selectbox___Sua_experi_ncia_em_vend_L555")
        with col2:
            objetivo_m = st.text_input("🎯 Objetivo mensal:", placeholder="ex: R$3.000/mês, viver do negócio, renda extra...", key="text_input___Objetivo_mensal__L557")
            tempo_disp = st.selectbox("⏰ Tempo disponível por dia:", ["1-2 horas","3-4 horas","Período integral","Final de semana"], key="selectbox___Tempo_dispon_vel_por_di_L558")
            tem_estoque= st.radio("📦 Tem produto em mãos?", ["Sim, tenho estoque","Não tenho ainda","Estou decidindo"], horizontal=True, key="radio___Tem_produto_em_m_os__L559")

        if st.button("🎯 DEFINIR MEU MODELO IDEAL"):
            if produto_m.strip():
                with st.spinner("Analisando o melhor modelo para você..."):
                    prompt = (
                        f"Defina o melhor modelo de venda de produto físico para essa situação.\n"
                        f"Produto: {produto_m}. Capital: {capital}. Experiência: {experiencia}.\n"
                        f"Objetivo: {objetivo_m}. Tempo: {tempo_disp}. Estoque: {tem_estoque}.\n\n"
                        f"MODELOS A AVALIAR:\n"
                        f"Estoque próprio | Revenda | Distribuição | Marca própria | Dropshipping nacional | Dropshipping internacional | Afiliado de produto físico | Produção artesanal\n\n"
                        f"ESTRUTURA:\n\n"
                        f"🎯 MODELO RECOMENDADO: [nome do modelo]\n\n"
                        f"✅ POR QUE ESSE MODELO:\n"
                        f"[3 razões específicas baseadas no perfil informado]\n\n"
                        f"📋 COMO COMEÇAR (passo a passo):\n"
                        f"Passo 1: [ação concreta]\n"
                        f"Passo 2: [ação concreta]\n"
                        f"Passo 3: [ação concreta]\n"
                        f"Passo 4: [ação concreta]\n"
                        f"Passo 5: [ação concreta]\n\n"
                        f"⚠️ RISCOS DESSE MODELO:\n[O que pode dar errado e como evitar]\n\n"
                        f"💰 PROJEÇÃO REALISTA:\n"
                        f"• Mês 1-3 (início): R$[X] a R$[X]/mês\n"
                        f"• Mês 4-6 (crescimento): R$[X] a R$[X]/mês\n"
                        f"• Mês 7-12 (consolidação): R$[X]+/mês\n\n"
                        f"🔄 MODELO ALTERNATIVO:\n"
                        f"[Segundo modelo que também pode funcionar — com quando migrar para ele]\n\n"
                        f"⚡ COMEÇO AINDA HOJE:\n"
                        f"[O que fazer nas próximas 2 horas para dar o primeiro passo]"
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Modelo de Venda", produto_m, res)
                    st.session_state['modelo_temp'] = res
                    st.markdown(f"<div class='card-blue'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('modelo_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar (.txt)", data=st.session_state['modelo_temp'], file_name="modelo_venda.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_mod", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Modelo de Venda','produto':produto_m if 'produto_m' in dir() else '','conteudo':st.session_state['modelo_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # ESTRATÉGIA DE OFERTA
    # ========================
    elif st.session_state.pagina == "Oferta":
        st.header("🛒 Estratégia de Oferta Irresistível")
        st.markdown("A IA cria sua oferta completa — do kit ao upsell, do brinde à escassez.")

        col1, col2 = st.columns(2)
        with col1:
            produto_o  = st.text_input("📦 Produto principal:", value=st.session_state.produto_padrao, key="text_input___Produto_principal__L615")
            preco_o    = st.number_input("💰 Preço atual (R$):", min_value=0.0, value=float(st.session_state.preco_venda), step=0.5, key="number_input___Pre_o_atual__R____L616")
            publico_o  = st.text_input("👤 Para quem é:", placeholder="ex: mulheres 25-45 anos com cabelo cacheado...", key="text_input___Para_quem____L617")
        with col2:
            elementos  = st.multiselect("🎁 Elementos da oferta:", [
                "Kit de produtos","Order bump","Upsell","Cross-sell","Brinde","Frete grátis estratégico",
                "Garantia estendida","Escassez (quantidade limitada)","Urgência (prazo)","Desconto progressivo",
                "Parcelamento especial","Promoção sazonal","Combo família","Combo presente",
            ], default=["Kit de produtos","Brinde","Garantia estendida","Escassez (quantidade limitada)"], key="widget_multi_2")
            canal_o    = st.selectbox("📲 Canal da oferta:", ["WhatsApp","Instagram","Marketplace","Loja virtual","Presencial"], key="selectbox___Canal_da_oferta__L624")

        if st.button("🛒 CRIAR OFERTA IRRESISTÍVEL"):
            if produto_o.strip():
                with st.spinner("Montando sua oferta..."):
                    elems = ", ".join(elementos) if elementos else "oferta básica"
                    prompt = (
                        f"Crie uma estratégia de oferta completa para produto físico.\n"
                        f"Produto: {produto_o}. Preço: R${preco_o}. Público: {publico_o}.\n"
                        f"Elementos: {elems}. Canal: {canal_o}.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"🛒 OFERTA IRRESISTÍVEL — {produto_o.upper()}\n\n"
                        f"🎯 OFERTA PRINCIPAL:\n"
                        f"[Nome da oferta + o que inclui + preço + justificativa do preço]\n\n"
                        f"{'📦 KITS SUGERIDOS:' if 'Kit' in elems else ''}\n"
                        f"{'• Kit Básico: [produto(s)] por R$[X]' if 'Kit' in elems else ''}\n"
                        f"{'• Kit Completo: [produto(s)] por R$[X]' if 'Kit' in elems else ''}\n"
                        f"{'• Kit Premium: [produto(s)] por R$[X]' if 'Kit' in elems else ''}\n\n"
                        f"{'⬆️ ORDER BUMP: [produto complementar] por R$[X] — script: [como oferecer]' if 'Order bump' in elems else ''}\n\n"
                        f"{'🚀 UPSELL: [oferta superior] por R$[X] — quando oferecer e como' if 'Upsell' in elems else ''}\n\n"
                        f"{'🎁 BRINDE ESTRATÉGICO: [o que dar] — por que esse brinde converte' if 'Brinde' in elems else ''}\n\n"
                        f"{'⏰ ESCASSEZ: [como criar urgência real sem parecer fake]' if 'Escassez' in elems or 'Urgência' in elems else ''}\n\n"
                        f"{'🛡️ GARANTIA: [tipo + prazo + como comunicar]' if 'Garantia' in elems else ''}\n\n"
                        f"💬 COMO APRESENTAR ESSA OFERTA NO {canal_o.upper()}:\n"
                        f"[Script completo de apresentação da oferta no canal escolhido]\n\n"
                        f"📊 PREVISÃO DE CONVERSÃO:\n"
                        f"[Estimativa de quantas pessoas que veem compram — e por quê]\n\n"
                        f"🔑 O QUE FAZ ESSA OFERTA SER IRRESISTÍVEL:\n"
                        f"[Os 3 elementos psicológicos que tornam difícil dizer não]"
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Oferta", produto_o, res)
                    st.session_state['oferta_temp'] = res
                    st.markdown(f"<div class='card-green'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('oferta_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar oferta (.txt)", data=st.session_state['oferta_temp'], file_name="estrategia_oferta.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_of", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Oferta','produto':produto_o if 'produto_o' in dir() else '','conteudo':st.session_state['oferta_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # PRECIFICAÇÃO
    # ========================
    elif st.session_state.pagina == "Precificacao":
        st.header("💰 Precificação Inteligente")
        st.markdown("Calcule o preço ideal, margem real, ponto de equilíbrio e projeção de lucro.")

        col1, col2 = st.columns(2)
        with col1:
            custo_prod   = st.number_input("💸 Custo do produto (R$):", min_value=0.0, value=float(st.session_state.preco_custo), step=0.5, key="number_input___Custo_do_produto__R____L679")
            frete_medio  = st.number_input("🚚 Frete médio (R$):", min_value=0.0, value=0.0, step=0.5, key="number_input___Frete_m_dio__R____L680")
            taxa_plat    = st.number_input("💳 Taxa da plataforma (%):", min_value=0.0, max_value=30.0, value=12.0, step=0.5, key="number_input___Taxa_da_plataforma______L681")
            custo_ads    = st.number_input("📢 Custo de anúncio por venda (R$):", min_value=0.0, value=0.0, step=0.5, key="number_input___Custo_de_an_ncio_por_ve_L682")
        with col2:
            preco_atual  = st.number_input("💰 Preço de venda (R$):", min_value=0.0, value=float(st.session_state.preco_venda), step=0.5, key="number_input___Pre_o_de_venda__R____L684")
            meta_vendas  = st.number_input("🎯 Meta de vendas por mês:", min_value=1, value=50, step=5, key="number_input___Meta_de_vendas_por_m_s__L685")
            nicho_prec   = st.text_input("🎯 Nicho:", value=st.session_state.nicho_padrao, key="text_input___Nicho__L686")
            produto_prec = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, key="text_input___Produto__L687")

        # Cálculos automáticos
        if preco_atual > 0 and custo_prod > 0:
            custo_total   = custo_prod + frete_medio + (preco_atual * taxa_plat/100) + custo_ads
            lucro_unit    = preco_atual - custo_total
            margem_real   = round(lucro_unit / preco_atual * 100, 1) if preco_atual > 0 else 0
            fat_mes       = preco_atual * meta_vendas
            lucro_mes     = lucro_unit * meta_vendas
            equilibrio    = round(custo_total / (preco_atual - custo_prod) * custo_prod, 2) if (preco_atual - custo_prod) > 0 else 0

            cor = "#059669" if margem_real >= 40 else ("#F59E0B" if margem_real >= 20 else "#EF4444")
            st.markdown(f"""<div style='background:#FFF8F0;border:2px solid {cor};border-radius:14px;padding:18px;margin:10px 0;'>
            <div style='display:grid;grid-template-columns:repeat(4,1fr);gap:12px;text-align:center;'>
            <div><div style='font-size:1.6em;font-weight:700;color:{cor};'>R${lucro_unit:.2f}</div><div style='font-size:0.8em;'>Lucro por venda</div></div>
            <div><div style='font-size:1.6em;font-weight:700;color:{cor};'>{margem_real}%</div><div style='font-size:0.8em;'>Margem real</div></div>
            <div><div style='font-size:1.6em;font-weight:700;color:#1D4ED8;'>R${lucro_mes:,.0f}</div><div style='font-size:0.8em;'>Lucro/mês ({meta_vendas} vendas)</div></div>
            <div><div style='font-size:1.6em;font-weight:700;color:#7C3AED;'>R${fat_mes:,.0f}</div><div style='font-size:0.8em;'>Faturamento/mês</div></div>
            </div></div>""", unsafe_allow_html=True)

        if st.button("💰 GERAR ANÁLISE COMPLETA DE PRECIFICAÇÃO"):
            if produto_prec.strip() and preco_atual > 0:
                with st.spinner("Calculando sua precificação ideal..."):
                    prompt = (
                        f"Crie uma análise completa de precificação para produto físico.\n"
                        f"Produto: {produto_prec}. Nicho: {nicho_prec}.\n"
                        f"Custo produto: R${custo_prod}. Frete: R${frete_medio}.\n"
                        f"Taxa plataforma: {taxa_plat}%. Custo de ads/venda: R${custo_ads}.\n"
                        f"Preço atual: R${preco_atual}. Meta: {meta_vendas} vendas/mês.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"💰 ANÁLISE DE PRECIFICAÇÃO — {produto_prec.upper()}\n\n"
                        f"📊 CUSTO TOTAL REAL POR VENDA:\n"
                        f"• Produto: R${custo_prod}\n"
                        f"• Frete: R${frete_medio}\n"
                        f"• Taxa plataforma: R${round(preco_atual*taxa_plat/100,2)}\n"
                        f"• Custo de ads: R${custo_ads}\n"
                        f"• TOTAL: R$[X]\n\n"
                        f"💡 ANÁLISE DO PREÇO ATUAL (R${preco_atual}):\n"
                        f"[O preço está bom, alto demais ou baixo demais para o mercado?]\n\n"
                        f"🎯 PREÇO IDEAL SUGERIDO:\n"
                        f"• Preço mínimo (sobrevivência): R$[X]\n"
                        f"• Preço ideal (crescimento): R$[X]\n"
                        f"• Preço premium (se tiver diferencial): R$[X]\n\n"
                        f"📊 SIMULAÇÃO DE LUCRO (com preço ideal):\n"
                        f"• 30 vendas/mês: R$[X] lucro\n"
                        f"• 50 vendas/mês: R$[X] lucro\n"
                        f"• 100 vendas/mês: R$[X] lucro\n\n"
                        f"⚖️ PONTO DE EQUILÍBRIO:\n"
                        f"[Quantas vendas por mês para cobrir todos os custos]\n\n"
                        f"📈 COMO AUMENTAR A MARGEM SEM AUMENTAR O PREÇO:\n"
                        f"[3 estratégias práticas para esse produto/nicho]\n\n"
                        f"🎯 ESTRATÉGIA DE PRECIFICAÇÃO PSICOLÓGICA:\n"
                        f"[Como usar o preço para aumentar o valor percebido]"
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Precificação", produto_prec, res)
                    st.session_state['prec_temp'] = res
                    st.markdown(f"<div class='card'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Preencha produto e preço.")

        if st.session_state.get('prec_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar (.txt)", data=st.session_state['prec_temp'], file_name="precificacao.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_prec", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Precificação','produto':produto_prec if 'produto_prec' in dir() else '','conteudo':st.session_state['prec_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # AVATAR DO CLIENTE
    # ========================
    elif st.session_state.pagina == "Avatar":
        st.header("👤 Avatar do Cliente Ideal")
        st.markdown("Perfil profundo do seu comprador — para falar a língua certa e converter mais.")

        col1, col2 = st.columns(2)
        with col1:
            produto_av = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, key="text_input___Produto__L766")
            nicho_av   = st.text_input("🎯 Nicho:", value=st.session_state.nicho_padrao, key="text_input___Nicho__L767")
            palpite_av = st.text_area("🤔 O que você já sabe sobre seu cliente:", height=80,
                placeholder="ex: mulheres de 30-45 anos, classe média, preocupadas com saúde...", key="widget_multi_3")
        with col2:
            preco_av   = st.number_input("💰 Preço do produto (R$):", min_value=0.0, value=float(st.session_state.preco_venda), step=0.5, key="number_input___Pre_o_do_produto__R____L771")
            canal_av   = st.selectbox("📲 Canal de venda:", ["WhatsApp","Instagram","Marketplace","Loja virtual","TikTok","Físico"], key="selectbox___Canal_de_venda__L772")

        if st.button("👤 CRIAR AVATAR COMPLETO"):
            if produto_av.strip():
                with st.spinner("Criando o perfil do seu cliente ideal..."):
                    prompt = (
                        f"Crie um avatar completo e profundo do cliente ideal.\n"
                        f"Produto: {produto_av}. Nicho: {nicho_av}. Preço: R${preco_av}.\n"
                        f"Canal: {canal_av}. O que já sei: {palpite_av or 'não informado'}.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"👤 AVATAR DO CLIENTE — {produto_av.upper()}\n\n"
                        f"🧑 PERFIL DEMOGRÁFICO:\n"
                        f"• Nome fictício: [nome]\n"
                        f"• Idade: [X] anos\n"
                        f"• Gênero predominante: [X]\n"
                        f"• Localização: [regiões do Brasil]\n"
                        f"• Faixa de renda: R$[X] a R$[X]/mês\n"
                        f"• Profissão mais comum: [X]\n"
                        f"• Estado civil: [X]\n\n"
                        f"😰 DORES PROFUNDAS (o que a tira o sono):\n"
                        f"• [Dor 1 — específica e emocional]\n"
                        f"• [Dor 2]\n"
                        f"• [Dor 3]\n\n"
                        f"✨ DESEJOS (o que ela quer de verdade):\n"
                        f"• [Desejo 1]\n"
                        f"• [Desejo 2]\n"
                        f"• [Desejo 3]\n\n"
                        f"😨 MEDOS (o que a impede de comprar):\n"
                        f"• [Medo 1 — relacionado ao produto]\n"
                        f"• [Medo 2]\n\n"
                        f"🤔 OBJEÇÕES (o que ela pensa antes de comprar):\n"
                        f"• [Objeção 1] — como quebrar: [resposta]\n"
                        f"• [Objeção 2] — como quebrar: [resposta]\n"
                        f"• [Objeção 3] — como quebrar: [resposta]\n\n"
                        f"🗣️ LINGUAGEM (como ela fala e o que ressoa):\n"
                        f"• Palavras que ela usa: [lista]\n"
                        f"• Palavras que ela ODEIA ver: [lista]\n"
                        f"• Tom que conecta com ela: [formal/informal/técnico/emocional]\n\n"
                        f"🛒 HÁBITOS DE COMPRA:\n"
                        f"• Onde pesquisa antes de comprar: [X]\n"
                        f"• O que a convence a comprar: [X]\n"
                        f"• O que a faz desistir: [X]\n"
                        f"• Melhor horário para abordar: [X]\n\n"
                        f"💥 GATILHOS EMOCIONAIS MAIS PODEROSOS:\n"
                        f"• [Gatilho 1 — com exemplo de como usar]\n"
                        f"• [Gatilho 2]\n"
                        f"• [Gatilho 3]\n\n"
                        f"📱 ONDE ENCONTRAR ESSE AVATAR:\n"
                        f"[Grupos, páginas, hashtags, canais onde esse cliente está]"
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Avatar", produto_av, res)
                    st.session_state['avatar_temp'] = res
                    st.markdown(f"<div class='card-purple'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('avatar_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar avatar (.txt)", data=st.session_state['avatar_temp'], file_name="avatar_cliente.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_av", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Avatar','produto':produto_av if 'produto_av' in dir() else '','conteudo':st.session_state['avatar_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # COPY
    # ========================
    elif st.session_state.pagina == "Copy":
        st.header("✍️ Copy para Produto Físico")
        st.markdown("Textos prontos que vendem — do título à descrição completa.")

        col1, col2 = st.columns(2)
        with col1:
            produto_c  = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, key="text_input___Produto__L847")
            descricao_c= st.text_area("📝 Descrição do produto:", height=80, placeholder="ex: creme leave-in 300ml, vegano, para cachos...", key="text_area___Descri__o_do_produto__L848")
            publico_c  = st.text_input("👤 Público-alvo:", placeholder="ex: mulheres com cabelo cacheado...", key="text_input___P_blico_alvo__L849")
        with col2:
            tipo_copy  = st.multiselect("📋 Que tipo de copy gerar:", [
                "Título de venda","Descrição do produto","Bullet points (benefícios)",
                "Storytelling do produto","Script de venda (conversa)","Copy emocional",
                "Copy racional","CTA (chamada para ação)","Copy para marketplace",
            ], default=["Título de venda","Bullet points (benefícios)","CTA (chamada para ação)"], key="widget_multi_4")
            preco_c    = st.number_input("💰 Preço (R$):", min_value=0.0, value=float(st.session_state.preco_venda), step=0.5, key="number_input___Pre_o__R____L856")
            tom_c      = st.radio("Tom:", ["Emocional e empático","Direto e racional","Urgente e escasso","Inspirador"], horizontal=True, key="radio_Tom__L857")

        if st.button("✍️ GERAR COPIES AGORA"):
            if produto_c.strip():
                with st.spinner("Escrevendo seus copies..."):
                    tipos_c = ", ".join(tipo_copy) if tipo_copy else "copy geral"
                    prompt = (
                        f"Crie copies de venda para produto físico.\n"
                        f"Produto: {produto_c}. Descrição: {descricao_c}.\n"
                        f"Público: {publico_c}. Preço: R${preco_c}. Tom: {tom_c}.\n"
                        f"Tipos solicitados: {tipos_c}.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"✍️ COPIES — {produto_c.upper()}\n\n"
                        + ("🏷️ TÍTULOS DE VENDA (3 opções):\n[Título 1 — ângulo emocional]\n[Título 2 — ângulo benefício]\n[Título 3 — ângulo curiosidade]\n\n" if "Título" in tipos_c else "")
                        + ("📝 DESCRIÇÃO COMPLETA DO PRODUTO:\n[Descrição persuasiva para loja/marketplace — SEO-friendly]\n\n" if "Descrição" in tipos_c else "")
                        + ("✅ BULLET POINTS (benefícios que vendem):\n• [Benefício 1 — transformação, não característica]\n• [Benefício 2]\n• [Benefício 3]\n• [Benefício 4]\n• [Benefício 5]\n\n" if "Bullet" in tipos_c else "")
                        + ("📖 STORYTELLING DO PRODUTO:\n[História de 3-5 parágrafos que conecta emocionalmente]\n\n" if "Storytelling" in tipos_c else "")
                        + ("💬 SCRIPT DE VENDA (WhatsApp/Instagram):\n[Conversa completa — do olá ao fechamento]\n\n" if "Script" in tipos_c else "")
                        + ("❤️ COPY EMOCIONAL:\n[Texto que fala com o coração — dores e desejos]\n\n" if "emocional" in tipos_c.lower() else "")
                        + ("🧠 COPY RACIONAL:\n[Texto com dados, lógica e prova social]\n\n" if "racional" in tipos_c.lower() else "")
                        + ("🎯 CTAs (5 opções):\n[CTA 1]\n[CTA 2]\n[CTA 3]\n[CTA 4]\n[CTA 5]\n\n" if "CTA" in tipos_c else "")
                        + ("🛍️ COPY PARA MARKETPLACE:\n[Título SEO + descrição otimizada para Mercado Livre/Shopee]\n\n" if "marketplace" in tipos_c.lower() else "")
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Copy", produto_c, res)
                    st.session_state['copy_temp'] = res
                    st.markdown(f"<div class='card-dark'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('copy_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar copies (.txt)", data=st.session_state['copy_temp'], file_name="copies_produto.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_copy", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Copy','produto':produto_c if 'produto_c' in dir() else '','conteudo':st.session_state['copy_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # CONTEÚDO
    # ========================
    elif st.session_state.pagina == "Conteudo":
        st.header("📱 Conteúdo para Redes Sociais")
        st.markdown("Posts, reels, stories e calendário editorial para vender sem parecer que está vendendo.")

        col1, col2 = st.columns(2)
        with col1:
            produto_ct = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, key="text_input___Produto__L905")
            nicho_ct   = st.text_input("🎯 Nicho:", value=st.session_state.nicho_padrao, key="text_input___Nicho__L906")
            plataformas= st.multiselect("📱 Plataformas:", ["Instagram","TikTok","YouTube Shorts","Facebook","Pinterest"], default=["Instagram","TikTok"], key="multiselect___Plataformas__L907")
        with col2:
            tipo_cont  = st.selectbox("📋 O que gerar:", [
                "Calendário editorial 30 dias","5 ideias de Reels/TikTok","10 ideias de posts",
                "3 sequências de Stories","5 ganchos virais","Roteiro de vídeo de venda",
                "Ideias de conteúdo educativo","Conteúdo de bastidores",
            ], key="widget_multi_5")
            frequencia = st.selectbox("⏰ Frequência de postagem:", ["1x por dia","3x por semana","5x por semana","7x por semana"], key="selectbox___Frequ_ncia_de_postagem__L914")

        if st.button("📱 GERAR CONTEÚDO"):
            if produto_ct.strip():
                with st.spinner("Criando seu conteúdo..."):
                    plats = ", ".join(plataformas) if plataformas else "Instagram"
                    prompt = (
                        f"Crie {tipo_cont} para venda de produto físico.\n"
                        f"Produto: {produto_ct}. Nicho: {nicho_ct}.\n"
                        f"Plataformas: {plats}. Frequência: {frequencia}.\n\n"
                        f"REGRAS:\n"
                        f"- Conteúdo que educa, entretém E vende — sem parecer propaganda\n"
                        f"- Use gatilhos de prova social, curiosidade e transformação\n"
                        f"- Ganchos nos primeiros 3 segundos para reter atenção\n"
                        f"- Inclua CTAs naturais (sem forçar)\n\n"
                        f"ESTRUTURA:\n\n"
                        f"📱 {tipo_cont.upper()} — {produto_ct.upper()}\n"
                        f"Plataformas: {plats}\n\n"
                        f"[Entregue o conteúdo completo conforme solicitado]\n\n"
                        f"Para cada post/reel/story:\n"
                        f"📌 [NÚMERO/DIA]\n"
                        f"Formato: [post/reel/story/carrossel]\n"
                        f"Gancho: [primeiros 3 segundos ou primeira linha]\n"
                        f"Conteúdo: [desenvolvimento]\n"
                        f"CTA: [chamada para ação]\n"
                        f"Caption/legenda: [texto para publicar]\n"
                        f"Hashtags: [10-15 hashtags estratégicas]\n\n"
                        f"💡 DICA DE PRODUÇÃO:\n"
                        f"[Como filmar/criar esse conteúdo com celular sem equipamento profissional]"
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Conteúdo", produto_ct, res)
                    st.session_state['cont_temp'] = res
                    st.markdown(f"<div class='card-green'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('cont_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar conteúdo (.txt)", data=st.session_state['cont_temp'], file_name="conteudo_redes.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_ct", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Conteúdo','produto':produto_ct if 'produto_ct' in dir() else '','conteudo':st.session_state['cont_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # CRIATIVOS
    # ========================
    elif st.session_state.pagina == "Criativos":
        st.header("🎥 Criativos para Anúncios")
        st.markdown("Scripts UGC, ângulos de venda e estrutura de anúncio vencedor.")

        col1, col2 = st.columns(2)
        with col1:
            produto_cr = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, key="text_input___Produto__L969")
            publico_cr = st.text_input("👤 Público:", placeholder="ex: mulheres 25-40, homens que praticam academia...", key="text_input___P_blico__L970")
            plataforma_cr = st.selectbox("📢 Plataforma do anúncio:", ["Meta Ads (Instagram/Facebook)","TikTok Ads","Google Ads","YouTube Ads"], key="selectbox___Plataforma_do_an_ncio__L971")
        with col2:
            tipo_cr    = st.multiselect("🎬 O que gerar:", [
                "Script UGC (depoimento real)","Script de vídeo de venda","3 headlines para testar",
                "Ângulos de venda (A/B)","Estrutura de anúncio vencedor","Copy para imagem estática",
                "Ideia de criativo nativo",
            ], default=["Script UGC (depoimento real)","3 headlines para testar","Ângulos de venda (A/B)"], key="widget_multi_6")
            objetivo_cr= st.radio("Objetivo do anúncio:", ["Venda direta","Lead/WhatsApp","Tráfego para loja","Reconhecimento"], horizontal=True, key="radio_Objetivo_do_an_ncio__L978")

        if st.button("🎥 GERAR CRIATIVOS"):
            if produto_cr.strip():
                with st.spinner("Criando seus anúncios..."):
                    tipos_cr = ", ".join(tipo_cr) if tipo_cr else "script geral"
                    prompt = (
                        f"Crie criativos de anúncio para produto físico.\n"
                        f"Produto: {produto_cr}. Público: {publico_cr}.\n"
                        f"Plataforma: {plataforma_cr}. Objetivo: {objetivo_cr}.\n"
                        f"Tipos: {tipos_cr}.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"🎥 CRIATIVOS — {produto_cr.upper()}\n"
                        f"Plataforma: {plataforma_cr} | Objetivo: {objetivo_cr}\n\n"
                        + ("📹 SCRIPT UGC (depoimento autêntico):\n"
                           "Hook (0-3s): [frase de abertura que para o scroll]\n"
                           "Problema (3-8s): [dor do avatar]\n"
                           "Descoberta (8-15s): [como encontrou o produto]\n"
                           "Resultado (15-25s): [transformação]\n"
                           "CTA (últimos 3s): [chamada]\n"
                           "LEGENDA: [texto do anúncio]\n\n" if "UGC" in tipos_cr else "")
                        + ("📹 SCRIPT VÍDEO DE VENDA:\n[Script completo de 30-60 segundos]\n\n" if "vídeo de venda" in tipos_cr.lower() else "")
                        + ("📌 3 HEADLINES PARA TESTAR:\n[Headline 1 — ângulo dor]\n[Headline 2 — ângulo benefício]\n[Headline 3 — ângulo curiosidade]\n\n" if "headline" in tipos_cr.lower() else "")
                        + ("🔄 ÂNGULOS DE VENDA (A/B):\nÂngulo A: [foco em X]\nCopy: [texto]\n\nÂngulo B: [foco em Y]\nCopy: [texto]\n\nÂngulo C: [foco em Z]\nCopy: [texto]\n\n" if "Ângulo" in tipos_cr else "")
                        + ("🏆 ESTRUTURA DE ANÚNCIO VENCEDOR:\n[Anatomia completa do anúncio que converte]\n\n" if "vencedor" in tipos_cr.lower() else "")
                        + (f"📊 ESTRATÉGIA DE TESTE A/B:\n[Como testar os criativos e o que medir]\n\n"
                           f"💰 ORÇAMENTO INICIAL SUGERIDO:\n[Quanto investir para validar — com cronograma]")
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Criativos", produto_cr, res)
                    st.session_state['cri_temp'] = res
                    st.markdown(f"<div class='card-red'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('cri_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar criativos (.txt)", data=st.session_state['cri_temp'], file_name="criativos_anuncios.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_cri", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Criativos','produto':produto_cr if 'produto_cr' in dir() else '','conteudo':st.session_state['cri_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # FECHAMENTO
    # ========================
    elif st.session_state.pagina == "Fechamento":
        st.header("💬 Fechamento de Vendas")
        st.markdown("Scripts prontos para WhatsApp/Instagram + quebra de objeções que funcionam de verdade.")

        tab1, tab2 = st.tabs(["📲 Scripts de Abordagem","🛡️ Quebra de Objeções"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                produto_f  = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, key="text_input___Produto__L1034")
                preco_f    = st.number_input("💰 Preço (R$):", min_value=0.0, value=float(st.session_state.preco_venda), step=0.5, key="number_input___Pre_o__R____L1035")
                situacao_f = st.selectbox("📍 Situação:", [
                    "Primeiro contato (lead frio)","Pessoa perguntou o preço","Pessoa pediu mais informações",
                    "Pessoa sumiu após ver o preço","Recuperação de carrinho abandonado",
                    "Follow-up após 24h sem resposta","Indicação de cliente",
                ], key="widget_multi_7")
            with col2:
                canal_f    = st.selectbox("📲 Canal:", ["WhatsApp","Instagram DM","Facebook Messenger"], key="selectbox___Canal__L1042")
                tom_f      = st.radio("Tom:", ["Consultivo e empático","Direto e objetivo","Amigável e descontraído"], horizontal=True, key="radio_Tom__L1043")

            if st.button("💬 GERAR SCRIPTS DE FECHAMENTO"):
                if produto_f.strip():
                    with st.spinner("Criando seus scripts..."):
                        prompt = (
                            f"Crie scripts de fechamento de vendas.\n"
                            f"Produto: {produto_f}. Preço: R${preco_f}. Canal: {canal_f}.\n"
                            f"Situação: {situacao_f}. Tom: {tom_f}.\n\n"
                            f"ESTRUTURA:\n\n"
                            f"💬 SCRIPTS DE FECHAMENTO — {produto_f.upper()}\n"
                            f"Canal: {canal_f} | Situação: {situacao_f}\n\n"
                            f"📱 SCRIPT PRINCIPAL:\n"
                            f"[Mensagem 1 — abertura]\n"
                            f"[Aguardar resposta]\n"
                            f"[Mensagem 2 — desenvolvimento]\n"
                            f"[Aguardar resposta]\n"
                            f"[Mensagem 3 — fechamento]\n\n"
                            f"🔄 VARIAÇÃO A (mais curta):\n[Script resumido — para quem não tem tempo]\n\n"
                            f"🔄 VARIAÇÃO B (mais emocional):\n[Script com mais gatilho emocional]\n\n"
                            f"📸 MENSAGEM COM MÍDIA:\n[Script para enviar junto com foto/vídeo do produto]\n\n"
                            f"⏰ SCRIPT DE FOLLOW-UP (caso não responda em 24h):\n[Mensagem de retomada — sem parecer desesperado]\n\n"
                            f"✅ COMO CONFIRMAR O PEDIDO:\n[Mensagem de fechamento + dados para pagamento]"
                        )
                        res = vendas_ia(prompt)
                        salvar_analise("Fechamento", produto_f, res)
                        st.session_state['fech_temp'] = res
                        st.markdown(f"<div class='card'>{res}</div>", unsafe_allow_html=True)
                else:
                    st.warning("Informe o produto.")

            if st.session_state.get('fech_temp'):
                col_dl, col_sv = st.columns(2)
                with col_dl:
                    st.download_button("📋 Baixar scripts (.txt)", data=st.session_state['fech_temp'], file_name="scripts_fechamento.txt", mime="text/plain", use_container_width=True)
                with col_sv:
                    if st.button("💾 Salvar", key="sv_fech", use_container_width=True):
                        st.session_state.materiais_salvos.append({'tipo':'Fechamento','produto':produto_f if 'produto_f' in dir() else '','conteudo':st.session_state['fech_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                        st.success("✅ Salvo!")

        with tab2:
            produto_obj = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, key="prod_obj")
            preco_obj   = st.number_input("💰 Preço (R$):", min_value=0.0, value=float(st.session_state.preco_venda), step=0.5, key="preco_obj")
            objecoes    = st.multiselect("🛡️ Objeções a quebrar:", [
                "Tá caro / Não tenho dinheiro","Vou pensar / Deixa eu ver",
                "Depois eu compro","Não confio / Não te conheço",
                "Tem garantia?","Meu marido/esposa decide",
                "Já tenho um parecido","Encontrei mais barato",
                "Não sei se vai funcionar pra mim","Tô desempregado",
            ], default=["Tá caro / Não tenho dinheiro","Vou pensar / Deixa eu ver","Não confio / Não te conheço"], key="widget_multi_8")

            if st.button("🛡️ GERAR QUEBRA DE OBJEÇÕES", key="btn_obj"):
                if produto_obj.strip() and objecoes:
                    with st.spinner("Preparando suas respostas..."):
                        objs = "\n".join([f"- {o}" for o in objecoes])
                        prompt = (
                            f"Crie scripts para quebrar objeções de venda.\n"
                            f"Produto: {produto_obj}. Preço: R${preco_obj}.\n\n"
                            f"Objeções a quebrar:\n{objs}\n\n"
                            f"Para CADA objeção:\n\n"
                            f"🛡️ OBJEÇÃO: '[objeção]'\n\n"
                            f"🧠 O QUE ELA REALMENTE SIGNIFICA:\n"
                            f"[O que o cliente está sentindo por baixo dessa objeção]\n\n"
                            f"💬 RESPOSTA PRINCIPAL:\n"
                            f"[Script word-for-word — natural, sem parecer ensaiado]\n\n"
                            f"🔄 RESPOSTA ALTERNATIVA:\n"
                            f"[Outra abordagem para o mesmo caso]\n\n"
                            f"⚡ RESPOSTA RÁPIDA (1 mensagem só):\n"
                            f"[Versão curta para WhatsApp]\n\n"
                            f"---\n\n"
                            f"[Repita para todas as objeções]\n\n"
                            f"💡 REGRA DE OURO DO FECHAMENTO:\n"
                            f"[O princípio mais importante para fechar vendas de produto físico]"
                        )
                        res = vendas_ia(prompt)
                        salvar_analise("Quebra de Objeções", produto_obj, res)
                        st.session_state['obj_temp'] = res
                        st.markdown(f"<div class='card-yellow'>{res}</div>", unsafe_allow_html=True)
                else:
                    st.warning("Informe o produto e selecione as objeções.")

            if st.session_state.get('obj_temp'):
                col_dl, col_sv = st.columns(2)
                with col_dl:
                    st.download_button("📋 Baixar (.txt)", data=st.session_state['obj_temp'], file_name="quebra_objecoes.txt", mime="text/plain", use_container_width=True)
                with col_sv:
                    if st.button("💾 Salvar", key="sv_obj", use_container_width=True):
                        st.session_state.materiais_salvos.append({'tipo':'Quebra de Objeções','produto':produto_obj,'conteudo':st.session_state['obj_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                        st.success("✅ Salvo!")

    # ========================
    # ATENDIMENTO
    # ========================
    elif st.session_state.pagina == "Atendimento":
        st.header("🤖 Atendimento Automático")
        st.markdown("FAQ, respostas automáticas e scripts humanizados para escalar sem perder qualidade.")

        col1, col2 = st.columns(2)
        with col1:
            produto_at = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, key="text_input___Produto__L1142")
            preco_at   = st.number_input("💰 Preço (R$):", min_value=0.0, value=float(st.session_state.preco_venda), step=0.5, key="number_input___Pre_o__R____L1143")
            prazo_entrega = st.text_input("🚚 Prazo de entrega:", placeholder="ex: 5-10 dias úteis, entrega no dia seguinte...", key="text_input___Prazo_de_entrega__L1144")
        with col2:
            tipo_at    = st.selectbox("📋 O que gerar:", [
                "FAQ completo do produto","Respostas automáticas (WhatsApp Business)","Scripts de pós-venda",
                "Recuperação de clientes frios","Scripts de recompra","Respostas para reclamações",
            ], key="widget_multi_9")
            canal_at   = st.selectbox("📲 Canal:", ["WhatsApp","Instagram","Marketplace","E-mail"], key="selectbox___Canal__L1150")

        if st.button("🤖 GERAR ATENDIMENTO AUTOMÁTICO"):
            if produto_at.strip():
                with st.spinner("Criando seus scripts de atendimento..."):
                    prompt = (
                        f"Crie {tipo_at} para produto físico.\n"
                        f"Produto: {produto_at}. Preço: R${preco_at}.\n"
                        f"Prazo entrega: {prazo_entrega or 'padrão'}. Canal: {canal_at}.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"🤖 {tipo_at.upper()} — {produto_at.upper()}\n\n"
                        + ("❓ FAQ COMPLETO:\n\nAs 15 perguntas mais feitas sobre esse produto:\n\nP: [pergunta]\nR: [resposta humanizada e completa]\n\n[Repita para 15 perguntas]\n\n" if "FAQ" in tipo_at else "")
                        + ("📱 RESPOSTAS AUTOMÁTICAS (copie para o WhatsApp Business):\n\n"
                           "🔵 BOAS-VINDAS:\n[mensagem]\n\n"
                           "🔵 AUSÊNCIA:\n[mensagem]\n\n"
                           "🔵 APÓS COMPRA:\n[mensagem]\n\n"
                           "🔵 RASTREAMENTO:\n[mensagem]\n\n" if "automáticas" in tipo_at.lower() else "")
                        + ("💌 SEQUÊNCIA PÓS-VENDA:\n\n"
                           "Mensagem 1 (logo após compra): [confirmação + expectativa]\n"
                           "Mensagem 2 (dia do envio): [rastreamento + antecipação]\n"
                           "Mensagem 3 (após entrega): [satisfação + prova social]\n"
                           "Mensagem 4 (7 dias): [resultado + recompra]\n"
                           "Mensagem 5 (30 dias): [reativação + oferta]\n\n" if "pós-venda" in tipo_at.lower() else "")
                        + ("🧊 RECUPERAÇÃO DE CLIENTES FRIOS:\n\n"
                           "[Scripts para reativar quem não compra há mais de 30/60/90 dias]\n\n" if "frios" in tipo_at.lower() else "")
                        + ("😡 RESPOSTAS PARA RECLAMAÇÕES:\n\n"
                           "Produto com defeito: [script]\n"
                           "Atraso na entrega: [script]\n"
                           "Produto diferente do esperado: [script]\n"
                           "Pedido de reembolso: [script]\n\n" if "reclamações" in tipo_at.lower() else "")
                        + "💡 TOM IDEAL:\n[Como manter um atendimento humanizado mesmo sendo automático]"
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Atendimento", produto_at, res)
                    st.session_state['at_temp'] = res
                    st.markdown(f"<div class='card-teal'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('at_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar (.txt)", data=st.session_state['at_temp'], file_name="atendimento_automatico.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_at", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Atendimento','produto':produto_at if 'produto_at' in dir() else '','conteudo':st.session_state['at_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # MARKETPLACE
    # ========================
    elif st.session_state.pagina == "Marketplace":
        st.header("🛍️ Marketplace Expert")
        st.markdown("Estratégias para dominar Mercado Livre, Shopee, Amazon e Magalu.")

        col1, col2 = st.columns(2)
        with col1:
            produto_mk = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, key="text_input___Produto__L1207")
            marketplace= st.selectbox("🛍️ Marketplace:", ["Mercado Livre","Shopee","Amazon Brasil","Magalu Marketplace","Facebook Marketplace"], key="selectbox____Marketplace__L1208")
            preco_mk   = st.number_input("💰 Preço (R$):", min_value=0.0, value=float(st.session_state.preco_venda), step=0.5, key="number_input___Pre_o__R____L1209")
        with col2:
            concorrentes_mk = st.text_input("🏆 Concorrentes no marketplace:", placeholder="ex: marcas que já vendem bem isso lá...", key="text_input___Concorrentes_no_marketp_L1211")
            objetivo_mk= st.selectbox("🎯 Objetivo:", ["Entrar no marketplace","Aumentar vendas","Melhorar posicionamento","Virar top seller"], key="selectbox___Objetivo__L1212")

        if st.button("🛍️ GERAR ESTRATÉGIA DE MARKETPLACE"):
            if produto_mk.strip():
                with st.spinner(f"Criando estratégia para {marketplace}..."):
                    prompt = (
                        f"Crie uma estratégia completa para vender no {marketplace}.\n"
                        f"Produto: {produto_mk}. Preço: R${preco_mk}.\n"
                        f"Concorrentes: {concorrentes_mk or 'não informado'}. Objetivo: {objetivo_mk}.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"🛍️ ESTRATÉGIA {marketplace.upper()} — {produto_mk.upper()}\n\n"
                        f"🔍 ANÁLISE DO MERCADO:\n"
                        f"• Nível de concorrência no {marketplace}: [Alto/Médio/Baixo]\n"
                        f"• Volume de busca estimado: [X buscas/mês]\n"
                        f"• Preço médio dos concorrentes: R$[X]\n"
                        f"• Seu posicionamento de preço: [competitivo/caro/barato]\n\n"
                        f"🏷️ TÍTULO CAMPEÃO (otimizado para SEO):\n"
                        f"[Título com as palavras-chave mais buscadas — máx 80 caracteres]\n\n"
                        f"🔑 PALAVRAS-CHAVE ESTRATÉGICAS:\n"
                        f"[As 15 palavras-chave que mais convertem para esse produto]\n\n"
                        f"📝 DESCRIÇÃO DO ANÚNCIO:\n"
                        f"[Descrição persuasiva e SEO-otimizada]\n\n"
                        f"📸 ESTRATÉGIA DE FOTOS:\n"
                        f"• Foto 1 (capa): [o que mostrar]\n"
                        f"• Foto 2-7: [sequência ideal]\n"
                        f"• Foto do verso/embalagem: [dica]\n\n"
                        f"⭐ COMO CONSEGUIR AS PRIMEIRAS AVALIAÇÕES:\n"
                        f"[Estratégia ética para acumular reviews]\n\n"
                        f"💰 ESTRATÉGIA DE PREÇO:\n"
                        f"[Como precificar para aparecer nas buscas e ainda ter margem]\n\n"
                        f"📦 FRETE E LOGÍSTICA:\n"
                        f"[Como usar o frete a seu favor para vender mais]\n\n"
                        f"📈 COMO VIRAR TOP SELLER:\n"
                        f"[Plano de 90 dias para escalar no {marketplace}]"
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Marketplace", produto_mk, res)
                    st.session_state['mk_temp'] = res
                    st.markdown(f"<div class='card-blue'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('mk_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar estratégia (.txt)", data=st.session_state['mk_temp'], file_name=f"marketplace_{marketplace if 'marketplace' in dir() else ''}.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_mk", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Marketplace','produto':produto_mk if 'produto_mk' in dir() else '','conteudo':st.session_state['mk_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # LOJA VIRTUAL
    # ========================
    elif st.session_state.pagina == "Loja":
        st.header("🌐 Loja Virtual Expert")
        st.markdown("Otimização completa da sua loja — do produto ao checkout.")

        col1, col2 = st.columns(2)
        with col1:
            produto_lv = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, key="text_input___Produto__L1272")
            plataforma_lv = st.selectbox("🌐 Plataforma:", ["Shopify","Nuvemshop","WooCommerce","Loja Integrada","Hotmart (físico)","Criar do zero"], key="selectbox___Plataforma__L1273")
        with col2:
            problema_lv= st.text_area("⚠️ Qual problema da sua loja:", height=80,
                placeholder="ex: muita visita e pouca venda, taxa de abandono alta, conversão baixa...", key="widget_multi_10")

        if st.button("🌐 GERAR ESTRATÉGIA DE LOJA"):
            if produto_lv.strip():
                with st.spinner("Otimizando sua loja..."):
                    prompt = (
                        f"Crie uma estratégia completa de loja virtual para produto físico.\n"
                        f"Produto: {produto_lv}. Plataforma: {plataforma_lv}.\n"
                        f"Problema atual: {problema_lv or 'otimização geral'}.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"🌐 ESTRATÉGIA DE LOJA — {produto_lv.upper()}\n"
                        f"Plataforma: {plataforma_lv}\n\n"
                        f"🏠 PÁGINA INICIAL:\n[O que deve ter acima da dobra — 5 elementos essenciais]\n\n"
                        f"📦 PÁGINA DO PRODUTO:\n"
                        f"• Título: [como escrever]\n"
                        f"• Fotos: [quantas e quais ângulos]\n"
                        f"• Descrição: [estrutura ideal]\n"
                        f"• Prova social: [onde e como colocar]\n"
                        f"• Botão comprar: [cor, texto, posição]\n"
                        f"• Urgência/escassez: [como aplicar]\n\n"
                        f"💳 CHECKOUT:\n"
                        f"[Os 5 elementos que aumentam a conversão no checkout]\n"
                        f"[O que NUNCA colocar no checkout]\n\n"
                        f"📊 MÉTRICAS QUE IMPORTAM:\n"
                        f"• Taxa de conversão ideal para esse nicho: [X%]\n"
                        f"• Taxa de abandono aceitável: [X%]\n"
                        f"• Como calcular o LTV do cliente\n\n"
                        f"🔧 CORREÇÕES PRIORITÁRIAS:\n"
                        f"[Top 5 mudanças que mais impactam a conversão — do mais fácil ao mais difícil]\n\n"
                        f"📈 COMO DOBRAR A CONVERSÃO EM 30 DIAS:\n"
                        f"[Plano de ação específico para {plataforma_lv}]"
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Loja Virtual", produto_lv, res)
                    st.session_state['lv_temp'] = res
                    st.markdown(f"<div class='card-purple'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('lv_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar (.txt)", data=st.session_state['lv_temp'], file_name="loja_virtual.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_lv", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Loja Virtual','produto':produto_lv if 'produto_lv' in dir() else '','conteudo':st.session_state['lv_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # TRÁFEGO PAGO
    # ========================
    elif st.session_state.pagina == "Trafego":
        st.header("📢 Tráfego Pago")
        st.markdown("Estratégia completa de anúncios — do orçamento inicial à escala.")

        col1, col2 = st.columns(2)
        with col1:
            produto_tp = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, key="text_input___Produto__L1333")
            orcamento_tp = st.number_input("💰 Orçamento disponível (R$/mês):", min_value=100, max_value=100000, value=500, step=100, key="number_input___Or_amento_dispon_vel__R_L1334")
            plataformas_tp = st.multiselect("📢 Plataformas:", ["Meta Ads","Google Ads","TikTok Ads"], default=["Meta Ads"], key="multiselect___Plataformas__L1335")
        with col2:
            experiencia_tp = st.selectbox("📊 Experiência com tráfego:", ["Nunca anunciei","Já anunciei mas não converti","Anuncio mas quero escalar"], key="selectbox___Experi_ncia_com_tr_fego_L1337")
            objetivo_tp    = st.selectbox("🎯 Objetivo:", ["Vendas diretas","Leads para WhatsApp","Tráfego para marketplace","Reconhecimento de marca"], key="selectbox___Objetivo__L1338")
            preco_tp       = st.number_input("💰 Preço do produto (R$):", min_value=0.0, value=float(st.session_state.preco_venda), step=0.5, key="number_input___Pre_o_do_produto__R____L1339")

        if st.button("📢 GERAR ESTRATÉGIA DE TRÁFEGO"):
            if produto_tp.strip():
                with st.spinner("Montando sua estratégia de anúncios..."):
                    plats = ", ".join(plataformas_tp) if plataformas_tp else "Meta Ads"
                    prompt = (
                        f"Crie uma estratégia completa de tráfego pago para produto físico.\n"
                        f"Produto: {produto_tp}. Preço: R${preco_tp}. Orçamento: R${orcamento_tp}/mês.\n"
                        f"Plataformas: {plats}. Experiência: {experiencia_tp}. Objetivo: {objetivo_tp}.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"📢 ESTRATÉGIA DE TRÁFEGO — {produto_tp.upper()}\n"
                        f"Orçamento: R${orcamento_tp}/mês | Plataformas: {plats}\n\n"
                        f"📊 ANÁLISE DE VIABILIDADE:\n"
                        f"• CPA máximo tolerável: R$[X] (para ter lucro com preço de R${preco_tp})\n"
                        f"• ROAS mínimo necessário: [X]x\n"
                        f"• Vendas necessárias para empatar: [X]/mês\n\n"
                        f"🎯 ESTRUTURA DE CAMPANHA:\n"
                        f"Fase 1 — Validação (R${round(orcamento_tp*0.3)}/mês):\n[O que testar primeiro]\n\n"
                        f"Fase 2 — Otimização (R${round(orcamento_tp*0.4)}/mês):\n[O que fazer após validar]\n\n"
                        f"Fase 3 — Escala (R${round(orcamento_tp*0.3)}/mês):\n[Como escalar o que funciona]\n\n"
                        f"👥 PÚBLICOS ESTRATÉGICOS:\n"
                        f"• Público frio 1: [configuração detalhada]\n"
                        f"• Público frio 2: [configuração detalhada]\n"
                        f"• Lookalike: [como criar]\n"
                        f"• Remarketing: [quem e com qual criativo]\n\n"
                        f"🎥 CRIATIVOS QUE CONVERTEM:\n"
                        f"[Os tipos de criativo que mais funcionam para esse produto/nicho]\n\n"
                        f"📊 COMO ANALISAR OS RESULTADOS:\n"
                        f"[As métricas que importam — o que olhar, o que ignorar]\n\n"
                        f"🚨 SINAIS DE ALERTA:\n"
                        f"[Quando pausar o anúncio e quando escalar]\n\n"
                        f"💡 ERRO MAIS COMUM EM TRÁFEGO PARA ESSE NICHO:\n"
                        f"[O que a maioria faz errado e como evitar]"
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Tráfego Pago", produto_tp, res)
                    st.session_state['tp_temp'] = res
                    st.markdown(f"<div class='card-red'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('tp_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar estratégia (.txt)", data=st.session_state['tp_temp'], file_name="trafego_pago.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_tp", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Tráfego Pago','produto':produto_tp if 'produto_tp' in dir() else '','conteudo':st.session_state['tp_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # VENDAS LOCAIS
    # ========================
    elif st.session_state.pagina == "Local":
        st.header("📍 Vendas Locais")
        st.markdown("Estratégias para dominar seu bairro, cidade e região.")

        col1, col2 = st.columns(2)
        with col1:
            produto_loc = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, key="text_input___Produto__L1399")
            cidade_loc  = st.text_input("📍 Sua cidade/bairro:", placeholder="ex: Fortaleza - CE, Lapa - SP...", key="text_input___Sua_cidade_bairro__L1400")
        with col2:
            canais_loc  = st.multiselect("📲 Canais locais:", [
                "WhatsApp e grupos locais","Google Meu Negócio","Facebook Marketplace",
                "Delivery (iFood/Rappi)","Panfletagem e offline","Parcerias com comércios",
                "Instagram com geolocalização",
            ], default=["WhatsApp e grupos locais","Google Meu Negócio"], key="widget_multi_11")

        if st.button("📍 GERAR ESTRATÉGIA LOCAL"):
            if produto_loc.strip():
                with st.spinner("Criando estratégia para sua região..."):
                    canais = ", ".join(canais_loc) if canais_loc else "WhatsApp"
                    prompt = (
                        f"Crie uma estratégia completa de vendas locais.\n"
                        f"Produto: {produto_loc}. Cidade/bairro: {cidade_loc}.\n"
                        f"Canais: {canais}.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"📍 ESTRATÉGIA LOCAL — {produto_loc.upper()}\n"
                        f"Região: {cidade_loc} | Canais: {canais}\n\n"
                        f"🗺️ MAPEAMENTO DO TERRITÓRIO:\n"
                        f"[Como identificar os melhores pontos de venda e distribuição na região]\n\n"
                        + ("📱 ESTRATÉGIA DE WHATSAPP LOCAL:\n"
                           "• Como encontrar grupos da região\n"
                           "• Script para entrar nos grupos sem parecer spam\n"
                           "• Catálogo digital — como montar\n"
                           "• Status do WhatsApp — estratégia\n\n" if "WhatsApp" in canais else "")
                        + ("🗺️ GOOGLE MEU NEGÓCIO:\n"
                           "• Como configurar a ficha completa\n"
                           "• Como aparecer nas buscas locais\n"
                           "• Estratégia de avaliações\n\n" if "Google" in canais else "")
                        + ("🛵 ESTRATÉGIA DE DELIVERY:\n"
                           "• Como cadastrar e precificar para o delivery\n"
                           "• Raio ideal de entrega\n"
                           "• Como se destacar na plataforma\n\n" if "Delivery" in canais else "")
                        + ("🤝 PARCERIAS LOCAIS:\n"
                           "• Que tipos de estabelecimentos abordar\n"
                           "• Script de abordagem para parceiros\n"
                           "• Modelo de comissão/consignação\n\n" if "Parcerias" in canais else "")
                        + f"📊 PROJEÇÃO DE CRESCIMENTO LOCAL:\n"
                        f"Mês 1: [foco e meta]\n"
                        f"Mês 2-3: [expansão]\n"
                        f"Mês 4-6: [consolidação]\n\n"
                        f"💡 VANTAGEM COMPETITIVA LOCAL:\n"
                        f"[O que você pode fazer localmente que nenhum grande concorrente online faz]"
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Vendas Locais", produto_loc, res)
                    st.session_state['loc_temp'] = res
                    st.markdown(f"<div class='card-green'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('loc_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar (.txt)", data=st.session_state['loc_temp'], file_name="vendas_locais.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_loc", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Vendas Locais','produto':produto_loc if 'produto_loc' in dir() else '','conteudo':st.session_state['loc_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # ESCALA
    # ========================
    elif st.session_state.pagina == "Escala":
        st.header("📈 Escala do Negócio")
        st.markdown("Como ir de vendas manuais para um negócio que funciona sozinho.")

        col1, col2 = st.columns(2)
        with col1:
            produto_es = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, key="text_input___Produto__L1470")
            fat_atual  = st.text_input("💰 Faturamento atual:", placeholder="ex: R$3.000/mês, R$15.000/mês...", key="text_input___Faturamento_atual__L1471")
            meta_es    = st.text_input("🎯 Meta de faturamento:", placeholder="ex: R$30.000/mês, R$100.000/mês...", key="text_input___Meta_de_faturamento__L1472")
        with col2:
            gargalo_es = st.text_area("🔧 Maior gargalo hoje:", height=80,
                placeholder="ex: não consigo atender tudo sozinho, não tenho capital para estoque, demoro muito para produzir...", key="widget_multi_12")

        if st.button("📈 GERAR PLANO DE ESCALA"):
            if produto_es.strip():
                with st.spinner("Montando seu plano de escala..."):
                    prompt = (
                        f"Crie um plano completo de escala para negócio de produto físico.\n"
                        f"Produto: {produto_es}. Faturamento atual: {fat_atual}. Meta: {meta_es}.\n"
                        f"Gargalo principal: {gargalo_es or 'não informado'}.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"📈 PLANO DE ESCALA — {produto_es.upper()}\n"
                        f"De {fat_atual} para {meta_es}\n\n"
                        f"🔍 DIAGNÓSTICO DO GARGALO:\n"
                        f"[Análise do que está travando o crescimento e como resolver]\n\n"
                        f"📋 OS 4 PILARES DA ESCALA:\n\n"
                        f"PILAR 1 — TICKET MÉDIO:\n[Como aumentar o valor médio por pedido]\n\n"
                        f"PILAR 2 — VOLUME DE VENDAS:\n[Como vender mais sem trabalhar mais horas]\n\n"
                        f"PILAR 3 — RECORRÊNCIA:\n[Como criar clientes que compram todo mês]\n\n"
                        f"PILAR 4 — AUTOMAÇÃO:\n[O que automatizar primeiro para ter mais tempo]\n\n"
                        f"👥 QUANDO E COMO CONTRATAR:\n"
                        f"• Primeira contratação (quando e quem)\n"
                        f"• Como treinar e padronizar processos\n"
                        f"• Como pagar (CLT, PJ, comissão)\n\n"
                        f"📦 EXPANSÃO DO CATÁLOGO:\n[Como adicionar produtos sem perder foco]\n\n"
                        f"📅 PLANO DE 6 MESES:\n"
                        f"Mês 1-2: [foco e meta]\n"
                        f"Mês 3-4: [foco e meta]\n"
                        f"Mês 5-6: [foco e meta]\n\n"
                        f"⚠️ ERROS QUE MATAM O CRESCIMENTO:\n"
                        f"[Os 5 erros mais comuns na fase de escala — como evitar]"
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Escala", produto_es, res)
                    st.session_state['esc_temp'] = res
                    st.markdown(f"<div class='card-dark'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('esc_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar plano (.txt)", data=st.session_state['esc_temp'], file_name="plano_escala.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_esc", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Escala','produto':produto_es if 'produto_es' in dir() else '','conteudo':st.session_state['esc_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # VALIDAÇÃO
    # ========================
    elif st.session_state.pagina == "Validacao":
        st.header("🧪 Validação de Produto")
        st.markdown("Antes de investir — vale a pena mesmo vender isso?")

        col1, col2 = st.columns(2)
        with col1:
            produto_val = st.text_input("📦 Produto que quer validar:", placeholder="ex: soro capilar para liso, nécessaire personalizada...", key="text_input___Produto_que_quer_valida_L1531")
            custo_val   = st.number_input("💸 Custo estimado (R$):", min_value=0.0, value=0.0, step=0.5, key="number_input___Custo_estimado__R____L1532")
            preco_val   = st.number_input("💰 Preço que pensa em cobrar (R$):", min_value=0.0, value=0.0, step=0.5, key="number_input___Pre_o_que_pensa_em_cobr_L1533")
        with col2:
            mercado_val = st.text_area("🤔 Por que você quer vender isso:", height=80,
                placeholder="ex: vi muita gente pedindo, está na tendência, minha amiga vende bem...", key="widget_multi_13")
            capital_val = st.text_input("💰 Capital para investir:", placeholder="ex: R$500, R$2.000...", key="text_input___Capital_para_investir__L1537")

        if st.button("🧪 VALIDAR MEU PRODUTO"):
            if produto_val.strip():
                with st.spinner("Analisando o potencial do produto..."):
                    margem_val = round((preco_val-custo_val)/preco_val*100,1) if preco_val > 0 else 0
                    prompt = (
                        f"Faça uma análise completa de validação de produto físico.\n"
                        f"Produto: {produto_val}. Custo: R${custo_val}. Preço pretendido: R${preco_val}.\n"
                        f"Margem: {margem_val}%. Capital: {capital_val}. Motivo: {mercado_val}.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"🧪 VALIDAÇÃO — {produto_val.upper()}\n\n"
                        f"📊 VEREDITO GERAL:\n"
                        f"[✅ VALE A PENA / ⚠️ VALE COM AJUSTES / 🚨 EVITE POR ENQUANTO]\n"
                        f"Nota geral: [X]/10\n\n"
                        f"🔍 ANÁLISE DE MERCADO:\n"
                        f"• Saturação: [Alta/Média/Baixa] — explicação\n"
                        f"• Demanda: [Alta/Média/Baixa] — evidências\n"
                        f"• Tendência: [Crescendo/Estável/Caindo]\n"
                        f"• É moda passageira ou nicho permanente? [análise]\n\n"
                        f"💰 ANÁLISE FINANCEIRA:\n"
                        f"• Margem atual ({margem_val}%): {'✅ saudável' if margem_val >= 40 else '⚠️ apertada' if margem_val >= 20 else '🚨 perigosa'}\n"
                        f"• Preço ideal sugerido: R$[X]\n"
                        f"• Investimento mínimo para começar: R$[X]\n"
                        f"• Tempo para recuperar investimento: [X meses]\n\n"
                        f"🏆 NÍVEL DE CONCORRÊNCIA:\n[Análise de quem já vende e como você pode se diferenciar]\n\n"
                        f"✅ PONTOS FAVORÁVEIS:\n[Por que esse produto pode dar certo]\n\n"
                        f"⚠️ RISCOS E ALERTAS:\n[Por que pode dar errado — seja honesto]\n\n"
                        f"🚀 COMO VALIDAR SEM RISCO:\n"
                        f"[Método de validação com o capital disponível — antes de comprar estoque grande]\n\n"
                        f"💡 ALTERNATIVAS SIMILARES:\n"
                        f"[Se esse não for ideal, 2-3 produtos do mesmo nicho com mais potencial]"
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Validação", produto_val, res)
                    st.session_state['val_temp'] = res
                    st.markdown(f"<div class='card'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('val_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar validação (.txt)", data=st.session_state['val_temp'], file_name="validacao_produto.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_val", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Validação','produto':produto_val if 'produto_val' in dir() else '','conteudo':st.session_state['val_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # AUDITORIA
    # ========================
    elif st.session_state.pagina == "Auditoria":
        st.header("📊 Auditoria Completa")
        st.markdown("Por que não estou vendendo? A IA encontra o gargalo.")

        col1, col2 = st.columns(2)
        with col1:
            produto_au = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, key="text_input___Produto__L1595")
            preco_au   = st.number_input("💰 Preço (R$):", min_value=0.0, value=float(st.session_state.preco_venda), step=0.5, key="number_input___Pre_o__R____L1596")
            visitas_au = st.text_input("👁️ Visitas/visualizações por dia:", placeholder="ex: 50 visitas na loja, 200 visualizações no story...", key="text_input____Visitas_visualiza__es__L1597")
            vendas_au  = st.text_input("💸 Vendas por semana:", placeholder="ex: 2 vendas, 10 vendas, quase nenhuma...", key="text_input___Vendas_por_semana__L1598")
        with col2:
            canal_au   = st.text_input("📲 Canal de venda:", value=st.session_state.canal_padrao, key="text_input___Canal_de_venda__L1600")
            copy_au    = st.text_area("✍️ Sua descrição/copy atual (cole aqui):", height=80, placeholder="Cole o texto que você usa para vender...", key="text_area____Sua_descri__o_copy_atu_L1601")
            estrategia = st.text_area("📋 O que você já tentou fazer:", height=60, placeholder="ex: já postei no Instagram, rodei anúncio, abaixei o preço...", key="text_area___O_que_voc__j__tentou_fa_L1602")

        if st.button("📊 AUDITAR MEU NEGÓCIO"):
            if produto_au.strip():
                with st.spinner("Auditando seu negócio..."):
                    prompt = (
                        f"Faça uma auditoria completa de vendas de produto físico.\n"
                        f"Produto: {produto_au}. Preço: R${preco_au}. Canal: {canal_au}.\n"
                        f"Visitas/dia: {visitas_au}. Vendas/semana: {vendas_au}.\n"
                        f"Copy atual: {copy_au or 'não informado'}.\n"
                        f"O que já tentou: {estrategia or 'não informado'}.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"📊 AUDITORIA COMPLETA — {produto_au.upper()}\n\n"
                        f"🎯 DIAGNÓSTICO RÁPIDO:\n"
                        f"O gargalo principal está em: [PRODUTO/OFERTA/TRÁFEGO/COPY/ATENDIMENTO/PREÇO]\n\n"
                        f"📊 ANÁLISE DE CONVERSÃO:\n"
                        f"• Taxa de conversão atual: [X%] — ideal seria [X%]\n"
                        f"• O que essa taxa indica: [análise]\n\n"
                        f"🔍 ANÁLISE POR ÁREA:\n\n"
                        f"📦 PRODUTO: [nota X/10 — o que está certo e errado]\n"
                        f"💰 PREÇO: [nota X/10 — está adequado?]\n"
                        f"🛒 OFERTA: [nota X/10 — é irresistível?]\n"
                        f"👁️ TRÁFEGO: [nota X/10 — está chegando ao público certo?]\n"
                        f"✍️ COPY: [nota X/10 — análise do texto fornecido]\n"
                        f"💬 ATENDIMENTO: [nota X/10 — está perdendo venda no atendimento?]\n\n"
                        f"🚨 OS 3 MAIORES PROBLEMAS:\n"
                        f"1. [Problema 1 — com solução específica]\n"
                        f"2. [Problema 2 — com solução]\n"
                        f"3. [Problema 3 — com solução]\n\n"
                        f"⚡ PLANO DE AÇÃO (próximos 7 dias):\n"
                        f"Dia 1-2: [ação imediata]\n"
                        f"Dia 3-4: [ação]\n"
                        f"Dia 5-7: [ação]\n\n"
                        f"📈 RESULTADO ESPERADO:\n"
                        f"[O que muda nas vendas se aplicar o plano — estimativa realista]"
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Auditoria", produto_au, res)
                    st.session_state['audit_temp'] = res
                    st.markdown(f"<div class='card-yellow'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('audit_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar auditoria (.txt)", data=st.session_state['audit_temp'], file_name="auditoria_negocios.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_audit", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Auditoria','produto':produto_au if 'produto_au' in dir() else '','conteudo':st.session_state['audit_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # ESTOQUE
    # ========================
    elif st.session_state.pagina == "Estoque":
        st.header("📦 Gestão de Estoque")
        st.markdown("Giro, produto parado, previsão de compra e organização simples.")

        col1, col2 = st.columns(2)
        with col1:
            produto_est = st.text_input("📦 Produto:", value=st.session_state.produto_padrao, key="text_input___Produto__L1663")
            qtd_estoque = st.number_input("📦 Quantidade em estoque:", min_value=0, value=50, step=5, key="number_input___Quantidade_em_estoque__L1664")
            vendas_mes  = st.number_input("💸 Vendas médias por mês:", min_value=0, value=20, step=5, key="number_input___Vendas_m_dias_por_m_s__L1665")
        with col2:
            custo_est   = st.number_input("💸 Custo por unidade (R$):", min_value=0.0, value=float(st.session_state.preco_custo), step=0.5, key="number_input___Custo_por_unidade__R____L1667")
            prazo_forn  = st.number_input("🚚 Prazo do fornecedor (dias):", min_value=1, value=15, step=1, key="number_input___Prazo_do_fornecedor__di_L1668")
            problema_est= st.text_input("⚠️ Problema atual:", placeholder="ex: muito estoque parado, sempre falta produto, não sei quando comprar...", key="text_input____Problema_atual__L1669")

        if st.button("📦 GERAR PLANO DE GESTÃO DE ESTOQUE"):
            if produto_est.strip():
                with st.spinner("Analisando seu estoque..."):
                    giro = round(vendas_mes / qtd_estoque * 30, 0) if qtd_estoque > 0 else 0
                    dias_estoque = round(qtd_estoque / vendas_mes * 30, 0) if vendas_mes > 0 else 0
                    prompt = (
                        f"Crie um plano de gestão de estoque para produto físico.\n"
                        f"Produto: {produto_est}. Estoque atual: {qtd_estoque} unidades.\n"
                        f"Vendas/mês: {vendas_mes}. Custo unit: R${custo_est}.\n"
                        f"Prazo fornecedor: {prazo_forn} dias. Problema: {problema_est or 'organização geral'}.\n\n"
                        f"DADOS CALCULADOS:\n"
                        f"• Dias de estoque: {dias_estoque} dias\n"
                        f"• Capital imobilizado: R${qtd_estoque * custo_est:,.0f}\n\n"
                        f"ESTRUTURA:\n\n"
                        f"📦 GESTÃO DE ESTOQUE — {produto_est.upper()}\n\n"
                        f"📊 DIAGNÓSTICO ATUAL:\n"
                        f"• Dias de estoque ({dias_estoque} dias): {'✅ saudável' if 30 <= dias_estoque <= 60 else '⚠️ atenção' if dias_estoque < 30 else '🚨 estoque alto'}\n"
                        f"• Capital imobilizado: R${qtd_estoque * custo_est:,.0f}\n"
                        f"• Giro de estoque: [análise]\n\n"
                        f"📅 PONTO DE PEDIDO:\n"
                        f"• Você deve pedir quando tiver [X] unidades\n"
                        f"• Quantidade ideal por pedido: [X] unidades\n"
                        f"• Por quê: [explicação com base no prazo do fornecedor]\n\n"
                        f"{'🚨 ESTRATÉGIA PARA PRODUTO PARADO:\n[Como girar estoque sem derrubar margem]\n\n' if 'parado' in problema_est.lower() else ''}"
                        f"📱 COMO CONTROLAR SEM SISTEMA:\n"
                        f"[Planilha simples ou app gratuito para controlar estoque no celular]\n\n"
                        f"💰 COMO NEGOCIAR COM FORNECEDOR:\n"
                        f"[Estratégia para pagar menos e ter prazo maior]\n\n"
                        f"📈 PREVISÃO DE COMPRA (próximos 3 meses):\n"
                        f"[Quanto comprar por mês considerando sazonalidade]"
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Estoque", produto_est, res)
                    st.session_state['est_temp'] = res
                    st.markdown(f"<div class='card-blue'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('est_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar (.txt)", data=st.session_state['est_temp'], file_name="gestao_estoque.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_est", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Estoque','produto':produto_est if 'produto_est' in dir() else '','conteudo':st.session_state['est_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # BRANDING
    # ========================
    elif st.session_state.pagina == "Branding":
        st.header("💎 Branding e Identidade de Marca")
        st.markdown("Nome, slogan, posicionamento e comunicação que criam fãs — não só compradores.")

        col1, col2 = st.columns(2)
        with col1:
            produto_br2 = st.text_input("📦 Produto/linha de produtos:", value=st.session_state.produto_padrao, key="text_input___Produto_linha_de_produt_L1727")
            nicho_br2   = st.text_input("🎯 Nicho:", value=st.session_state.nicho_padrao, key="text_input___Nicho__L1728")
            publico_br2 = st.text_input("👤 Público-alvo:", placeholder="ex: mulheres empreendedoras 28-45 anos...", key="text_input___P_blico_alvo__L1729")
        with col2:
            tem_nome    = st.text_input("🏷️ Nome atual (se tiver):", placeholder="ex: Beleza Natural, Produtos do João...", key="text_input____Nome_atual__se_tiver___L1731")
            posiciona   = st.selectbox("🎯 Posicionamento desejado:", [
                "Premium/exclusivo","Popular/acessível","Natural/sustentável",
                "Científico/técnico","Emocional/lifestyle","Local/artesanal",
            ], key="widget_multi_14")
            valores     = st.text_input("💎 Valores da marca:", placeholder="ex: autenticidade, sustentabilidade, resultado...", key="text_input___Valores_da_marca__L1736")

        if st.button("💎 CRIAR IDENTIDADE DE MARCA"):
            if produto_br2.strip():
                with st.spinner("Criando sua marca..."):
                    prompt = (
                        f"Crie uma identidade de marca completa para produto físico.\n"
                        f"Produto: {produto_br2}. Nicho: {nicho_br2}. Público: {publico_br2}.\n"
                        f"Nome atual: {tem_nome or 'ainda não tem'}. Posicionamento: {posiciona}.\n"
                        f"Valores: {valores or 'não definidos'}.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"💎 IDENTIDADE DE MARCA — {produto_br2.upper()}\n\n"
                        f"🏷️ OPÇÕES DE NOME:\n"
                        f"Nome 1: [nome] — significado e por que funciona\n"
                        f"Nome 2: [nome] — significado e por que funciona\n"
                        f"Nome 3: [nome] — significado e por que funciona\n"
                        f"Nome 4: [nome] — significado e por que funciona\n"
                        f"Nome 5: [nome] — significado e por que funciona\n\n"
                        f"🎯 SLOGAN (3 opções):\n"
                        f"[Slogan 1]\n[Slogan 2]\n[Slogan 3]\n\n"
                        f"📍 DECLARAÇÃO DE POSICIONAMENTO:\n"
                        f"[Frase completa: Para [público], a [marca] é a [categoria] que [benefício único] porque [razão para acreditar]]\n\n"
                        f"🗣️ TOM DE VOZ DA MARCA:\n"
                        f"• Como a marca fala: [adjetivos]\n"
                        f"• Como a marca NÃO fala: [o que evitar]\n"
                        f"• Exemplo de post com tom certo: [exemplo]\n"
                        f"• Exemplo de post com tom errado: [contra-exemplo]\n\n"
                        f"🎨 IDENTIDADE VISUAL (direcionamento):\n"
                        f"• Paleta de cores sugerida: [cores + sensação que transmitem]\n"
                        f"• Estilo de foto: [como devem ser as fotos dos produtos]\n"
                        f"• Fontes que combinam: [tipo de fonte]\n\n"
                        f"💡 COMO SE DIFERENCIAR DOS CONCORRENTES:\n"
                        f"[O que fazer para ser lembrado e inimitável no nicho {nicho_br2}]"
                    )
                    res = vendas_ia(prompt)
                    salvar_analise("Branding", produto_br2, res)
                    st.session_state['brand_temp'] = res
                    st.markdown(f"<div class='card-purple'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o produto.")

        if st.session_state.get('brand_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar identidade (.txt)", data=st.session_state['brand_temp'], file_name="identidade_marca.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("💾 Salvar", key="sv_brand", use_container_width=True):
                    st.session_state.materiais_salvos.append({'tipo':'Branding','produto':produto_br2 if 'produto_br2' in dir() else '','conteudo':st.session_state['brand_temp'],'data':datetime.now().strftime('%d/%m %H:%M')})
                    st.success("✅ Salvo!")

    # ========================
    # MENTOR 24H
    # ========================
    elif st.session_state.pagina == "Mentor":
        st.header("🧠 Mentor Estratégico 24h")
        st.markdown("Fale com seu consultor de vendas — direto, sem enrolação, sem teoria.")

        st.markdown("""<div style="background:#FFF8F0;border:1px solid #F97316;border-radius:12px;
        padding:12px 16px;margin-bottom:16px;font-size:0.86em;color:#1A1A2E;">
        💡 <strong>Exemplos de perguntas:</strong> "Estou sem vendas há 5 dias, o que faço?" · 
        "Tenho R$300, como começo?" · "Meu anúncio parou de converter" · 
        "Qual produto me indica para começar?" · "Como precificar para o Mercado Livre?"
        </div>""", unsafe_allow_html=True)

        # Histórico do chat
        if st.session_state.chat_mentor:
            for msg in st.session_state.chat_mentor:
                if msg['role'] == 'user':
                    st.markdown(f"<div style='background:#FFF8F0;border:1px solid #F97316;border-radius:12px 12px 4px 12px;padding:12px 16px;margin:8px 0;'><b>Você:</b> {msg['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='card' style='margin:8px 0;'><b>🧠 Mentor:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown("""<div style="background:#FFF8F0;border:1px solid #F97316;border-radius:12px;padding:20px;text-align:center;">
            🧠 <strong>Olá! Sou seu Mentor de Vendas.</strong><br>
            Me conta o que está acontecendo no seu negócio — vou ser direto com você.
            </div>""", unsafe_allow_html=True)

        # Sugestões rápidas
        st.markdown("<br>**⚡ Situações comuns — clique para consultar:**", unsafe_allow_html=True)
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        sugestoes_m = [
            "Estou sem vendas, o que faço?",
            f"Tenho R$300 para investir em {st.session_state.produto_padrao or 'meu produto'}, como começar?",
            "Por que meu anúncio parou de converter?",
            "Como aumentar meu ticket médio?",
        ]
        for idx, (col, sug) in enumerate(zip([col_s1,col_s2,col_s3,col_s4], sugestoes_m)):
            if col.button(f"→ {sug[:30]}...", key=f"sug_m_{idx}"):
                with st.spinner("Mentor respondendo..."):
                    resp = vendas_ia(sug, "Você é um mentor direto e prático. Responda como um consultor experiente — sem enrolação. Máx 5 parágrafos.")
                st.session_state.chat_mentor.append({"role": "user", "content": sug})
                st.session_state.chat_mentor.append({"role": "assistant", "content": resp})
                salvar_analise("Mentor", sug[:40], resp)
                st.rerun()

        # Input
        pergunta_m = st.text_input("💬 Sua situação ou dúvida:", key=f"mentor_input_{st.session_state.chat_key}",
            placeholder="ex: Estou sem vendas há 3 dias, já tentei postar no story mas não adianta...")

        col_env, col_limpar = st.columns([3, 1])
        with col_env:
            if st.button("📤 CONSULTAR MENTOR"):
                if pergunta_m.strip():
                    with st.spinner("Mentor analisando sua situação..."):
                        historico_msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_mentor[-10:]]
                        resp = vendas_ia(
                            pergunta_m,
                            "Você é um mentor de vendas físicas extremamente experiente e direto. Responda como consultor — diagnóstico + solução prática. Sem teoria, sem enrolação. Máx 5 parágrafos."
                        )
                    st.session_state.chat_mentor.append({"role": "user", "content": pergunta_m})
                    st.session_state.chat_mentor.append({"role": "assistant", "content": resp})
                    st.session_state.chat_key += 1
                    salvar_analise("Mentor", pergunta_m[:40], resp)
                    st.rerun()
                else:
                    st.warning("Digite sua dúvida ou situação.")
        with col_limpar:
            if st.button("🗑️ Limpar"):
                st.session_state.chat_mentor = []
                st.rerun()

    # ========================
    # MATERIAIS SALVOS (acessível no progresso)
    # ========================
    if st.session_state.pagina not in [
        "Home","Diagnostico","ModeloVenda","Oferta","Precificacao","Avatar",
        "Copy","Conteudo","Criativos","Fechamento","Atendimento","Marketplace",
        "Loja","Trafego","Local","Escala","Validacao","Auditoria","Estoque","Branding","Mentor"
    ]:
        st.info("Selecione um módulo acima.")

    # RODAPÉ COM ESTATÍSTICAS
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    tipos_count = {}
    for a in st.session_state.historico_analises:
        tipos_count[a['tipo']] = tipos_count.get(a['tipo'], 0) + 1

    if st.session_state.materiais_salvos:
        with st.expander(f"📚 Materiais Salvos ({len(st.session_state.materiais_salvos)}) — clique para ver"):
            filtro_s = st.selectbox("Filtrar:", ["Todos"] + list(set(m['tipo'] for m in st.session_state.materiais_salvos)), key="filtro_salvos")
            for i, item in enumerate(reversed(st.session_state.materiais_salvos)):
                if filtro_s != "Todos" and item['tipo'] != filtro_s:
                    continue
                idx_real = len(st.session_state.materiais_salvos) - 1 - i
                with st.expander(f"[{item['tipo']}] {item['produto']} — {item['data']}", expanded=False):
                    st.markdown(f"<div class='card'>{item['conteudo']}</div>", unsafe_allow_html=True)
                    col_dl, col_del = st.columns([3,1])
                    with col_dl:
                        st.download_button("📋 Baixar", data=item['conteudo'],
                            file_name=f"{item['tipo'].lower().replace(' ','_')}.txt",
                            mime="text/plain", key=f"dl_salvo_{i}")
                    with col_del:
                        if st.button("🗑️", key=f"del_salvo_{i}"):
                            st.session_state.materiais_salvos.pop(idx_real)
                            st.rerun()

# --- RODAPÉ ---
st.markdown(
    "<div style='text-align:center;color:#999;font-size:0.8em;margin-top:40px;'>"
    "© 2026 Mestre de Vendas Físicas IA — O canivete suíço do vendedor brasileiro · Quiz Com Prêmios"
    "</div>", unsafe_allow_html=True
)
