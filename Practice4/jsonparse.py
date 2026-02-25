import json

with open('sample-data.json') as file:
    data = json.load(file)

print("Interface Status")
print("=" * 80)
print(f"{'DN':<50} {'Description':<20} {'Speed':<10} {'MTU':<5}")
print(f"{'-' * 50:<50} {'-' * 20:<20} {'-' * 10:<10} {'-' * 5:<5}")

for item in data['imdata']:
    attributes = item['l1PhysIf']['attributes']
    dn = attributes['dn']
    description = attributes['descr']
    speed = attributes['speed']
    mtu = attributes['mtu']
    print(f"{dn:<50} {description:<20} {speed:<10} {mtu:<5}")