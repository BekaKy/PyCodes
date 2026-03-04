import re
import json
with open('raw.txt', 'r', encoding='utf-8') as file:
    text = file.read()

pattern_price = r"Стоимость\s(\d+,\d+)"
prices = re.findall(pattern_price, text)
print(prices)


pattern_names = r"^\d+\.\n(.+)"
names = re.findall(pattern_names, text, re.MULTILINE)
print(names)


pattern_quantities = r'(\d+,\d+)\s*x\s*(\d+,\d+)'
quantities = re.findall(pattern_quantities, text)
total = 0
for qty, price in quantities:
    qty = float(qty.replace(',', '.'))
    price = float(price.replace(',', '.'))
    subtotal = qty * price
    total += subtotal
    print(f"{qty} x {price} = {subtotal:.2f}")

print(f"Total: {total:.2f}")


pattern_dates = r'Время:\s+(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})'
dates = re.findall(pattern_dates, text)


payment_method = r"Банковская карта:"
method = re.findall(payment_method, text)


items = []
for name, (qty, price_per_unit), total_price in zip(names, quantities, prices):
    qty = float(qty.replace(',', '.'))
    price_per_unit = float(price_per_unit.replace(',', '.'))
    items.append({
        "name": name,
        "quantity": qty,
        "price per unit": price_per_unit,
        "subtotal": float(total_price.replace(',', '.'))
    })

receipt = {
    "date": dates[0][0] if dates else None,
    "time": dates[0][1] if dates else None,
    "payment method": "Банковская карта" if method else "Наличные",
    "items": items,
    "total": sum(item["subtotal"] for item in items)
}

print(json.dumps(receipt, ensure_ascii=False, indent=2))

