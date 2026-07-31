"""
UNIFIED MENU DATABASE — Spice Garden Restaurant
All dishes in ONE place: website menu + pan-India regional + international.

Fields:
- id: unique identifier
- name: dish name
- category: indian / chinese / continental / pizza / breads / appetizers /
            salads / desserts / drinks / regional_india / mexican
- price: in Rs.
- description: short description
- tags: list — veg, spicy, special
- spice: 0-5
- on_website: True = shown on website menu grid, False = hidden (AI-only, on request)
- region: optional, for regional dishes (e.g. "Gujarat", "Kerala")
"""

MENU = [
    # ══════════════════════════════════════════════════════════════════════
    # WEBSITE MENU — shown on the site (on_website: True)
    # ══════════════════════════════════════════════════════════════════════

    # Indian
    {"id": 1,  "name": "Dal Baati Churma",        "category": "indian",      "price": 249, "description": "Rajasthani classic - baked wheat dumplings with spiced lentils and sweet crumble.", "tags": ["veg", "special"], "spice": 2, "on_website": True},
    {"id": 2,  "name": "Gatte Ki Sabzi",           "category": "indian",      "price": 269, "description": "Gram flour dumplings simmered in a tangy yogurt-based masala.", "tags": ["veg", "special"], "spice": 3, "on_website": True},
    {"id": 3,  "name": "Paneer Butter Masala",     "category": "indian",      "price": 329, "description": "Cubes of cottage cheese simmered in a rich tomato-butter gravy.", "tags": ["veg", "special"], "spice": 2, "on_website": True},
    {"id": 4,  "name": "Paneer Tikka Masala",      "category": "indian",      "price": 289, "description": "Grilled cottage cheese cubes in a rich, smoky masala gravy.", "tags": ["veg"], "spice": 3, "on_website": True},
    {"id": 5,  "name": "Veg Dum Biryani",          "category": "indian",      "price": 299, "description": "Slow-cooked basmati rice layered with spiced vegetables.", "tags": ["veg", "special"], "spice": 3, "on_website": True},
    {"id": 6,  "name": "Kadhi Pakora",             "category": "indian",      "price": 199, "description": "Yoghurt-based curry with crispy gram flour fritters.", "tags": ["veg"], "spice": 2, "on_website": True},
    {"id": 18, "name": "Chole Bhature",            "category": "indian",      "price": 249, "description": "Spicy chickpea curry served with fluffy deep-fried bread.", "tags": ["veg", "special"], "spice": 3, "on_website": True},
    {"id": 19, "name": "Aloo Paratha",             "category": "indian",      "price": 149, "description": "Stuffed flatbread with spiced potato filling, served with butter and pickle.", "tags": ["veg"], "spice": 2, "on_website": True},
    {"id": 21, "name": "Paneer Kadai",             "category": "indian",      "price": 319, "description": "Flavoursome kadai gravy with bell peppers and freshly ground spices.", "tags": ["veg"], "spice": 3, "on_website": True},
    {"id": 22, "name": "Palak Paneer",             "category": "indian",      "price": 289, "description": "Creamy spinach curry with cubes of cottage cheese.", "tags": ["veg"], "spice": 2, "on_website": True},
    {"id": 68, "name": "Rajasthani Ker Sangri",    "category": "indian",      "price": 279, "description": "Dried beans and berries cooked in traditional Rajasthani spices.", "tags": ["veg", "special"], "spice": 2, "on_website": True},
    {"id": 70, "name": "Baingan Bharta",           "category": "indian",      "price": 219, "description": "Roasted eggplant mashed with onions, tomatoes, and spices.", "tags": ["veg"], "spice": 2, "on_website": True},
    {"id": 71, "name": "Rajma Chawal",             "category": "indian",      "price": 249, "description": "Kidney beans curry served with fragrant basmati rice.", "tags": ["veg"], "spice": 2, "on_website": True},

    # Chinese
    {"id": 7,  "name": "Chilli Paneer",            "category": "chinese",     "price": 319, "description": "Crispy paneer tossed with capsicum, onions, and bold chilli sauces.", "tags": ["veg", "spicy", "special"], "spice": 4, "on_website": True},
    {"id": 8,  "name": "Veg Manchurian",           "category": "chinese",     "price": 229, "description": "Crispy veggie balls in a tangy, spicy Manchurian sauce.", "tags": ["veg", "spicy"], "spice": 3, "on_website": True},
    {"id": 9,  "name": "Hakka Noodles",            "category": "chinese",     "price": 249, "description": "Stir-fried noodles with colourful vegetables in a light soy-garlic sauce.", "tags": ["veg"], "spice": 2, "on_website": True},
    {"id": 10, "name": "Honey Garlic Baby Corn",   "category": "chinese",     "price": 299, "description": "Baby corn tossed in a sweet honey-garlic glaze.", "tags": ["veg", "special"], "spice": 1, "on_website": True},
    {"id": 20, "name": "Veg Spring Rolls",         "category": "chinese",     "price": 199, "description": "Crispy rolls stuffed with crunchy mixed vegetables.", "tags": ["veg", "special"], "spice": 2, "on_website": True},
    {"id": 23, "name": "Schezwan Fried Rice",      "category": "chinese",     "price": 219, "description": "Wok-tossed rice with vegetables in a spicy schezwan sauce.", "tags": ["veg", "spicy"], "spice": 4, "on_website": True},
    {"id": 27, "name": "Honey Chilli Broccoli",    "category": "chinese",     "price": 239, "description": "Crunchy broccoli glazed in sweet and spicy honey-chilli dressing.", "tags": ["veg", "special"], "spice": 2, "on_website": True},

    # Continental
    {"id": 11, "name": "Mushroom Risotto",         "category": "continental", "price": 329, "description": "Creamy Arborio rice with wild mushrooms and truffle oil.", "tags": ["veg", "special"], "spice": 0, "on_website": True},
    {"id": 12, "name": "Grilled Veg Pasta",        "category": "continental", "price": 339, "description": "Penne with grilled vegetables in herb tomato-basil sauce.", "tags": ["veg"], "spice": 1, "on_website": True},
    {"id": 31, "name": "Creamy Tomato Basil Pasta","category": "continental", "price": 329, "description": "Penne in velvety tomato-basil cream sauce.", "tags": ["veg"], "spice": 1, "on_website": True},
    {"id": 34, "name": "Mushroom Truffle Pizza",   "category": "continental", "price": 399, "description": "Thin crust pizza with mushrooms, truffle oil, and mozzarella.", "tags": ["veg", "special"], "spice": 0, "on_website": True},

    # Pizza
    {"id": 52, "name": "Margherita Pizza",         "category": "pizza",       "price": 349, "description": "Classic pizza with tomato, mozzarella, and basil.", "tags": ["veg", "special"], "spice": 0, "on_website": True},
    {"id": 53, "name": "Paneer & Onion Pizza",     "category": "pizza",       "price": 379, "description": "Paneer chunks and caramelised onions on crispy crust.", "tags": ["veg", "special"], "spice": 1, "on_website": True},
    {"id": 55, "name": "Spicy Jalapeno Pizza",     "category": "pizza",       "price": 389, "description": "Fiery jalapenos, green chillies, and mozzarella.", "tags": ["veg", "spicy"], "spice": 4, "on_website": True},

    # Breads
    {"id": 56, "name": "Garlic Naan",              "category": "breads",      "price": 89,  "description": "Soft bread brushed with garlic and herb butter.", "tags": ["veg"], "spice": 0, "on_website": True},
    {"id": 57, "name": "Cheese Naan",              "category": "breads",      "price": 109, "description": "Fluffy naan with melted cheese and aromatic spices.", "tags": ["veg", "special"], "spice": 0, "on_website": True},
    {"id": 58, "name": "Tandoori Roti",            "category": "breads",      "price": 49,  "description": "Whole wheat flatbread from traditional tandoor.", "tags": ["veg"], "spice": 0, "on_website": True},

    # Appetizers
    {"id": 60, "name": "Samosa",                   "category": "appetizers",  "price": 79,  "description": "Crispy pastry stuffed with spiced potato and peas.", "tags": ["veg", "special"], "spice": 2, "on_website": True},
    {"id": 62, "name": "Paneer Tikka",             "category": "appetizers",  "price": 219, "description": "Marinated paneer grilled with bell peppers and onions.", "tags": ["veg", "special"], "spice": 2, "on_website": True},
    {"id": 87, "name": "Mushroom Cutlet",          "category": "appetizers",  "price": 159, "description": "Crispy mushroom patties with tamarind chutney.", "tags": ["veg", "special"], "spice": 1, "on_website": True},

    # Desserts
    {"id": 13, "name": "Gulab Jamun",              "category": "desserts",    "price": 129, "description": "Milk dumplings in rose-saffron sugar syrup.", "tags": ["veg", "special"], "spice": 0, "on_website": True},
    {"id": 14, "name": "Chocolate Lava Cake",      "category": "desserts",    "price": 179, "description": "Warm fondant with molten centre and vanilla ice cream.", "tags": ["veg"], "spice": 0, "on_website": True},
    {"id": 37, "name": "Rasmalai",                 "category": "desserts",    "price": 149, "description": "Cottage cheese patties in chilled saffron milk.", "tags": ["veg", "special"], "spice": 0, "on_website": True},
    {"id": 96, "name": "Tiramisu",                 "category": "desserts",    "price": 229, "description": "Italian dessert with mascarpone, coffee, and cocoa.", "tags": ["veg"], "spice": 0, "on_website": True},

    # Drinks
    {"id": 15, "name": "Mango Lassi",              "category": "drinks",      "price": 99,  "description": "Chilled yoghurt drink with Alphonso mangoes.", "tags": ["veg"], "spice": 0, "on_website": True},
    {"id": 16, "name": "Masala Chai",              "category": "drinks",      "price": 59,  "description": "Spiced tea with ginger, cardamom, and cinnamon.", "tags": ["veg"], "spice": 1, "on_website": True},
    {"id": 17, "name": "Virgin Mojito",            "category": "drinks",      "price": 129, "description": "Fresh mint, lime, and soda.", "tags": ["veg"], "spice": 0, "on_website": True},
    {"id": 46, "name": "Cold Coffee",              "category": "drinks",      "price": 119, "description": "Iced coffee blended with milk and chocolate.", "tags": ["veg"], "spice": 0, "on_website": True},

    # ══════════════════════════════════════════════════════════════════════
    # HIDDEN — Pan-India regional dishes (on_website: False, AI-only)
    # ══════════════════════════════════════════════════════════════════════
    {"id": 501, "name": "Amritsari Kulcha",         "category": "regional_india", "price": 149, "description": "Stuffed leavened bread baked in tandoor, served with chole.", "tags": ["veg"], "spice": 2, "on_website": False, "region": "Punjab"},
    {"id": 502, "name": "Sarson Ka Saag",           "category": "regional_india", "price": 219, "description": "Mustard greens curry served with makki di roti.", "tags": ["veg"], "spice": 2, "on_website": False, "region": "Punjab"},
    {"id": 503, "name": "Pani Puri",                "category": "regional_india", "price": 79,  "description": "Crispy hollow puris filled with spicy tangy water and potato.", "tags": ["veg", "spicy"], "spice": 4, "on_website": False, "region": "North India"},
    {"id": 504, "name": "Bhel Puri",                "category": "regional_india", "price": 89,  "description": "Puffed rice mixed with veggies, chutneys and sev.", "tags": ["veg"], "spice": 2, "on_website": False, "region": "Mumbai"},
    {"id": 505, "name": "Vada Pav",                 "category": "regional_india", "price": 69,  "description": "Spiced potato fritter in a soft bun with chutneys.", "tags": ["veg", "spicy"], "spice": 3, "on_website": False, "region": "Mumbai"},
    {"id": 506, "name": "Pav Bhaji",                "category": "regional_india", "price": 149, "description": "Buttery mixed vegetable mash served with soft bread rolls.", "tags": ["veg", "special"], "spice": 3, "on_website": False, "region": "Mumbai"},
    {"id": 507, "name": "Pyaaz Kachori",            "category": "regional_india", "price": 59,  "description": "Flaky pastry stuffed with spiced onion filling.", "tags": ["veg", "spicy"], "spice": 3, "on_website": False, "region": "Rajasthan"},
    {"id": 508, "name": "Mirchi Bada",              "category": "regional_india", "price": 79,  "description": "Large green chillies stuffed with spiced potato, batter-fried.", "tags": ["veg", "spicy"], "spice": 4, "on_website": False, "region": "Rajasthan"},
    {"id": 509, "name": "Ghevar",                   "category": "regional_india", "price": 129, "description": "Disc-shaped sweet soaked in sugar syrup, topped with rabri.", "tags": ["veg"], "spice": 0, "on_website": False, "region": "Rajasthan"},
    {"id": 510, "name": "Dhokla",                   "category": "regional_india", "price": 99,  "description": "Steamed savoury cake made from fermented gram flour batter.", "tags": ["veg"], "spice": 1, "on_website": False, "region": "Gujarat"},
    {"id": 511, "name": "Khandvi",                  "category": "regional_india", "price": 109, "description": "Thin rolled gram-flour bites tempered with mustard seeds.", "tags": ["veg"], "spice": 1, "on_website": False, "region": "Gujarat"},
    {"id": 512, "name": "Undhiyu",                  "category": "regional_india", "price": 219, "description": "Mixed winter vegetable casserole cooked slow with spices.", "tags": ["veg", "special"], "spice": 2, "on_website": False, "region": "Gujarat"},
    {"id": 513, "name": "Thepla",                   "category": "regional_india", "price": 89,  "description": "Spiced flatbread made with fenugreek leaves.", "tags": ["veg"], "spice": 1, "on_website": False, "region": "Gujarat"},
    {"id": 514, "name": "Fafda Jalebi",             "category": "regional_india", "price": 119, "description": "Crispy gram-flour strips served with sweet jalebi.", "tags": ["veg"], "spice": 1, "on_website": False, "region": "Gujarat"},
    {"id": 515, "name": "Masala Dosa",              "category": "regional_india", "price": 149, "description": "Crispy rice crepe filled with spiced potato masala.", "tags": ["veg", "special"], "spice": 2, "on_website": False, "region": "South India"},
    {"id": 516, "name": "Idli Sambar",              "category": "regional_india", "price": 89,  "description": "Steamed rice cakes served with lentil soup and chutney.", "tags": ["veg"], "spice": 2, "on_website": False, "region": "South India"},
    {"id": 517, "name": "Medu Vada",                "category": "regional_india", "price": 79,  "description": "Crispy fried lentil doughnuts served with sambar.", "tags": ["veg"], "spice": 2, "on_website": False, "region": "South India"},
    {"id": 518, "name": "Uttapam",                  "category": "regional_india", "price": 119, "description": "Thick savoury pancake topped with onions and tomatoes.", "tags": ["veg"], "spice": 2, "on_website": False, "region": "South India"},
    {"id": 519, "name": "Curd Rice",                "category": "regional_india", "price": 99,  "description": "Comforting rice mixed with yogurt, tempered with mustard seeds.", "tags": ["veg"], "spice": 0, "on_website": False, "region": "South India"},
    {"id": 520, "name": "Bisi Bele Bath",           "category": "regional_india", "price": 159, "description": "Spicy rice and lentil dish cooked with vegetables and tamarind.", "tags": ["veg", "spicy"], "spice": 3, "on_website": False, "region": "Karnataka"},
    {"id": 521, "name": "Pongal",                   "category": "regional_india", "price": 109, "description": "Rice and moong dal porridge tempered with pepper and cumin.", "tags": ["veg"], "spice": 1, "on_website": False, "region": "Tamil Nadu"},
    {"id": 522, "name": "Misal Pav",                "category": "regional_india", "price": 129, "description": "Spicy sprouted lentil curry topped with farsan, served with pav.", "tags": ["veg", "spicy", "special"], "spice": 4, "on_website": False, "region": "Maharashtra"},
    {"id": 523, "name": "Sabudana Khichdi",         "category": "regional_india", "price": 99,  "description": "Tapioca pearls sautéed with peanuts and mild spices.", "tags": ["veg"], "spice": 2, "on_website": False, "region": "Maharashtra"},
    {"id": 524, "name": "Puran Poli",               "category": "regional_india", "price": 119, "description": "Sweet flatbread stuffed with jaggery and lentil filling.", "tags": ["veg"], "spice": 0, "on_website": False, "region": "Maharashtra"},
    {"id": 525, "name": "Aloo Posto",               "category": "regional_india", "price": 159, "description": "Potatoes cooked in a poppy seed paste.", "tags": ["veg"], "spice": 1, "on_website": False, "region": "West Bengal"},
    {"id": 526, "name": "Cholar Dal",               "category": "regional_india", "price": 139, "description": "Bengal gram lentils cooked with coconut and mild spices.", "tags": ["veg"], "spice": 1, "on_website": False, "region": "West Bengal"},
    {"id": 527, "name": "Rasgulla",                 "category": "regional_india", "price": 89,  "description": "Soft spongy cottage cheese balls soaked in light sugar syrup.", "tags": ["veg"], "spice": 0, "on_website": False, "region": "West Bengal"},
    {"id": 528, "name": "Mishti Doi",               "category": "regional_india", "price": 79,  "description": "Sweetened fermented yogurt, a classic Bengali dessert.", "tags": ["veg"], "spice": 0, "on_website": False, "region": "West Bengal"},
    {"id": 529, "name": "Dum Aloo Kashmiri",        "category": "regional_india", "price": 199, "description": "Baby potatoes cooked in a rich yogurt-based gravy.", "tags": ["veg", "spicy"], "spice": 3, "on_website": False, "region": "Kashmir"},
    {"id": 530, "name": "Kashmiri Pulao",           "category": "regional_india", "price": 229, "description": "Fragrant rice cooked with dry fruits and mild spices.", "tags": ["veg"], "spice": 1, "on_website": False, "region": "Kashmir"},
    {"id": 531, "name": "Litti Chokha",             "category": "regional_india", "price": 149, "description": "Roasted wheat balls stuffed with sattu, served with mashed veggies.", "tags": ["veg"], "spice": 2, "on_website": False, "region": "Bihar"},
    {"id": 532, "name": "Dahi Vada",                "category": "regional_india", "price": 99,  "description": "Lentil dumplings soaked in spiced yogurt.", "tags": ["veg"], "spice": 2, "on_website": False, "region": "North India"},
    {"id": 533, "name": "Avial",                    "category": "regional_india", "price": 169, "description": "Mixed vegetables in a coconut and yogurt gravy.", "tags": ["veg"], "spice": 1, "on_website": False, "region": "Kerala"},
    {"id": 534, "name": "Puttu with Kadala Curry",  "category": "regional_india", "price": 139, "description": "Steamed rice cake served with black chickpea curry.", "tags": ["veg"], "spice": 2, "on_website": False, "region": "Kerala"},
    {"id": 535, "name": "Aam Ras",                  "category": "regional_india", "price": 119, "description": "Fresh pureed Alphonso mango pulp, a summer favourite.", "tags": ["veg", "special"], "spice": 0, "on_website": False, "region": "Gujarat/UP"},
    {"id": 536, "name": "Kesar Pista Kulfi",        "category": "regional_india", "price": 99,  "description": "Rich saffron pistachio frozen dessert.", "tags": ["veg"], "spice": 0, "on_website": False, "region": "North India"},
    {"id": 537, "name": "Thandai",                  "category": "regional_india", "price": 99,  "description": "Chilled milk drink infused with nuts, saffron and spices.", "tags": ["veg"], "spice": 0, "on_website": False, "region": "North India"},
    {"id": 538, "name": "Filter Coffee",            "category": "regional_india", "price": 59,  "description": "Strong South Indian coffee with frothy milk.", "tags": ["veg"], "spice": 0, "on_website": False, "region": "South India"},
    {"id": 539, "name": "Aloo Tikki Chaat",         "category": "regional_india", "price": 99,  "description": "Crispy potato patties topped with chutneys and yogurt.", "tags": ["veg", "spicy"], "spice": 3, "on_website": False, "region": "Delhi"},

    # ══════════════════════════════════════════════════════════════════════
    # HIDDEN — Mexican dishes (on_website: False, AI-only)
    # ══════════════════════════════════════════════════════════════════════
    {"id": 601, "name": "Veg Burrito",              "category": "mexican", "price": 299, "description": "Flour tortilla stuffed with spiced rice, beans, salsa, and sour cream.", "tags": ["veg"], "spice": 2, "on_website": False},
    {"id": 602, "name": "Nachos with Salsa",        "category": "mexican", "price": 199, "description": "Crispy tortilla chips with tomato salsa, guacamole, and sour cream.", "tags": ["veg"], "spice": 2, "on_website": False},
    {"id": 603, "name": "Veg Quesadilla",           "category": "mexican", "price": 249, "description": "Grilled flour tortilla filled with cheese, peppers, and spiced vegetables.", "tags": ["veg"], "spice": 2, "on_website": False},
    {"id": 604, "name": "Veg Tacos (2 pcs)",        "category": "mexican", "price": 229, "description": "Soft corn tacos with seasoned veggies, salsa, and fresh lime.", "tags": ["veg"], "spice": 3, "on_website": False},
    {"id": 605, "name": "Guacamole & Chips",        "category": "mexican", "price": 179, "description": "Fresh avocado guacamole with crispy tortilla chips.", "tags": ["veg"], "spice": 1, "on_website": False},
    {"id": 606, "name": "Chilli Cheese Fries",      "category": "mexican", "price": 189, "description": "Crispy fries topped with spicy chilli, melted cheese, and jalapenos.", "tags": ["veg", "spicy"], "spice": 4, "on_website": False},
    {"id": 607, "name": "Churros with Chocolate",   "category": "mexican", "price": 159, "description": "Crispy fried dough sticks dusted with cinnamon sugar, served with chocolate dip.", "tags": ["veg"], "spice": 0, "on_website": False},
]

CATEGORIES = sorted(set(item["category"] for item in MENU if item["on_website"]))
