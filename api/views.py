from django.contrib.auth import login, logout as django_logout
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import viewsets, status, mixins, serializers
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action, authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Category, Comment, Favorite, Ingredient, Rating, Recipe, RecipeIngredient, Step, \
    User, Unit
from api.permissions import IsAdminOrIsOwnerOrSingup, IsAdminOrReadOnly, IsOwnerOrCreateOrReadOnly, \
    IsAdminOrCreateOrReadOnly, IsOwnerRecipeOrCreateOrReadOnly
from api.serializers.ingredient import IngredientSerializer, IngredientDisplaySerializer
from api.serializers.recipe import RecipeSerializer, RecipeDisplaySerializer
from api.serializers.recipe_ingredient import RecipeIngredientSerializer, RecipeIngredientUpdateSerializer
from api.serializers.serializers import FavoriteSerializer, RatingSerializer, CategorySerializer, StepSerializer, \
    CommentSerializer
from api.serializers.unit import UnitSerializer
from api.serializers.user import UserSerializer


class AuthenticationView(ViewSet):
    permission_classes = (IsAuthenticated,)

    @authentication_classes([BasicAuthentication, ])
    def login(self, request, *args, **kwargs):
        refresh = RefreshToken.for_user(request.user)
        serializer = UserSerializer(request.user)
        login(request=request, user=request.user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': serializer.data['username'],
            'email': serializer.data['email']
        })

    def logout(self, request, *args, **kwargs):
        django_logout(request)
        return Response({'message': 'Successfully logged out!'})


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def get_mine_favourites(request):
    user = request.user
    favourites = Favorite.objects.filter(user_id=user.id)
    serialized = FavoriteSerializer(favourites, many=True)
    return Response(serialized.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrIsOwnerOrSingup,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrCreateOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return RecipeDisplaySerializer
        return RecipeSerializer

    def create(self, request, *args, **kwargs):
        categories = request.data.get('categories')
        ingredients = request.data.get('ingredients')
        steps = request.data.get('steps')

        if len(categories) == 0:
            return Response({"error": "Recipe is required to have at least one category!"},
                            status=status.HTTP_400_BAD_REQUEST)

        if len(ingredients) == 0:
            return Response({"error": "Recipe is required to have at least one ingredient!"},
                            status=status.HTTP_400_BAD_REQUEST)
        if len(steps) == 0:
            return Response({"error": "Recipe is required to have at least one step!"},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['POST'])
    def rate(self, request, pk=None):
        if 'stars' not in request.data:
            response = {'error': 'You need to provide stars!'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        recipe = self.get_object()
        stars = request.data['stars']
        user = request.user

        try:
            rating = Rating.objects.get(user=user.id, recipe=recipe.id)
            data_to_change = {'stars': stars}
            serializer = RatingSerializer(rating, data=data_to_change, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Rating.DoesNotExist:
            data = {'stars': stars}
            serializer = RatingSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'])
    def favourite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        data = {'recipe': recipe.id, 'user': user.id}
        serializer = FavoriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticated, IsAdminOrReadOnly)


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = (IsAuthenticated, IsAdminOrReadOnly)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticated, IsAdminOrCreateOrReadOnly)

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return IngredientDisplaySerializer
        return IngredientSerializer


class RecipeIngredientViewSet(mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.RetrieveModelMixin,
                              mixins.DestroyModelMixin,
                              GenericViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer
    permission_classes = (IsAuthenticated, IsOwnerRecipeOrCreateOrReadOnly)

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return RecipeIngredientUpdateSerializer
        return RecipeIngredientSerializer

    def create(self, request, *args, **kwargs):
        rci_id = self.kwargs.get('pk')
        try:
            recipe = Recipe.objects.get(id=rci_id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Recipe with id = ' + str(rci_id) + ' dose not exists.')
        data = request.data
        data['recipe'] = recipe.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class StepViewSet(mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    permission_classes = (IsAuthenticated, IsOwnerRecipeOrCreateOrReadOnly)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError:
            return Response({"error": "There is already such a step in this recipe!"}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        rci_id = self.kwargs.get('pk')
        try:
            recipe = Recipe.objects.get(id=rci_id)
            if recipe:
                serializer.save(recipe=recipe)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Recipe with id = ' + str(rci_id) + ' dose not exists.')


class CommentViewSet(mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrCreateOrReadOnly)

    def perform_create(self, serializer):
        rci_id = self.kwargs.get('pk')
        try:
            recipe = Recipe.objects.get(id=rci_id)
            if recipe:
                serializer.save(user=self.request.user, recipe=recipe)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Recipe with id = ' + str(rci_id) + ' dose not exists.')
