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