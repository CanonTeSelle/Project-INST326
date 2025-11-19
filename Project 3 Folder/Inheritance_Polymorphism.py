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