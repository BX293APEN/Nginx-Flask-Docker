"""
### app.py

nginx から `/` 以下をリバースプロキシされる Flask アプリ。

| パス | メソッド | 説明 |
| --- | --- | --- |
| `/` | GET | トップページ(`templates/index.html`) |
| `/api/health` | GET | ヘルスチェック(JSON) |
| `/api/echo` | POST | 受け取った JSON をそのまま返す |
| `/static/*` | GET | nginx が `html/static` から直接配信(Flaskは関与しない) |

| 項目 | 内容 |
| --- | --- |
| 配置 | `/${ENTRY_DIR}/${WS}/nginx/html/flask/` |
| 起動 | `start.sh` が gunicorn 経由で起動する(`app:app`) |
| 反映 | コード変更後は `docker compose restart` |
"""

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    """
    #### トップページを返す

    | 引数 | 型 | 説明 |
    | --- | --- | --- |
    | なし | - | - |

    | 戻り値 | 型 | 説明 |
    | --- | --- | --- |
    | HTML | `str` | `templates/index.html` を描画した結果 |
    """
    return render_template(
        "index.html",
        client_ip=request.headers.get("X-Real-IP", request.remote_addr),
        host=request.host,
    )


@app.route("/api/health")
def health():
    """
    #### ヘルスチェック

    | 引数 | 型 | 説明 |
    | --- | --- | --- |
    | なし | - | - |

    | 戻り値 | 型 | 説明 |
    | --- | --- | --- |
    | レスポンス | `Response` | `{"status": "ok"}` の JSON |
    """
    return jsonify(status="ok")


@app.route("/api/echo", methods=["POST"])
def echo():
    """
    #### リクエストボディの JSON をそのまま返す

    | 引数 | 型 | 説明 |
    | --- | --- | --- |
    | リクエストボディ | `JSON` | 任意の JSON(関数の引数は無し) |

    | 戻り値 | 型 | 説明 |
    | --- | --- | --- |
    | レスポンス | `Response` | 受け取った JSON(不正な場合は `{}`) |
    """
    return jsonify(request.get_json(silent=True) or {})
