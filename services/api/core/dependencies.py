from fastapi import Depends
from sqlalchemy.orm import Session

from core.database import get_db
from repositories.exercise_repository import ExerciseRepository
from repositories.food_log_repository import FoodLogRepository
from repositories.health_profile_repository import HealthProfileRepository
from repositories.nutrition_repository import NutritionItemRepository
from repositories.user_goal_repository import UserGoalRepository
from repositories.user_metric_repository import UserMetricRepository
from repositories.user_repository import UserRepository
from repositories.workout_log_repository import WorkoutLogRepository
from services.exercise_service import ExerciseService
from services.food_log_service import FoodLogService
from services.health_profile_service import HealthProfileService
from services.nutrition_service import NutritionItemService
from services.user_goal_service import UserGoalService
from services.user_metric_service import UserMetricService
from services.user_service import UserService
from services.workout_log_service import WorkoutLogService


# DB dependency
DBSession = Session


def get_user_service(db: DBSession = Depends(get_db)) -> UserService:
    return UserService(UserRepository())


def get_nutrition_item_service(db: DBSession = Depends(get_db)) -> NutritionItemService:
    return NutritionItemService(NutritionItemRepository())


def get_food_log_service(db: DBSession = Depends(get_db)) -> FoodLogService:
    return FoodLogService(FoodLogRepository())


def get_user_metric_service(db: DBSession = Depends(get_db)) -> UserMetricService:
    return UserMetricService(UserMetricRepository())


def get_exercise_service(db: DBSession = Depends(get_db)) -> ExerciseService:
    return ExerciseService(ExerciseRepository())


def get_workout_log_service(db: DBSession = Depends(get_db)) -> WorkoutLogService:
    return WorkoutLogService(WorkoutLogRepository())


def get_user_goal_service(db: DBSession = Depends(get_db)) -> UserGoalService:
    return UserGoalService(UserGoalRepository())


def get_health_profile_service(db: DBSession = Depends(get_db)) -> HealthProfileService:
    return HealthProfileService(HealthProfileRepository())
