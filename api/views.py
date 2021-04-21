from django.contrib.auth import login, logout as django_logout
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
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
    CommentSerializer, StepCreateSerializer
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


class UserMe(ViewSet):
    permission_classes(IsAuthenticated, )

    def get_favourites(self, request, *args, **kwargs):
        user = request.user
        favourites = Favorite.objects.filter(user_id=user.id)
        serialized = FavoriteSerializer(favourites, many=True)
        return Response(serialized.data)

    def get_ratings(self, request, *args, **kwargs):
        user = request.user
        ratings = Rating.objects.filter(user_id=user.id)
        serialized = RatingSerializer(ratings, many=True)
        return Response(serialized.data)

    def update(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrIsOwnerOrSingup,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrCreateOrReadOnly)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        if request.user is not None and request.user.is_anonymous is False:
            user_favourites = list(map(lambda f: f.recipe, request.user.favourites.all()))

            user_rates = {'stars': [], 'recipes': []}
            for r in request.user.rates.all():
                user_rates['stars'].append(r.stars)
                user_rates['recipes'].append(r.recipe)

            for q in queryset:
                if q in user_favourites:
                    q.user_favourite = True
                if q in user_rates['recipes']:
                    index = user_rates['recipes'].index(q)
                    q.user_rating = user_rates['stars'][index]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if request.user is not None and request.user.is_anonymous is False:
            for r in request.user.rates.all():
                if r.recipe == instance:
                    instance.user_rating = r.stars
                    break

            for f in request.user.favourites.all():

                if f.recipe == instance:
                    instance.user_favourite = True
                    break

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return RecipeDisplaySerializer
        return RecipeSerializer

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
        is_many = isinstance(data, list)
        with transaction.atomic():
            try:
                if not is_many:
                    data['recipe'] = recipe.id
                    serializer = self.get_serializer(data=data)
                else:
                    for rci in data:
                        rci['recipe'] = recipe.id
                    serializer = self.get_serializer(data=data, many=True)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            except IntegrityError as e:
                return Response({"error": "In the recipe there cannot be any recipe_ingredient with the same "
                                          "ingredient.id!"},
                                status=status.HTTP_400_BAD_REQUEST)


class StepViewSet(mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  GenericViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    permission_classes = (IsAuthenticated, IsOwnerRecipeOrCreateOrReadOnly)

    def get_serializer_class(self):
        if self.action == 'create':
            return StepCreateSerializer
        return StepSerializer

    def create(self, request, *args, **kwargs):
        rci_id = self.kwargs.get('pk')
        try:
            recipe = Recipe.objects.get(id=rci_id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Recipe with id = ' + str(rci_id) + ' dose not exists.')

        data = request.data
        is_many = isinstance(data, list)
        with transaction.atomic():
            try:
                if not is_many:
                    data['recipe'] = recipe.id
                    serializer = self.get_serializer(data=data)
                else:
                    for step in data:
                        step['recipe'] = recipe.id
                    serializer = self.get_serializer(data=data, many=True)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            except IntegrityError as e:
                return Response({"error": "In the recipe there cannot be any step with the same step.order number!"},
                                status=status.HTTP_400_BAD_REQUEST)


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


class FavouriteViewSet(mixins.DestroyModelMixin,
                       GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated, IsOwnerRecipeOrCreateOrReadOnly)


class RatingViewSet(mixins.DestroyModelMixin,
                    GenericViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = (IsAuthenticated, IsOwnerRecipeOrCreateOrReadOnly)
