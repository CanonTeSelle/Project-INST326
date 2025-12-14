# tests/test_project4.py
import unittest
import tempfile
from pathlib import Path
from datetime import date, timedelta, datetime
import json

from project_4_fianl_code import Batch, PerishableItem, NonPerishableItem, Inventory, UsageLog

class UnitTests(unittest.TestCase):
    def test_batch_use_and_expiration(self):
        b = Batch(10, date.today() + timedelta(days=1))
        self.assertEqual(b.available_quantity, 10)
        b.use(3)
        self.assertEqual(b.available_quantity, 7)
        self.assertFalse(b.is_expired())

    def test_perishable_compute_and_alert(self):
        p = PerishableItem("p1", "Milk", "L", threshold=1)
        p.add_batch(5, date.today() + timedelta(days=1))
        p.add_batch(2, date.today() + timedelta(days=10))
        self.assertEqual(p.compute_available_quantity(), 7)
        alerts = p.alert_expiring_items(days_threshold=2)
        self.assertTrue(len(alerts) >= 1)

    def test_nonperishable_compute(self):
        n = NonPerishableItem("n1", "Rice", "kg", threshold=1)
        n.add_batch(20)
        self.assertEqual(n.compute_available_quantity(), 20)
        self.assertEqual(n.alert_expiring_items(), [])

class IntegrationTests(unittest.TestCase):
    def test_inventory_save_load_and_restock(self):
        inv = Inventory()
        milk = PerishableItem("001", "Milk", "L", threshold=5)
        milk.add_batch(10, date.today() + timedelta(days=2))
        inv.add_item(milk)

        beans = NonPerishableItem("002", "Beans", "can", threshold=10)
        beans.add_batch(50)
        inv.add_item(beans)

        usage = {"001": [2,3,1,2], "002":[1,2,1]}
        # save to temp file
        tmp = Path(tempfile.gettempdir()) / "test_inv.json"
        inv.save(str(tmp))
        self.assertTrue(tmp.exists())

        loaded = Inventory.load(str(tmp))
        self.assertIn("001", loaded._items)
        # restock plan
        plan = loaded.generate_restock_plan(usage, lead_time_days=3)
        self.assertIsInstance(plan, dict)

        tmp.unlink()

    def test_import_csv_and_export(self):
        csv_txt = "item_id,name,unit,quantity,expiration,threshold\n"
        csv_txt += f"c1,Cheese,kg,5,{(date.today()+timedelta(days=3)).isoformat()},2\n"
        tmp_csv = Path(tempfile.gettempdir()) / "test_import.csv"
        tmp_csv.write_text(csv_txt)

        inv = Inventory()
        inv.import_from_csv(str(tmp_csv))
        self.assertIn("c1", inv._items)
        # export csv
        out_csv = Path(tempfile.gettempdir()) / "out_inv.csv"
        if out_csv.exists():
            out_csv.unlink()
        inv.export_csv(str(out_csv))
        self.assertTrue(out_csv.exists())

        tmp_csv.unlink()
        out_csv.unlink()

class SystemTests(unittest.TestCase):
    def test_end_to_end_save_load_and_snapshot(self):
        inv = Inventory()
        milk = PerishableItem("s1", "Yogurt", "cup", threshold=3)
        milk.add_batch(6, date.today()+timedelta(days=1))
        inv.add_item(milk)
        usage = {"s1":[1,2,1,1]}
        tmp = Path(tempfile.gettempdir()) / "sys_inv.json"
        inv.save(str(tmp))
        loaded = Inventory.load(str(tmp))
        snap = loaded.format_snapshot()
        self.assertIn("Yogurt", snap)
        tmp.unlink()

if __name__ == "__main__":
    unittest.main()