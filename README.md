
# Universal Restaurant Inventory Management System

Project Overview
The Universal Restaurant Inventory Management System  is a Python-based library designed to help restaurants efficiently manage both perishable and non-perishable inventory. The system tracks items in batches, supports FIFO (first-in-first-out) consumption, alerts for near-expiring stock, generates waste reports, forecasts demand, and produces restock plans.  

Goal: Reduce food waste, prevent stockouts, and streamline restocking by tracking per-batch inventory and predicting demand during peak periods.


Team Members and Roles

| Name           | Role                                    | Responsibilities |
|----------------|----------------------------------------|-----------------|
| Canon Teselle  | OOP & Integration                       | Design object-oriented classes; integrate Project 1 functions into Inventory, InventoryItem, Batch, UsageLog, and RestockPlanner classes |
| Benjamin Jahries | Function Library & Data                | Implement core inventory functions such as adding items, adding batches, formatting inventory snapshots, exporting CSV, and file checksums |
| Saad Alkinani  | Testing & Reports                       | Implement functions to record usage patterns, mark expired items, generate waste reports, forecast demand, and calculate reorder lists |

---

Features

Inventory Management
- Track all items in the restaurant inventory
- Manage perishable and non-perishable stock
- Record stock in **batches**, with quantity and expiration
- Compute available quantities (with optional inclusion of expired stock)
- Reduce stock on sales automatically (FIFO supported)
- Alert for near-expiring items

Usage and Demand Tracking
- Record item usage over time
- Forecast daily demand based on historical usage
- Generate reports of waste per item and per date range

Restocking
- Calculate items below restock thresholds
- Generate suggested restock plans based on usage patterns and lead times

Export and Reporting
- Format inventory snapshots in readable tables
- Export inventory data to CSV for external reporting
- Generate SHA256 file checksums for data integrity


Function Library (Project 1 Integration)

Canon’s Functions
- `generate_unique_id(prefix='ITEM')` – Create unique IDs for inventory items
- `reduce_stock_on_sale(inventory, item_id, quantity, use_fifo=True)` – Deduct sold quantities from inventory using FIFO
- `compute_available_quantity(inventory, item_id, include_expired=False)` – Compute total stock
- `alert_expiring_items(inventory, days_threshold=3)` – Return items that are close to expiration
- `generate_restock_plan(inventory, usage_log, lead_time_days=3)` – Suggest items to restock

Benjamin’s Functions
- `add_new_item(inventory, item_id, name, unit, threshold=0)` – Add a new item to inventory
- `add_batch(inventory, item_id, quantity, expiration=None)` – Add a batch for an existing item
- `format_inventory_snapshot(inventory)` – Return a formatted snapshot of all inventory items
- `export_inventory_csv(inventory, filepath)` – Export inventory data to CSV
- `calculate_file_checksum(path)` – Compute SHA256 checksum for a file

Saad’s Functions
- `record_usage_pattern(usage_log, item_id, quantity, timestamp=None)` – Record item usage
- `generate_waste_report(waste_log, start, end)` – Aggregate waste quantities per item within a date range
- `mark_expired_items(inventory)` – Mark expired batches as unusable
- `calculate_reorder_list(inventory)` – Return items below threshold
- `forecast_demand(usage_log, item_id, window_days=30)` – Predict daily demand for items

---

 Object-Oriented Classes (Project 2)

The Project 1 functions have been integrated into an object-oriented system:

1. Batch
   - Represents a single batch of an inventory item
   - Tracks quantity, expiration, and used quantity
   - Methods: `use(quantity)`, `is_expired()`, `available_quantity`, `__str__()`, `__repr__()`

2. InventoryItem
   - Represents an inventory item with multiple batches
   - Methods: `add_batch()`, `compute_available_quantity()`, `reduce_stock()`, `alert_expiring_items()`, `__str__()`, `__repr__()`

3. Inventory
   - Manages all inventory items
   - Methods: `add_new_item()`, `get_item()`, `mark_expired_items()`, `calculate_reorder_list()`, `format_snapshot()`, `export_csv()`, `generate_restock_plan()`

4. UsageLog
   - Tracks usage events per item
   - Methods: `record_usage()`, `forecast_demand()`, `generate_waste_report()`


Project 3

Overview: Python system to track perishable and non-perishable inventory. Handles batches, FIFO, expiration alerts, waste reporting, demand forecasting, and restock planning. Designed using inheritance, polymorphism, and composition.


Inheritance:

AbstractInventoryItem → PerishableItem, NonPerishableItem

Shared methods: compute_available_quantity, alert_expiring_items

Specialized behavior for perishable vs non-perishable items


Composition:

Inventory contains multiple inventory items

InventoryItem contains multiple batches


Polymorphism:

Methods like compute_available_quantity and alert_expiring_items behave differently depending on item type

Eliminates long if/else statements
