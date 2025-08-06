import streamlit as st
from modules.agents import get_agent
from modules.utils.llm_client import LLMClient

class ChatInterface:
    def __init__(self):
        self.llm_client = LLMClient()

    def render(self):
        """チャットインターフェースをレンダリング"""
        # ヘッダー
        st.markdown("### AI Agent Assistant")

        # メッセージ履歴表示
        self.display_messages()

        # 入力フォーム
        self.render_input_form()

    def display_messages(self):
        """メッセージ履歴を表示"""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    def render_input_form(self):
        """入力フォームをレンダリング"""
        if prompt := st.chat_input("メッセージを入力..."):
            # ユーザーメッセージを追加
            st.session_state.messages.append({"role": "user", "content": prompt})

            # エージェント応答を生成
            with st.chat_message("assistant"):
                with st.spinner("考え中..."):
                    response = self.get_agent_response(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

    def get_agent_response(self, prompt: str) -> str:
        """エージェントから応答を取得"""
        agent = get_agent(
            st.session_state.current_agent,
            self.llm_client,
            st.session_state.get('tools', []),
            st.session_state.memory
        )
        return agent.run(prompt)
