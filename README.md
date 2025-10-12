Library of Functions:
Universal Restaurant Inventory Management System —  library of functions to manage perishable and non-perishable supplies for restaurants. The library tracks batches, supports FIFO consumption, expiration alerts, waste reporting, and restock planning.

Team members and roles:

Canon Teselle — OOP & Integration

Benjamin Jahries — Function Library & Data 

Saad Alkinani — Testing & Reports 

For the function libraray all team members must implement 3-5 functions and contribute to this README


Main Project focus: Helps restaurants avoid stockouts, reduce food waste, and plan restocking by tracking per-batch inventory and predicting demand during peak periods.


Here is a list of functions that will be implememted by each person, 15 total functions: 

Ben (Function Library & Data) — implement:
add_new_item, add_batch, format_inventory_snapshot, export_inventory_csv, calculate_file_checksum

Canon (OOP & Integration) — implement:
generate_unique_id, reduce_stock_on_sale, compute_available_quantity, alert_expiring_items, generate_restock_plan 

Saad (Testing & Reports) — implement:
record_usage_pattern, generate_waste_report, mark_expired_items, calculate_reorder_list, forecast_demand 


Function Library:

Canon:

generate_unique_id(prefix='ITEM') – Generate a unique ID for a new inventory item.

reduce_stock_on_sale(inventory, item_id, quantity, use_fifo=True) – Reduce stock for sold items using FIFO.

compute_available_quantity(inventory, item_id, include_expired=False) – Compute total available quantity for an item.

alert_expiring_items(inventory, days_threshold=3) – List batches expiring within a threshold.

generate_restock_plan(inventory, usage_log, lead_time_days=3) – Produce a suggested restock plan.




Ben:

add_new_item(inventory, item_id, name, unit, threshold=0) – Add a new item to the inventory.

add_batch(inventory, item_id, quantity, expiration=None) – Add a batch for an item with quantity and optional expiration date.

format_inventory_snapshot(inventory) – Return a readable table of inventory items and quantities.

export_inventory_csv(inventory, filepath) – Export inventory batches to a CSV file.

calculate_file_checksum(path) – Compute SHA256 checksum of a file.



Saad:

record_usage_pattern(usage_log, item_id, quantity, timestamp=None) – Record a usage event for analysis.

generate_waste_report(waste_log, start, end) – Aggregate waste quantities per item within a date range.

mark_expired_items(inventory) – Mark expired batches as unusable and return list of affected items.

calculate_reorder_list(inventory) – Return items below threshold for restocking.

forecast_demand(usage_log, item_id, window_days=30) – Predict daily demand based on recent usage history.
