from drafter import *
from dataclasses import dataclass

set_website_title("My Meal Planner")
set_site_information(
    author="Jai-dra08",
    description="Find a meal plan that fits your diet, budget, and goals.",
    sources="Thanks to the Drafter docs",
    planning=["plan.pdf", "design.pdf"],
    links=["https://github.com/Jai-dra08/your-repository"]
)
hide_debug_information()
set_website_framed(False)


# data
@dataclass
class Food:
    name: str
    classification: str
    price: float


@dataclass
class State:
    meal_type: str
    favored_foods: list[Food]
    budget: float
    chosen_diet: str
    personal_goal: str
    plan: list[Food]


MEAL_TYPES = ["Breakfast", "Lunch", "Dinner"]
DIETS = ["No diet", "Vegetarian", "Vegan", "Keto", "Mediterranean",
         "Pescatarian", "Flexitarian", "Carnivore"]

# data
MENU = {
    "Breakfast": [
        Food("Oatmeal", "Grain", 2.50),
        Food("Scrambled eggs", "Egg", 3.00),
        Food("Pancakes", "Grain", 4.00),
        Food("Bacon", "Meat", 3.50),
        Food("Banana bread", "Fruit", 2.75),
        Food("Yogurt parfait", "Dairy", 3.25),
        Food("Doughnuts", "Grain", 2.00),
    ],
    "Lunch": [
        Food("Tuna salad", "Seafood", 6.50),
        Food("Grilled cheese", "Dairy", 4.50),
        Food("Quinoa bowl", "Grain", 6.00),
        Food("Tomato soup", "Vegetable", 3.50),
        Food("Buffalo chicken wrap", "Meat", 7.00),
        Food("Pasta salad", "Grain", 5.00),
    ],
    "Dinner": [
        Food("Seared salmon", "Seafood", 12.00),
        Food("Chicken parmesan", "Meat", 11.00),
        Food("Vegetable stir fry", "Vegetable", 8.00),
        Food("Beef stew", "Meat", 10.00),
        Food("Macaroni and cheese", "Dairy", 6.00),
        Food("Fruit and rice bowl", "Fruit", 5.50),
        Food("Crab cakes", "Seafood", 13.00),
    ],
}

ALL_CLASSES = ["Meat", "Seafood", "Dairy", "Egg", "Vegetable", "Fruit", "Grain"]

# Which food classifications each diet allows
DIET_CLASSES = {
    "No diet": ALL_CLASSES,
    "Vegetarian": ["Dairy", "Egg", "Vegetable", "Fruit", "Grain"],
    "Vegan": ["Vegetable", "Fruit", "Grain"],
    "Keto": ["Meat", "Seafood", "Dairy", "Egg", "Vegetable"],
    "Mediterranean": ALL_CLASSES,
    "Pescatarian": ["Seafood", "Dairy", "Egg", "Vegetable", "Fruit", "Grain"],
    "Flexitarian": ALL_CLASSES,
    "Carnivore": ["Meat", "Seafood", "Egg", "Dairy"],
}

# Specific foods a diet excludes even when their classification is allowed
DIET_BANNED_NAMES = {
    "Mediterranean": ["Bacon", "Doughnuts"],
    "Keto": ["Banana bread"],
}


# helpers
def diet_ok(food: Food, diet: str) -> bool:
    """Does this food fit the diet?"""
    if food.classification not in DIET_CLASSES[diet]:
        return False
    if diet in DIET_BANNED_NAMES and food.name in DIET_BANNED_NAMES[diet]:
        return False
    return True


def parse_budget(text: str) -> float:
    """Turn the budget text into a number, or -1.0 if it isn't valid."""
    cleaned = text.strip()
    try:
        value = float(cleaned)
    except ValueError:
        return -1.0
    if value < 0:
        return -1.0
    return value


def find_favorites(meal_type: str, favorites_text: str) -> list[Food]:
    """Foods on this meal's menu whose name contains a typed favorite."""
    words = []
    for piece in favorites_text.split(","):
        cleaned = piece.strip().lower()
        if cleaned:
            words.append(cleaned)
    result = []
    for food in MENU[meal_type]:
        for word in words:
            if word in food.name.lower():
                result.append(food)
                break
    return result


def matching_foods(state: State) -> list[Food]:
    """Foods for the chosen meal that fit the budget and the diet."""
    result = []
    for food in MENU[state.meal_type]:
        if food.price <= state.budget:
            if diet_ok(food, state.chosen_diet):
                result.append(food)
    return result


def names_of(foods: list[Food]) -> list[str]:
    result = []
    for food in foods:
        result.append(food.name)
    return result


def total_cost(foods: list[Food]) -> float:
    total = 0.0
    for food in foods:
        total += food.price
    return total


def is_favored(state: State, food: Food) -> bool:
    for favorite in state.favored_foods:
        if favorite.name == food.name:
            return True
    return False


def money(amount: float) -> str:
    return "$" + format(amount, ".2f")


# routes
@route
def index(state: State) -> Page:
    return Page(state, [
        Header("Meal Planner"),
        "Tell us your diet, budget, and goals, and we'll help you build a meal plan.\n",
        Button("Create Plan", give_preferences),
    ])


@route
def give_preferences(state: State) -> Page:
    return Page(state, [
        Header("Your Preferences"),
        "Chosen meal type: ",
        SelectBox("meal_type", MEAL_TYPES, state.meal_type),
        "\nChosen diet: ",
        SelectBox("diet", DIETS, state.chosen_diet),
        "\nPrioritized foods (separate with commas): ",
        TextBox("favorites", ""),
        "\nYour ideal goal: ",
        TextBox("goal", state.personal_goal),
        "\nHighest price per food (in dollars): ",
        TextBox("budget", ""),
        "\n",
        Button("Submit", diet_results),
    ])


@route
def diet_results(state: State, meal_type: str, diet: str, favorites: str,
                 goal: str, budget: str) -> Page:
    amount = parse_budget(budget)
    if amount < 0:
        return Page(state, [
            Header("Invalid Budget"),
            "Please enter the budget as a number, like 8 or 12.50.\n",
            Button("Back", give_preferences),
        ])
    state.meal_type = meal_type
    state.chosen_diet = diet
    state.personal_goal = goal
    state.budget = amount
    state.favored_foods = find_favorites(meal_type, favorites)
    matches = matching_foods(state)
    return Page(state, [
        Header("Your Results"),
        "Meal type: " + state.meal_type + "\n",
        "Diet: " + state.chosen_diet + "\n",
        "Budget per food: " + money(state.budget) + "\n",
        "Goal: " + state.personal_goal + "\n",
        "Prioritized foods found: " + ", ".join(names_of(state.favored_foods)) + "\n",
        str(len(matches)) + " foods fit your diet and budget.\n",
        Button("See Foods", search_results),
        Button("Change Preferences", give_preferences),
    ])


@route
def search_results(state: State) -> Page:
    matches = matching_foods(state)
    content = [Header("Foods For You")]
    if len(matches) == 0:
        content.append("No foods fit your diet and budget. Try changing your preferences.\n")
        content.append(Button("Change Preferences", give_preferences))
        return Page(state, content)
    for food in matches:
        line = food.name + " (" + food.classification + ") " + money(food.price)
        if is_favored(state, food):
            line = "* " + line + "  <- one of your prioritized foods"
        content.append(line + "\n")
    content.append("\nPick a food to add: ")
    content.append(SelectBox("food_name", names_of(matches), matches[0].name))
    content.append(Button("Add to Plan", add_to_plan))
    content.append(Button("View My Plan", show_plan))
    return Page(state, content)


@route
def add_to_plan(state: State, food_name: str) -> Page:
    already = names_of(state.plan)
    if food_name not in already:
        for food in matching_foods(state):
            if food.name == food_name:
                state.plan.append(food)
    return show_plan(state)


@route
def remove_from_plan(state: State, food_name: str) -> Page:
    kept = []
    for food in state.plan:
        if food.name != food_name:
            kept.append(food)
    state.plan = kept
    return show_plan(state)


@route
def show_plan(state: State) -> Page:
    content = [Header("Your Current Plan")]
    if len(state.plan) == 0:
        content.append("Your plan is empty. Add some foods first.\n")
        content.append(Button("Find Foods", search_results))
        return Page(state, content)
    for food in state.plan:
        content.append(food.name + " - " + money(food.price) + "\n")
    content.append("Total: " + money(total_cost(state.plan)) + "\n")
    content.append("\nPick a food to remove: ")
    content.append(SelectBox("food_name", names_of(state.plan), state.plan[0].name))
    content.append(Button("Remove", remove_from_plan))
    content.append(Button("Add More Foods", search_results))
    content.append(Button("Finish Plan", complete_plan))
    return Page(state, content)


@route
def complete_plan(state: State) -> Page:
    content = [Header("Your Finished Meal Plan")]
    content.append("Goal: " + state.personal_goal + "\n")
    content.append("Diet: " + state.chosen_diet + "   Meal: " + state.meal_type + "\n\n")
    for food in state.plan:
        content.append("- " + food.name + " (" + money(food.price) + ")\n")
    content.append("\nTotal cost: " + money(total_cost(state.plan)) + "\n")
    content.append(Button("Edit Plan", show_plan))
    content.append(Button("Start A New Plan", start_over))
    return Page(state, content)


@route
def start_over(state: State) -> Page:
    state.meal_type = "Breakfast"
    state.favored_foods = []
    state.budget = 0.0
    state.chosen_diet = "No diet"
    state.personal_goal = ""
    state.plan = []
    return index(state)
    
# tests
assert_equal(diet_ok(Food("Bacon", "Meat", 3.5), "Vegan"), False)
assert_equal(diet_ok(Food("Oatmeal", "Grain", 2.5), "Vegan"), True)
assert_equal(diet_ok(Food("Bacon", "Meat", 3.5), "Mediterranean"), False)
assert_equal(parse_budget("12.50"), 12.5)
assert_equal(parse_budget("abc"), -1.0)
assert_equal(total_cost([Food("A", "Grain", 1.5), Food("B", "Meat", 2.0)]), 3.5)

start_server(State("Breakfast", [], 0.0, "No diet", "", []))
