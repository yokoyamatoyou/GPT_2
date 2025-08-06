# AGENT - Streamlit移行・モジュール化開発指示書

## 1. プロジェクト概要

### 1.1 目的
既存のCustomTkinterデスクトップアプリケーションを、Streamlitベースのモダンなウェブアプリケーションに移行し、Google Cloud環境での運用を可能にする。

### 1.2 主要変更点
- **GUI Framework**: CustomTkinter → Streamlit
- **デザイン**: Claudeのようなシンプルで洗練されたUI（絵文字不要）
- **インフラ**: ローカル実行 → Google Cloud Run
- **認証**: なし → Identity Platform
- **検索機能**: 基本的なWebスクレイパー → OpenAI準拠のWeb検索
- **アーキテクチャ**: モノリシック → モジュール化

## 2. ディレクトリ構造

```
/agent-web
├── app.py                          # Streamlitメインアプリケーション
├── requirements.txt                # 依存関係
├── Dockerfile                      # コンテナ化用
├── .env.example                    # 環境変数テンプレート
├── cloudbuild.yaml                 # Google Cloud Build設定
│
├── /config
│   ├── __init__.py
│   ├── settings.py                 # アプリケーション設定
│   └── gcp_config.py              # Google Cloud設定
│
├── /modules
│   ├── __init__.py
│   ├── /auth
│   │   ├── __init__.py
│   │   └── identity_platform.py   # Identity Platform認証
│   │
│   ├── /agents
│   │   ├── __init__.py
│   │   ├── base_agent.py          # 基底クラス
│   │   ├── react_agent.py         # ReActエージェント
│   │   ├── cot_agent.py           # CoTエージェント
│   │   └── tot_agent.py           # ToTエージェント
│   │
│   ├── /tools
│   │   ├── __init__.py
│   │   ├── base_tool.py           # ツール基底クラス
│   │   ├── web_search.py          # OpenAI準拠Web検索
│   │   ├── sql_query.py           # SQLクエリツール
│   │   └── diagram_generator.py   # 図生成ツール
│   │
│   ├── /memory
│   │   ├── __init__.py
│   │   ├── base_memory.py         # メモリ基底クラス
│   │   ├── conversation_memory.py # 会話メモリ
│   │   └── vector_memory.py       # ベクトルメモリ
│   │
│   ├── /ui
│   │   ├── __init__.py
│   │   ├── chat_interface.py      # チャットUI
│   │   ├── sidebar.py             # サイドバー
│   │   └── styles.py              # カスタムCSS
│   │
│   └── /utils
│       ├── __init__.py
│       ├── llm_client.py          # LLMクライアント
│       ├── file_processor.py      # ファイル処理
│       └── conversation_manager.py # 会話管理
│
├── /static
│   └── custom.css                  # カスタムスタイルシート
│
└── /tests
    └── ...                         # テストファイル

```

## 3. 実装詳細仕様

### 3.1 メインアプリケーション (app.py)

```python
import streamlit as st
from modules.ui.chat_interface import ChatInterface
from modules.ui.sidebar import Sidebar
from modules.auth.identity_platform import IdentityPlatformAuth
from config.settings import Settings

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

if __name__ == "__main__":
    main()
```

### 3.2 認証モジュール (modules/auth/identity_platform.py)

```python
import streamlit as st
from google.cloud import identityplatform
from typing import Optional

class IdentityPlatformAuth:
    def __init__(self):
        self.client = identityplatform.Client()
        
    def check_authentication(self) -> bool:
        """認証状態をチェック"""
        return st.session_state.get('authenticated', False)
    
    def show_login_page(self):
        """ログインページを表示"""
        st.title("ログイン")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            email = st.text_input("メールアドレス")
            password = st.text_input("パスワード", type="password")
            
            if st.button("ログイン", use_container_width=True):
                if self.authenticate(email, password):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("認証に失敗しました")
    
    def authenticate(self, email: str, password: str) -> bool:
        """Identity Platformで認証"""
        try:
            # Identity Platform認証ロジック
            # TODO: 実装
            return True
        except Exception as e:
            st.error(f"認証エラー: {e}")
            return False
```

### 3.3 チャットインターフェース (modules/ui/chat_interface.py)

```python
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
            st.session_state.get('tools', [])
        )
        return agent.run(prompt)
```

### 3.4 サイドバー (modules/ui/sidebar.py)

```python
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
```

### 3.5 Web検索ツール (modules/tools/web_search.py)

```python
from typing import Dict, Any
import requests
from bs4 import BeautifulSoup
from modules.tools.base_tool import BaseTool

class WebSearchTool(BaseTool):
    """OpenAI公式ガイドラインに準拠したWeb検索ツール"""
    
    name = "web_search"
    description = "Web検索を実行して関連情報を取得"
    
    def __init__(self):
        self.search_api_key = self.get_search_api_key()
    
    def execute(self, query: str) -> str:
        """
        OpenAI推奨の実装パターン：
        1. 検索APIを使用（Google Custom Search API推奨）
        2. 結果の要約と引用
        3. レート制限の遵守
        """
        try:
            # Google Custom Search APIを使用
            results = self.search_google(query)
            
            # 結果を処理して要約
            summaries = []
            for result in results[:3]:  # 上位3件を処理
                content = self.fetch_and_extract(result['link'])
                summary = self.summarize_content(content, query)
                summaries.append({
                    'title': result['title'],
                    'url': result['link'],
                    'summary': summary
                })
            
            return self.format_results(summaries)
            
        except Exception as e:
            return f"検索エラー: {str(e)}"
    
    def search_google(self, query: str) -> List[Dict]:
        """Google Custom Search APIで検索"""
        endpoint = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.search_api_key,
            'cx': self.get_search_engine_id(),
            'q': query,
            'num': 5
        }
        response = requests.get(endpoint, params=params)
        return response.json().get('items', [])
    
    def fetch_and_extract(self, url: str) -> str:
        """URLからコンテンツを抽出"""
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # メインコンテンツを抽出
        main = soup.find('main') or soup.find('article') or soup.find('body')
        if main:
            # ノイズを除去
            for tag in main.find_all(['script', 'style', 'nav', 'footer']):
                tag.decompose()
            return main.get_text(separator=' ', strip=True)[:2000]
        return ""
```

### 3.6 LLMクライアント (modules/utils/llm_client.py)

```python
from openai import OpenAI
import streamlit as st
from typing import Generator

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
```

### 3.7 カスタムCSS (static/custom.css)

```css
/* Claudeライクなシンプルなデザイン */

/* メインコンテナ */
.main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

/* チャットメッセージ */
.stChatMessage {
    border-radius: 8px;
    margin-bottom: 1rem;
    padding: 1rem;
    background: #ffffff;
    border: 1px solid #e0e0e0;
}

/* ユーザーメッセージ */
.stChatMessage[data-testid="user-message"] {
    background: #f7f7f7;
}

/* アシスタントメッセージ */
.stChatMessage[data-testid="assistant-message"] {
    background: #ffffff;
}

/* 入力フィールド */
.stChatInput > div {
    border-radius: 8px;
    border: 2px solid #e0e0e0;
}

.stChatInput > div:focus-within {
    border-color: #4a5568;
}

/* サイドバー */
.css-1d391kg {
    background: #f9f9f9;
    border-right: 1px solid #e0e0e0;
}

/* ボタン */
.stButton > button {
    background: #4a5568;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1rem;
    transition: background 0.2s;
}

.stButton > button:hover {
    background: #2d3748;
}

/* セレクトボックス */
.stSelectbox > div > div {
    border-radius: 6px;
    border: 1px solid #e0e0e0;
}

/* 絵文字を非表示 */
.stChatMessage [data-testid="chatAvatarIcon"] {
    display: none;
}
```

### 3.8 Google Cloud設定

#### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 依存関係インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコピー
COPY . .

# Streamlitポート
EXPOSE 8080

# 起動コマンド
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
```

#### cloudbuild.yaml

```yaml
steps:
  # Docker イメージビルド
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/agent-web:$COMMIT_SHA', '.']
  
  # イメージをプッシュ
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/agent-web:$COMMIT_SHA']
  
  # Cloud Runにデプロイ
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'agent-web'
      - '--image=gcr.io/$PROJECT_ID/agent-web:$COMMIT_SHA'
      - '--region=asia-northeast1'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--set-env-vars=OPENAI_API_KEY=$$OPENAI_API_KEY'

options:
  logging: CLOUD_LOGGING_ONLY
```

### 3.9 requirements.txt

```txt
streamlit==1.29.0
openai==1.6.0
google-cloud-identity-platform==0.2.0
google-cloud-secret-manager==2.16.0
beautifulsoup4==4.12.2
requests==2.31.0
pydantic==2.5.0
scikit-learn==1.3.2
numpy==1.26.2
pandas==2.1.4
python-dotenv==1.0.0
```

## 4. 実装手順

### Phase 1: 基盤構築（1週目）
1. プロジェクト構造の作成
2. 設定管理システムの実装
3. 基本的なStreamlitアプリケーションのセットアップ
4. カスタムCSSによるClaudeライクなデザイン適用

### Phase 2: 認証とセキュリティ（2週目）
1. Identity Platform統合
2. セッション管理
3. APIキーのSecret Manager管理
4. CORS設定

### Phase 3: コア機能移植（3-4週目）
1. エージェントモジュールの移植
   - ReActエージェント
   - CoTエージェント
   - ToTエージェント
2. メモリシステムの移植
3. ツールシステムの移植

### Phase 4: Web検索機能実装（5週目）
1. Google Custom Search API統合
2. OpenAI準拠の検索結果処理
3. 引用システムの実装
4. レート制限とキャッシング

### Phase 5: UI/UX最適化（6週目）
1. ストリーミング応答の実装
2. ファイルアップロード機能
3. 会話管理機能
4. レスポンシブデザイン調整

### Phase 6: デプロイと運用（7週目）
1. Cloud Runへのデプロイ
2. CI/CDパイプライン構築
3. モニタリング設定
4. ロギングとエラートラッキング

## 5. 重要な実装ポイント

### 5.1 モジュール化の原則
- **単一責任の原則**: 各モジュールは1つの明確な責任を持つ
- **依存性注入**: モジュール間の結合度を低く保つ
- **インターフェース定義**: 基底クラスを使用して共通インターフェースを定義
- **設定の外部化**: 環境変数とSecret Managerを活用

### 5.2 パフォーマンス最適化
- **キャッシング**: `@st.cache_data`と`@st.cache_resource`の活用
- **遅延読み込み**: 必要なモジュールのみをインポート
- **非同期処理**: 可能な限り非同期処理を使用
- **ストリーミング**: LLM応答のストリーミング表示

### 5.3 セキュリティ考慮事項
- **認証**: Identity Platformによる強固な認証
- **認可**: ロールベースのアクセス制御
- **データ保護**: 機密情報のSecret Manager管理
- **入力検証**: すべてのユーザー入力を検証

### 5.4 エラーハンドリング
```python
class AgentError(Exception):
    """エージェント関連のエラー基底クラス"""
    pass

class ToolExecutionError(AgentError):
    """ツール実行エラー"""
    pass

def handle_errors(func):
    """エラーハンドリングデコレータ"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AgentError as e:
            st.error(f"エージェントエラー: {e}")
            logging.error(f"Agent error: {e}", exc_info=True)
        except Exception as e:
            st.error("予期しないエラーが発生しました")
            logging.error(f"Unexpected error: {e}", exc_info=True)
    return wrapper
```

## 6. テスト戦略

### 6.1 単体テスト
```python
# tests/test_agents.py
import pytest
from modules.agents.react_agent import ReActAgent

def test_react_agent_initialization():
    agent = ReActAgent(llm_client=MockLLMClient())
    assert agent is not None

def test_react_agent_run():
    agent = ReActAgent(llm_client=MockLLMClient())
    response = agent.run("テスト質問")
    assert response is not None
```

### 6.2 統合テスト
```python
# tests/test_integration.py
def test_end_to_end_chat_flow():
    # Streamlitアプリケーションの起動
    # ユーザー入力のシミュレーション
    # 応答の検証
    pass
```

## 7. デプロイチェックリスト

- [ ] 環境変数の設定確認
- [ ] Secret Managerへのシークレット登録
- [ ] Identity Platform設定
- [ ] Cloud Run サービスの作成
- [ ] カスタムドメインの設定
- [ ] SSL証明書の設定
- [ ] ロードバランサーの設定
- [ ] モニタリングアラートの設定
- [ ] バックアップポリシーの設定
- [ ] 本番環境へのデプロイ

## 8. 保守・運用

### 8.1 ログ管理
```python
import logging
from google.cloud import logging as cloud_logging

# Cloud Loggingクライアント初期化
client = cloud_logging.Client()
client.setup_logging()

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 8.2 メトリクス監視
- レスポンスタイム
- エラー率
- 同時接続数
- API使用量
- コスト

### 8.3 定期メンテナンス
- 週次: ログレビュー、パフォーマンス分析
- 月次: セキュリティアップデート、依存関係更新
- 四半期: アーキテクチャレビュー、スケーリング評価

## 9. 追加推奨事項

### 9.1 将来的な拡張
- **マルチ言語対応**: i18n実装
- **プラグインシステム**: 動的なツール追加
- **分析ダッシュボード**: 使用統計の可視化
- **A/Bテスト**: 機能の効果測定

### 9.2 パフォーマンス向上
- **Redis導入**: セッションとキャッシュ管理
- **CDN活用**: 静的アセットの配信最適化
- **データベース最適化**: Cloud SQL導入検討

この指示書に従って実装を進めることで、スケーラブルで保守性の高いStreamlitベースのAIエージェントアプリケーションを構築できます。
