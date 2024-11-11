import flet as ft
from datetime import datetime
import requests

API_BASE_URL = "http://127.0.0.1:8000"


def add_bill(page):
    bill_items = []

    def add_bill_item(e):
        item_id_field = ft.TextField(label="Item ID", keyboard_type=ft.KeyboardType.NUMBER)
        quantity_field = ft.TextField(label="Quantity", keyboard_type=ft.KeyboardType.NUMBER)

        item_row = ft.Row([item_id_field, quantity_field], tight=True)
        bill_items_container.controls.append(item_row)
        bill_items.append((item_id_field, quantity_field))
        bill_items_container.update()

    def submit_bill(e):
        try:
            bill_date = datetime.strptime(date_field.value, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Invalid date format. Use YYYY-MM-DD"), bgcolor="red")
            page.snack_bar.open = True
            return

        bill_items_data = []
        for item_id_field, quantity_field in bill_items:
            try:
                item_id = int(item_id_field.value)
                quantity = int(quantity_field.value)
            except ValueError:
                page.snack_bar = ft.SnackBar(ft.Text("Invalid item ID or quantity"), bgcolor="red")
                page.snack_bar.open = True
                return

            item_response = requests.get(f"{API_BASE_URL}/items/{item_id}")
            if item_response.status_code == 200:
                item_data = item_response.json()
                rate = item_data["rate"]
                amount = rate * quantity
                bill_items_data.append({
                    "quantity": quantity,
                    "item_id": item_id,
                    "rate": rate,
                    "amount": amount
                })
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Item not found"), bgcolor="red")
                page.snack_bar.open = True
                return

        data = {
            "date": bill_date,
            "sl_number": int(sl_number_field.value),
            "company_id": int(company_id_field.value),
            "bill_items": bill_items_data
        }

        response = requests.post(f"{API_BASE_URL}/bills/", json=data)
        if response.status_code == 200:
            page.snack_bar = ft.SnackBar(ft.Text("Bill added successfully"))
            page.snack_bar.open = True
            page.go("/")
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Failed to add bill"), bgcolor="red")
            page.snack_bar.open = True

    date_field = ft.TextField(label="Date (YYYY-MM-DD)")
    sl_number_field = ft.TextField(label="SL Number", keyboard_type=ft.KeyboardType.NUMBER)
    company_id_field = ft.TextField(label="Company ID", keyboard_type=ft.KeyboardType.NUMBER)

    bill_items_container = ft.Column()
    add_item_button = ft.TextButton("Add Bill Item", on_click=add_bill_item)

    page.clean()
    page.add(
        ft.AppBar(
            title=ft.Text("Add Bill"),
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: page.go("/"))
        ),
        ft.Column([
            date_field,
            sl_number_field,
            company_id_field,
            add_item_button,
            bill_items_container,
            ft.ElevatedButton(text="Submit Bill", on_click=submit_bill)
        ])
    )


def get_bill(page):
    def fetch_bill(e):
        bill_id = int(bill_id_field.value)
        response = requests.get(f"{API_BASE_URL}/bills/{bill_id}")
        if response.status_code == 200:
            bill_data = response.json()
            items = "\n".join(
                [f"Item ID: {item['item_id']}, Quantity: {item['quantity']}, Amount: {item['amount']}" for item in
                 bill_data["bill_items"]])
            bill_info = f"Bill Date: {bill_data['bill']['date']}\nTotal: {bill_data['bill']['total']}\nItems:\n{items}"
            bill_result.value = bill_info
        else:
            bill_result.value = "Bill not found"
        page.update()

    bill_id_field = ft.TextField(label="Bill ID", keyboard_type=ft.KeyboardType.NUMBER)
    bill_result = ft.Text(value="", selectable=True)
    fetch_bill_button = ft.ElevatedButton("Fetch", on_click=fetch_bill)
    page.clean()
    page.add(
        ft.AppBar(
            title=ft.Text("Add Bill"),
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: page.go("/"))
        ),
        ft.Column([bill_id_field, fetch_bill_button, bill_result])
    )
    page.update()


def add_item(page):
    def submit_item(e):
        data = {
            "item_name": item_name_field.value,
            "rate": float(rate_field.value)
        }
        response = requests.post(f"{API_BASE_URL}/items/", json=data)
        if response.status_code == 200:
            page.snack_bar = ft.SnackBar(ft.Text("Item added successfully"))
            page.snack_bar.open = True
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Failed to add item"), bgcolor="red")
            page.snack_bar.open = True
        page.update()

    item_name_field = ft.TextField(label="Item Name")
    rate_field = ft.TextField(label="Rate", keyboard_type=ft.KeyboardType.NUMBER)
    submit_item_button = ft.ElevatedButton("Submit New Item", on_click=submit_item)
    page.clean()
    page.add(
        ft.AppBar(
            title=ft.Text("Add Bill"),
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: page.go("/"))
        ),
        ft.Column([item_name_field, rate_field, submit_item_button])
    )
    page.update()


def add_company(page):
    def submit_company(e):
        data = {
            "name": name_field.value,
            "address": address_field.value,
            "phone": phone_field.value,
            "city": city_field.value,
            "state": state_field.value,
            "zipcode": zipcode_field.value
        }
        response = requests.post(f"{API_BASE_URL}/companies/", json=data)
        if response.status_code == 200:
            snack_bar = ft.SnackBar(ft.Text("Company added successfully"))
            page.overlay.append(snack_bar)
            snack_bar.open = True
        else:
            snack_bar = ft.SnackBar(ft.Text("Failed to add company"), bgcolor="red")
            page.overlay.append(snack_bar)
            snack_bar.open = True
        page.update()

    name_field = ft.TextField(label="Name")
    address_field = ft.TextField(label="Address")
    phone_field = ft.TextField(label="Phone")
    city_field = ft.TextField(label="City")
    state_field = ft.TextField(label="State")
    zipcode_field = ft.TextField(label="Zipcode")
    submit_button = ft.ElevatedButton("Submit New Company", on_click=submit_company)

    page.clean()
    page.add(
        ft.AppBar(
            title=ft.Text("Add Bill"),
            leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: page.go("/"))
        ),
        ft.Column([name_field, address_field, phone_field, city_field, state_field, zipcode_field, submit_button])
    )
    page.update()


def main(page: ft.Page):
    page.clean()
    page.title = "Mariyam's Kitchen - Bill Migration"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.height = 600
    page.window.width = 800
    page.scroll = ft.ScrollMode.AUTO
    page.window.center()

    add_comp_btn = ft.CupertinoFilledButton(text="Add Company", on_click=lambda e: page.go("/add-company"))
    add_item_btn = ft.CupertinoFilledButton(text="Add Item", on_click=lambda e: page.go("/add-item"))
    add_bill_btn = ft.CupertinoFilledButton(text="Add Bill", on_click=lambda e: page.go("/add-bill"))
    get_bill_btn = ft.CupertinoFilledButton(text="Get Bill", on_click=lambda e: page.go("/get-bill"))

    def route_change(route):
        if page.route == "/":
            main(page)
        elif page.route == "/add-bill":
            add_bill(page)
        elif page.route == "/add-company":
            add_company(page)
        elif page.route == "/add-item":
            add_item(page)
        elif page.route == "/get-bill":
            get_bill(page)

    page.on_route_change = route_change

    title_container = ft.Container(
        ft.Text("Mariyam's Kitchen", style=ft.TextThemeStyle.HEADLINE_LARGE, color=ft.colors.ORANGE,
                weight=ft.FontWeight.BOLD),
        alignment=ft.Alignment(0, 0),
    )
    sub_title_container = ft.Container(
        ft.Text("Bill Migration", style=ft.TextThemeStyle.TITLE_SMALL, weight=ft.FontWeight.W_100),
        alignment=ft.Alignment(0, 0),
    )

    page.add(title_container, sub_title_container,
             ft.Column([add_comp_btn, add_item_btn, add_bill_btn, get_bill_btn], alignment=ft.MainAxisAlignment.CENTER,
                       horizontal_alignment=ft.CrossAxisAlignment.CENTER)
             )


ft.app(target=main)
