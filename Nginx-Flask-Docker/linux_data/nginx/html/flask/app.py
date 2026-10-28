"""
### app.py

nginx から `/` 以下をリバースプロキシされる Flask アプリ。
メモリ使用量(ゲージ)とCPU使用率(ゲージ)を表示する。

| パス | メソッド | 説明 |
| --- | --- | --- |
| `/` | GET | トップページ(`templates/index.html`)。ゲージの初回描画を含む |
| `/partials/gauges` | GET | ゲージ部分のHTML断片(`static/js/index.js` が定期的に取得して差し替える) |
| `/api/health` | GET | ヘルスチェック(JSON) |
| `/api/echo` | POST | 受け取った JSON をそのまま返す |
| `/static/*` | GET | nginx が `html/static` から直接配信(Flaskは関与しない) |

| 項目 | 内容 |
| --- | --- |
| 配置 | `/${ENTRY_DIR}/${WS}/nginx/html/flask/` |
| 起動 | `start.sh` が gunicorn 経由で起動する(`app:app`) |
| 反映 | コード変更後は `docker compose restart` |

#### 構成

| ファイル | 役割 |
| --- | --- |
| `app.py` | ルーティング(このファイル) |
| `metrics.py` | `psutil` によるメモリ・CPUの取得 |
| `gauge.py` | ゲージ(SVG)の座標計算 |
| `templates/index.html` | ページ全体 |
| `templates/_gauges.html` | ゲージ部分(`index.html` からの include と `/partials/gauges` で共用) |

#### 定数

| 名前 | 値 | 説明 |
| --- | --- | --- |
| `REFRESH_SEC` | `5` | ブラウザがゲージを更新する間隔(秒) |
"""

from flask import Flask, jsonify, make_response, render_template, request

from gauge import build_gauge
from metrics import read_cpu, read_memory

REFRESH_SEC = 5

app = Flask(__name__)


def _gauge_context():
    """
    #### ゲージ部分のテンプレート変数を作る

    | 引数 | 型 | 説明 |
    | --- | --- | --- |
    | なし | - | - |

    | 戻り値 | 型 | 説明 |
    | --- | --- | --- |
    | テンプレート変数 | `dict` | `memory` `memory_gauge` `cpu` `cpu_gauge` (`templates/_gauges.html` 参照) |
    """
    memory = read_memory()
    cpu = read_cpu()
    return {
        "memory": memory,
        "memory_gauge": build_gauge(memory.percent),
        "cpu": cpu,
        "cpu_gauge": build_gauge(cpu.percent),
    }


@app.route("/")
def index():
    """
    #### トップページを返す

    | 引数 | 型 | 説明 |
    | --- | --- | --- |
    | なし | - | - |

    | 戻り値 | 型 | 説明 |
    | --- | --- | --- |
    | HTML | `str` | `templates/index.html` を描画した結果(ゲージ込み) |
    """
    return render_template("index.html", refresh_sec=REFRESH_SEC, **_gauge_context())


@app.route("/partials/gauges")
def gauges():
    """
    #### ゲージ部分のHTML断片を返す

    | 引数 | 型 | 説明 |
    | --- | --- | --- |
    | なし | - | - |

    | 戻り値 | 型 | 説明 |
    | --- | --- | --- |
    | レスポンス | `Response` | `templates/_gauges.html` を描画した結果。`Cache-Control: no-store` 付き |
    """
    response = make_response(render_template("_gauges.html", **_gauge_context()))
    response.headers["Cache-Control"] = "no-store"
    return response


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
