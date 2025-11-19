import uuid
from datetime import date, datetime, timedelta
from abc import ABC, abstractmethod
from collections import defaultdict
import csv

# Batch Class (Composition)
class Batch:
    def __init__(self, quantity: int, expiration: date = None):
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        self._quantity = quantity
        if expiration and not isinstance(expiration, date):
            raise TypeError("Expiration must be a datetime.date object")
        self._expiration = expiration
        self._used_quantity = 0
        self._batch_id = str(uuid.uuid4())[:8]

    @property
    def batch_id(self):
        return self._batch_id

    @property
    def expiration(self):
        return self._expiration

    @property
    def available_quantity(self):
        return self._quantity - self._used_quantity

    def is_expired(self):
        return self._expiration and self._expiration < date.today()

    def use(self, quantity: int):
        if quantity > self.available_quantity:
            raise ValueError("Not enough quantity in batch")
        self._used_quantity += quantity

    def __str__(self):
        status = "Expired" if self.is_expired() else "Good"
        return f"Batch {self._batch_id}: {self.available_quantity} units ({status})"

    def __repr__(self):
        return f"Batch({self._batch_id}, {self._quantity}, {self._expiration})"
    

    
    # Abstract Inventory Item (Inheritance)

class AbstractInventoryItem(ABC):
    def __init__(self, item_id: str, name: str, unit: str, threshold: int = 0):
        self._item_id = item_id
        self._name = name
        self._unit = unit
        self._threshold = threshold
        self._batches = []

    @property
    def item_id(self):
        return self._item_id

    @property
    def name(self):
        return self._name

    @property
    def unit(self):
        return self._unit

    @abstractmethod
    def compute_available_quantity(self, include_expired=False):
        # To be implemented by subclasses
        pass

    @abstractmethod
    def alert_expiring_items(self, days_threshold=3):
        pass

    # Add batch
    def add_batch(self, quantity: int, expiration: date = None):
        self._batches.append(Batch(quantity, expiration))

    # Reduce stock (FIFO)
    def reduce_stock(self, quantity: int, use_fifo=True):
        remaining = quantity
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
            raise ValueError("Insufficient stock to fulfill request")
        

# Perishable Item (Subclass)

class PerishableItem(AbstractInventoryItem):
    def compute_available_quantity(self, include_expired=False):
        total = 0
        for batch in self._batches:
            if include_expired or not batch.is_expired():
                total += batch.available_quantity
        return total

    def alert_expiring_items(self, days_threshold=3):
        alerts = []
        for batch in self._batches:
            if batch.expiration and 0 <= (batch.expiration - date.today()).days <= days_threshold:
                alerts.append(batch)
        return alerts
    
# Non-Perishable Item (Subclass)

class NonPerishableItem(AbstractInventoryItem):
    def compute_available_quantity(self, include_expired=False):
        return sum(batch.available_quantity for batch in self._batches)

    def alert_expiring_items(self, days_threshold=3):
        return []
    

# Inventory (Composition)
class Inventory:
    def __init__(self):
        self._items = {}

    def add_item(self, item: AbstractInventoryItem):
        self._items[item.item_id] = item

    def get_item(self, item_id):
        return self._items.get(item_id)

    def mark_expired_items(self):
        expired_items = []
        for item in self._items.values():
            for batch in item._batches:
                if batch.is_expired() and batch.available_quantity > 0:
                    batch.use(batch.available_quantity)
                    expired_items.append(item.item_id)
                    break
        return expired_items

    def calculate_reorder_list(self):
        reorder = []
        for item in self._items.values():
            if item.compute_available_quantity() < getattr(item, "_threshold", 0):
                reorder.append(item.item_id)
        return reorder

    def generate_restock_plan(self, usage_log: dict, lead_time_days=3):
        plan = {}
        for item_id, usage in usage_log.items():
            item = self.get_item(item_id)
            if not item:
                continue
            avg_daily = sum(usage[-7:]) / min(len(usage), 7)
            available = item.compute_available_quantity()
            if available < avg_daily * lead_time_days:
                plan[item_id] = round(avg_daily * lead_time_days - available)
        return plan

    def format_snapshot(self):
        snapshot = []
        for item in self._items.values():
            total = item.compute_available_quantity()
            snapshot.append(f"{item.item_id} | {item.name} | {total} {item.unit}")
        return "\n".join(snapshot)

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