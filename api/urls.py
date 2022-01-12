from django.conf.urls import include
from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import CategoryViewSet, CommentViewSet, IngredientViewSet, \
    RecipeIngredientViewSet, RecipeViewSet, StepViewSet, UserViewSet, AuthenticationView, \
    FavouriteViewSet, UserMe, RatingViewSet

router = routers.DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('categories', CategoryViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users', UserViewSet)
router.register('favourites', FavouriteViewSet)
router.register('ratings', RatingViewSet)

create_comment = CommentViewSet.as_view({
    'post': 'create',
})

comments_view = CommentViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

create_recipe_ingredient = RecipeIngredientViewSet.as_view({
    'post': 'create',
})

recipe_ingredient_view = RecipeIngredientViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

create_step = StepViewSet.as_view({
    'post': 'create',
})

step_view = StepViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})
urlpatterns = [
    path('users/me/favourites/', UserMe.as_view({'get': 'get_favourites'}), name='get_favourites'),
    path('users/me/ratings/', UserMe.as_view({'get': 'get_ratings'}), name='get_ratings'),
    path('users/me/', UserMe.as_view({'patch': 'partial_update', 'put': 'update'}), name='update_user'),

    path('', include(router.urls)),

    path('comments/<int:pk>/', comments_view),
    path('recipes/<int:pk>/comments/', create_comment),

    path('recipe-ingredients/<int:pk>/', recipe_ingredient_view),
    path('recipes/<int:pk>/recipe-ingredients/', create_recipe_ingredient),

    path('steps/<int:pk>/', step_view),
    path('recipes/<int:pk>/steps/', create_step),

    path('auth/logout/', AuthenticationView.as_view({'post': 'logout'}), name='logout'),
    path('auth/login/', AuthenticationView.as_view({'post': 'login'}), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/recaptcha/', AuthenticationView.as_view({'post': 'recaptcha'}), name='recaptcha'),

]
