import requests
from bs4 import BeautifulSoup

# === 設定 ===
PAGE_URL = "https://pokecabook.com/archives/1417"
WEBHOOK_URL = "https://discord.com/api/webhooks/1424388844308135969/R7AMAJeIsJJb_BMwqJJDqSSN2RiV8fJZo8OBMgFvxRvKXnEvHolljNFHfZ3RZn-nDaTo"

    def main():
    # 1️⃣ ページ取得
    res = requests.get(PAGE_URL)
    soup = BeautifulSoup(res.text, "html.parser")

    # 2️⃣ 画像を抽出（幅800・高さ450の画像を対象）   
    images = []
    for img in soup.find_all("img"):
        src = img.get("src")
        if src and src.startswith("http"):  #http/httpsのみを対象にする
            width = img.get("width")
            height = img.get("height")
            if width == "800" and height == "450" and "ティア表" in src:
                images.append(src)

    #print("見つかった画像:", images)

    # 3️⃣ 画像をダウンロードしてDiscordに投稿


    # 画像1枚ずつ別メッセージで投稿
    for i, img_url in enumerate(images[:2]):  # 投稿したい枚数
        img_data = requests.get(img_url).content
        filename = f'image_{i+1}.jpg'
        with open(filename, 'wb') as f:
            f.write(img_data)

        with open(filename, 'rb') as f:
            res = requests.post(
                WEBHOOK_URL,
                data={"content": f"📸 画像{i+1}です　@894601971095457833"},
                files={"file": f}
            )
    #print(f"投稿{i+1}結果:", res.status_code)

if __name__ == "__main__":
    main()
