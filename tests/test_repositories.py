import tempfile
import unittest
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from dietapp.database import Base
from dietapp.models import User
from dietapp.migrations import migrate_legacy_passwords
from dietapp.repositories import (
    authenticate_user,
    get_food_alternatives,
    get_user_diet,
    get_user_purchases,
    register_user,
    replace_food_alternatives,
    save_purchase,
    save_user_plan,
)
from dietapp.security import is_password_hash


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        path = Path(self.tempdir.name) / "test.db"
        self.engine = create_engine(f"sqlite:///{path.as_posix()}")
        Base.metadata.create_all(self.engine)

    def tearDown(self):
        self.engine.dispose()
        self.tempdir.cleanup()

    def test_user_plan_and_purchase_round_trip(self):
        with Session(self.engine) as db:
            self.assertTrue(
                register_user(
                    db,
                    "Mario.Rossi",
                    "Mario",
                    "Rossi",
                    "mario@example.com",
                    "Password1",
                )
            )
            user = db.scalar(select(User))
            self.assertEqual(user.username, "mario.rossi")
            self.assertTrue(is_password_hash(user.password))
            self.assertTrue(authenticate_user(db, "MARIO.ROSSI", "Password1"))

            diet = {"Lunedì": {"Pranzo": {}}}
            self.assertTrue(save_user_plan(db, user.username, diet, ["pasta"]))
            self.assertEqual(get_user_diet(db, user.username), diet)
            self.assertTrue(
                save_purchase(
                    db,
                    user.username,
                    "2026-07-30",
                    {"pasta": {"Quantità": 100, "Unità": "g"}},
                )
            )
            purchases = get_user_purchases(db, user.username)
            self.assertEqual(purchases[0]["lista_spesa"]["pasta"]["Quantità"], 100)

    def test_legacy_plaintext_password_is_migrated(self):
        with Session(self.engine) as db:
            db.add(User(username="Legacy", password="OldPassword1"))
            db.commit()
            self.assertTrue(authenticate_user(db, "legacy", "OldPassword1"))
            db.refresh(db.scalar(select(User)))
            self.assertTrue(is_password_hash(db.scalar(select(User)).password))

    def test_startup_migration_hashes_legacy_passwords(self):
        with Session(self.engine) as db:
            db.add(User(username="Legacy", password="OldPassword1"))
            db.commit()
            self.assertEqual(migrate_legacy_passwords(db), 1)
            db.commit()
            user = db.scalar(select(User))
            self.assertTrue(is_password_hash(user.password))
            self.assertTrue(authenticate_user(db, "legacy", "OldPassword1"))

    def test_food_alternatives_are_replaced_atomically(self):
        with Session(self.engine) as db:
            register_user(
                db,
                "mario",
                "Mario",
                "Rossi",
                "mario@example.com",
                "Password1",
            )
            rows = [
                {
                    "group_name": "Carboidrati",
                    "food_name": "pasta",
                    "quantity": 80.0,
                    "unit": "g",
                    "calories": None,
                    "carbohydrates": None,
                    "protein": None,
                    "fats": None,
                    "notes": None,
                },
                {
                    "group_name": "Carboidrati",
                    "food_name": "riso",
                    "quantity": 100.0,
                    "unit": "g",
                    "calories": None,
                    "carbohydrates": None,
                    "protein": None,
                    "fats": None,
                    "notes": None,
                },
            ]
            self.assertTrue(replace_food_alternatives(db, "mario", rows))
            self.assertEqual(len(get_food_alternatives(db, "mario")), 2)

            self.assertTrue(replace_food_alternatives(db, "mario", []))
            self.assertEqual(get_food_alternatives(db, "mario"), [])


if __name__ == "__main__":
    unittest.main()
