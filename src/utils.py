from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
import requests
import json

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPLIER_ID = os.getenv("SUPLIER_ID")
TRENDYOL_AUTH = os.getenv("TRENDYOL_AUTH")


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
                "productUrl": product.get("productUrl"),
                "image": product["images"][0]["url"] if product.get("images") else None,
                "category": product.get("categoryName"),
                "brand": product.get("brand"),
                "attributes": {
                    attr["attributeName"]: attr["attributeValue"]
                    for attr in product.get("attributes", [])
                }
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


if __name__ == "__main__":
    products = get_product()
    if products:
        save_products_to_json(products)
    else:
        print("⚠️ No products fetched.")