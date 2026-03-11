import json
import os
from datetime import datetime, timezone, timedelta

INPUT_FILE = "pharma_data.json"
OUTPUT_FILE = "index.html"

def generate_html(data):
    JST = timezone(timedelta(hours=9), 'JST')
    updated_at = data.get("updated_at", datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S"))
    
    # Escape data for JS injection
    json_data = json.dumps(data, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <base target="_top">
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>医薬品調達・在庫ダッシュボード</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body {{ font-family: 'Inter', sans-serif; background-color: #f3f4f6; }}
    .glass-card {{ background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); }}
    .spinner {{ animation: spin 1s linear infinite; }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    .fade-in {{ animation: fadeIn 0.4s ease-in-out; }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    .alternative-card {{ background: linear-gradient(to right, #ffffff, #f0fdf4); border-left-color: #10b981 !important; }}
    .badge-alt {{ background-color: #10b981; color: white; font-size: 0.7rem; padding: 0.15rem 0.4rem; border-radius: 4px; margin-right: 0.5rem; font-weight: bold; }}
    .status-badge {{ display: inline-block; padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600; }}
    .status-danger {{ background-color: #fee2e2; color: #b91c1c; border: 1px solid rgba(185, 28, 28, 0.1); }}
    .status-success {{ background-color: #dcfce7; color: #166534; border: 1px solid rgba(22, 101, 52, 0.1); }}
    .status-warning {{ background-color: #fef3c7; color: #b45309; border: 1px solid rgba(180, 83, 9, 0.1); }}
    .card-header {{ padding: 0.75rem 1rem; color: white; font-weight: 600; }}
  </style>
</head>
<body class="antialiased text-gray-800">
  <div id="app" class="min-h-screen flex flex-col items-center p-4 sm:p-6 md:p-8">
    <header class="w-full max-w-6xl mb-6 text-center">
      <h1 class="text-3xl font-bold text-indigo-700 flex items-center justify-center gap-3">
        <i class="fa-solid fa-pills"></i> 医薬品調達・在庫ダッシュボード
      </h1>
      <p class="text-gray-400 text-xs mt-2">最終更新: {updated_at}</p>
    </header>

    <nav class="w-full max-w-3xl mb-6">
      <div class="glass-card rounded-xl p-1 flex gap-1">
        <button @click="activeTab = 'dashboard'" :class="activeTab === 'dashboard' ? 'bg-indigo-600 text-white shadow' : 'text-gray-500 hover:bg-gray-100'" class="flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all flex items-center justify-center gap-1">
          <i class="fa-solid fa-chart-line"></i> 統合
        </button>
        <button @click="activeTab = 'search'" :class="activeTab === 'search' ? 'bg-indigo-600 text-white shadow' : 'text-gray-500 hover:bg-gray-100'" class="flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all flex items-center justify-center gap-1">
          <i class="fa-solid fa-magnifying-glass"></i> 薬を探す
        </button>
      </div>
    </nav>

    <main class="w-full max-w-7xl">
      <!-- Dashboard Tab -->
      <div v-if="activeTab === 'dashboard'" class="grid grid-cols-1 md:grid-cols-3 gap-6 fade-in">
        <!-- Collabo Card -->
        <section class="glass-card rounded-2xl overflow-hidden flex flex-col h-[700px]">
          <div class="card-header bg-sky-400 flex justify-between">
            <span>Collabo Portal</span>
            <span class="text-xs bg-white/20 px-2 rounded-full">{{ pharmaData.collabo?.length || 0 }}件</span>
          </div>
          <div class="overflow-y-auto p-2 space-y-2">
            <div v-for="item in pharmaData.collabo" class="p-3 bg-white border border-gray-100 rounded-lg shadow-sm">
              <div class="text-[10px] text-gray-400 font-bold mb-1">{{ item.maker }}</div>
              <div class="font-bold text-sm text-gray-800 mb-1 leading-tight">{{ item.name }}</div>
              <div class="flex justify-between items-center mt-2">
                <span :class="getStatusClass(item.status)" class="status-badge">{{ item.status }}</span>
                <span class="text-[10px] text-gray-400">{{ item.date }}</span>
              </div>
              <div v-if="item.remarks" class="mt-2 text-[10px] text-amber-600 bg-amber-50 p-1.5 rounded border-l-2 border-amber-300">
                {{ item.remarks }}
              </div>
            </div>
          </div>
        </section>

        <!-- Medipal Card -->
        <section class="glass-card rounded-2xl overflow-hidden flex flex-col h-[700px]">
          <div class="card-header bg-green-600 flex justify-between">
            <span>MEDIPAL</span>
            <span class="text-xs bg-white/20 px-2 rounded-full">{{ pharmaData.medipal?.length || 0 }}件</span>
          </div>
          <div class="overflow-y-auto p-2 space-y-2">
            <div v-for="item in pharmaData.medipal" class="p-3 bg-white border border-gray-100 rounded-lg shadow-sm">
              <div class="text-[10px] text-gray-400 font-bold mb-1">{{ item.maker }}</div>
              <div class="font-bold text-sm text-gray-800 mb-1 leading-tight">{{ item.name }}</div>
              <div class="mt-2">
                <span :class="item.remarks?.includes('調整') ? 'status-danger' : 'status-success'" class="status-badge">
                  {{ item.remarks?.includes('調整') ? '出荷調整' : '通常' }}
                </span>
                <p class="text-[10px] text-gray-500 mt-1">{{ item.remarks }}</p>
              </div>
            </div>
          </div>
        </section>

        <!-- AlfWeb Card -->
        <section class="glass-card rounded-2xl overflow-hidden flex flex-col h-[700px]">
          <div class="card-header bg-blue-500 flex justify-between">
            <span>ALF-Web</span>
            <span class="text-xs bg-white/20 px-2 rounded-full">{{ pharmaData.alfweb?.length || 0 }}件</span>
          </div>
          <div class="overflow-y-auto p-2 space-y-2">
            <div v-for="item in pharmaData.alfweb" class="p-3 bg-white border border-gray-100 rounded-lg shadow-sm">
              <div class="text-[10px] text-gray-400 font-bold mb-1">{{ item.maker }}</div>
              <div class="font-bold text-sm text-gray-800 mb-1 leading-tight">{{ item.name }}</div>
              <div class="flex justify-between items-center mt-2">
                <span class="status-badge status-danger">{{ item.status || '入荷未定' }}</span>
                <span v-if="item.date" class="text-[10px] text-gray-400">更新: {{ item.date }}</span>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- Search Tab -->
      <div v-if="activeTab === 'search'" class="max-w-3xl mx-auto fade-in">
        <div class="glass-card rounded-2xl p-6 mb-6">
          <div class="relative flex items-center w-full h-14 rounded-xl bg-white overflow-hidden border-2 border-indigo-100 focus-within:border-indigo-500 transition-all">
            <div class="grid place-items-center h-full w-12 text-indigo-400">
              <i class="fa-solid fa-magnifying-glass"></i>
            </div>
            <input v-model="query" @keyup.enter="performLocalSearch" class="h-full w-full outline-none text-gray-700 text-lg font-medium pl-2" type="text" placeholder="薬の名前を入力...">
            <button @click="performLocalSearch" class="bg-indigo-600 text-white h-full px-8 font-semibold hover:bg-indigo-700 transition-colors">検索</button>
          </div>
        </div>

        <div v-if="results.length > 0" class="space-y-4">
          <div v-for="item in results" :class="item.isPrimary === false ? 'alternative-card' : ''" class="glass-card rounded-xl p-5 border-l-4 border-indigo-500">
            <div class="flex justify-between items-start gap-4">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <span v-if="item.isPrimary === false" class="badge-alt">代替提案</span>
                  <span class="text-[10px] font-bold text-indigo-500 uppercase">薬品名</span>
                </div>
                <h3 class="text-xl font-bold text-gray-900 leading-tight">{{ item.name }}</h3>
                <div class="mt-3 flex gap-4">
                  <div v-if="item.shelf" class="bg-indigo-50 px-3 py-1 rounded border border-indigo-100 text-sm">
                    <span class="text-xs text-indigo-400 block font-bold">棚番</span>
                    <span class="font-bold text-indigo-800">{{ item.shelf }}</span>
                  </div>
                  <div class="bg-gray-50 px-3 py-1 rounded border border-gray-100 text-sm">
                    <span class="text-xs text-gray-400 block font-bold">在庫</span>
                    <span class="font-bold text-gray-800">{{ item.stock !== '' ? item.stock : '-' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="hasSearched" class="glass-card rounded-2xl p-10 text-center text-gray-400">
          <p>「{{ lastQuery }}」に一致する結果はありませんでした。</p>
        </div>
      </div>
    </main>

    <footer class="mt-10 pb-6 text-center text-xs text-gray-400">
      <p>© 2026 薬の在庫・棚番検索システム (GitHub Pages版)</p>
    </footer>
  </div>

  <script>
    const {{ createApp, ref }} = Vue;
    const pharmaData = {json_data};

    createApp({{
      setup() {{
        const activeTab = ref('dashboard');
        const query = ref('');
        const lastQuery = ref('');
        const results = ref([]);
        const hasSearched = ref(false);

        const getStatusClass = (status) => {{
          if (!status) return 'status-warning';
          const s = status.toLowerCase();
          if (s.includes('辞退') || s.includes('停止') || s.includes('未定') || s.includes('欠品')) return 'status-danger';
          if (s.includes('納品済') || s.includes('準備中') || s.includes('中') || s.includes('済')) return 'status-success';
          return 'status-warning';
        }};

        const performLocalSearch = () => {{
          const q = query.value.trim().toLowerCase();
          if (!q) return;
          lastQuery.value = query.value;
          
          const res = [];
          ['collabo', 'medipal', 'alfweb'].forEach(key => {{
            if (pharmaData[key]) {{
              pharmaData[key].forEach(item => {{
                if (item.name.toLowerCase().includes(q)) {{
                  res.push({{
                    name: item.name,
                    shelf: item.shelf || '',
                    stock: item.stock || item.quantity || item.order_qty || '',
                    isPrimary: true
                  }});
                }}
              }});
            }}
          }});
          
          results.value = res;
          hasSearched.value = true;
        }};

        return {{ activeTab, pharmaData, query, lastQuery, results, hasSearched, getStatusClass, performLocalSearch }};
      }}
    }}).mount('#app');
  </script>
</body>
</html>"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard generated at: {os.path.abspath(OUTPUT_FILE)}")

if __name__ == "__main__":
    if os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        generate_html(data)
    else:
        print(f"Error: {INPUT_FILE} not found. Please run fetch_data.py first.")