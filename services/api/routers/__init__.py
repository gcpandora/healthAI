from fastapi import APIRouter

from routers.exercise_router import router as exercise_router
from routers.food_log_router import router as food_log_router
from routers.health_profile_router import router as health_profile_router
from routers.nutrition_router import router as nutrition_router
from routers.user_goal_router import router as user_goal_router
from routers.user_metric_router import router as user_metric_router
from routers.user_router import router as user_router
from routers.vision_router import router as vision_router
from routers.workout_log_router import router as workout_log_router

api_router = APIRouter()
api_router.include_router(user_router)
api_router.include_router(nutrition_router)
api_router.include_router(food_log_router)
api_router.include_router(user_metric_router)
api_router.include_router(exercise_router)
api_router.include_router(workout_log_router)
api_router.include_router(user_goal_router)
api_router.include_router(health_profile_router)
api_router.include_router(vision_router)
