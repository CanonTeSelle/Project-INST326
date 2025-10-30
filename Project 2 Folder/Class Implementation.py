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
    

    #