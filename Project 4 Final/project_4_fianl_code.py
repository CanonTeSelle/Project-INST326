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