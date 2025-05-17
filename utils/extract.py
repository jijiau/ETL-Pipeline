import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import time

# Tambahkan user-agent ke dalam header untuk menghindari blokir oleh server
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
}

def fetching_content(url):
    """Mengambil konten HTML dari URL yang diberikan."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan ketika melakukan requests terhadap {url}: {e}")
        return None

def scrape_main(article):
    try:
        title_elem = article.select_one("h3.product-title")
        if not title_elem:
            print("Tidak menemukan elemen judul, lewati artikel.")
            return None

        title = title_elem.text.strip()

        price_elem = article.select_one("span.price")
        if price_elem:
            price = price_elem.text.strip()
        else:
            price = "Price Unavailable"  # ✅ Jangan lewati, tetap catat dengan teks ini

        p_tags = article.find_all("p")

        if len(p_tags) < 4:
            print("Jumlah elemen <p> kurang dari 4, lewati artikel.")
            return None

        rating = p_tags[0].text.strip().replace("Rating: ⭐", "").strip()
        colors = p_tags[1].text.strip()
        size = p_tags[2].text.strip().replace("Size:", "").strip()
        gender = p_tags[3].text.strip().replace("Gender:", "").strip()

        data = {
            "Title": title,
            "Price": price,
            "Rating": rating,
            "Colors": colors,
            "Size": size,
            "Gender": gender,
            "timestamp": datetime.now().isoformat()
        }

        return data

    except Exception as inner_err:
        print(f"Error parsing satu produk: {inner_err}")
        return None

def scrape_products():
    data = []
    for page in range(1, 51):
        url = 'https://fashion-studio.dicoding.dev' if page == 1 else f'https://fashion-studio.dicoding.dev/page{page}'
        try:
            content = fetching_content(url)
            if not content:
                print(f"[WARN] Page {page} skipped: Empty content.")
                continue
        except Exception as e:
            print(f"[ERROR] Failed to fetch content from page {page}: {e}")
            continue

        try:
            soup = BeautifulSoup(content, "html.parser")
            articles = soup.select("div.product-details")
        except Exception as e:
            print(f"[ERROR] Failed to parse HTML on page {page}: {e}")
            continue

        for article in articles:
            try:
                result = scrape_main(article)
                if result:
                    data.append(result)
            except Exception as e:
                print(f"[ERROR] Failed to scrape product on page {page}: {e}")
                continue

        time.sleep(1)  # Delay to avoid hitting server too quickly

    if not data:
        print("[ERROR] No data scraped.")
    else:
        print(f"[INFO] Successfully scraped {len(data)} products.")

    return data

# def main():
#     """Fungsi utama"""
#     all_data = scrape_products()
#     df = pd.DataFrame(all_data)
#     df.to_csv("products.csv", index=False)
#     print(f"Total data yang berhasil diambil: {len(df)}")
#     print(df.head())

# if __name__ == '__main__':
#     main()
