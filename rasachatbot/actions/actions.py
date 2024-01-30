# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/
# This is a simple example for a custom action which utters "Hello World!"
import json
import logging
import random
from token import AT
from typing import Dict, Text, Any, List, Union, Optional
from rasa_sdk.types import DomainDict
import psycopg2
from rasa_sdk import Action, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction, AllSlotsReset, EventType, ConversationPaused, UserUtteranceReverted
import requests
from rasa_sdk import Tracker


class ActionProduct(Action):
    def name(self):
        return 'action_product'

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict):
        url = 'https://localhost:5001/api/Products'
        headers = {'Content-Type': 'application/json'}
        request = requests.get(url, headers=headers, verify=False)

        if request.status_code == 200:
            try:
                products = request.json()

                # Check if the button was clicked
                if tracker.latest_message['intent']['name'] == 'add_to_cart':
                    # Extract product information from the intent entities
                    entities = tracker.latest_message['entities']
                    product_info = {
                        "ProductId": next((entity['value'] for entity in entities if entity['entity'] == 'ProductId'), None),
                        "Count": next((entity['value'] for entity in entities if entity['entity'] == 'Count'), 1)
                    }

                    # Set product information as a slot
                    dispatcher.utter_message(text="Thông tin sản phẩm đã được chọn.")
                    return [SlotSet("product_info", json.dumps(product_info))]

                # Show the message only once
                dispatcher.utter_message(text="Sản phẩm hiện có:")

                # Iterate through each product and send a separate message for each
                for product in products:
                    response_text = f"Tên: {product['name']}<br>Giá: ${product['price']}"

                    # Constructing the full image URL including 'https://localhost:5001'
                    image_url = f"https://localhost:5001{product['imageUrl']}"

                    # Add a button to add the product to the cart
                    button_payload = f'/add_to_cart{{"ProductId": {product["id"]}, "Count": 1}}'
                    button = {
                        "title": "Thêm vào giỏ hàng",
                        "payload": button_payload
                    }

                    # Send a message for each product with the button
                    dispatcher.utter_message(text=response_text)
                    dispatcher.utter_message(image=image_url)
                    dispatcher.utter_message(buttons=[button])

                return []
            except json.JSONDecodeError:
                dispatcher.utter_message(text='Lấy JSON từ API thất bại')
                return []
        else:
            dispatcher.utter_message(text='Đang có vấn đề, thử lại sau!!!')
            return []
        

class ActionSearchProduct(Action):
    def name(self) -> Text:
        return 'action_search_product'

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Extract the value of the 'category' entity
        category_entity = tracker.get_slot('category')

        if category_entity:
            # Make a request to your ASP.NET API with the category parameter
            url = f'https://localhost:5001/api/Products?CateItem={category_entity}'
            headers = {'Content-Type': 'application/json'}

            try:
                # Make the request
                request = requests.get(url, headers=headers, verify=False)

                # Check the response status
                if request.status_code == 200:
                    products = request.json()
                                    # Check if the button was clicked
                    if tracker.latest_message['intent']['name'] == 'add_to_cart':
                        # Extract product information from the intent entities
                        entities = tracker.latest_message['entities']
                        product_info = {
                            "ProductId": next((entity['value'] for entity in entities if entity['entity'] == 'ProductId'), None),
                            "Count": next((entity['value'] for entity in entities if entity['entity'] == 'Count'), 1)
                        }

                        # Set product information as a slot
                        dispatcher.utter_message(text="Thông tin sản phẩm đã được chọn.")
                        return [SlotSet("product_info", json.dumps(product_info))]

                    # Check if there are products
                    if products:
                        dispatcher.utter_message(text=f"Sản phẩm trong danh mục {category_entity} là:")

                        # Iterate through each product and send a separate message for each
                        for product in products:
                            response_text = f"Tên: {product['name']}<br>Giá: ${product['price']}"
                            image_url = f"https://localhost:5001{product['imageUrl']}"
                            # Add a button to add the product to the cart
                            button_payload = f'/add_to_cart{{"ProductId": {product["id"]}, "Count": 1}}'
                            button = {
                                "title": "Thêm vào giỏ hàng",
                                "payload": button_payload
                            }
                            dispatcher.utter_message(text=response_text)
                            dispatcher.utter_message(image=image_url)
                            dispatcher.utter_message(buttons=[button])

                    else:
                        dispatcher.utter_message(text=f'Không có sản phẩm trong danh mục {category_entity}.')

                else:
                    dispatcher.utter_message(text=f"Không tìm thấy sản phẩm. Status code: {request.status_code}")

            except requests.RequestException as e:
                dispatcher.utter_message(text=f"Lỗi API. Error: {str(e)}")

        else:
            dispatcher.utter_message(text='Không tìm thấy danh mục')
        
        return []





class ActionGetCategories(Action):
    def name(self):
        return 'action_categories_list'

    def run(self, dispatcher, tracker, domain):
        url = 'https://localhost:5001/api/CateItems'
        headers = {'Content-Type': 'application/json'}
        request = requests.get(url, headers=headers, verify=False)

        if request.status_code == 200:
            try:
                categories_data = request.json()
                categories = [item["name"] for item in categories_data]

                # Create a user-friendly response
                response = "Danh mục sản phẩm hiện có: " + ", ".join(categories) + "<br>Bạn muốn tìm kiếm sản phẩm trong danh mục nào?"
                dispatcher.utter_message(text=response)

                return []
            except json.JSONDecodeError:
                dispatcher.utter_message(text='Lấy JSON từ API thất bại.')
                return []
        else:
            dispatcher.utter_message(text='Đang gặp vấn đề, thử lại sau!!!')
            return []


class ActionAddToCart(Action):
    def name(self) -> Text:
        return 'action_add_to_cart'

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> List[Dict[Text, Any]]:
        try:
            entities = tracker.latest_message.get('entities', [])
            print(f"Debug: Entities - {json.dumps(entities)}")

            product_id = next((entity['value'] for entity in entities if entity['entity'] == 'ProductId'), None)
            count = next((entity['value'] for entity in entities if entity['entity'] == 'Count'), 1)

            print(f"Debug: Product ID - {product_id}, Count - {count}")

            if product_id is not None and count is not None:
                url = 'https://localhost:5001/api/Details'
                headers = {'Content-Type': 'application/json'}
                request_data = json.dumps({"ProductId": product_id, "Count": count})

                print(f"Debug: Request Data - {request_data}")

                request = requests.post(url, data=request_data, headers=headers, verify=False)

                print(f"Debug: Status Code - {request.status_code}, Response - {request.text}")

                if request.status_code == 200:
                    dispatcher.utter_message(text="Sản phẩm đã thêm vào giỏ hàng thành công!")
                else:
                    dispatcher.utter_message(text='Thất bại. Thử lại sau.')

            else:
                dispatcher.utter_message(text="Lấy thông tin sản phẩm thất bại.")

        except json.JSONDecodeError:
            dispatcher.utter_message(text='Lấy JSON thất bại')
        except Exception as e:
            dispatcher.utter_message(text=f'Error: {str(e)}')

        return []


class ActionDefaultFallback(Action):
    def name(self):
        return 'action_default_fallback'

    def run(self, dispatcher, tracker, domain):
        # Your fallback logic here
        dispatcher.utter_message(text="Tôi xin lỗi, tôi không hiểu!")
        return []