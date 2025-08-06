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
