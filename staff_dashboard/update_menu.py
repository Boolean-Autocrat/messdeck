import pandas as pd


def update_mess_menu():
    dict = {}
    day_arr = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    df = pd.read_excel("mess-menu.xlsx").transpose().values.tolist()

    for menu_day in df:
        count = 0
        mealCount = 0
        currentMeal = ""
        try:
            currentDate = menu_day[0].strftime("%Y-%m-%d")
        except:
            return (
                "Error: Date not found in column "
                + str(count)
                + ". Please check the excel file and try again.",
                True,
            )
            continue
        dict[currentDate] = {}
        for item in menu_day:
            if (
                isinstance(item, str)
                and item.strip()
                and item.lower() is not None
                and "*" not in item
                and item.lower() not in day_arr
            ):
                if item.lower() in ["breakfast", "lunch", "dinner"]:
                    currentMeal = item.upper()
                    dict[menu_day[0].strftime("%Y-%m-%d")][currentMeal] = []
                    mealCount += 1
                else:
                    dict[currentDate][currentMeal].append(item)
        if mealCount != 3:
            return (
                "Error: Incorrect number of meals in column for date: "
                + currentDate
                + ". Please check the excel file and try again.",
                True,
            )
        count += 1

    return (dict, False)
