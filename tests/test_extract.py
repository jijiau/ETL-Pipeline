import pytest
from unittest.mock import patch, MagicMock
from utils.extract import fetching_content, scrape_main, scrape_products
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError

# Test sudah ada
def test_fetching_content_success():
    with patch("utils.extract.requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html></html>"
        result = fetching_content("https://example.com")
        assert result == "<html></html>"

def test_fetching_content_fail():
    with patch("utils.extract.requests.get", side_effect=Exception("Error")):
        result = fetching_content("https://invalid.url")
        assert result is None

# ✅ Tambahan test
def test_fetching_content_status_not_ok():
    with patch("utils.extract.requests.get") as mock_get:
        mock_get.return_value.status_code = 404
        mock_get.return_value.text = "Not Found"
        mock_get.return_value.raise_for_status.side_effect = HTTPError("404 Client Error")
        
        result = fetching_content("https://example.com/notfound")
        assert result is None

def test_scrape_main_success():
    sample_html = """
    <html>
        <body>
            <div class="product-details">
                <h3 class="product-title">Product A</h3>
                <span class="price">$10.00</span>
                <p>Rating: ⭐ 4.5 / 5</p>
                <p>3 Colors</p>
                <p>Size: M</p>
                <p>Gender: Unisex</p>
            </div>
        </body>
    </html>
    """
    soup = BeautifulSoup(sample_html, "html.parser")
    article = soup.select_one("div.product-details")  # sesuai struktur aslinya
    result = scrape_main(article)

    assert isinstance(result, dict)
    assert result["Title"] == "Product A"
    assert result["Price"] == "$10.00"
    assert result["Rating"] == "4.5 / 5"
    assert result["Colors"] == "3 Colors"
    assert result["Size"] == "M"
    assert result["Gender"] == "Unisex"
    assert "timestamp" in result

def test_scrape_main_empty():
    empty_html = "<html><body><div>No products</div></body></html>"
    soup = BeautifulSoup(empty_html, "html.parser")
    result = scrape_main(soup)

    assert result is None  # ✅ karena scrape_main return None jika gagal

def test_scrape_main_missing_price():
    sample_html = """
    <html>
        <body>
            <div class="product-details">
                <h3 class="product-title">Product B</h3>
                <p>Rating: ⭐ 3.0 / 5</p>
                <p>2 Colors</p>
                <p>Size: L</p>
                <p>Gender: Male</p>
            </div>
        </body>
    </html>
    """
    soup = BeautifulSoup(sample_html, "html.parser")
    article = soup.select_one("div.product-details")
    result = scrape_main(article)

    assert isinstance(result, dict)
    assert result["Price"] == "Price Unavailable"

def test_scrape_main_incomplete_p_tags():
    sample_html = """
    <html>
        <body>
            <div class="product-details">
                <h3 class="product-title">Product C</h3>
                <span class="price">$20.00</span>
                <p>Rating: ⭐ 5.0 / 5</p>
                <p>1 Colors</p>
            </div>
        </body>
    </html>
    """
    soup = BeautifulSoup(sample_html, "html.parser")
    article = soup.select_one("div.product-details")
    result = scrape_main(article)

    assert result is None  # Karena <p> tags kurang dari 4

def test_scrape_main_missing_title():
    sample_html = """
    <html>
        <body>
            <div class="product-details">
                <span class="price">$30.00</span>
                <p>Rating: ⭐ 4.0 / 5</p>
                <p>2 Colors</p>
                <p>Size: S</p>
                <p>Gender: Female</p>
            </div>
        </body>
    </html>
    """
    soup = BeautifulSoup(sample_html, "html.parser")
    article = soup.select_one("div.product-details")
    result = scrape_main(article)

    assert result is None  # Karena title tidak ditemukan

@patch("utils.extract.fetching_content")
@patch("utils.extract.BeautifulSoup")
def test_scrape_products_one_page(mock_soup_class, mock_fetching_content):
    # Simulasi HTML content yang berhasil di-fetch
    mock_fetching_content.return_value = "<html></html>"

    # Simulasi objek soup
    mock_soup = MagicMock()
    mock_soup_class.return_value = mock_soup

    # Simulasi menemukan 1 produk di halaman tsb
    mock_article = MagicMock()
    mock_soup.select.return_value = [mock_article]

    # Patch scrape_main agar langsung return dict dummy
    with patch("utils.extract.scrape_main", return_value={
        "Title": "Product D",
        "Price": "$50.00",
        "Rating": "4.0 / 5",
        "Colors": "2 Colors",
        "Size": "L",
        "Gender": "Unisex",
        "timestamp": "2025-01-01T00:00:00"
    }):
        result = scrape_products()

    assert isinstance(result, list)
    assert len(result) > 0
    assert result[0]["Title"] == "Product D"

@patch("utils.extract.fetching_content", return_value=None)
def test_scrape_products_fetch_fail(mock_fetching_content):
    from utils.extract import scrape_products

    result = scrape_products()

    assert isinstance(result, list)
    assert len(result) == 0  # Karena fetching gagal

@patch("utils.extract.fetching_content")
@patch("utils.extract.BeautifulSoup")
def test_scrape_products_no_articles(mock_soup_class, mock_fetching_content):
    mock_fetching_content.return_value = "<html></html>"
    mock_soup = MagicMock()
    mock_soup_class.return_value = mock_soup

    # Simulasi tidak ada artikel ditemukan
    mock_soup.select.return_value = []

    result = scrape_products()

    assert isinstance(result, list)
    assert len(result) == 0  # Tidak ada data yang diappend
