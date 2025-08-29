from fastapi import FastAPI
import requests
import xml.etree.ElementTree as ET

app = FastAPI()

# Ссылка на твой XML
XML_URL = "https://drive.google.com/uc?export=download&id=1-ycbD4OPkFn_DfYxJjtjCj4Qfefn8wgr"

@app.get("/")
def root():
    return {"status": "ok", "message": "API работает"}

@app.get("/get_product_info")
def get_product_info(product_id: str):
    """
    Возвращает информацию о товаре по его ID из тегов <offer>.
    Работает, даже если <offer> находится вложенно.
    """
    try:
        response = requests.get(XML_URL)
        response.raise_for_status()
        root = ET.fromstring(response.content)
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
