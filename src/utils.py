"""
📦 Beyorganik Product Sync & Agent Tools

This script includes tools for:
- Fetching product data from Trendyol API
- Saving & loading product data as JSON
- Inserting products into a MySQL database
- Enabling AI agents to retrieve product information

Required environment variables (stored in `.env`):
- OPENAI_API_KEY
- SUPLIER_ID
- TRENDYOL_AUTH
- MYSQL_HOST
- MYSQL_USER
- MYSQL_PASSWORD
- DB

Author: Murat Can
"""

from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
import requests
import json
import mysql.connector
from agents import function_tool

# 🌱 Load environment variables
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
    Strips HTML tags from a given string.

    Args:
        html_content (str): Raw HTML content.

    Returns:
        str: Cleaned plain text content.
    """
    if html_content:
        return BeautifulSoup(html_content, "html.parser").get_text(separator="\n").strip()
    return ""


def get_product() -> dict[str, dict]:
    """
    Fetches all product data from the Trendyol API for the given supplier ID.

    Returns:
        dict[str, dict]: A dictionary where each key is a product barcode,
                         and the value is a dictionary containing product details.
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
                "price": product.get("salePrice"),  # Consider also: listPrice, discountedPrice
                "productUrl": product.get("productUrl"),
                "category": product.get("categoryName"),
                "brand": product.get("brand")
            }

        if page_num >= data.get("totalPages", 0) - 1:
            break
        page_num += 1

    return product_map


def save_products_to_json(products: dict[str, dict], filename: str = "data/external/products.json") -> None:
    """
    Saves the product dictionary to a local JSON file.

    Args:
        products (dict[str, dict]): The product data to be saved.
        filename (str): Path to the JSON file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(products)} products to {filename}")


@function_tool
def load_products_from_json() -> dict[str, dict]:
    """
    Loads products from a local JSON file for use with AI agents.

    Returns:
        dict[str, dict]: Product dictionary loaded from JSON.
    """
    filename = "data/external/products.json"
    with open(filename, "r", encoding="utf-8") as f:
        products = json.load(f)
    print(f"📦 Loaded {len(products)} products from {filename}")
    return products


def get_product_by_barcode(barcode: str) -> dict:
    """
    Looks up a product by its barcode from the loaded JSON file.

    Args:
        barcode (str): The product's barcode.

    Returns:
        dict: Product metadata or empty dict if not found.
    """
    products = load_products_from_json()
    return products.get(barcode, {})


def insert_products_to_mysql():
    """
    Inserts new products into the MySQL 'products' table
    only if the product barcode does not already exist.
    """
    json_path = "data/external/products.json"

    conn = mysql.connector.connect(
        host=mysqlHost,
        user=mysqlUser,
        password=mysqlPassword,
        database=mysqlDatabase
    )
    cursor = conn.cursor()

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    inserted = 0
    skipped = 0

    for barcode, product in data.items():
        try:
            # Skip if product already exists
            cursor.execute("SELECT 1 FROM products WHERE barcode = %s LIMIT 1", (barcode,))
            if cursor.fetchone():
                skipped += 1
                continue

            # Insert new product
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

    print(f"✅ Inserted: {inserted} | Skipped (exists): {skipped}")


@function_tool
def get_all_product_titles_and_prices() -> list[dict]:
    """
    Retrieves all product titles and prices from the MySQL 'products' table.

    This function connects to the database using credentials provided via environment variables,
    queries all entries in the 'products' table, and returns a list of dictionaries, each containing:
    - title: The name of the product
    - price: The product's price in Turkish Lira (₺)

    Returns:
        list[dict]: A list of product records in the format:
        [
            {"title": "Product A", "price": 499.9},
            {"title": "Product B", "price": 349.0},
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

    cursor.close()
    conn.close()

    return results