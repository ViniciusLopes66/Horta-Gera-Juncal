import os
import pandas as pd
import streamlit as st

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Horta Comunitária Gera Juncal",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização personalizada com CSS (Cores verdes sustentáveis, cartões e botões elegantes)
st.markdown(
    """
    <style>
    /* Estilo do título principal */
    .main-header {
        font-size: 2.2rem;
        color: #1B5E20;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1rem;
        color: #4CAF50;
        margin-bottom: 20px;
        font-weight: 500;
    }
    
    /* Cartões de métricas (KPIs) */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #2E7D32 !important;
        font-weight: bold;
    }
    div[data-testid="stMetric"] {
        background-color: #F1F8E9;
        border-radius: 10px;
        padding: 12px 16px;
        border-left: 5px solid #4CAF50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Botão de salvar */
    .stButton>button {
        background-color: #2E7D32 !important;
        color: white !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        border: none !important;
        width: 100%;
        margin-top: 15px;
    }
    .stButton>button:hover {
        background-color: #1B5E20 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

EXCEL_FILE = "Dashboard_Horta_Comunitaria_Gera_Juncal.xlsx"

# ==========================================
# CARREGAMENTO DOS DADOS DO EXCEL
# ==========================================
@st.cache_data(ttl=1)  # Recarrega se o arquivo mudar
def carregar_dados():
    if not os.path.exists(EXCEL_FILE):
        st.error(f"O arquivo '{EXCEL_FILE}' não foi encontrado no diretório!")
        st.stop()

    xls = pd.ExcelFile(EXCEL_FILE)

    # 1. Voluntários
    df_voluntarios = pd.read_excel(xls, sheet_name="Voluntarios", skiprows=1)
    df_voluntarios = df_voluntarios.dropna(how="all")

    # 2. Colheitas
    df_colheitas = pd.read_excel(xls, sheet_name="Colheitas", skiprows=1)
    df_colheitas = df_colheitas.dropna(how="all")

    # 3. Compostagem
    df_compostagem = pd.read_excel(xls, sheet_name="Compostagem", skiprows=1)
    df_compostagem = df_compostagem.dropna(how="all")

    # 4. Canteiros (Lido da aba Dashboard)
    df_dash_raw = pd.read_excel(xls, sheet_name="Dashboard", header=None)
    
    # Extrai Canteiros (Linhas 7 a 12)
    df_canteiros = df_dash_raw.iloc[7:13, 1:5].copy()
    df_canteiros.columns = [
        "Canteiro",
        "Cultura",
        "Status",
        "Previsão Colheita",
    ]
    df_canteiros = df_canteiros.iloc[1:].reset_index(drop=True)

    # Extrai Impacto Mensal Compostagem (Linhas 7 a 12, colunas F a I)
    df_impacto = df_dash_raw.iloc[7:12, 6:10].copy()
    df_impacto.columns = [
        "Mês",
        "Orgânicos Coletados (kg)",
        "Adubo Gerado (kg)",
        "Participantes",
    ]
    df_impacto = df_impacto.iloc[1:].reset_index(drop=True)

    return df_voluntarios, df_colheitas, df_compostagem, df_canteiros, df_impacto


df_voluntarios, df_colheitas, df_compostagem, df_canteiros, df_impacto = (
    carregar_dados()
)

# ==========================================
# CABEÇALHO DO APLICATIVO
# ==========================================
st.markdown(
    '<div class="main-header">🌱 Gestão Horta Comunitária Gera Juncal</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Eixo: Economia Sustentável & Tecnologia | Sistema de Sincronização em Tempo Real</div>',
    unsafe_allow_html=True,
)

# Navegação por Abas
tab_dash, tab_vol, tab_col, tab_comp = st.tabs(
    [
        "📊 Dashboard Geral",
        "👥 Voluntários",
        "🧺 Colheitas",
        "♻️ Compostagem",
    ]
)

# ==========================================
# ABA 1: DASHBOARD PRINCIPAL
# ==========================================
with tab_dash:
    # Recálculo em tempo real dos Indicadores (KPIs)
    tot_voluntarios = len(
        df_voluntarios[df_voluntarios["Status"] == "Ativo"]
    ) if "Status" in df_voluntarios.columns else len(df_voluntarios)
    
    tot_residuos = (
        pd.to_numeric(df_compostagem["Peso Entregue (kg)"], errors="coerce").sum()
        if "Peso Entregue (kg)" in df_compostagem.columns
        else 0
    )
    
    tot_colheita = (
        pd.to_numeric(df_colheitas["Qtd Colhida (kg)"], errors="coerce").sum()
        if "Qtd Colhida (kg)" in df_colheitas.columns
        else 0
    )
    
    tot_doado = (
        pd.to_numeric(
            df_colheitas["Doado p/ Comunidade (kg)"], errors="coerce"
        ).sum()
        if "Doado p/ Comunidade (kg)" in df_colheitas.columns
        else 0
    )

    # Exibição dos Cartões Indicadores
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Voluntários Ativos", f"{tot_voluntarios} pessoas")
    col2.metric("Resíduos Compostados", f"{tot_residuos:.1f} kg")
    col3.metric("Colheita Total", f"{tot_colheita:.1f} kg")
    col4.metric("Alimentos Doados", f"{tot_doado:.1f} kg")

    st.markdown("---")

    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.subheader("🌱 Status dos Canteiros e Produção")
        canteiros_editados = st.data_editor(
            df_canteiros, num_rows="dynamic", use_container_width=True, key="ed_canteiros"
        )

    with col_dir:
        st.subheader("♻️ Impacto de Compostagem (Histórico Mensal)")
        impacto_editado = st.data_editor(
            df_impacto, num_rows="dynamic", use_container_width=True, key="ed_impacto"
        )

# ==========================================
# ABA 2: GERENCIAMENTO DE VOLUNTÁRIOS
# ==========================================
with tab_vol:
    st.subheader("👥 Escala e Cadastro de Voluntários")
    st.info("Você pode adicionar novos voluntários ou editar horários e status diretamente na tabela abaixo.")
    voluntarios_editados = st.data_editor(
        df_voluntarios, num_rows="dynamic", use_container_width=True, key="ed_voluntarios"
    )

# ==========================================
# ABA 3: REGISTRO DE COLHEITAS
# ==========================================
with tab_col:
    st.subheader("🧺 Registro de Plantio e Colheitas")
    st.info("Insira os quilos colhidos, doados ou trocados/vendidos para atualizar os indicadores da horta.")
    colheitas_editadas = st.data_editor(
        df_colheitas, num_rows="dynamic", use_container_width=True, key="ed_colheitas"
    )

# ==========================================
# ABA 4: REGISTRO DE COMPOSTAGEM
# ==========================================
with tab_comp:
    st.subheader("♻️ Registro de Compostagem e Economia Circular")
    st.info("Registre os resíduos entregues pelas famílias para acompanhamento de pontos/adubo gerado.")
    compostagem_editada = st.data_editor(
        df_compostagem, num_rows="dynamic", use_container_width=True, key="ed_compostagem"
    )

# ==========================================
# BOTÃO DE SALVAMENTO NO EXCEL
# ==========================================
st.markdown("---")
if st.button("💾 SALVAR TODAS AS ALTERAÇÕES NO EXCEL"):
    try:
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            # 1. Montar a aba Dashboard idêntica à estrutura original
            dash_builder = []
            dash_builder.append(["", "DASHBOARD DE GESTÃO - HORTA COMUNITÁRIA GERA JUNCAL", "", "", "", "", "", "", "", ""])
            dash_builder.append(["", "Eixo: Economia Sustentável & Tecnologia | Indicadores Operacionais e Comunitários", "", "", "", "", "", "", "", ""])
            dash_builder.append([""] * 10)
            dash_builder.append(["", "VOLUNTÁRIOS ATIVOS", "", "RESÍDUOS COMPOSTADOS (KG)", "", "COLHEITA TOTAL (KG)", "", "ALIMENTOS DOADOS (KG)", "", ""])
            dash_builder.append(["", tot_voluntarios, "", tot_residuos, "", tot_colheita, "", tot_doado, "", ""])
            dash_builder.append([""] * 10)
            dash_builder.append(["", "🌱 Status dos Canteiros e Produção", "", "", "", "", "♻️ Impacto de Compostagem (Economia Circular)", "", "", ""])
            
            # Cabeçalhos das duas tabelas lado a lado
            dash_builder.append(["", "Canteiro", "Cultura", "Status", "Previsão Colheita", "", "Mês", "Orgânicos Coletados (kg)", "Adubo Gerado (kg)", "Participantes"])

            # Adicionar dados das duas tabelas lado a lado
            max_rows = max(len(canteiros_editados), len(impacto_editado))
            cant_list = canteiros_editados.values.tolist()
            imp_list = impacto_editado.values.tolist()

            for i in range(max_rows):
                row = [""]
                if i < len(cant_list):
                    row.extend(cant_list[i])
                else:
                    row.extend(["", "", "", ""])
                
                row.append("") # Espaçador coluna F
                
                if i < len(imp_list):
                    row.extend(imp_list[i])
                else:
                    row.extend(["", "", "", ""])
                
                dash_builder.append(row)

            df_final_dash = pd.DataFrame(dash_builder)
            df_final_dash.to_excel(writer, sheet_name="Dashboard", index=False, header=False)

            # 2. Salvar Aba Voluntários
            df_vol_header = pd.DataFrame([["CADASTRO E ESCALA DE VOLUNTÁRIOS"] + [""]*5])
            df_vol_final = pd.concat([df_vol_header, pd.DataFrame([voluntarios_editados.columns.tolist()]), voluntarios_editados], ignore_index=True)
            df_vol_final.to_excel(writer, sheet_name="Voluntarios", index=False, header=False)

            # 3. Salvar Aba Colheitas
            df_col_header = pd.DataFrame([["REGISTRO DE PLANTIO E COLHEITAS"] + [""]*5])
            df_col_final = pd.concat([df_col_header, pd.DataFrame([colheitas_editadas.columns.tolist()]), colheitas_editadas], ignore_index=True)
            df_col_final.to_excel(writer, sheet_name="Colheitas", index=False, header=False)

            # 4. Salvar Aba Compostagem
            df_comp_header = pd.DataFrame([["REGISTRO DE COMPOSTAGEM E ECONOMIA CIRCULAR"] + [""]*4])
            df_comp_final = pd.concat([df_comp_header, pd.DataFrame([compostagem_editada.columns.tolist()]), compostagem_editada], ignore_index=True)
            df_comp_final.to_excel(writer, sheet_name="Compostagem", index=False, header=False)

        st.success("✅ Arquivo Excel atualizado com sucesso! Todas as alterações foram salvas.")
        st.cache_data.clear()

    except Exception as e:
        st.error(f"Erro ao salvar o arquivo: {e}")