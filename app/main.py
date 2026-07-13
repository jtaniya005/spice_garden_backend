"""
FastAPI Backend for Spice Garden Restaurant
Using Ollama (llama3.2) - No API key needed!
Run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests
from fastapi import FastAPI

app = FastAPI()

app = FastAPI(title="Spice Garden API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2"

# ── Pydantic Models ──────────────────────────────────────────────────────────

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class OrderItem(BaseModel):
    id: int
    name: str
    price: int
    qty: int

class OrderRequest(BaseModel):
    items: List[OrderItem]
    customer_name: Optional[str] = "Guest"
    address: Optional[str] = ""

# ── Menu Data (Python dicts) ─────────────────────────────────────────────────

MENU = [
    # Indian
    {"id": 1,  "name": "Dal Baati Churma",        "category": "indian",      "price": 249, "description": "Rajasthani classic - baked wheat dumplings with spiced lentils and sweet crumble.", "tags": ["veg", "special"], "spice": 2},
    {"id": 2,  "name": "Gatte Ki Sabzi",           "category": "indian",      "price": 269, "description": "Gram flour dumplings simmered in a tangy yogurt-based masala.", "tags": ["veg", "special"], "spice": 3},
    {"id": 3,  "name": "Paneer Butter Masala",     "category": "indian",      "price": 329, "description": "Cubes of cottage cheese simmered in a rich tomato-butter gravy.", "tags": ["veg", "special"], "spice": 2},
    {"id": 4,  "name": "Paneer Tikka Masala",      "category": "indian",      "price": 289, "description": "Grilled cottage cheese cubes in a rich, smoky masala gravy.", "tags": ["veg"], "spice": 3},
    {"id": 5,  "name": "Veg Dum Biryani",          "category": "indian",      "price": 299, "description": "Slow-cooked basmati rice layered with spiced vegetables.", "tags": ["veg", "special"], "spice": 3},
    {"id": 6,  "name": "Kadhi Pakora",             "category": "indian",      "price": 199, "description": "Yoghurt-based curry with crispy gram flour fritters.", "tags": ["veg"], "spice": 2},
    {"id": 18, "name": "Chole Bhature",            "category": "indian",      "price": 249, "description": "Spicy chickpea curry served with fluffy deep-fried bread.", "tags": ["veg", "special"], "spice": 3},
    {"id": 19, "name": "Aloo Paratha",             "category": "indian",      "price": 149, "description": "Stuffed flatbread with spiced potato filling, served with butter and pickle.", "tags": ["veg"], "spice": 2},
    {"id": 21, "name": "Paneer Kadai",             "category": "indian",      "price": 319, "description": "Flavoursome kadai gravy with bell peppers and freshly ground spices.", "tags": ["veg"], "spice": 3},
    {"id": 22, "name": "Palak Paneer",             "category": "indian",      "price": 289, "description": "Creamy spinach curry with cubes of cottage cheese.", "tags": ["veg"], "spice": 2},
    {"id": 68, "name": "Rajasthani Ker Sangri",    "category": "indian",      "price": 279, "description": "Dried beans and berries cooked in traditional Rajasthani spices.", "tags": ["veg", "special"], "spice": 2},
    {"id": 69, "name": "Laal Maas",                "category": "indian",      "price": 299, "description": "A fiery red curry with potatoes cooked in aromatic spices.", "tags": ["veg", "spicy"], "spice": 4},
    {"id": 70, "name": "Baingan Bharta",           "category": "indian",      "price": 219, "description": "Roasted eggplant mashed with onions, tomatoes, and spices.", "tags": ["veg"], "spice": 2},
    {"id": 71, "name": "Rajma Chawal",             "category": "indian",      "price": 249, "description": "Kidney beans curry served with fragrant basmati rice.", "tags": ["veg"], "spice": 2},
    # Chinese
    {"id": 7,  "name": "Chilli Paneer",            "category": "chinese",     "price": 319, "description": "Crispy paneer tossed with capsicum, onions, and bold chilli sauces.", "tags": ["veg", "spicy", "special"], "spice": 4},
    {"id": 8,  "name": "Veg Manchurian",           "category": "chinese",     "price": 229, "description": "Crispy veggie balls in a tangy, spicy Manchurian sauce.", "tags": ["veg", "spicy"], "spice": 3},
    {"id": 9,  "name": "Hakka Noodles",            "category": "chinese",     "price": 249, "description": "Stir-fried noodles with colourful vegetables in a light soy-garlic sauce.", "tags": ["veg"], "spice": 2},
    {"id": 10, "name": "Honey Garlic Baby Corn",   "category": "chinese",     "price": 299, "description": "Baby corn tossed in a sweet honey-garlic glaze.", "tags": ["veg", "special"], "spice": 1},
    {"id": 20, "name": "Veg Spring Rolls",         "category": "chinese",     "price": 199, "description": "Crispy rolls stuffed with crunchy mixed vegetables.", "tags": ["veg", "special"], "spice": 2},
    {"id": 23, "name": "Schezwan Fried Rice",      "category": "chinese",     "price": 219, "description": "Wok-tossed rice with vegetables in a spicy schezwan sauce.", "tags": ["veg", "spicy"], "spice": 4},
    {"id": 24, "name": "Veg Spring Onion Noodles", "category": "chinese",     "price": 229, "description": "Soft noodles tossed with spring onion, bean sprouts, and a light soy glaze.", "tags": ["veg"], "spice": 2},
    {"id": 25, "name": "Chilli Garlic Tofu",       "category": "chinese",     "price": 269, "description": "Crispy tofu cubes in a fragrant chilli-garlic sauce.", "tags": ["veg", "spicy"], "spice": 4},
    {"id": 26, "name": "Mushroom Manchurian",      "category": "chinese",     "price": 249, "description": "Golden mushrooms in a tangy Indo-Chinese sauce.", "tags": ["veg", "spicy"], "spice": 3},
    {"id": 27, "name": "Honey Chilli Broccoli",    "category": "chinese",     "price": 239, "description": "Crunchy broccoli florets glazed in sweet and spicy honey-chilli dressing.", "tags": ["veg", "special"], "spice": 2},
    {"id": 28, "name": "Schezwan Paneer",          "category": "chinese",     "price": 289, "description": "Paneer cubes wok-fried with vegetables in bold schezwan spices.", "tags": ["veg", "spicy"], "spice": 4},
    {"id": 72, "name": "Cashew Nut Vegetables",    "category": "chinese",     "price": 289, "description": "Stir-fried vegetables with roasted cashews in a creamy sauce.", "tags": ["veg", "special"], "spice": 1},
    {"id": 73, "name": "Singapore Mei Fun",        "category": "chinese",     "price": 269, "description": "Thin rice noodles with curry powder and mixed vegetables.", "tags": ["veg", "spicy"], "spice": 3},
    {"id": 74, "name": "Egg Fried Rice",           "category": "chinese",     "price": 199, "description": "Fluffy rice stir-fried with scrambled eggs and green peas.", "tags": ["veg"], "spice": 1},
    {"id": 75, "name": "Crispy Chilli Potatoes",   "category": "chinese",     "price": 189, "description": "Crispy potato cubes tossed with fresh chillies and garlic.", "tags": ["veg", "spicy"], "spice": 3},
    # Continental
    {"id": 11, "name": "Mushroom Risotto",         "category": "continental", "price": 329, "description": "Creamy Arborio rice with wild mushrooms, parmesan, and truffle oil.", "tags": ["veg", "special"], "spice": 0},
    {"id": 12, "name": "Grilled Veg Pasta",        "category": "continental", "price": 339, "description": "Al dente penne with grilled vegetables in herb-infused tomato-basil sauce.", "tags": ["veg"], "spice": 1},
    {"id": 29, "name": "Hot and Sour Soup",        "category": "continental", "price": 179, "description": "Classic bowl of hot and sour broth with mushrooms and vegetables.", "tags": ["veg"], "spice": 2},
    {"id": 30, "name": "Garlic Bread",             "category": "continental", "price": 149, "description": "Toasted baguette slices brushed with garlic-herb butter and parmesan.", "tags": ["veg"], "spice": 0},
    {"id": 31, "name": "Creamy Tomato Basil Pasta","category": "continental", "price": 329, "description": "Penne in a velvety tomato-basil cream sauce topped with fresh herbs.", "tags": ["veg"], "spice": 1},
    {"id": 32, "name": "Grilled Vegetable Skewers","category": "continental", "price": 279, "description": "Seasonal veggies chargrilled with lemon, rosemary, and garlic.", "tags": ["veg", "special"], "spice": 1},
    {"id": 33, "name": "Spinach Ricotta Cannelloni","category": "continental","price": 349, "description": "Pasta tubes stuffed with spinach and ricotta, baked in rich tomato sauce.", "tags": ["veg"], "spice": 0},
    {"id": 34, "name": "Mushroom and Truffle Pizza","category": "continental","price": 399, "description": "Thin crust pizza topped with mushrooms, truffle oil, and melting mozzarella.", "tags": ["veg", "special"], "spice": 0},
    {"id": 35, "name": "Caesar Salad",             "category": "continental", "price": 219, "description": "Crisp romaine with parmesan, croutons, and creamy Caesar dressing.", "tags": ["veg"], "spice": 0},
    {"id": 36, "name": "Roasted Pumpkin Risotto",  "category": "continental", "price": 339, "description": "Creamy Arborio rice cooked with roasted pumpkin and sage.", "tags": ["veg"], "spice": 0},
    {"id": 76, "name": "Baked Vegetable Parmesan", "category": "continental", "price": 299, "description": "Layers of eggplant, tomato, and cheese baked to perfection.", "tags": ["veg"], "spice": 0},
    {"id": 77, "name": "Orzo Pasta Primavera",     "category": "continental", "price": 319, "description": "Pearl pasta with seasonal vegetables in garlic-white wine sauce.", "tags": ["veg", "special"], "spice": 1},
    {"id": 78, "name": "Minestrone Soup",          "category": "continental", "price": 159, "description": "Hearty vegetable and pasta soup with Italian herbs.", "tags": ["veg"], "spice": 0},
    {"id": 79, "name": "Vegetable Quiche",         "category": "continental", "price": 279, "description": "Savory pie with mixed vegetables, cheese, and cream.", "tags": ["veg", "special"], "spice": 0},
    # Pizza
    {"id": 52, "name": "Margherita Pizza",         "category": "pizza",       "price": 349, "description": "Classic pizza with fresh tomato, mozzarella, and basil.", "tags": ["veg", "special"], "spice": 0},
    {"id": 53, "name": "Paneer & Onion Pizza",     "category": "pizza",       "price": 379, "description": "Paneer chunks and caramelised onions on a crispy crust.", "tags": ["veg", "special"], "spice": 1},
    {"id": 54, "name": "Vegetable Supreme Pizza",  "category": "pizza",       "price": 399, "description": "Loaded with bell peppers, mushrooms, olives, and fresh herbs.", "tags": ["veg"], "spice": 1},
    {"id": 55, "name": "Spicy Jalapeno Pizza",     "category": "pizza",       "price": 389, "description": "Fiery jalapenos, green chillies, and mozzarella on thin crust.", "tags": ["veg", "spicy"], "spice": 4},
    {"id": 80, "name": "BBQ Vegetable Pizza",      "category": "pizza",       "price": 389, "description": "Smoky BBQ sauce with grilled vegetables and melted cheese.", "tags": ["veg", "special"], "spice": 1},
    {"id": 81, "name": "White Sauce Pizza",        "category": "pizza",       "price": 379, "description": "Creamy white sauce base with mushrooms and corn.", "tags": ["veg"], "spice": 0},
    {"id": 82, "name": "Pesto Vegetable Pizza",    "category": "pizza",       "price": 399, "description": "Fresh basil pesto with mixed vegetables and pine nuts.", "tags": ["veg", "special"], "spice": 0},
    # Breads
    {"id": 56, "name": "Garlic Naan",              "category": "breads",      "price": 89,  "description": "Soft Indian bread brushed with garlic and herb butter.", "tags": ["veg"], "spice": 0},
    {"id": 57, "name": "Cheese Naan",              "category": "breads",      "price": 109, "description": "Fluffy naan topped with melted cheese and aromatic spices.", "tags": ["veg", "special"], "spice": 0},
    {"id": 58, "name": "Tandoori Roti",            "category": "breads",      "price": 49,  "description": "Whole wheat flatbread cooked in traditional tandoor.", "tags": ["veg"], "spice": 0},
    {"id": 59, "name": "Paneer Kulcha",            "category": "breads",      "price": 129, "description": "Stuffed bread with spiced paneer and herbs.", "tags": ["veg"], "spice": 1},
    {"id": 83, "name": "Methi Naan",               "category": "breads",      "price": 99,  "description": "Soft naan infused with fresh fenugreek leaves.", "tags": ["veg"], "spice": 0},
    {"id": 84, "name": "Stuffed Kulcha",           "category": "breads",      "price": 119, "description": "Flatbread with mixed vegetable filling and herbs.", "tags": ["veg"], "spice": 1},
    {"id": 85, "name": "Lachcha Paratha",          "category": "breads",      "price": 89,  "description": "Layered flatbread with clarified butter - flaky and delicious.", "tags": ["veg"], "spice": 0},
    {"id": 86, "name": "Puri",                     "category": "breads",      "price": 69,  "description": "Deep-fried puffed bread, perfect with curries.", "tags": ["veg"], "spice": 0},
    # Appetizers
    {"id": 60, "name": "Samosa",                   "category": "appetizers",  "price": 79,  "description": "Crispy fried pastry stuffed with spiced potato and peas.", "tags": ["veg", "special"], "spice": 2},
    {"id": 61, "name": "Pakora Mix",               "category": "appetizers",  "price": 149, "description": "Assorted vegetables dipped in gram flour and deep-fried.", "tags": ["veg"], "spice": 2},
    {"id": 62, "name": "Paneer Tikka",             "category": "appetizers",  "price": 219, "description": "Marinated paneer grilled to perfection with bell peppers and onions.", "tags": ["veg", "special"], "spice": 2},
    {"id": 63, "name": "Bruschetta",               "category": "appetizers",  "price": 179, "description": "Crispy bread slices topped with tomato, garlic, and basil.", "tags": ["veg"], "spice": 0},
    {"id": 87, "name": "Mushroom Cutlet",          "category": "appetizers",  "price": 159, "description": "Crispy breaded mushroom patties served with tamarind chutney.", "tags": ["veg", "special"], "spice": 1},
    {"id": 88, "name": "Corn & Cheese Fritters",   "category": "appetizers",  "price": 149, "description": "Golden fritters with sweet corn and melted cheese.", "tags": ["veg"], "spice": 0},
    {"id": 89, "name": "Vegetable Kebab",          "category": "appetizers",  "price": 189, "description": "Grilled vegetable skewers with spiced yogurt coating.", "tags": ["veg", "special"], "spice": 2},
    {"id": 90, "name": "Garlic Bread with Cheese", "category": "appetizers",  "price": 169, "description": "Toasted bread with garlic butter and melted cheese.", "tags": ["veg"], "spice": 0},
    # Salads
    {"id": 64, "name": "Green Garden Salad",       "category": "salads",      "price": 149, "description": "Fresh mixed greens with cucumber, tomato, and house dressing.", "tags": ["veg"], "spice": 0},
    {"id": 65, "name": "Greek Salad",              "category": "salads",      "price": 189, "description": "Tomatoes, cucumbers, feta cheese, olives with olive oil dressing.", "tags": ["veg"], "spice": 0},
    {"id": 66, "name": "Beetroot & Walnut Salad",  "category": "salads",      "price": 199, "description": "Roasted beetroot with walnuts and tangy vinaigrette.", "tags": ["veg", "special"], "spice": 0},
    {"id": 67, "name": "Caprese Salad",            "category": "salads",      "price": 169, "description": "Fresh mozzarella, tomato, and basil with balsamic glaze.", "tags": ["veg"], "spice": 0},
    {"id": 91, "name": "Spinach & Pomegranate Salad","category": "salads",    "price": 179, "description": "Fresh spinach with pomegranate seeds and walnut dressing.", "tags": ["veg", "special"], "spice": 0},
    {"id": 92, "name": "Coleslaw",                 "category": "salads",      "price": 129, "description": "Crispy cabbage and carrot slaw with creamy dressing.", "tags": ["veg"], "spice": 0},
    {"id": 93, "name": "Corn & Bell Pepper Salad", "category": "salads",      "price": 149, "description": "Sweet corn with colorful peppers and lemon vinaigrette.", "tags": ["veg"], "spice": 0},
    {"id": 94, "name": "Mixed Leaf Salad",         "category": "salads",      "price": 159, "description": "Rocket, spinach, and mixed greens with honey mustard dressing.", "tags": ["veg"], "spice": 0},
    # Desserts
    {"id": 13, "name": "Gulab Jamun",              "category": "desserts",    "price": 129, "description": "Soft milk-solid dumplings soaked in rose-saffron sugar syrup.", "tags": ["veg", "special"], "spice": 0},
    {"id": 14, "name": "Chocolate Lava Cake",      "category": "desserts",    "price": 179, "description": "Warm fondant with a gooey molten centre, served with vanilla ice cream.", "tags": ["veg"], "spice": 0},
    {"id": 37, "name": "Rasmalai",                 "category": "desserts",    "price": 149, "description": "Soft cottage cheese patties soaked in chilled saffron milk.", "tags": ["veg", "special"], "spice": 0},
    {"id": 38, "name": "Kheer",                    "category": "desserts",    "price": 139, "description": "Creamy rice pudding simmered with cardamom and garnished with nuts.", "tags": ["veg"], "spice": 0},
    {"id": 39, "name": "Jalebi",                   "category": "desserts",    "price": 119, "description": "Crispy syrup-soaked spirals with bright orange crunch.", "tags": ["veg"], "spice": 0},
    {"id": 40, "name": "Strawberry Cheesecake",    "category": "desserts",    "price": 219, "description": "Smooth cheesecake topped with fresh strawberry compote.", "tags": ["veg"], "spice": 0},
    {"id": 41, "name": "Brownie Sundae",           "category": "desserts",    "price": 189, "description": "Warm chocolate brownie served with vanilla ice cream and nuts.", "tags": ["veg", "special"], "spice": 0},
    {"id": 42, "name": "Caramel Custard",          "category": "desserts",    "price": 129, "description": "Silky baked custard with a layer of golden caramel sauce.", "tags": ["veg"], "spice": 0},
    {"id": 43, "name": "Fruit Salad",              "category": "desserts",    "price": 139, "description": "Seasonal fruits drizzled with honey and lime.", "tags": ["veg"], "spice": 0},
    {"id": 44, "name": "Pistachio Kulfi",          "category": "desserts",    "price": 159, "description": "Rich frozen Indian ice cream with roasted pistachios.", "tags": ["veg"], "spice": 0},
    {"id": 95, "name": "Mango Sorbet",             "category": "desserts",    "price": 139, "description": "Refreshing frozen mango puree with a hint of cardamom.", "tags": ["veg", "special"], "spice": 0},
    {"id": 96, "name": "Tiramisu",                 "category": "desserts",    "price": 229, "description": "Classic Italian dessert with mascarpone, coffee, and cocoa.", "tags": ["veg"], "spice": 0},
    {"id": 97, "name": "Malai Peda",               "category": "desserts",    "price": 119, "description": "Rich milk-based sweets with a creamy texture.", "tags": ["veg"], "spice": 0},
    {"id": 98, "name": "Coconut Halwa",            "category": "desserts",    "price": 129, "description": "Slow-cooked coconut with jaggery and nuts.", "tags": ["veg", "special"], "spice": 0},
    {"id": 99, "name": "Paneer Jalebi",            "category": "desserts",    "price": 149, "description": "Sweet paneer strands in sugar syrup with a modern twist.", "tags": ["veg"], "spice": 0},
    # Drinks
    {"id": 15, "name": "Mango Lassi",              "category": "drinks",      "price": 99,  "description": "Chilled yoghurt drink blended with sweet Alphonso mangoes.", "tags": ["veg"], "spice": 0},
    {"id": 16, "name": "Masala Chai",              "category": "drinks",      "price": 59,  "description": "Aromatic spiced tea with ginger, cardamom, and cinnamon.", "tags": ["veg"], "spice": 1},
    {"id": 17, "name": "Virgin Mojito",            "category": "drinks",      "price": 129, "description": "Fresh mint, lime, and soda - perfectly refreshing.", "tags": ["veg"], "spice": 0},
    {"id": 45, "name": "Lemon Iced Tea",           "category": "drinks",      "price": 99,  "description": "Chilled tea brewed with lemon and mint.", "tags": ["veg"], "spice": 0},
    {"id": 46, "name": "Cold Coffee",              "category": "drinks",      "price": 119, "description": "Iced coffee blended with milk and a hint of chocolate.", "tags": ["veg"], "spice": 0},
    {"id": 47, "name": "Blueberry Smoothie",       "category": "drinks",      "price": 139, "description": "Creamy smoothie made with fresh blueberries and yogurt.", "tags": ["veg"], "spice": 0},
    {"id": 48, "name": "Watermelon Cooler",        "category": "drinks",      "price": 109, "description": "Fresh watermelon juice with a splash of lime and mint.", "tags": ["veg"], "spice": 0},
    {"id": 49, "name": "Orange Fizz",              "category": "drinks",      "price": 119, "description": "Sparkling orange soda with zesty citrus notes.", "tags": ["veg"], "spice": 0},
    {"id": 50, "name": "Mint Lime Soda",           "category": "drinks",      "price": 99,  "description": "Cooling soda with fresh mint and lime.", "tags": ["veg"], "spice": 0},
    {"id": 51, "name": "Strawberry Shake",         "category": "drinks",      "price": 149, "description": "Thick strawberry shake topped with whipped cream.", "tags": ["veg"], "spice": 0},
    {"id": 100,"name": "Aamras",                   "category": "drinks",      "price": 119, "description": "Thick mango pulp smoothie - summer favorite.", "tags": ["veg"], "spice": 0},
    {"id": 101,"name": "Chikhalwali",              "category": "drinks",      "price": 99,  "description": "Traditional sweet buttermilk drink with spices.", "tags": ["veg"], "spice": 0},
    {"id": 102,"name": "Ginger Lemon Honey Tea",   "category": "drinks",      "price": 89,  "description": "Warm herbal tea with ginger, lemon, and honey.", "tags": ["veg"], "spice": 1},
    {"id": 103,"name": "Sugarcane Juice",          "category": "drinks",      "price": 79,  "description": "Fresh sugarcane juice with lime and ginger.", "tags": ["veg"], "spice": 0},
    {"id": 104,"name": "Guava Smoothie",           "category": "drinks",      "price": 109, "description": "Creamy smoothie made with fresh guava and yogurt.", "tags": ["veg"], "spice": 0},
]

# ── System Prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are "Spice" - a friendly AI food assistant for Spice Garden Restaurant in Jodhpur, Rajasthan, India.

Your personality:
- Warm, enthusiastic, helpful like a genuine waiter
- Speak in Hinglish (mix of Hindi + English) naturally
- Use Hindi words like: bilkul, zaroor, bahut accha, ji, aapka swagat hai
- Use food emojis generously

Your jobs:
1. Greet customers warmly
2. Recommend dishes based on cuisine type, spice level, or diet (veg)
3. Answer questions about menu items and ingredients
4. Take orders - confirm dish name, quantity, and total price
5. Suggest chef specials (items tagged special)

FULL MENU:
""" + "\n".join([
    f"- {i['name']} ({i['category']}) Rs.{i['price']} | Spice:{i['spice']}/5 | Tags:{','.join(i['tags'])}"
    for i in MENU
]) + """

RULES:
- Keep replies short and conversational (2-4 sentences max)
- Only suggest Chinese items when asked for Chinese food
- Only suggest veg items (all items here are veg)
- When taking order, always confirm with total price
- Never make up dishes not in the menu above
"""

# ── In-memory order storage ──────────────────────────────────────────────────

orders_db = {}
order_counter = 1

# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Spice Garden API is running!", "model": MODEL_NAME}


@app.get("/api/menu")
def get_menu(category: Optional[str] = None):
    if category and category != "all":
        return [i for i in MENU if i["category"] == category]
    return MENU


@app.get("/api/menu/{item_id}")
def get_menu_item(item_id: int):
    item = next((i for i in MENU if i["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/api/chat")
def chat(req: ChatRequest):
    global order_counter
    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "stream": False,
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        reply = data["message"]["content"]
        return {"reply": reply}
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Ollama is not running! Run: ollama serve")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/orders")
def create_order(req: OrderRequest):
    global order_counter
    total = sum(i.price * i.qty for i in req.items)
    order_id = f"SG{order_counter:04d}"
    order_counter += 1

    order = {
        "order_id": order_id,
        "status": "confirmed",
        "items": [i.dict() for i in req.items],
        "total": total,
        "customer_name": req.customer_name,
        "address": req.address,
        "eta_minutes": 28,
    }
    orders_db[order_id] = order
    return order


@app.get("/api/orders/{order_id}")
def get_order(order_id: str):
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.get("/api/orders")
def get_all_orders():
    return list(orders_db.values())


@app.get("/api/health")
def health():
    try:
        res = requests.get("http://localhost:11434/api/tags", timeout=3)
        ollama_status = "running" if res.status_code == 200 else "error"
        models = [m["name"] for m in res.json().get("models", [])]
    except Exception:
        ollama_status = "not running"
        models = []

    return {
        "api": "ok",
        "ollama": ollama_status,
        "available_models": models,
    }