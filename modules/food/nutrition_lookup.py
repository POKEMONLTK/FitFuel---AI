"""FitFuel AI Nutrition Lookup Service.

Queries food catalogs, calculates scaled macronutrient values, checks allergen
constraints, and rolls up complete meal estimates.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    import csv

from .portion_estimator import PortionEstimator

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


import difflib

# Common culinary aliases and transliterations
FOOD_ALIASES: Dict[str, str] = {
    "roti": "Roti (Whole Wheat Chapati)",
    "chapati": "Roti (Whole Wheat Chapati)",
    "chappati": "Roti (Whole Wheat Chapati)",
    "phulka": "Roti (Whole Wheat Chapati)",
    "chapatti": "Roti (Whole Wheat Chapati)",
    "dal": "Dal Tadka",
    "dhal": "Dal Tadka",
    "daal": "Dal Tadka",
    "yellow dal": "Dal Tadka",
    "rice": "White Rice (Cooked)",
    "chawal": "White Rice (Cooked)",
    "plain rice": "White Rice (Cooked)",
    "brown rice": "Brown Rice (Cooked)",
    "egg": "Boiled Egg",
    "boiled egg": "Boiled Egg",
    "boiled eggs": "Boiled Egg",
    "eggs": "Boiled Egg",
    "anda": "Boiled Egg",
    "paneer": "Paneer Butter Masala (Paneer Makhani)",
    "paneer butter masala": "Paneer Butter Masala (Paneer Makhani)",
    "paneer makhani": "Paneer Butter Masala (Paneer Makhani)",
    "paneer tikka masala": "Paneer Butter Masala (Paneer Makhani)",
    "paneer curry": "Paneer Butter Masala (Paneer Makhani)",
    "shahi paneer": "Shahi Paneer",
    "kadai paneer": "Kadai Paneer",
    "matar paneer": "Matar Paneer",
    "butter chicken": "Butter Chicken (Murgh Makhani)",
    "murgh makhani": "Butter Chicken (Murgh Makhani)",
    "paneer tikka": "Paneer Tikka",
    "curd": "Curd (Plain Dahi)",
    "dahi": "Curd (Plain Dahi)",
    "yogurt": "Curd (Plain Dahi)",
    "salad": "Mixed Salad Greens",
    "green salad": "Mixed Salad Greens",
    "greens": "Mixed Salad Greens",
    "idli": "Idli (Steamed Rice Cakes)",
    "idly": "Idli (Steamed Rice Cakes)",
    "sambar": "Sambar",
    "sambhar": "Sambar",
    "chicken": "Grilled Chicken Breast",
    "chicken breast": "Grilled Chicken Breast",
    "chole": "Chole (Chickpea Curry)",
    "chana": "Chole (Chickpea Curry)",
    "chana masala": "Chole (Chickpea Curry)",
    "rajma": "Rajma (Kidney Bean Curry)",
    "palak paneer": "Palak Paneer",
    "spinach": "Palak Paneer",
    "sabzi": "Mix Vegetable Sabzi",
    "vegetable": "Mix Vegetable Sabzi",
    "mix veg": "Mix Vegetable Sabzi",
}


class NutritionLookup:
    """Manages local nutrition database lookups, scaling, and meal aggregations."""

    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        self.data_dir = data_dir
        self.catalog_df = None
        self.catalog_list: List[Dict[str, Any]] = []
        self._load_catalogs()

    def _load_catalogs(self) -> None:
        """Load and merge foods.csv and indian_foods.csv into unified catalog."""
        foods_csv = self.data_dir / "foods.csv"
        indian_csv = self.data_dir / "indian_foods.csv"

        if PANDAS_AVAILABLE:
            dfs = []
            if foods_csv.exists():
                dfs.append(pd.read_csv(foods_csv))
            if indian_csv.exists():
                dfs.append(pd.read_csv(indian_csv))
            if dfs:
                combined = pd.concat(dfs, ignore_index=True)
                combined.drop_duplicates(subset=["name"], keep="last", inplace=True)
                self.catalog_df = combined
                self.catalog_list = combined.to_dict(orient="records")
            else:
                self.catalog_df = pd.DataFrame()
                self.catalog_list = []
        else:
            records: Dict[str, Dict[str, Any]] = {}
            for csv_path in [foods_csv, indian_csv]:
                if csv_path.exists():
                    with open(csv_path, mode="r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            records[row["name"]] = row
            self.catalog_list = list(records.values())

    def get_all_food_names(self) -> List[str]:
        """Return alphabetized list of all available catalog foods."""
        if self.catalog_list:
            return sorted(r["name"] for r in self.catalog_list)
        return []

    def find_food(self, query_name: str) -> Optional[Dict[str, Any]]:
        """Exact, alias, substring, or fuzzy match for food item in catalog."""
        if not self.catalog_list or not query_name:
            return None

        q = query_name.strip().lower()

        # 1. Exact case-insensitive match
        for r in self.catalog_list:
            if r["name"].strip().lower() == q:
                return r

        # 2. Known alias dictionary lookup
        if q in FOOD_ALIASES:
            canonical_alias = FOOD_ALIASES[q]
            for r in self.catalog_list:
                if r["name"].strip().lower() == canonical_alias.lower():
                    return r

        # 3. Substring match
        for r in self.catalog_list:
            name_lower = r["name"].strip().lower()
            if q in name_lower or name_lower in q:
                return r

        # 4. Fuzzy approximate matching using difflib
        name_map = {r["name"].lower(): r for r in self.catalog_list}
        all_names = list(name_map.keys())
        matches = difflib.get_close_matches(q, all_names, n=1, cutoff=0.50)
        if matches:
            return name_map[matches[0]]

        return None

    def calculate_item_nutrition(
        self,
        food_name: str,
        portion_category: str = "medium",
        custom_multiplier: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Lookup and scale nutrition values for a specific food item.

        Args:
            food_name: Name of food.
            portion_category: e.g., 'small', 'medium', 'large', '2 pieces'.
            custom_multiplier: Optional manual scaling factor.

        Returns:
            Dictionary with scaled nutrient figures and metadata.
        """
        food_record = self.find_food(food_name)
        multiplier = custom_multiplier if custom_multiplier is not None else PortionEstimator.get_multiplier(portion_category)

        if not food_record:
            # Fallback default values
            return {
                "name": food_name,
                "portion_category": portion_category,
                "portion_multiplier": multiplier,
                "serving_size": "Estimated portion",
                "calories": round(150.0 * multiplier, 1),
                "protein_g": round(5.0 * multiplier, 1),
                "carbs_g": round(25.0 * multiplier, 1),
                "fat_g": round(3.0 * multiplier, 1),
                "fiber_g": round(2.0 * multiplier, 1),
                "diet_type": "vegetarian",
                "allergens": "none",
                "cuisine": "global",
            }

        return {
            "name": food_record["name"],
            "portion_category": portion_category,
            "portion_multiplier": multiplier,
            "serving_size": food_record.get("serving_size", "1 serving"),
            "calories": round(float(food_record["calories"]) * multiplier, 1),
            "protein_g": round(float(food_record["protein_g"]) * multiplier, 1),
            "carbs_g": round(float(food_record["carbs_g"]) * multiplier, 1),
            "fat_g": round(float(food_record["fat_g"]) * multiplier, 1),
            "fiber_g": round(float(food_record.get("fiber_g", 0.0)) * multiplier, 1),
            "diet_type": food_record.get("diet_type", "vegetarian"),
            "allergens": str(food_record.get("allergens", "none")),
            "cuisine": food_record.get("cuisine", "global"),
        }

    def aggregate_meal(
        self,
        items: List[Dict[str, Any]],
        meal_type: str = "lunch",
    ) -> Dict[str, Any]:
        """Roll up multiple scaled food items into a total meal summary.

        Args:
            items: List of item dictionaries (with scaled nutrients).
            meal_type: 'breakfast', 'lunch', 'dinner', or 'snack'.

        Returns:
            Dictionary with total calories, protein, carbs, fat, fiber and item details.
        """
        total_cal = 0.0
        total_prot = 0.0
        total_carbs = 0.0
        total_fat = 0.0
        total_fiber = 0.0
        allergens_detected = set()

        processed_items = []
        for it in items:
            name = it.get("name", "")
            portion = it.get("portion_category", "medium")
            mult = it.get("portion_multiplier", PortionEstimator.get_multiplier(portion))

            # If nutrients already precalculated, use them; otherwise calculate
            if "calories" in it and "protein_g" in it:
                item_data = it.copy()
            else:
                item_data = self.calculate_item_nutrition(name, portion, mult)

            total_cal += float(item_data["calories"])
            total_prot += float(item_data["protein_g"])
            total_carbs += float(item_data["carbs_g"])
            total_fat += float(item_data["fat_g"])
            total_fiber += float(item_data.get("fiber_g", 0.0))

            raw_allergens = str(item_data.get("allergens", "none"))
            if raw_allergens.lower() != "none":
                for a in raw_allergens.split("|"):
                    if a.strip():
                        allergens_detected.add(a.strip())

            processed_items.append(item_data)

        # Macro ratios
        prot_cals = total_prot * 4.0
        carb_cals = total_carbs * 4.0
        fat_cals = total_fat * 9.0
        sum_cals = max(1.0, prot_cals + carb_cals + fat_cals)

        return {
            "meal_type": meal_type,
            "total_calories": round(total_cal, 1),
            "total_protein_g": round(total_prot, 1),
            "total_carbs_g": round(total_carbs, 1),
            "total_fat_g": round(total_fat, 1),
            "total_fiber_g": round(total_fiber, 1),
            "macro_percentages": {
                "protein": round((prot_cals / sum_cals) * 100, 1),
                "carbs": round((carb_cals / sum_cals) * 100, 1),
                "fat": round((fat_cals / sum_cals) * 100, 1),
            },
            "allergens": list(allergens_detected),
            "items": processed_items,
        }
