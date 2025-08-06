import streamlit as st
from typing import List

class Sidebar:
    def render(self):
        """サイドバーをレンダリング"""
        st.markdown("## 設定")

        # モデル選択
        self.render_model_selector()

        # エージェント選択
        self.render_agent_selector()

        # ツール設定
        self.render_tool_settings()

        # 会話管理
        self.render_conversation_controls()

    def render_model_selector(self):
        """モデル選択UI"""
        st.session_state.model = st.selectbox(
            "モデル",
            ["gpt-4.1-mini", "gpt-4.1"],
            index=0
        )

    def render_agent_selector(self):
        """エージェント選択UI"""
        st.session_state.current_agent = st.selectbox(
            "エージェント",
            ["react", "cot", "tot"],
            format_func=lambda x: {
                "react": "ReAct (推論+行動)",
                "cot": "Chain of Thought",
                "tot": "Tree of Thoughts"
            }.get(x, x)
        )

    def render_tool_settings(self):
        """ツール設定UI"""
        st.markdown("### ツール")

        tools = []
        if st.checkbox("Web検索", value=True):
            tools.append("web_search")
        if st.checkbox("SQL Query"):
            tools.append("sql_query")
        if st.checkbox("図生成"):
            tools.append("diagram")

        st.session_state.tools = tools

    def render_conversation_controls(self):
        """会話管理コントロール"""
        st.markdown("### 会話")

        if st.button("新規会話", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        if st.button("会話を保存", use_container_width=True):
            self.save_conversation()

        if st.button("会話を読み込み", use_container_width=True):
            self.load_conversation()
