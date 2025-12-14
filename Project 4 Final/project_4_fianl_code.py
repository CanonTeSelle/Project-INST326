# project4.py
import uuid
import json
from datetime import date, datetime, timedelta
from abc import ABC, abstractmethod
from collections import defaultdict
import csv
from pathlib import Path


# Batch Class
class Batch:
    def __init__(self, quantity: int, expiration: date = None, batch_id: str = None, used_quantity: int = 0):
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        self._quantity = quantity
        if expiration and not isinstance(expiration, date):
            raise TypeError("Expiration must be a datetime.date object")
        self._expiration = expiration
        self._used_quantity = used_quantity
        self._batch_id = batch_id or str(uuid.uuid4())[:8]

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

    # serialization helpers
    def to_dict(self):
        return {
            "batch_id": self._batch_id,
            "quantity": self._quantity,
            "used_quantity": self._used_quantity,
            "expiration": self._expiration.isoformat() if self._expiration else None
        }

    @classmethod
    def from_dict(cls, d):
        exp = date.fromisoformat(d["expiration"]) if d.get("expiration") else None
        return cls(quantity=d["quantity"], expiration=exp, batch_id=d.get("batch_id"), used_quantity=d.get("used_quantity", 0))

    def __str__(self):
        status = "Expired" if self.is_expired() else "Good"
        return f"Batch {self._batch_id}: {self.available_quantity} units ({status})"

    def __repr__(self):
        return f"Batch({self._batch_id}, {self._quantity}, {self._expiration})"
    

# Abstract Inventory Item (Inheritance + serialization)

class AbstractInventoryItem(ABC):
    def __init__(self, item_id: str, name: str, unit: str, threshold: int = 0):
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

    @property
    def threshold(self):
        return self._threshold

    # required polymorphic methods
    @abstractmethod
    def compute_available_quantity(self, include_expired=False):
        pass

    @abstractmethod
    def alert_expiring_items(self, days_threshold=3):
        pass

    # common behavior
    def add_batch(self, quantity: int, expiration: date = None):
        self._batches.append(Batch(quantity, expiration))

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

    # serialization
    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "item_id": self._item_id,
            "name": self._name,
            "unit": self._unit,
            "threshold": self._threshold,
            "batches": [b.to_dict() for b in self._batches]
        }

    @classmethod
    def from_dict_common(cls, d):
        # helper used by subclasses
        item = cls(d["item_id"], d["name"], d["unit"], d.get("threshold", 0))
        for b in d.get("batches", []):
            item._batches.append(Batch.from_dict(b))
        return item
    

# Perishable and NonPerishable subclasses

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

    @classmethod
    def from_dict(cls, d):
        item = cls(d["item_id"], d["name"], d["unit"], d.get("threshold", 0))
        for b in d.get("batches", []):
            item._batches.append(Batch.from_dict(b))
        return item

class NonPerishableItem(AbstractInventoryItem):
    def compute_available_quantity(self, include_expired=False):
        return sum(batch.available_quantity for batch in self._batches)

    def alert_expiring_items(self, days_threshold=3):
        return []

    @classmethod
    def from_dict(cls, d):
        item = cls(d["item_id"], d["name"], d["unit"], d.get("threshold", 0))
        for b in d.get("batches", []):
            item._batches.append(Batch.from_dict(b))
        return item
    

# Inventory

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
            if item.compute_available_quantity() < item.threshold:
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
        p = Path(filepath)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open("w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Item ID", "Name", "Quantity", "Unit"])
                for item in self._items.values():
                    qty = item.compute_available_quantity()
                    writer.writerow([item.item_id, item.name, qty, item.unit])
        except Exception as e:
            raise IOError(f"Failed to write CSV file: {e}")

    def export_json_report(self, filepath: str):
        p = Path(filepath)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            data = {item_id: item.to_dict() for item_id, item in self._items.items()}
            with p.open("w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            raise IOError(f"Failed to write JSON report: {e}")

    # persistence: save/load entire inventory to JSON
    def save(self, filepath: str):
        p = Path(filepath)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            payload = {item_id: item.to_dict() for item_id, item in self._items.items()}
            with p.open("w") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            raise IOError(f"Failed to save inventory: {e}")

    @classmethod
    def load(cls, filepath: str):
        p = Path(filepath)
        if not p.exists():
            raise FileNotFoundError(f"No file at {filepath}")
        try:
            with p.open("r") as f:
                payload = json.load(f)
        except Exception as e:
            raise IOError(f"Failed to load inventory: {e}")

        inv = cls()
        for item_id, d in payload.items():
            typ = d.get("type", "NonPerishableItem")
            if typ == "PerishableItem":
                obj = PerishableItem.from_dict(d)
            elif typ == "NonPerishableItem":
                obj = NonPerishableItem.from_dict(d)
            else:
                # fallback: try nonperishable
                obj = NonPerishableItem.from_dict(d)
            inv.add_item(obj)
        return inv

    # CSV import expects columns: item_id,name,unit,quantity,expiration (YYYY-MM-DD or empty),threshold(optional)
    def import_from_csv(self, filepath: str):
        p = Path(filepath)
        if not p.exists():
            raise FileNotFoundError(f"No CSV at {filepath}")
        try:
            with p.open("r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    item_id = row.get("item_id") or row.get("Item ID") or row.get("id")
                    name = row.get("name") or row.get("Name")
                    unit = row.get("unit") or row.get("Unit") or "unit"
                    q = int(row.get("quantity") or row.get("Quantity") or 0)
                    exp_raw = row.get("expiration") or row.get("Expiration") or ""
                    exp = date.fromisoformat(exp_raw) if exp_raw else None
                    threshold = int(row.get("threshold") or row.get("Threshold") or 0)

                    if item_id in self._items:
                        self._items[item_id].add_batch(q, exp)
                    else:
                        # Choose perishable if expiration present
                        if exp:
                            item = PerishableItem(item_id, name, unit, threshold)
                        else:
                            item = NonPerishableItem(item_id, name, unit, threshold)
                        item.add_batch(q, exp)
                        self.add_item(item)
        except Exception as e:
            raise IOError(f"Failed to import CSV: {e}")


# Usage Log

class UsageLog:
    def __init__(self):
        self._usage_records = defaultdict(list)

    def record_usage(self, item_id: str, quantity: int, timestamp: datetime = None):
        if timestamp is None:
            timestamp = datetime.now()
        self._usage_records[item_id].append({"quantity": quantity, "timestamp": timestamp})

    def forecast_demand(self, item_id: str, window_days: int = 30):
        if item_id not in self._usage_records or not self._usage_records[item_id]:
            raise KeyError(f"No usage data for {item_id}")
        data = self._usage_records[item_id][-window_days:]
        total_qty = sum(entry["quantity"] for entry in data)
        unique_days = len(set(e["timestamp"].date() for e in data))
        return round(total_qty / max(unique_days, 1), 2)

    def generate_waste_report(self, waste_log: list, start: date, end: date):
        report = defaultdict(int)
        for entry in waste_log:
            if start <= entry["date"] <= end:
                report[entry["item_id"]] += entry["quantity"]
        return dict(report)
    


