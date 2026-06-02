from __future__ import annotations

import base64
import hashlib
import json
import re
from io import BytesIO
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
STATIC_DEMO_DIR = Path(__file__).resolve().parent
PRIMARY_IMAGE_DIR = ROOT / "static_demo" / "products_images"
FALLBACK_IMAGE_DIR = STATIC_DEMO_DIR / "product_images"
IMAGE_DIR = PRIMARY_IMAGE_DIR if PRIMARY_IMAGE_DIR.exists() else FALLBACK_IMAGE_DIR
METADATA_FILE = STATIC_DEMO_DIR / "product_metadata.json"
OUT_FILE = STATIC_DEMO_DIR / "index.html"

DEFAULT_PRODUCT_META = [
    {"filename": "Coffee.jpg", "article": "DEMO-COFFEE", "name": "Ground Coffee", "category": "Beverages"},
    {"filename": "nescafee.jpg", "article": "DEMO-NESCAFE", "name": "Nescafe Classic", "category": "Beverages"},
    {"filename": "Green beans.jpg", "article": "DEMO-GREEN-BEANS", "name": "Green Beans", "category": "Canned Food"},
    {"filename": "canned tomatoes.png", "article": "DEMO-TOMATOES", "name": "Canned Tomatoes", "category": "Canned Food"},
    {"filename": "white-beans.png", "article": "DEMO-WHITE-BEANS", "name": "White Beans", "category": "Canned Food"},
    {"filename": "canned tuna.jpg", "article": "DEMO-TUNA", "name": "Canned Tuna", "category": "Canned Food"},
    {"filename": "MissionFoods6PlainWraps.jpg", "article": "DEMO-WRAPS", "name": "Plain Tortilla Wraps", "category": "Bakery"},
    {"filename": "Natural-Greek-Yogurt.jpg", "article": "DEMO-YOGURT", "name": "Natural Greek Yogurt", "category": "Dairy"},
    {"filename": "penne-pasta-in-box-E74J88.jpg", "article": "DEMO-PASTA", "name": "Penne Pasta", "category": "Pantry"},
    {"filename": "popcorn.jpg", "article": "DEMO-POPCORN", "name": "Popcorn", "category": "Snacks"},
]

SIMILARITY_OVERRIDES = {
    ("DEMO-COFFEE", "DEMO-NESCAFE"): 0.91,
    ("DEMO-GREEN-BEANS", "DEMO-WHITE-BEANS"): 0.86,
    ("DEMO-GREEN-BEANS", "DEMO-TOMATOES"): 0.79,
    ("DEMO-WHITE-BEANS", "DEMO-TOMATOES"): 0.82,
    ("DEMO-TUNA", "DEMO-TOMATOES"): 0.67,
    ("DEMO-PASTA", "DEMO-WRAPS"): 0.58,
    ("DEMO-POPCORN", "DEMO-WRAPS"): 0.49,
    ("DEMO-YOGURT", "DEMO-WRAPS"): 0.44,
}


def image_data_url(path: Path) -> str:
    image = Image.open(path).convert("RGB")
    image.thumbnail((520, 520))
    output = BytesIO()
    image.save(output, format="JPEG", quality=76, optimize=True)
    encoded = base64.b64encode(output.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def barcode(article: str) -> str:
    digest = hashlib.sha1(article.encode("utf-8")).hexdigest()
    digits = re.sub(r"\D", "", digest)
    return f"demo-{digits[:8].ljust(8, '0')}"


def similarity_for(source: dict, target: dict) -> float:
    pair = (source["article"], target["article"])
    reverse_pair = (target["article"], source["article"])
    if pair in SIMILARITY_OVERRIDES:
        return SIMILARITY_OVERRIDES[pair]
    if reverse_pair in SIMILARITY_OVERRIDES:
        return SIMILARITY_OVERRIDES[reverse_pair]
    if source["category"] == target["category"]:
        return 0.72
    return 0.31 + ((len(source["name"]) + len(target["name"])) % 17) / 100


def load_product_metadata() -> list[dict]:
    if not METADATA_FILE.exists() or METADATA_FILE.stat().st_size == 0:
        return DEFAULT_PRODUCT_META

    metadata = json.loads(METADATA_FILE.read_text(encoding="utf-8"))
    if not isinstance(metadata, list):
        raise ValueError(f"{METADATA_FILE} must contain a JSON list")

    required = {"filename", "article", "name", "category"}
    for index, product in enumerate(metadata, start=1):
        if not isinstance(product, dict):
            raise ValueError(f"Product metadata item {index} must be an object")
        missing = sorted(required - product.keys())
        if missing:
            raise ValueError(f"Product metadata item {index} is missing: {', '.join(missing)}")
    return metadata


def build_products() -> list[dict]:
    products = []
    for product in load_product_metadata():
        path = IMAGE_DIR / product["filename"]
        if not path.exists():
            print(f"Skipping missing image: {path}")
            continue
        products.append(
            {
                "article": product["article"],
                "name": product["name"],
                "category": product["category"],
                "barcode": product.get("barcode") or barcode(product["article"]),
                "image": image_data_url(path),
            }
        )
    return products


def build_html(products: list[dict]) -> str:
    data = json.dumps(products, separators=(",", ":"))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Product Similarity Demo</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #18212f;
      --muted: #667085;
      --line: #d9e1ea;
      --panel: #ffffff;
      --soft: #f5f8fb;
      --accent: #0f766e;
      --accent-2: #b42318;
      --warn: #b54708;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--soft);
      color: var(--ink);
    }}
    header {{
      padding: 22px clamp(16px, 4vw, 44px);
      background: #ffffff;
      border-bottom: 1px solid var(--line);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(24px, 4vw, 38px);
      line-height: 1.05;
      letter-spacing: 0;
    }}
    .subtitle {{ color: var(--muted); margin-top: 8px; max-width: 760px; }}
    main {{ padding: 22px clamp(16px, 4vw, 44px) 42px; }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(4, minmax(130px, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}
    .stat, .panel, .product, .match {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .stat {{ padding: 14px; }}
    .stat strong {{ display: block; font-size: 24px; margin-bottom: 2px; }}
    .stat span {{ color: var(--muted); font-size: 13px; }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(260px, 360px) 1fr;
      gap: 18px;
      align-items: start;
    }}
    .panel {{ padding: 16px; }}
    h2, h3 {{ margin: 0 0 12px; letter-spacing: 0; }}
    h2 {{ font-size: 18px; }}
    h3 {{ font-size: 15px; }}
    label {{ display: block; color: var(--muted); font-size: 13px; margin: 14px 0 6px; }}
    select, input[type="range"] {{ width: 100%; }}
    select {{
      appearance: none;
      border: 1px solid var(--line);
      background: #fff;
      color: var(--ink);
      border-radius: 6px;
      padding: 11px 12px;
      font: inherit;
    }}
    button {{
      width: 100%;
      margin-top: 16px;
      border: 0;
      border-radius: 6px;
      padding: 12px 14px;
      background: var(--accent);
      color: #fff;
      font-weight: 700;
      cursor: pointer;
    }}
    button:hover {{ filter: brightness(0.96); }}
    .reference {{
      margin-top: 14px;
      display: grid;
      gap: 10px;
    }}
    .reference img {{
      width: 100%;
      aspect-ratio: 1 / 1;
      object-fit: contain;
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .meta {{ display: grid; gap: 5px; font-size: 14px; }}
    .meta span {{ color: var(--muted); }}
    .toolbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }}
    .pill {{
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 5px 9px;
      border-radius: 999px;
      background: #e8f3f1;
      color: #134e48;
      font-size: 12px;
      font-weight: 700;
    }}
    .matches {{ display: grid; gap: 12px; }}
    .match {{
      display: grid;
      grid-template-columns: 116px 1fr;
      gap: 14px;
      padding: 12px;
      align-items: center;
    }}
    .match img {{
      width: 116px;
      height: 116px;
      object-fit: contain;
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 6px;
    }}
    .match h3 {{ margin-bottom: 5px; }}
    .score-row {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin-top: 10px;
    }}
    .bar {{
      height: 9px;
      border-radius: 999px;
      background: #e8edf2;
      overflow: hidden;
      flex: 1;
    }}
    .bar i {{ display: block; height: 100%; background: var(--accent); }}
    .confidence {{ color: var(--muted); font-size: 13px; min-width: 118px; text-align: right; }}
    .catalog {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
      gap: 12px;
      margin-top: 18px;
    }}
    .product {{ padding: 10px; cursor: pointer; }}
    .product.selected {{ border-color: var(--accent); box-shadow: inset 0 0 0 1px var(--accent); }}
    .product img {{
      width: 100%;
      aspect-ratio: 1 / 1;
      object-fit: contain;
      border-radius: 6px;
      background: #fff;
    }}
    .product strong {{ display: block; margin-top: 8px; font-size: 14px; }}
    .product span {{ color: var(--muted); font-size: 12px; }}
    .notice {{
      margin-top: 12px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
    }}
    .assistant-panel {{
      margin-top: 18px;
    }}
    .assistant-intro {{
      color: var(--muted);
      font-size: 13px;
      line-height: 1.45;
      margin: -4px 0 12px;
    }}
    .chat-list {{
      display: grid;
      gap: 10px;
      margin: 12px 0;
    }}
    .chat-item {{
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
    }}
    .chat-item.user {{
      background: #e8f3f1;
      border-color: #b9ded9;
    }}
    .chat-item.assistant {{
      background: #fff7ed;
      border-color: #fed7aa;
    }}
    .chat-meta {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 6px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }}
    .chat-text {{
      margin: 0;
      line-height: 1.45;
      white-space: pre-wrap;
      font-size: 14px;
    }}
    .chat-actions {{
      display: grid;
      grid-template-columns: 1fr 150px;
      gap: 10px;
      align-items: end;
    }}
    textarea {{
      width: 100%;
      min-height: 78px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 12px;
      font: inherit;
      color: var(--ink);
      background: #fff;
    }}
    .chat-button-stack {{
      display: grid;
      gap: 8px;
    }}
    .chat-button-stack button {{
      margin-top: 0;
    }}
    .secondary-button {{
      background: #344054;
    }}
    .assistant-status {{
      min-height: 20px;
      margin-top: 10px;
      color: var(--muted);
      font-size: 13px;
    }}
    @media (max-width: 860px) {{
      .layout, .stats {{ grid-template-columns: 1fr; }}
      .match {{ grid-template-columns: 92px 1fr; }}
      .match img {{ width: 92px; height: 92px; }}
      .confidence {{ min-width: auto; }}
      .chat-actions {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Product Similarity Demo</h1>
      <div class="subtitle">Offline browser preview using embedded product images and simulated similarity scores.</div>
    </div>
    <span class="pill">Single HTML file</span>
  </header>
  <main>
    <section class="stats" aria-label="Demo statistics">
      <div class="stat"><strong id="countProducts">0</strong><span>demo products</span></div>
      <div class="stat"><strong>3</strong><span>top matches</span></div>
      <div class="stat"><strong>0</strong><span>external images</span></div>
      <div class="stat"><strong>Offline</strong><span>no database required</span></div>
    </section>

    <section class="layout">
      <aside class="panel">
        <h2>Reference Product</h2>
        <label for="productSelect">Choose product</label>
        <select id="productSelect"></select>
        <label for="threshold">Similarity threshold: <strong id="thresholdValue">0.00</strong></label>
        <input id="threshold" type="range" min="0" max="1" value="0" step="0.05">
        <button id="searchButton" type="button">Find Similar Products</button>
        <div class="reference" id="reference"></div>
        <p class="notice">This demo does not call OpenAI CLIP or PostgreSQL. It mirrors the sales flow for quick browser viewing on a laptop or phone.</p>
      </aside>

      <section>
        <div class="panel">
          <div class="toolbar">
            <h2>Similarity Results</h2>
            <span class="pill" id="resultCount">0 matches</span>
          </div>
          <div class="matches" id="matches"></div>
        </div>
        <div class="catalog" id="catalog"></div>
      </section>
    </section>

    <section class="panel assistant-panel">
      <div class="toolbar">
        <h2>Local Guidance Assistant</h2>
        <span class="pill">Browser only</span>
      </div>
      <p class="assistant-intro">Ask how to use the demo, interpret scores, choose a threshold, review duplicates or variants, or add products through product_metadata.json.</p>
      <div id="chatList" class="chat-list"></div>
      <div class="chat-actions">
        <textarea id="chatInput" rows="3" placeholder="Ask about similarity scores, thresholds, duplicates, variants, barcodes, or adding products"></textarea>
        <div class="chat-button-stack">
          <button id="sendChatButton" type="button">Send</button>
          <button id="clearChatButton" class="secondary-button" type="button">Clear chat</button>
        </div>
      </div>
      <div id="chatMessage" class="assistant-status"></div>
    </section>
  </main>
  <script>
    const products = {data};
    const storageKey = 'product_similarity_demo_chat_messages';
    const maxChatMessages = 24;
    const defaultAssistantGreeting = 'I am your local product similarity guide. I can explain how to use this static demo, read scores, choose thresholds, and add products to product_metadata.json.';
    const select = document.getElementById('productSelect');
    const reference = document.getElementById('reference');
    const matches = document.getElementById('matches');
    const catalog = document.getElementById('catalog');
    const threshold = document.getElementById('threshold');
    const thresholdValue = document.getElementById('thresholdValue');
    const resultCount = document.getElementById('resultCount');
    const countProducts = document.getElementById('countProducts');
    const chatList = document.getElementById('chatList');
    const chatInput = document.getElementById('chatInput');
    const chatMessage = document.getElementById('chatMessage');
    let chatMessages = loadChatMessages();
    const similarityOverrides = {{
      'DEMO-COFFEE|DEMO-NESCAFE': 0.91,
      'DEMO-GREEN-BEANS|DEMO-WHITE-BEANS': 0.86,
      'DEMO-GREEN-BEANS|DEMO-TOMATOES': 0.79,
      'DEMO-WHITE-BEANS|DEMO-TOMATOES': 0.82,
      'DEMO-TUNA|DEMO-TOMATOES': 0.67,
      'DEMO-PASTA|DEMO-WRAPS': 0.58,
      'DEMO-POPCORN|DEMO-WRAPS': 0.49,
      'DEMO-YOGURT|DEMO-WRAPS': 0.44
    }};

    function score(a, b) {{
      const key = `${{a.article}}|${{b.article}}`;
      const reverse = `${{b.article}}|${{a.article}}`;
      if (similarityOverrides[key]) return similarityOverrides[key];
      if (similarityOverrides[reverse]) return similarityOverrides[reverse];
      if (a.category === b.category) return 0.72;
      return 0.31 + ((a.name.length + b.name.length) % 17) / 100;
    }}

    function confidence(value) {{
      if (value >= 0.9) return 'Very high confidence';
      if (value >= 0.8) return 'High confidence';
      if (value >= 0.6) return 'Medium confidence';
      return 'Low confidence';
    }}

    function loadChatMessages() {{
      try {{
        const stored = JSON.parse(localStorage.getItem(storageKey) || '[]');
        if (Array.isArray(stored) && stored.length) return stored;
      }} catch (error) {{
        localStorage.removeItem(storageKey);
      }}
      return [createChatMessage('Assistant', defaultAssistantGreeting)];
    }}

    function persistChatMessages() {{
      localStorage.setItem(storageKey, JSON.stringify(chatMessages.slice(-maxChatMessages)));
    }}

    function createChatMessage(role, text) {{
      return {{
        role,
        text,
        createdAtLabel: new Date().toLocaleTimeString([], {{ hour: '2-digit', minute: '2-digit' }})
      }};
    }}

    function renderChatMessages() {{
      chatList.innerHTML = chatMessages.slice(-6).map((message) => `
        <article class="chat-item ${{message.role === 'User' ? 'user' : 'assistant'}}">
          <div class="chat-meta">
            <span>${{message.role === 'User' ? 'You' : 'Assistant'}}</span>
            <span>${{message.createdAtLabel}}</span>
          </div>
          <p class="chat-text">${{escapeHtml(message.text)}}</p>
        </article>
      `).join('');
    }}

    function escapeHtml(value) {{
      return value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }}

    function sendChatMessage() {{
      const userText = chatInput.value.trim();
      if (!userText) {{
        chatMessage.textContent = 'Type a question before sending.';
        return;
      }}

      chatMessages = [...chatMessages, createChatMessage('User', userText)].slice(-maxChatMessages);
      chatMessages = [...chatMessages, createChatMessage('Assistant', buildAssistantReply(userText))].slice(-maxChatMessages);
      persistChatMessages();
      renderChatMessages();
      chatInput.value = '';
      chatMessage.textContent = '';
    }}

    function clearChatHistory() {{
      chatMessages = [createChatMessage('Assistant', defaultAssistantGreeting)];
      persistChatMessages();
      renderChatMessages();
      chatInput.value = '';
      chatMessage.textContent = 'Previous guidance chat cleared from browser storage.';
    }}

    function buildAssistantReply(userText) {{
      const text = userText.toLowerCase();
      const selected = products.find((product) => product.article === select.value);
      const thresholdText = Number(threshold.value).toFixed(2);
      const context = selected ? `Current reference: ${{selected.name}} (${{selected.article}}). Current threshold: ${{thresholdText}}.` : '';

      if (matchesAny(text, ['start', 'use', 'how', 'workflow', 'steps'])) {{
        return `${{context}}\n\nBasic workflow: choose a reference product, review the top matches, adjust the threshold, then decide whether each match is a duplicate, valid variant, old packaging version, or catalog mistake.`;
      }}
      if (matchesAny(text, ['threshold', 'slider', 'filter', 'no result', 'no match'])) {{
        return `${{context}}\n\nUse the threshold slider to control strictness. Lower values show more possible matches for exploration. Higher values hide weaker matches when you only want close visual candidates. If no matches appear, lower the threshold.`;
      }}
      if (matchesAny(text, ['score', 'confidence', 'percent', 'percentage'])) {{
        return 'Scores in this static preview are simulated. Treat 90%+ as very close, 80-89% as strong, 60-79% as worth checking, and lower scores as weak candidates. In a real pilot these scores should come from image embeddings.';
      }}
      if (matchesAny(text, ['duplicate', 'same product', 'catalog mistake'])) {{
        return 'For duplicate review, compare the product name, article/SKU, barcode, size, flavor, and packaging image. A visually close match with conflicting catalog data is a good candidate for manual QA.';
      }}
      if (matchesAny(text, ['variant', 'flavor', 'size', 'pack size', 'old packaging', 'old package'])) {{
        return 'A variant can be a different flavor, size, pack count, or package design for the same product family. Old packaging means a previous visual design that may still appear in stock, marketplace photos, or catalog records.';
      }}
      if (matchesAny(text, ['barcode', 'sku', 'article'])) {{
        return 'Barcode, SKU, and article number help explain whether a visually similar item is truly the same product. In this static demo, barcodes are generated demo values unless you add real barcode values in product_metadata.json.';
      }}
      if (matchesAny(text, ['add', 'new product', 'metadata', 'json', 'image', 'rebuild'])) {{
        return 'To add products: put the image in static_demo/product_images, add a matching entry in product_metadata.json with filename, article, name, category, and optional barcode, then run python3 demos/product_similarity/static_demo/build_demo.py. The rebuilt index.html embeds the images for offline viewing.';
      }}
      if (matchesAny(text, ['clip', 'postgres', 'database', 'real', 'backend', 'pilot'])) {{
        return 'This static demo is a browser preview. It does not call CLIP, PostgreSQL, or a backend. A real pilot should replace the simulated scores with embeddings, store metadata, and measure top-match quality and review-time savings.';
      }}
      return `${{context}}\n\nI can help with the demo workflow, thresholds, score interpretation, duplicate checks, variants, old packaging, barcode/SKU meaning, and adding products through product_metadata.json.`;
    }}

    function matchesAny(text, terms) {{
      return terms.some((term) => text.includes(term));
    }}

    function renderReference(product) {{
      reference.innerHTML = `
        <img src="${{product.image}}" alt="${{product.name}}">
        <div class="meta">
          <strong>${{product.name}}</strong>
          <span>Article: ${{product.article}}</span>
          <span>Barcode: ${{product.barcode}}</span>
          <span>Category: ${{product.category}}</span>
        </div>
      `;
    }}

    function renderMatches() {{
      const selected = products.find((product) => product.article === select.value);
      const minScore = Number(threshold.value);
      renderReference(selected);
      thresholdValue.textContent = minScore.toFixed(2);
      const ranked = products
        .filter((product) => product.article !== selected.article)
        .map((product) => ({{ ...product, score: score(selected, product) }}))
        .filter((product) => product.score >= minScore)
        .sort((a, b) => b.score - a.score)
        .slice(0, 3);

      resultCount.textContent = `${{ranked.length}} match${{ranked.length === 1 ? '' : 'es'}}`;
      matches.innerHTML = ranked.map((product, index) => `
        <article class="match">
          <img src="${{product.image}}" alt="${{product.name}}">
          <div>
            <h3>${{index + 1}}. ${{product.name}}</h3>
            <div class="meta">
              <span>Article: ${{product.article}}</span>
              <span>Category: ${{product.category}}</span>
            </div>
            <div class="score-row">
              <div class="bar" aria-hidden="true"><i style="width: ${{Math.round(product.score * 100)}}%"></i></div>
              <strong>${{Math.round(product.score * 100)}}%</strong>
            </div>
            <div class="confidence">${{confidence(product.score)}}</div>
          </div>
        </article>
      `).join('') || '<p class="notice">No products match the current threshold.</p>';
      renderCatalog(selected.article);
    }}

    function renderCatalog(selectedArticle) {{
      catalog.innerHTML = products.map((product) => `
        <article class="product ${{product.article === selectedArticle ? 'selected' : ''}}" data-article="${{product.article}}">
          <img src="${{product.image}}" alt="${{product.name}}">
          <strong>${{product.name}}</strong>
          <span>${{product.article}}</span>
        </article>
      `).join('');
    }}

    products.forEach((product) => {{
      const option = document.createElement('option');
      option.value = product.article;
      option.textContent = `${{product.article}} - ${{product.name}}`;
      select.appendChild(option);
    }});
    countProducts.textContent = products.length;
    document.getElementById('searchButton').addEventListener('click', renderMatches);
    document.getElementById('sendChatButton').addEventListener('click', sendChatMessage);
    document.getElementById('clearChatButton').addEventListener('click', clearChatHistory);
    threshold.addEventListener('input', renderMatches);
    select.addEventListener('change', renderMatches);
    chatInput.addEventListener('keydown', (event) => {{
      if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {{
        sendChatMessage();
      }}
    }});
    catalog.addEventListener('click', (event) => {{
      const card = event.target.closest('[data-article]');
      if (!card) return;
      select.value = card.dataset.article;
      renderMatches();
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }});
    renderMatches();
    renderChatMessages();
  </script>
</body>
</html>
"""


def main() -> None:
    products = build_products()
    if not products:
        raise SystemExit(f"No product images found in {IMAGE_DIR}")
    OUT_FILE.write_text(build_html(products), encoding="utf-8")
    print(f"Wrote {OUT_FILE}")


if __name__ == "__main__":
    main()
