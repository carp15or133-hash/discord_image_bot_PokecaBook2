import requests
from bs4 import BeautifulSoup
import os
import time

# --- Discord 投稿をリトライする関数 ---
def post_with_retry(url, files=None, data=None, max_retries=3, retry_wait=5):
    for attempt in range(1, max_retries + 1):
        try:
            # 💡 テキストデータも一緒に送信できるように data=data を追加
            response = requests.post(url, files=files, data=data)

            if response.status_code in (200, 204):
                print(f"✔ 成功: ステータスコード {response.status_code}")
                return True

            print(f"⚠ 投稿失敗（{response.status_code}） - {attempt}/{max_retries}")

        except Exception as e:
            print(f"⚠ 例外発生 - {attempt}/{max_retries}: {e}")

        if attempt < max_retries:
            print(f"⏳ {retry_wait} 秒後に再試行します…")
            time.sleep(retry_wait)

    print("❌ 全てのリトライに失敗しました。")
    return False


# --- Discord Webhook URL ---
WEBHOOK_URL = os.environ['WEBHOOK_URL']
PAGE_URL = "https://pokecabook.com/archives/1417"


def main():
    # 1️⃣ ページ取得
    res = requests.get(PAGE_URL)
    soup = BeautifulSoup(res.text, "html.parser")

    # 2️⃣ 画像抽出 (処理内容は変更なし)
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if not src or not src.startswith("http"):
            continue

        width = img.get("width")
        height = img.get("height")

        # --- サイズ + ティア表 で条件抽出
        if width == "800" and height == "450":
        #if width == "800" and height == "450" and "ティア表" in src:
            images.append(src)

    print("投稿対象の画像:", images)

    if not images:
        print("⚠️ 投稿対象の画像がありません")
        return

    # 3️⃣ 1枚ずつ投稿
    for i, img_url in enumerate(images[:2]):
        print(f"\n--- {i+1}枚目の画像 ({img_url}) の処理を開始 ---")
        img_data = requests.get(img_url).content
        filename = f'image_{i+1}.jpg'

        # ファイル書き出し
        with open(filename, 'wb') as f:
            f.write(img_data)

        # テキストメッセージ（投稿URLを添える）
        # data = {"content": f"**投稿画像 {i+1}**：\n元記事: {PAGE_URL}"}

        # リトライ投稿
        with open(filename, 'rb') as f:
            success = post_with_retry(
                WEBHOOK_URL,
                files={"file": f},
                # data=data # テキストメッセージも送信
            )

        # 4️⃣ ダウンロードしたファイルを削除（★追加）
        try:
            os.remove(filename)
            print(f"✅ ファイルを削除しました: {filename}")
        except OSError as e:
            print(f"❌ ファイル削除失敗: {e}")
        
        # 5️⃣ Discordのレート制限対策で待機（★追加）
        time.sleep(1)


if __name__ == "__main__":
    main()
