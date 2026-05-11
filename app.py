from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Load data 
df = pd.read_csv("allergy.csv")
df.columns = df.columns.str.strip()

NON_ALLERGEN = ['Dish Name', 'Category']
ALLERGEN_COLS = [col for col in df.columns if col not in NON_ALLERGEN]


# ---------------- TEST ROUTE ----------------
@app.route("/", methods=["GET", "POST"])
def home():

    result = None
    dish_name = ""

    if request.method == "POST":
        print("Form data:", request.form)
        print("Filter mode:", request.form.get("filter_mode"))
        print("Selected allergens:", request.form.getlist("allergens"))
        dish_name = request.form.get("dish")
        dish = dish_name

        match = df.copy()

        #Search
        if dish.strip():
            match = match[match['Dish Name'].str.contains(dish, case = False, na= False)]
        #Filter
        filter_mode = request.form.get("filter_mode")

        #select allergy
        selected_allergens = request.form.getlist("allergens")

        if selected_allergens:
            for allergen in selected_allergens:
                if allergen in ALLERGEN_COLS:
                    if filter_mode == "with":
                        match = match[match[allergen]==1]
                    elif filter_mode == "without":
                        match = match[match[allergen]==0]

        if match.empty:

            result = {
                "found": False
            }

        else:

            dishes = []

            for _, row in match.iterrows():

                allergens = [
                    col for col in ALLERGEN_COLS
                    if row[col] == 1
                ]

                dishes.append({
                    "dish": row["Dish Name"],
                    "category": row["Category"],
                    "allergens": allergens
                })

            result = {
                "found": True,
                "dishes": dishes
            }

    return render_template(
        "index.html",
        result=result,
        dish_name=dish_name,
        allergens = ALLERGEN_COLS
    )


# ---------------- SEARCH FUNCTION ----------------
@app.route("/search", methods=["GET"])
def search_dish():
    dish = request.args.get("dish")

    if not dish:
        return {"error": "No dish provided"}

    match = df[df['Dish Name'].str.contains(dish, case=False, na=False)]

    if match.empty:
        return {"result": "not found"}

    row = match.iloc[0]
    allergens = [col for col in ALLERGEN_COLS if row[col] == 1]

    return {
        "dish": row["Dish Name"],
        "category": row["Category"],
        "allergens": allergens
    }


# ---------------- ADD DISH ----------------
@app.route("/add", methods=["POST"])
def add_dish():
    global df

    data = request.json

    new_row = {
        "Dish Name": data["dish"],
        "Category": data["category"]
    }

    for col in ALLERGEN_COLS:
        new_row[col] = 1 if col in data.get("allergens", []) else 0

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv("allergy.csv", index=False)

    return {"status": "added"}


# ---------------- DELETE DISH ----------------
@app.route("/delete", methods=["POST"])
def delete_dish():
    global df

    dish = request.json.get("dish")
    df = df[df["Dish Name"] != dish]
    df.to_csv("allergy.csv", index=False)

    return {"status": "deleted"}


# ---------------- RUN ----------------
if __name__ == "__main__":
    print("Starting server...")
    app.run(host="0.0.0.0", port=5000, debug=True)