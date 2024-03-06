import hashlib
import aiohttp
from data.config import TINKOFF_TERMINAL_KEY, TINKOFF_PASSWORD

class TinkoffPaymentsAPI:
    PAYMENTS_BASE_URL = "https://securepay.tinkoff.ru/v2/"
    objects_to_ignore = ["Shops", "Receipt", "DATA"]

    def __init__(self, terminal_key, password):
        self.terminal_key = terminal_key
        self.password = password

    @staticmethod
    def get_hash(text : str):
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def get_str_to_hash(d : dict):
        return ''.join(map(str,d.values()))

    async def get_signature(self, dict_for_signature : dict):

        temp_dict = {}
        for key, value in dict_for_signature.items():
            if key not in self.objects_to_ignore:
                temp_dict[key] = value
        dict_for_signature = temp_dict

        dict_for_signature['password'] = self.password
        ordered_dict = dict(sorted(dict_for_signature.items(), key= lambda x: x[0].lower()))
        return self.get_hash(self.get_str_to_hash(ordered_dict))

    async def make_request(self, method : str, json : dict):
        url = self.PAYMENTS_BASE_URL + method

        json['Token'] = await self.get_signature(json)
        async with aiohttp.ClientSession() as session:
            resp = await session.post(url=url, json = json)

            if resp.status != 200:
                print(await resp.text())

            resp_json = await resp.json()
            return resp_json


    async def init(self, Quantity : int, PriceOne : int, OrderId : str, Description : str, DATA : dict, Email : str) -> dict:
        Receipt = {"Email": Email,
                   "Taxation": "usn_income",
                   "Items": [{"Name": "bot vip",
                              "Quantity": Quantity,
                              "Price": PriceOne,
                              "Amount": Quantity * PriceOne,
                              "Tax": "vat20"}]}

        json = {"TerminalKey" : self.terminal_key,
                "Amount" : Receipt['Items'][0]["Amount"],
                "OrderId" : OrderId,
                "Description" : Description,
                "DATA" : DATA,
                "Receipt" : Receipt}
        return await self.make_request(method="Init", json=json)

    async def check_order(self, OrderId : str):
        json = {"TerminalKey" : self.terminal_key,
                "OrderId" : OrderId}
        return await self.make_request(method="CheckOrder", json=json)

tinkoff_payments = TinkoffPaymentsAPI(terminal_key=TINKOFF_TERMINAL_KEY, password= TINKOFF_PASSWORD)