import requests
from bs4 import BeautifulSoup
import os

# --- Discord Webhook URL は GitHub Secrets から取得 ---
WEBHOOK_URL = os.environ['WEBHOOK_URL']
PAGE_URL = "https://pokecabook.com/archives/1417"

def main():
    # 1️⃣ ページを取得
    res = requests.get(PAGE_URL)
    soup = BeautifulSoup(res.text, "html.parser")

    # 2️⃣ 条件を満たす画像を抽出
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if not src or not src.startswith("http"):
            continue  # base64など無効なURLはスキップ

        width = img.get("width")
        height = img.get("height")
        # --- 変更箇所：サイズとファイル名に「ティア表」を含むことを条件に追加 ---
        if width == "800" and height == "450" and "ティア表" in src:
            images.append(src)

    print("投稿対象の画像:", images)

    if not images:
        print("⚠️ 投稿対象の画像がありません")
        return

    # 3️⃣ 画像を1枚ずつ別メッセージで投稿
    for i, img_url in enumerate(images[:2]):  # 投稿枚数を制御（最大2枚）
        img_data = requests.get(img_url).content
        filename = f'image_{i+1}.jpg'

        with open(filename, 'wb') as f:
            f.write(img_data)

        # --- 1枚ずつ別メッセージで投稿するため、ループ内でpost ---
        with open(filename, 'rb') as f:
            res = requests.post(
                WEBHOOK_URL,
                #data={"content": f"📸 画像{i+1}です"},
                files={"file": f}
            )
        print(f"投稿{i+1}結果:", res.status_code)

if __name__ == "__main__":
    main()
