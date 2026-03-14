import json
import os
from datetime import datetime, timezone, timedelta

INPUT_FILE = "pharma_data.json"

def generate_html(data):
    JST = timezone(timedelta(hours=9), 'JST')
    updated_at = data.get("updated_at", datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S"))
    
    collabo_items = data.get("collabo", [])
    medipal_items = data.get("medipal", [])
    alfweb_items = data.get("alfweb", [])

    def get_badge_class(status):
        if '納品済' in status:
            return 'badge-delivered'
        elif '出荷準備中' in status:
            return 'badge-preparing'
        elif '調達中' in status:
            return 'badge-procuring'
        elif '入荷未定' in status or '欠品' in status:
            return 'badge-unavailable'
        return 'badge-default'

    def get_collabo_rows(items):
        rows = ""
        for item in items:
            status = item.get('status', '')
            badge_cls = get_badge_class(status)
            
            # EPI機能：見た目を変えずに行をクリック可能にする
            is_pending = "調達中" in status or "入荷未定" in status or "出荷準備中" in status or "欠品" in status or "未納" in status or "未定" in status or "受注辞退" in status
            tr_attr = f''' onclick="openOrderEpi('{item.get("name", "")}')" style="cursor: pointer;" title="クリックしてEPI発注"''' if is_pending else ""

            rows += f"""
                    <tr{tr_attr}>
                        <td>
                            <span class="maker-name">{item.get('maker', '')}</span>
                            <div class="product-name">{item.get('name', '')}</div>
                            <span class="product-code">JAN: {item.get('code', '')}</span>
                            {f'<div class="remarks">{item.get("remarks")}</div>' if item.get('remarks') else ''}
                        </td>
                        <td>
                            <span class="status-badge {badge_cls}">{status}</span>
                            {f'<div class="receipt-date">受付: {item.get("date")}</div>' if item.get('date') else ''}
                        </td>
                        <td class="qty-block">
                            <div>発注: <b>{item.get('order_qty', '')}</b></div>
                            <div>納品予定: <b>{item.get('deliv_qty', '')}</b></div>
                        </td>
                    </tr>"""
        return rows

    def get_medipal_rows(items):
        rows = ""
        for item in items:
            is_danger = "調整" in item.get('remarks', '')
            badge_cls = 'badge-unavailable' if is_danger else 'badge-default'
            status_text = "入荷未定" if is_danger else "通常"
            
            # EPI機能：見た目を変えずに行をクリック可能にする
            is_pending = "入荷未定" in status_text or "調整" in item.get('remarks', '')
            tr_attr = f''' onclick="openOrderEpi('{item.get("name", "")}')" style="cursor: pointer;" title="クリックしてEPI発注"''' if is_pending else ""

            rows += f"""
                    <tr{tr_attr}>
                        <td>
                            <span class="maker-name">{item.get('code', '')}</span>
                            <div class="product-name">{item.get('name', '')}</div>
                            <span class="product-code">{item.get('maker', '')}</span>
                        </td>
                        <td>
                            <span class="status-badge {badge_cls}">{status_text}</span>
                            <div class="receipt-date">{item.get('remarks', '')}</div>
                        </td>
                    </tr>"""
        return rows

    def get_alfweb_rows(items):
        rows = ""
        for item in items:
            # EPI機能：見た目を変えずに行をクリック可能にする
            tr_attr = f''' onclick="openOrderEpi('{item.get("name", "")}')" style="cursor: pointer;" title="クリックしてEPI発注"'''
            rows += f"""
                    <tr{tr_attr}>
                        <td>
                            <span class="maker-name">{item.get('maker', '')}</span>
                            <div class="product-name">{item.get('name', '')}</div>
                        </td>
                        <td>
                            <span class="status-badge badge-unavailable">入荷未定</span>
                            <div class="receipt-date">更新: {item.get('date', '')}</div>
                        </td>
                        <td class="qty-block">
                            <b>{item.get('order_qty', '')}</b>
                        </td>
                    </tr>"""
        return rows

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>医薬品調達情報 統合ダッシュボード</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #3730a3;
            --primary-light: #4f46e5;
            --primary-hover: #312e81;
            --collabo: #5b21b6;
            --collabo-light: #7c3aed;
            --medipal: #1e40af;
            --medipal-light: #2563eb;
            --alfweb: #065f46;
            --alfweb-light: #059669;
            --bg: #eef0f9;
            --surface: #ffffff;
            --text: #1e1b4b;
            --text-secondary: #6b7280;
            --border: #e5e7eb;
            --danger: #dc2626;
            --warning: #d97706;
            --success: #16a34a;
            --info: #2563eb;
        }}

        * {{ box-sizing: border-box; }}

        body {{
            font-family: 'Noto Sans JP', 'Segoe UI', sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 0;
            line-height: 1.6;
        }}

        /* ─── ヘッダー ─── */
        .header {{
            background: var(--surface);
            padding: 1.25rem 1.5rem;
            box-shadow: 0 1px 0 rgba(0,0,0,0.08), 0 4px 12px rgba(55,48,163,0.06);
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .header-title {{
            margin: 0 0 0.25rem 0;
            font-size: 1.6rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .header-meta {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 1.2rem;
            font-size: 0.82rem;
            color: var(--text-secondary);
        }}

        .header-meta .updated-icon {{
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
        }}

        /* ─── タブバー ─── */
        .tab-bar {{
            max-width: 760px;
            margin: 1rem auto 0;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 0.35rem;
            display: flex;
            gap: 0.25rem;
        }}

        .tab-btn {{
            flex: 1;
            padding: 0.5rem 0.75rem;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            font-family: inherit;
            font-size: 0.85rem;
            font-weight: 600;
            transition: all 0.2s;
            background: transparent;
            color: var(--text-secondary);
            white-space: nowrap;
        }}

        .tab-btn:hover:not(.active) {{
            background: #f3f4f6;
            color: var(--text);
        }}

        .tab-btn.active {{
            background: var(--primary);
            color: #fff;
            box-shadow: 0 2px 8px rgba(55,48,163,0.3);
        }}

        /* ─── コンテンツ領域 ─── */
        .main-content {{
            max-width: 1440px;
            margin: 1.5rem auto;
            padding: 0 1.25rem;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 1.25rem;
        }}

        /* ─── カード ─── */
        .card {{
            background: var(--surface);
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06), 0 0 0 1px rgba(0,0,0,0.04);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: box-shadow 0.2s;
        }}

        .card:hover {{
            box-shadow: 0 8px 24px rgba(55,48,163,0.1), 0 0 0 1px rgba(0,0,0,0.04);
        }}

        .card-header {{
            padding: 1rem 1.25rem;
            color: white;
            font-weight: 700;
            font-size: 0.95rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            letter-spacing: 0.01em;
        }}

        .card-collabo {{
            background: linear-gradient(135deg, var(--collabo) 0%, var(--collabo-light) 100%);
        }}
        .card-medipal {{
            background: linear-gradient(135deg, var(--medipal) 0%, var(--medipal-light) 100%);
        }}
        .card-alfweb {{
            background: linear-gradient(135deg, var(--alfweb) 0%, var(--alfweb-light) 100%);
        }}

        .item-count {{
            background: rgba(255,255,255,0.25);
            padding: 0.2rem 0.65rem;
            border-radius: 20px;
            font-size: 0.82rem;
            font-weight: 600;
        }}

        .table-container {{
            overflow-x: auto;
            flex-grow: 1;
            max-height: 1200px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.88rem;
        }}

        th {{
            background-color: #f9fafb;
            padding: 0.7rem 1rem;
            font-weight: 600;
            font-size: 0.8rem;
            color: var(--text-secondary);
            border-bottom: 2px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 10;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }}

        td {{
            padding: 0.8rem 1rem;
            border-bottom: 1px solid var(--border);
            vertical-align: top;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr:hover td {{
            background-color: #f5f3ff;
        }}

        /* ─── テーブルセル内の要素 ─── */
        .maker-name {{
            font-size: 0.75rem;
            color: var(--text-secondary);
            display: block;
            margin-bottom: 0.2rem;
            font-weight: 500;
        }}

        .product-name {{
            font-weight: 600;
            color: var(--text);
            margin-bottom: 0.25rem;
            line-height: 1.4;
        }}

        .product-code {{
            font-size: 0.72rem;
            color: #9ca3af;
            font-family: 'SF Mono', 'Consolas', monospace;
        }}

        .remarks {{
            font-size: 0.78rem;
            color: #92400e;
            background-color: #fef3c7;
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            border-left: 3px solid #f59e0b;
            margin-top: 0.4rem;
            display: inline-block;
        }}

        /* ─── ステータスバッジ ─── */
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.22rem 0.6rem;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 600;
            white-space: nowrap;
        }}

        .badge-preparing {{
            background: #dbeafe;
            color: var(--info);
        }}

        .badge-delivered {{
            background: #dcfce7;
            color: var(--success);
        }}

        .badge-procuring {{
            background: #fef3c7;
            color: var(--warning);
        }}

        .badge-unavailable {{
            background: #fee2e2;
            color: var(--danger);
        }}

        .badge-default {{
            background: #f3f4f6;
            color: var(--text-secondary);
        }}

        .receipt-date {{
            font-size: 0.78rem;
            color: var(--text-secondary);
            margin-top: 0.35rem;
        }}

        .qty-block div {{
            font-size: 0.85rem;
            color: var(--text-secondary);
        }}

        .qty-block b {{
            color: var(--text);
            font-weight: 700;
        }}

        .empty-state {{
            padding: 3rem;
            text-align: center;
            color: var(--text-secondary);
            font-style: italic;
        }}

    </style>
</head>
<body>
    <!-- ヘッダー -->
    <div class="header">
        <h1 class="header-title">💊 医薬品調達情報 統合ダッシュボード</h1>
        <div class="header-meta">
            <span class="updated-icon">🕐 最終更新: {updated_at}</span>
        </div>

        <!-- タブバー -->
        <div class="tab-bar">
            <button id="btn-all" class="tab-btn active" onclick="filterItems('all')">📋 すべて表示</button>
            <button id="btn-pending" class="tab-btn" onclick="filterItems('pending')">⚠️ 未納・未定のみ</button>
        </div>
    </div>

    <!-- メインコンテンツ -->
    <div class="main-content">

        <div class="card">
            <div class="card-header card-collabo">
                <span>🔷 Collabo Portal（調達中・受注辞退）</span>
                <span class="item-count">{len(collabo_items)}件</span>
            </div>
            <div class="table-container">
                <table><thead><tr><th>品名 / メーカー</th><th>ステータス</th><th>数量</th></tr></thead><tbody>
                {get_collabo_rows(collabo_items)}
                </tbody></table>
            </div>
        </div>

        <div class="card">
            <div class="card-header card-medipal">
                <span>🔶 MEDIPAL（出荷調整・入荷未定）</span>
                <span class="item-count">{len(medipal_items)}件</span>
            </div>
            <div class="table-container">
                <table><thead><tr><th>品名 / メーカー</th><th>状況・備考</th></tr></thead><tbody>
                {get_medipal_rows(medipal_items)}
                </tbody></table>
            </div>
        </div>

        <div class="card">
            <div class="card-header card-alfweb">
                <span>🟢 ALF-Web（欠品・出荷調整）</span>
                <span class="item-count">{len(alfweb_items)}件</span>
            </div>
            <div class="table-container">
                <table><thead><tr><th>品名 / メーカー</th><th>状況</th><th>数量</th></tr></thead><tbody>
                {get_alfweb_rows(alfweb_items)}
                </tbody></table>
            </div>
        </div>

    </div>

    <script>
        function filterItems(mode) {{
            const rows = document.querySelectorAll('tbody tr');
            const btnAll = document.getElementById('btn-all');
            const btnPending = document.getElementById('btn-pending');

            if (mode === 'all') {{
                rows.forEach(row => row.style.display = '');
                btnAll.classList.add('active');
                btnPending.classList.remove('active');
            }} else {{
                rows.forEach(row => {{
                    const badge = row.querySelector('.status-badge');
                    if (!badge) return;
                    const status = badge.textContent.trim();
                    const isPending = status.includes('調達中') || status.includes('入荷未定') || status.includes('出荷準備中') || status.includes('受注辞退') || status.includes('欠品');
                    row.style.display = isPending ? '' : 'none';
                }});
                btnAll.classList.remove('active');
                btnPending.classList.add('active');
            }}
        }}

        const openOrderEpi = async (itemName) => {{
            if (!itemName) return;
            
            // (先)や(後)などの接頭辞を削除
            let searchKeyword = itemName.replace(/^\\([前後]\\)\\s*/, '');
            
            try {{
                if (navigator.clipboard) {{
                    await navigator.clipboard.writeText(searchKeyword);
                }} else {{
                    const textArea = document.createElement("textarea");
                    textArea.value = searchKeyword;
                    textArea.style.position = "fixed";
                    document.body.appendChild(textArea);
                    textArea.focus();
                    textArea.select();
                    try {{
                        document.execCommand('copy');
                    }} catch (err) {{
                        console.error('Fallback: Oops, unable to copy', err);
                    }}
                    document.body.removeChild(textArea);
                }}
            }} catch (err) {{
                console.error('Failed to copy text: ', err);
            }}
            
            window.open("https://www.order-epi.com/order/", "_blank");
        }};
    </script>
</body>
</html>"""
    
    for filename in ["index.html", "dashboard.html"]:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Generated: {filename}")

if __name__ == "__main__":
    if os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        generate_html(data)
    else:
        print(f"Error: {INPUT_FILE} not found.")