# Class Implementation

import uuid
from datetime import date, datetime, timedelta
import csv
from collections import defaultdict


# Batch class - represents a batch of an inventory item
class Batch:
    # Initialize a batch with quantity and optional expiration
    def __init__(self, quantity: int, expiration: date = None):
        # Validate quantity
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        self._quantity = quantity  # Total quantity in this batch
        # Validate expiration if provided
        if expiration and not isinstance(expiration, date):
            raise TypeError("Expiration must be a datetime.date object")
        self._expiration = expiration  # Expiration date
        self._used_quantity = 0  # Track used quantity
        self._batch_id = str(uuid.uuid4())[:8]  # Unique batch ID

    # Property to get batch ID (read-only)
    @property
    def batch_id(self):
        return self._batch_id

    # Property to get expiration date
    @property
    def expiration(self):
        return self._expiration

    # Property to get available quantity
    @property
    def available_quantity(self):
        return self._quantity - self._used_quantity

    # Check if the batch is expired
    def is_expired(self):
        return self._expiration and self._expiration < date.today()

    # Use a certain quantity from this batch
    def use(self, quantity: int):
        # Ensure enough stock
        if quantity > self.available_quantity:
            raise ValueError("Not enough quantity in batch")
        self._used_quantity += quantity

    # String representation for printing
    def __str__(self):
        status = "Expired" if self.is_expired() else "Good"
        return f"Batch {self._batch_id}: {self.available_quantity} units ({status})"

    # Debug representation
    def __repr__(self):
        return f"Batch({self._batch_id}, {self._quantity}, {self._expiration})"
    






# InventoryItem class - represents an item in inventory
class InventoryItem:
    # Initialize inventory item
    def __init__(self, item_id: str, name: str, unit: str, threshold: int = 0):
        # Validate parameters
        if not item_id or not isinstance(item_id, str):
            raise ValueError("item_id must be a non-empty string")
        if not name or not isinstance(name, str):
            raise ValueError("name must be a non-empty string")
        if not unit or not isinstance(unit, str):
            raise ValueError("unit must be a non-empty string")
        if not isinstance(threshold, int) or threshold < 0:
            raise ValueError("threshold must be a non-negative integer")

        self._item_id = item_id
        self._name = name
        self._unit = unit
        self._threshold = threshold
        self._batches = []  # List of Batch objects

    # Properties for read-only access
    @property
    def item_id(self):
        return self._item_id

    @property
    def name(self):
        return self._name

    @property
    def unit(self):
        return self._unit

    @property
    def threshold(self):
        return self._threshold

    # Add a batch to this item
    def add_batch(self, quantity: int, expiration: date = None):
        batch = Batch(quantity, expiration)
        self._batches.append(batch)

    # Compute total available quantity
    def compute_available_quantity(self, include_expired=False) -> int:
        total = 0
        for batch in self._batches:
            if include_expired or not batch.is_expired():
                total += batch.available_quantity
        return total

    # Reduce stock for sold items (integrates FIFO if requested)
    def reduce_stock(self, quantity: int, use_fifo=True):
        remaining = quantity
        # Sort batches by expiration date if FIFO
        batches = sorted(self._batches, key=lambda b: b.expiration or date.max) if use_fifo else self._batches
        for batch in batches:
            available = batch.available_quantity
            if available >= remaining:
                batch.use(remaining)
                return
            else:
                batch.use(available)
                remaining -= available
        if remaining > 0:
            raise ValueError("Insufficient stock to fulfill sale")

    # Alert batches expiring soon
    def alert_expiring_items(self, days_threshold=3):
        alerts = []
        for batch in self._batches:
            if batch.expiration and 0 <= (batch.expiration - date.today()).days <= days_threshold:
                alerts.append(batch)
        return alerts

    # String representation
    def __str__(self):
        return f"{self._name} ({self._unit}) - {self.compute_available_quantity()} units"

    # Debug representation
    def __repr__(self):
        return f"InventoryItem({self._item_id}, {self._name})"
    




# Inventory class - manages all inventory items
class Inventory:
    # Initialize inventory
    def __init__(self):
        self._items = {}  # Dictionary mapping item_id -> InventoryItem

    # Add new item to inventory
    def add_new_item(self, item_id: str, name: str, unit: str, threshold: int = 0):
        if item_id in self._items:
            raise ValueError(f"Item {item_id} already exists")
        item = InventoryItem(item_id, name, unit, threshold)
        self._items[item_id] = item

    # Get item by ID
    def get_item(self, item_id: str):
        if item_id not in self._items:
            raise KeyError(f"Item {item_id} not found")
        return self._items[item_id]

    # Mark expired batches as unusable
    def mark_expired_items(self):
        expired_items = []
        for item in self._items.values():
            for batch in item._batches:
                if batch.is_expired() and batch.available_quantity > 0:
                    batch.use(batch.available_quantity)  # mark entire batch as used
                    expired_items.append(item.item_id)
                    break
        return expired_items

    # Calculate items below threshold
    def calculate_reorder_list(self):
        reorder = []
        for item in self._items.values():
            if item.compute_available_quantity() < item.threshold:
                reorder.append(item.item_id)
        return reorder

    # Format inventory snapshot
    def format_snapshot(self):
        snapshot = []
        for item in self._items.values():
            total = item.compute_available_quantity()
            snapshot.append(f"{item.item_id} | {item.name} | {total} {item.unit}")
        return "\n".join(snapshot)

    # Export inventory to CSV
    def export_csv(self, filepath: str):
        try:
            with open(filepath, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Item ID", "Name", "Quantity", "Unit"])
                for item in self._items.values():
                    qty = item.compute_available_quantity()
                    writer.writerow([item.item_id, item.name, qty, item.unit])
        except Exception as e:
            raise IOError(f"Failed to write CSV file: {e}")

    # Generate restock plan based on usage log
    def generate_restock_plan(self, usage_log: dict, lead_time_days: int = 3):
        plan = {}
        for item_id, usage in usage_log.items():
            avg_daily = sum(usage[-7:]) / min(len(usage), 7)
            available = self.get_item(item_id).compute_available_quantity()
            if available < avg_daily * lead_time_days:
                plan[item_id] = round(avg_daily * lead_time_days - available)
        return plan




 #UsageLog class - tracks usage and forecasts demand
class UsageLog:
    # Initialize usage log
    def __init__(self):
        self._usage_records = defaultdict(list)  # item_id -> list of {"quantity", "timestamp"}

    # Record a usage event
    def record_usage(self, item_id: str, quantity: int, timestamp: datetime = None):
        if timestamp is None:
            timestamp = datetime.now()
        self._usage_records[item_id].append({"quantity": quantity, "timestamp": timestamp})

    # Forecast demand for an item
    def forecast_demand(self, item_id: str, window_days: int = 30):
        if item_id not in self._usage_records or not self._usage_records[item_id]:
            raise KeyError(f"No usage data for {item_id}")
        data = self._usage_records[item_id][-window_days:]
        total_qty = sum(entry["quantity"] for entry in data)
        unique_days = len(set(e["timestamp"].date() for e in data))
        return round(total_qty / max(unique_days, 1), 2)

    # Generate waste report for a period
    def generate_waste_report(self, waste_log: list, start: date, end: date):
        report = defaultdict(int)
        for entry in waste_log:
            if start <= entry["date"] <= end:
                report[entry["item_id"]] += entry["quantity"]
        return dict(report)
