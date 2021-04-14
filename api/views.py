from django.contrib.auth.models import User
from api.serializers import FavoriteSerializer, RecipeCategorySerializer, CategorySerializer, CommentSerializer, IngredientSerializer, RatingSerializer, RecipeIngredientSerializer, RecipeSerializer, StepSerializer, UserSerializer
from api.models import Category, Comment, Favorite, Ingredient, Rating, Recipe, RecipeCategory, RecipeIngredient, Step
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
import json

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    @action(detail=True, methods=['POST'])
    def rate_recipe(self, request, pk=None): 
        if 'stars' in request.data:

            recipe = Recipe.objects.get(id=pk)
            stars = request.data['stars']
            user = request.user

            try:
                rating = Rating.objects.get(user=user.id, recipe=recipe.id)
                rating.stars = stars
                rating.save()
                serializer = RatingSerializer(rating, many=False)
                response = {'message': 'Rating updated', 'result': serializer.data}
                return Response(response, status=status.HTTP_200_OK)
            except: 
                rating = Rating.objects.create(user=user, recipe=recipe, stars=stars)
                serializer = RatingSerializer(rating, many=False)
                response = {'message': 'Rating created', 'result': serializer.data}
                return Response(response, status=status.HTTP_200_OK)

        else:
            response = {'message': 'You need to provide stars'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def add_categories(self, request, pk=None): 
        if 'categories' in request.data:

            recipe = Recipe.objects.get(id=pk)
            categories = request.data['categories']

            for category in categories:
                try:
                    existingCategory = Category.objects.get(name=category)
                    recipe.categories.add(existingCategory)
                    recipe.save()
                except: 
                    newCategory = Category.objects.create(name=category)
                    newCategory.save()
                    recipe.categories.add(newCategory)
                    recipe.save()
                    # serializer = CategorySerializer(newCategory, many=False)
                    # serializerRecipe = RecipeSerializer(recipe, many=False)
                    # response = response.add({'message': 'Rating created', 'result': serializer.data, 'res2': serializerRecipe.data})
            return Response({'message': 'GUT'}, status=status.HTTP_200_OK)
        else:
            response = {'message': 'You need to provide stars'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['POST'])
    def add_ingredients(self, request, pk=None): 
        if 'ingredients' in request.data:

            recipe = Recipe.objects.get(id=pk)
            ingredients = request.data['ingredients']

            for ingredient in ingredients:
                try:
                    existingIngredient = Ingredient.objects.get(name=ingredient['name'])
                    existingRecipeIngredient = RecipeIngredient.objects.get(ingredient=existingIngredient, quantity=ingredient['quantity'], unit=ingredient['unit'])
                    recipe.ingredients.add(existingRecipeIngredient)
                    recipe.save()
                except RecipeIngredient.DoesNotExist:
                    print('hello 3', existingIngredient)
                    newRI = RecipeIngredient.objects.create(ingredient = existingIngredient, quantity=ingredient['quantity'], unit=ingredient['unit'])
                    newRI.save()
                    recipe.ingredients.add(newRI)
                    recipe.save()
                except Ingredient.DoesNotExist: 
                    newIg = Ingredient.objects.create(name=ingredient['name'])
                    newIg.save()
                    newRI = RecipeIngredient.objects.create(ingredient=newIg, quantity=ingredient['quantity'], unit=ingredient['unit'])

                    newRI.save()
                    recipe.ingredients.add(newRI)
                    recipe.save()
            return Response({'message': 'GUT'}, status=status.HTTP_200_OK)
        else:
            response = {'message': 'You need to provide stars'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def update(self, request, *args, **kwargs):
        response = {'message': 'You cant update rating like that'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request, *args, **kwargs):
        response = {'message': 'You cant create rating like that'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def update(self, request, *args, **kwargs):
        response = {'message': 'You cant update rating like that'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request, *args, **kwargs):
        response = {'message': 'You cant create rating like that'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    
    @action(detail=True, methods=['GET']) 
    def mine(self, request, pk=None):
        user = request.user
        print('USER', user);


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    # def update(self, request, *args, **kwargs):
    #     response = {'message': 'You cant update rating like that'}
    #     return Response(response, status=status.HTTP_400_BAD_REQUEST)
    
    # def create(self, request, *args, **kwargs):
    #     response = {'message': 'You cant create rating like that'}
    #     return Response(response, status=status.HTTP_400_BAD_REQUEST)

class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

class RecipeCategoryViewSet(viewsets.ModelViewSet):
    queryset = RecipeCategory.objects.all()
    serializer_class = RecipeCategorySerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

class StepViewSet(viewsets.ModelViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
