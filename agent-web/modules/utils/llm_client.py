from openai import OpenAI
import streamlit as st
from typing import Generator, List, Dict

class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    def chat(self, messages: List[Dict], stream: bool = True) -> Generator:
        """チャット補完を実行"""
        model = st.session_state.get('model', 'gpt-4.1-mini')

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=stream,
            temperature=0.7
        )

        if stream:
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            return response.choices[0].message.content

    def with_tools(self, messages: List[Dict], tools: List[Dict]) -> Dict:
        """ツール使用を含むチャット"""
        model = st.session_state.get('model', 'gpt-4.1-mini')

        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
