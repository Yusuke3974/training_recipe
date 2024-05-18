# ベースイメージ
FROM python:3.9-slim

# Poetryのインストール
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean

# Poetryのパスを通す
ENV PATH="/root/.local/bin:$PATH"

# 作業ディレクトリの設定
WORKDIR /app

# Poetryのプロジェクトファイルをコピー
COPY pyproject.toml poetry.lock ./

# 依存関係のインストール
RUN poetry install --no-root

# アプリケーションのコピー
COPY . .

# Streamlitのポートを公開
EXPOSE 8501

# アプリケーションの実行
CMD ["poetry", "run", "streamlit", "run", "home.py"]