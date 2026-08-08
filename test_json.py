import json
import re

content = 'function=submit_order>{"customer_name": "Taniya", "items": "[{\\"name\\": \\"Cheese Sandwich\\", \\"price\\": 99, \\"qty\\": 1, \\"instructions\\": \\"{\\\\\\"spice\\\\\\": \\\\\\"normal\\\\\\"}\\"}, {\\"name\\": \\"Cold Coffee with Whipped Cream\\", \\"price\\": 79, \\"qty\\": 1, \\"instructions\\": \\"\\"}]", "payment_method": "Cash"}</function> Please check out our new Guest Reviews section to leave your feedback!'

match = re.search(r"<?function=([^>]+)>(.*?)</function>", content, re.DOTALL)
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
