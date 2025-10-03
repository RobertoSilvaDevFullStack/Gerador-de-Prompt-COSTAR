import streamlit as st
import requests
import json

st.set_page_config(
    page_title="🎯 COSTAR Generator",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 COSTAR Prompt Generator")
st.markdown("Crie prompts estruturados e profissionais")

# Interface COSTAR
col1, col2 = st.columns(2)

with col1:
    context = st.text_area("📋 Context", placeholder="Descreva o contexto...")
    objective = st.text_area("🎯 Objective", placeholder="Qual o objetivo?")
    style = st.text_input("🎨 Style", placeholder="Ex: formal, casual...")

with col2:
    tone = st.text_input("🗣️ Tone", placeholder="Ex: profissional, amigável...")
    audience = st.text_input("👥 Audience", placeholder="Para quem é?")
    response = st.text_input("📝 Response", placeholder="Formato da resposta")

if st.button("✨ Gerar Prompt COSTAR", type="primary"):
    if all([context, objective, style, tone, audience, response]):
        # Gerar prompt
        prompt = f"""**PROMPT COSTAR**

**Context:** {context}

**Objective:** {objective}

**Style:** {style}

**Tone:** {tone}

**Audience:** {audience}

**Response:** {response}"""
        
        st.success("✅ Prompt gerado com sucesso!")
        st.code(prompt, language="markdown")
        
        # Botão para copiar
        st.download_button(
            "📥 Download Prompt",
            prompt,
            file_name="prompt_costar.txt",
            mime="text/plain"
        )
    else:
        st.error("❌ Preencha todos os campos!")

# Sidebar com informações
st.sidebar.success("🚀 Sistema Online")
st.sidebar.info("📊 Versão: 1.0 (Streamlit)")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 Links:")
st.sidebar.markdown("- [GitHub](https://github.com)")
st.sidebar.markdown("- [Documentação](https://docs.streamlit.io)")