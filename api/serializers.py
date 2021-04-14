from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Category, Comment, Favorite, Ingredient, Rating, Recipe, RecipeIngredient, Step
from rest_framework.authtoken.models import Token
import json

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name']

class CategoryIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(many=False)

    class Meta:
        model = RecipeIngredient
        fields = ['id',  'quantity', 'ingredient', 'unit']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class RecipeIngredientSerializer1(serializers.ModelSerializer):
    ingredient = IngredientSerializer(many=False)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'ingredient', 'unit', 'quantity']

class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ['id', 'step']


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer1(many=True)
    categories = CategorySerializer(many=True)
    steps = StepSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'no_of_rating', 'avg_rating', 'imageUrl', 'categories', 'ingredients', 'preparationTime', 'steps', 'level', 'dateAdded']

    def create(self, validated_data):
        ingredients = validated_data.get('ingredients')
        print(json.dumps(ingredients))

        categories = validated_data['categories']
        steps = validated_data['steps']
        title = validated_data['title']
        description = validated_data['description']
        imageUrl = validated_data['imageUrl']
        categoriesIds = []
        stepsIds = []
        ingredientsIds = []

        for ingredient in ingredients:
                ingredientJson = json.loads(json.dumps(ingredient))
                
                try:
                    existingIngredient = Ingredient.objects.get(name=ingredientJson["ingredient"]["name"])
                    existingRecipeIngredient = RecipeIngredient.objects.get(ingredient=existingIngredient, quantity=ingredientJson["quantity"], unit=ingredientJson["unit"])
                    ingredientsIds.append(existingRecipeIngredient.id)
                except RecipeIngredient.DoesNotExist:
                    newRI = RecipeIngredient.objects.create(ingredient = existingIngredient, quantity=ingredientJson["quantity"], unit=ingredientJson["unit"])
                    newRI.save()
                    ingredientsIds.append(newRI.id)
                except Ingredient.DoesNotExist: 
                    newIg = Ingredient.objects.create(name=ingredientJson["ingredient"]["name"])
                    newIg.save()
                    newRI = RecipeIngredient.objects.create(ingredient=newIg, quantity=ingredientJson["quantity"], unit=ingredientJson["unit"])
                    newRI.save()
                    ingredientsIds.append(newRI.id)
        
        for category in categories:
                categoryJson = json.loads(json.dumps(category))
                try:
                    existingCategory = Category.objects.get(name=categoryJson["name"])
                    categoriesIds.append(existingCategory.id)
                except Category.DoesNotExist:
                    newCate = Category.objects.create(name = categoryJson["name"])
                    newCate.save()
                    categoriesIds.append(newCate.id)

        for step in steps:
                stepJson = json.loads(json.dumps(step))
                try:
                    existingStep = Step.objects.get(step=stepJson["step"])
                    stepsIds.append(existingStep.id)
                except Step.DoesNotExist:
                    newStep = Step.objects.create(step = stepJson["step"])
                    newStep.save()
                    stepsIds.append(newStep.id)


                    # TODO  - AFTER RECPE CREATION !!

        newRecipe = Recipe.objects.create(
            title = title,
            description = description,
            imageUrl = imageUrl,
        )
        newRecipe.categories.set(categoriesIds),
        newRecipe.steps.set(stepsIds),
        newRecipe.ingredients.set(ingredientsIds)
        newRecipe.save();
        return newRecipe


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(many=False)
    recipe = RecipeSerializer(many=False)

    class Meta:
        model = RecipeIngredient
        fields = ['id',  'recipe', 'ingredient', 'unit', 'quantity']

class RecipeCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=False)
    recipe = RecipeSerializer(many=False)

    class Meta:
        model = RecipeIngredient
        fields = ['id',  'recipe', 'category']

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'recipe', 'user', 'stars']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    
    class Meta:
        model = Comment
        fields = ['id', 'dateAdded', 'user', 'recipe', 'content']

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'recipe', 'user']
  