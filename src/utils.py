from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
import requests
import json
from agents import function_tool
import mysql.connector
# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPLIER_ID = os.getenv("SUPLIER_ID")
TRENDYOL_AUTH = os.getenv("TRENDYOL_AUTH")
mysqlHost = os.getenv("MYSQL_HOST")
mysqlUser = os.getenv("MYSQL_USER")
mysqlPassword = os.getenv("MYSQL_PASSWORD")
mysqlDatabase = os.getenv("DB")


def clean_html(html_content: str) -> str:
    """
    Removes HTML tags and returns clean text.

    Args:
        html_content (str): The HTML string to clean.

    Returns:
        str: Cleaned plain text.
    """
    if html_content:
        return BeautifulSoup(html_content, "html.parser").get_text(separator="\n").strip()
    return ""


def get_product() -> dict[str, dict]:
    """
    Fetches all product data from the Trendyol API for a given supplier.

    Returns:
        dict[str, dict]: A dictionary where each key is a product barcode, and the value is a dictionary
                         containing product metadata (title, description, image URL, etc.).
    """
    product_map = {}
    headers = {"Authorization": f"{TRENDYOL_AUTH}"}
    base_url = f"https://apigw.trendyol.com/integration/product/sellers/{SUPLIER_ID}/products"
    page_num = 0

    while True:
        try:
            url = f"{base_url}?page={page_num}&onSale=true"
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                print(f"❌ Request failed with status code: {response.status_code}")
                return {}

            data = response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ Request exception occurred: {e}")
            return {}

        for product in data.get("content", []):
            barcode = product.get("barcode")
            if not barcode:
                continue

            product_map[barcode] = {
                "title": product.get("title"),
                "description": clean_html(product.get("description", "")),
                "price": product.get("salePrice"),  # or try "salePrice" or "discountedPrice"
                "productUrl": product.get("productUrl"),
                "category": product.get("categoryName"),
                "brand": product.get("brand")
            }

        # Stop if last page
        if page_num >= data.get("totalPages", 0) - 1:
            break
        page_num += 1

    return product_map


def save_products_to_json(products: dict[str, dict], filename: str = "data/external/products.json") -> None:
    """
    Saves product data to a JSON file.

    Args:
        products (dict[str, dict]): The product dictionary to save.
        filename (str): Output filename. Defaults to 'products.json'.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(products)} products to {filename}")

@function_tool
def load_products_from_json() -> dict[str, dict]:
    """
    Loads product data from the default JSON file.
    Returns:
        dict[str, dict]: The loaded product dictionary.
    """
    filename = "data/external/products.json"
    with open(filename, "r", encoding="utf-8") as f:
        products = json.load(f)
    print(f"Loaded {len(products)} products from {filename}")
    return products

def get_product_by_barcode(barcode: str) -> dict:
    """
    Fetches product data for a specific barcode.

    Args:
        barcode (str): The barcode of the product.

    Returns:
        dict: A dictionary containing product metadata (title, description, image URL, etc.).
    """
    products = load_products_from_json()
    return products.get(barcode, {})

def insert_products_to_mysql():
    json_path: str = "data/external/products.json"
    # Connect to MySQL
    conn = mysql.connector.connect(
        host=mysqlHost,
        user=mysqlUser,
        password=mysqlPassword,
        database=mysqlDatabase
    )
    cursor = conn.cursor()

    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    inserted = 0
    skipped = 0

    for barcode, product in data.items():
        try:
            # Check if product already exists
            cursor.execute("SELECT 1 FROM products WHERE barcode = %s LIMIT 1", (barcode,))
            if cursor.fetchone():
                skipped += 1
                continue

            # Insert if not exists
            cursor.execute("""
                INSERT INTO products (barcode, title, description, price, productUrl, category, brand)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                barcode,
                product.get("title", "")[:65535],
                product.get("description", "")[:65535],
                float(product.get("price", 0.0)),
                product.get("productUrl", "")[:65535],
                product.get("category", "")[:65535],
                product.get("brand", "")[:65535],
            ))
            inserted += 1

        except Exception as e:
            print(f"❌ Error inserting barcode {barcode}: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ {inserted} new products inserted. 🔁 {skipped} skipped (already in DB).")

import mysql.connector
from agents import function_tool

@function_tool
def get_all_product_titles_and_prices() -> str:
    """
    MySQL'deki 'products' tablosundan tüm ürünlerin başlık (title) ve fiyat (price) bilgisini getirir.

    Args:
        host (str): MySQL sunucu adresi
        user (str): MySQL kullanıcı adı
        password (str): MySQL şifresi
        database (str): Veritabanı ismi
        limit (int): Döndürülecek maksimum ürün sayısı (varsayılan: 100)

    Returns:
        list[dict]: [
            {"title": "...", "price": ...},
            ...
        ]
    """
    conn = mysql.connector.connect(
        host=mysqlHost,
        user=mysqlUser,
        password=mysqlPassword,
        database=mysqlDatabase
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT title, price FROM products")
    results = cursor.fetchall()
    final = ""
    for dic in results:
        title = dic["title"]
        price = dic["price"]
        final += f"Title: {title}, Price: {price} "
        
    cursor.close()
    conn.close()

    return final
# if __name__ == "__main__":
  # insert_products_to_mysql()
  # print(get_all_product_titles_and_prices())