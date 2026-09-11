"""FitFuel AI Adaptive Recommendation Engine."""
from .personalization import filter_safe_recipes
from .ranking import rank_recipes
from .recommender import RecommendationEngine

__all__ = ["filter_safe_recipes", "rank_recipes", "RecommendationEngine"]
