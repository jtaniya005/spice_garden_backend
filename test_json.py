import json
import re

content = 'It\'s a bit brief! Could you please tell me your full name so I can confirm it? (function=ask_name_and_payment){ "items": [{"id": 609, "name": "Hakka Noodles", "price": 149, "qty": 1, "instructions": {"spice": "high"}}], "customer_name": null, "payment_method": null, "name": "yes"}</function'

match = re.search(r"[<(]?function=([^>)]+)[>)](.*?)(?:</function>?|$)", content, re.DOTALL)
if match:
    print("Match found!")
    tool_name = match.group(1)
    args_str = match.group(2)
    print("Args:", args_str)
    try:
        args = json.loads(args_str)
        print("Success:", args)
    except Exception as e:
        print("Error:", e)
else:
    print("No match")
