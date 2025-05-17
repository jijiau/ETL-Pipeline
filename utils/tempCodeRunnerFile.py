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
    session = requests.Session()
    response = session.get(url, headers=HEADERS)
    try:
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan ketika melakukan requests terhadap {url}: {e}")
        return None

from datetime import datetime

def scrape_main(article):
    try:
        title_elem = article.select_one("h3.product-title")
        if not title_elem:
            print("Tidak menemukan elemen judul, lewati artikel.")
            return None

        title = title_elem.text.strip()

        price_elem = article.select_one("span.price")
        if not price_elem:
            print("Tidak menemukan elemen harga, lewati artikel.")
            return None

        price = price_elem.text.strip()
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

def scrape_book(base_url, start_page=1, delay=2):
    """Fungsi utama untuk mengambil keseluruhan data, mulai dari requests hingga menyimpannya dalam variabel data."""
    data = []
    page_number = start_page
 
    while True:
        url = base_url.format(page_number)
        print(f"Scraping halaman: {url}")
 
        content = fetching_content(url)
        if content:
            soup = BeautifulSoup(content, "html.parser")
            articles_element = soup.find_all('article', class_='product_pod')
            for article in articles_element:
                book = extract_book_data(article)
                data.append(book)
 
            next_button = soup.find('li', class_='next')
            if next_button:
                page_number += 1
                time.sleep(delay) # Delay sebelum halaman berikutnya
            else:
                break # Berhenti jika sudah tidak ada next button
        else:
            break # Berhenti jika ada kesalahan
 
    return data

def main():
    """Fungsi utama untuk keseluruhan proses scraping hingga menyimpannya."""
    BASE_URL = 'https://fashion-studio.dicoding.dev/page{}'
    all_books_data = scrape_book(BASE_URL)
    df = pd.DataFrame(all_books_data)
    print(df)
 
 
if __name__ == '__main__':
    main()