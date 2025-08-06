import streamlit as st
from modules.ui.chat_interface import ChatInterface
from modules.ui.sidebar import Sidebar
from modules.auth.identity_platform import IdentityPlatformAuth
from config.settings import Settings
from modules.memory.conversation_memory import ConversationMemory

def main():
    # ページ設定
    st.set_page_config(
        page_title="AI Agent Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # カスタムCSS適用
    apply_custom_styles()

    # 認証チェック
    auth = IdentityPlatformAuth()
    if not auth.check_authentication():
        auth.show_login_page()
        return

    # セッション状態初期化
    initialize_session_state()

    # サイドバー
    with st.sidebar:
        sidebar = Sidebar()
        sidebar.render()

    # メインチャットインターフェース
    chat = ChatInterface()
    chat.render()

def apply_custom_styles():
    """Claudeライクなシンプルなスタイルを適用"""
    with open('static/custom.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def initialize_session_state():
    """セッション状態の初期化"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_agent' not in st.session_state:
        st.session_state.current_agent = 'react'
    if 'model' not in st.session_state:
        st.session_state.model = 'gpt-4.1-mini'
    if 'memory' not in st.session_state:
        st.session_state.memory = ConversationMemory()

if __name__ == "__main__":
    main()
