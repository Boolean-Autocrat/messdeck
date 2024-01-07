import json
import re
from urllib.request import urlopen
import sqlite3
from datetime import datetime
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "messdeck.settings")
import django

django.setup()
from staff_dashboard.models import Menu, Food

static_breakfast = [
    "CHOICE OF EGG",
    "CORNFLAKES",
    "BREAD + JAM",
    "TEA + COFFEE",
    "MILK",
]

url = "https://raw.githubusercontent.com/Ka1Thakkar/bppc-mess-menu/main/data/menu.js"
response = urlopen(url)
data_str = response.read().decode("utf-8")
data_str = re.sub(r"//.*", "", data_str)
data_str = data_str.removeprefix("const data = ").removesuffix("export default data;")
data_str = (
    data_str.replace("\n", "")
    .replace("Day :", '"Day" :')
    .replace("Day:", '"Day" :')
    .replace("Date:", '"Date" :')
    .replace("Date :", '"Date" :')
    .replace("B:", '"B" :')
    .replace("L:", '"L" :')
    .replace("D:", '"D" :')
    .replace("'", '"')
    .strip()
)

data = data_str.split("},")
data[-1] = data[-1].replace("}]", "")
data[0] = data[0].replace("[{", "{")
data = [x + "}" for x in data]
for i in range(len(data)):
    data[i] = re.sub(r",\s*]", "]", data[i])
    data[i] = re.sub(r",\s*}", "}", data[i])
    data[i] = json.loads(data[i])

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()
for meal in data:
    date = datetime.strptime(meal["Date"], "%d %b %Y")
    date = date.strftime("%Y-%m-%d")
    meal["B"] = [x for x in meal["B"] if x != ""]
    if meal["Day"] != "Tuesday":
        meal["B"] = static_breakfast + meal["B"]
    else:
        meal["B"] = static_breakfast[1:] + meal["B"]
    meal["L"] = [x for x in meal["L"] if x != ""]
    meal["D"] = [x for x in meal["D"] if x != ""]
    for item in meal:
        if Menu.objects.filter(date=date).exists():
            menu = Menu.objects.get(date=date)
            menu.save()
            for food in meal["B"]:
                if not Food.objects.filter(menu=menu, meal="Breakfast", item=food):
                    food = Food(menu=menu, meal="Breakfast", item=food)
                    food.save()
            for food in meal["L"]:
                if not Food.objects.filter(menu=menu, meal="Lunch", item=food):
                    food = Food(menu=menu, meal="Lunch", item=food)
                    food.save()
            for food in meal["D"]:
                if not Food.objects.filter(menu=menu, meal="Dinner", item=food):
                    food = Food(menu=menu, meal="Dinner", item=food)
                    food.save()
        else:
            menu = Menu(date=date)
            menu.save()
            for food in meal["B"]:
                food = Food(menu=menu, meal="Breakfast", item=food)
                food.save()
            for food in meal["L"]:
                food = Food(menu=menu, meal="Lunch", item=food)
                food.save()
            for food in meal["D"]:
                food = Food(menu=menu, meal="Dinner", item=food)
                food.save()
