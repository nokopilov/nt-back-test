from fastapi import FastAPI
import xml.etree.ElementTree as ET
from pathlib import Path

app = FastAPI()

# Путь к локальному XML
XML_PATH = Path(__file__).parent / "data" / "TEST_retail_rocket.xml"

@app.get("/")
def root():
    return {"status": "ok", "message": "API работает"}

@app.get("/get_product_info")
def get_product_info(product_id: str):
    """
    Возвращает информацию о товаре по его ID из тегов <offer>.
    """
    try:
        tree = ET.parse(XML_PATH)
        root = tree.getroot()
    except Exception as e:
        return {"ошибка": f"Не удалось загрузить XML: {e}"}

    # Ищем offer на любом уровне
    for offer in root.iter("offer"):
        if offer.get("id") == str(product_id):
            return {
                "id": offer.get("id"),
                "available": offer.get("available"),
                "group_id": offer.get("group_id"),
                "название": offer.findtext("name"),
                "описание": offer.findtext("description"),
                "цена": offer.findtext("price"),
                "старая_цена": offer.findtext("oldprice"),
                "ссылка": offer.findtext("url"),
                "картинка": offer.findtext("picture"),
            }

    return {"ошибка": f"Товар с id={product_id} не найден"}
