# AIAgents — Intelligent Beyorganik Product Agent
 
## 🧠 Project Description
 
**AIAgents** is a local GPT-based product assistant designed to recommend and summarize Beyorganik product data stored in a MySQL database or fetched from Trendyol’s API. It allows GPT-4o to access tools like `load_products_from_mysql`, `get_all_product_titles_and_prices`, and more — while maintaining full control over token limits, MySQL access, and user intents.
 
Users can ask:
> "Show me organic ginger shots for summer immunity support."
 
The assistant processes the query, accesses the database, filters results, and returns a helpful, human-like product suggestion.
 
---
 
## 🧰 System Tools
 
- `get_product()` – Fetches current products via Trendyol API and returns structured data.
- `save_products_to_json()` – Saves the fetched data to a local JSON file.
- `insert_products_to_mysql()` – Loads product data into a local MySQL database.
- `load_products_from_json()` – Loads previously saved products from JSON file.
- `get_all_product_titles_and_prices()` – Lightweight tool to return product names and prices for AI output.
 
## 🧠 GPT Agent Behavior
 
The GPT agent:
- Uses `GPT-4o` to interpret natural language queries.
- Automatically selects the best tool to handle a user’s need.
- Filters product listings based on keywords or categories.
- Formats outputs into natural-language recommendations.
 
### Example Output:
 
```
‘Organik Ginger Shot’ is a cold-pressed functional beverage with ginger, turmeric, and apple extract — ideal for seasonal immunity.
```
 
---
 
## 🗺️ File Structure
 
```
AIAgents/
├── src/
│   ├── utils.py                    # Core functions for data fetch, load, insert
│   └── basic.py                    # GPT agent orchestration
├── data/
│   ├── external/products.json      # Cached product data from Trendyol
│   ├── raw/                        # Raw data sources (optional)
│   ├── processed/                  # Processed/cleaned datasets (optional)
├── notebooks/                      # Jupyter exploration notebooks
├── reports/                        # Final reports, summaries, charts
├── .env                            # Environment secrets (API keys, DB creds)
├── requirements.txt                # Dependencies for pip install
```
 
---
 
## ▶️ How to Run the Project
 
1. **Set up a virtual environment** (recommended)
 
```bash
python -m venv aienv
source aienv/bin/activate  # or aienv\Scripts\activate on Windows
```
 
2. **Install requirements**
 
```bash
pip install -r requirements.txt
```
 
3. **Set environment variables**
 
Create a `.env` file in the root directory:
 
```
OPENAI_API_KEY=your_openai_key
SUPLIER_ID=108813
TRENDYOL_AUTH=Basic your_encoded_token
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=
DB=beyorganik
```
 
4. **Run the agent**
 
```bash
python src/basic.py
```
 
---
 
## 📌 Notes
 
- This system is optimized to avoid token overload by slicing descriptions and limiting result sets.
- Can be extended with semantic search, embedding filters, or Claude-style LLMs.
- Token-efficient architecture for 1000+ products.
