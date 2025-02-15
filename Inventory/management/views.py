from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

from django.shortcuts import render, redirect
from .models import CustomerModel

def customer_register(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        phone = request.POST["phone"]
        customer_model = CustomerModel()
        customer_model.create_customer(email, phone, password)
        return redirect("customer_login")  # Redirect to customer login page
    return render(request, "customer_register.html")

from .models import WorkplaceModel

from pymongo import MongoClient
from django.contrib.auth.hashers import make_password

def workplace_register(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        address = request.POST["address"]
        workplace_type = request.POST["workplace_type"]
        inventory_type = request.POST["inventory_type"]
        password = make_password(request.POST["password"])  # Hash password before storing

        workplace_model = WorkplaceModel()
        
        # Check if workplace already exists
        existing_workplace = workplace_model.find_workplace(email)
        if existing_workplace:
            return render(request, "workplace_register.html", {"error": "Email already registered"})

        # Store workplace details
        workplace_model.create_workplace(name, email, address, workplace_type, inventory_type, password)

        # Create a new MongoDB database for this workplace
        client = MongoClient("mongodb://localhost:27017/")
        new_db = client[name]  # Database name is the workplace name
        
        # Create collections for inventory and sales
        new_db.create_collection("sales")
        new_db.create_collection("inventory")

        return redirect("workplace_login")  # Redirect to workplace login page

    return render(request, "workplace_register.html")

def customer_login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        customer_model = CustomerModel()
        customer = customer_model.find_customer(email)
        if customer and customer["password"] == password:
            request.session["user_type"] = "customer"
            request.session["email"] = email
            return redirect("shop")  # Redirect to shop page
        else:
            return render(request, "customer_login.html", {"error": "Customer not found"})
    return render(request, "customer_login.html")

from pymongo import MongoClient
from django.contrib.auth.hashers import check_password

def workplace_login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        workplace_model = WorkplaceModel()
        workplace = workplace_model.find_workplace(email)  # Fetch workplace by email

        if workplace and check_password(password, workplace["password"]):  # Check hashed password
            request.session["user_type"] = "workplace"
            request.session["email"] = email
            request.session["workspace"] = workplace["name"]  # Store workplace name for DB access

            return redirect("dashboard")  # Redirect to dashboard
        else:
            return render(request, "workplace_login.html", {"error": "Invalid credentials"})

    return render(request, "workplace_login.html")


def shop(request):
    if request.session.get("user_type") == "customer":
        return render(request, "shop.html")
    return redirect("customer_login")


from django.shortcuts import render, redirect

from django.shortcuts import render, redirect
from django.http import JsonResponse
from pymongo import MongoClient
from django.contrib.sessions.models import Session

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["inventory_db"]

def dashboard(request):
    workspace = request.session.get("workspace")  # Fetch workspace name from session
    if not workspace:
        return redirect("workplace_login")

    return render(request, "dashboard.html", {"workspace": workspace})

# API to Fetch Sales & Inventory Data
def get_dashboard_data(request):
    workspace = request.session.get('workspace', None)
    if not workspace:
        return JsonResponse({'error': 'Not logged in'}, status=401)

    sales_data = db.sales.find({'workspace': workspace})
    inventory_data = db.inventory.find({'workspace': workspace})

    sales = [{"category": sale["category"], "amount": sale["amount"]} for sale in sales_data]
    inventory = [{"item": inv["item"], "quantity": inv["quantity"]} for inv in inventory_data]

    return JsonResponse({'sales': sales, 'inventory': inventory})

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def add_sale(request):
    workspace = request.session.get("workspace")
    if not workspace:
        return JsonResponse({"error": "Not logged in"}, status=401)

    if request.method == "POST":
        item = request.POST["item"]
        quantity = int(request.POST["quantity"])

        client = MongoClient("mongodb://localhost:27017/")
        db = client[workspace]
        db.sales.insert_one({"item": item, "quantity": quantity})

        return JsonResponse({"message": "Sale added successfully"})

@csrf_exempt
def add_inventory(request):
    workspace = request.session.get("workspace")
    if not workspace:
        return JsonResponse({"error": "Not logged in"}, status=401)

    if request.method == "POST":
        item = request.POST["item"]
        quantity = int(request.POST["quantity"])

        client = MongoClient("mongodb://localhost:27017/")
        db = client[workspace]
        db.inventory.insert_one({"item": item, "quantity": quantity})

        return JsonResponse({"message": "Item added to inventory"})
    
    from django.http import JsonResponse
from pymongo import MongoClient
from django.views.decorators.csrf import csrf_exempt
import json

client = MongoClient("mongodb://localhost:27017/")
main_db = client["workplaces"]  # Main DB storing all workspace details

def get_workspaces(request):
    """Fetch all workspaces."""
    workspaces = list(main_db["workplace_details"].find({}, {"_id": 0}))
    return JsonResponse({"workspaces": workspaces})

def get_menu(request, workspace):
    """Fetch menu from the selected workspace."""
    db = client[workspace]  # Select the correct workspace DB
    menu = list(db["menu"].find({}, {"_id": 0}))
    return JsonResponse({"menu": menu})

@csrf_exempt
def order(request):
    """Handle ordering process."""
    if request.method == "POST":
        data = json.loads(request.body)
        workspace = data["workspace"]
        dish_name = data["dish"]

        # Connect to the right database
        db = client[workspace]

        # Fetch dish ingredients
        dish = db["menu"].find_one({"name": dish_name})
        if not dish:
            return JsonResponse({"message": "Dish not found"}, status=404)

        ingredients_needed = dish["ingredients"]

        # Update inventory
        for ingredient, quantity in ingredients_needed.items():
            db["inventory"].update_one(
                {"name": ingredient},
                {"$inc": {"stock": -quantity}}
            )

        # Add sale record
        sale_record = {"dish": dish_name, "price": dish["price"], "date": "2025-02-14"}
        db["sales"].insert_one(sale_record)

        return JsonResponse({"message": "Order placed successfully!"})

    return JsonResponse({"message": "Invalid request"}, status=400)