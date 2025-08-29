from fastapi import FastAPI, HTTPException
import requests
import xml.etree.ElementTree as ET

app = FastAPI()

# Прямая ссылка на XML из Google Drive (замени ID на свой!)
XML_URL = "https://drive.google.com/uc?export=download&id=1-ycbD4OPkFn_DfYxJjtjCj4Qfefn8wgr"

def load_xml():
    """Загружает XML по ссылке и возвращает корень"""
    try:
        response = requests.get(XML_URL)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки XML: {str(e)}")
    
    try:
        root = ET.fromstring(response.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга XML: {str(e)}")
    
    return root

@app.get("/product/{product_id}")
def get_product(product_id: str):
    root = load_xml()

    # проходим по офферам
    for offer in root.findall(".//offer"):
        if offer.attrib.get("id") == product_id:
            product_data = {
                "id": offer.attrib.get("id"),
                "available": offer.attrib.get("available"),
                "group_id": offer.attrib.get("group_id"),
            }
            # добавляем вложенные элементы (например <name>, <price>)
            for child in offer:
                product_data[child.tag] = child.text
            return product_data

    raise HTTPException(status_code=404, detail=f"Товар с id={product_id} не найден")
