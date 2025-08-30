import os
import requests
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ссылка на XML
XML_URL = "https://raw.githubusercontent.com/yourname/yourrepo/main/TEST_retail_rocket.xml"


def get_product_info(product_id: str):
    """Парсит XML и возвращает информацию о товаре по ID"""
    try:
        resp = requests.get(XML_URL)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)

        offer = root.find(f".//offer[@id='{product_id}']")
        if offer is None:
            return {"error": f"Товар с id={product_id} не найден"}

        name = offer.find("name").text if offer.find("name") is not None else "Без названия"
        price = offer.find("price").text if offer.find("price") is not None else "Нет цены"
        available = offer.attrib.get("available", "unknown")

        return {
            "id": product_id,
            "name": name,
            "price": price,
            "available": available
        }
    except Exception as e:
        return {"error": str(e)}


@app.route("/chat", methods=["POST"])
def chat():
    """
    Получает сообщение пользователя и запускает Responses API с функцией get_product_info.
    """
    user_message = request.json.get("message")

    # вызываем OpenAI с описанием функции
    response = client.responses.create(
        model="gpt-4.1",
        input=user_message,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "get_product_info",
                    "description": "Получить информацию о товаре по его ID из XML",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "string", "description": "ID товара"}
                        },
                        "required": ["product_id"]
                    }
                }
            }
        ]
    )

    # проверяем: ассистент хочет вызвать функцию?
    if response.output and response.output[0].type == "tool_call":
        tool_call = response.output[0].tool_call
        if tool_call.function.name == "get_product_info":
            product_id = tool_call.function.arguments.get("product_id")
            product_info = get_product_info(product_id)

            # возвращаем результат в модель
            followup = client.responses.create(
                model="gpt-4.1",
                input=[
                    {"role": "user", "content": user_message},
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(product_info)
                    }
                ]
            )
            return jsonify({"assistant_reply": followup.output_text})

    # если функции не понадобились — обычный ответ
    return jsonify({"assistant_reply": response.output_text})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)