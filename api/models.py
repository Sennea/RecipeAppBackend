from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.files.storage import FileSystemStorage
from django.conf import settings
# Create your models here.

class Category(models.Model): 
    name = models.CharField(max_length=150, blank=False, unique=True);

    def __str__(self):
        return self.name

class Ingredient(models.Model): 
    name = models.CharField(max_length=150, blank=False)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(blank=False, null=True, default=0)
    unit = models.CharField(max_length=30, null=True, blank=True, default = '')

    def __str__(self):
        if self.unit:
            return  self.ingredient.name  + ' ' + str(self.quantity) + ' ' + self.unit
        else:
            return  self.ingredient.name  + ' ' + str(self.quantity)

class Step(models.Model):
    step = models.TextField(max_length=1500, blank=False);

    def __str__(self):
        return self.step[0: 20]

LEVEL_CHOICES = (
    ('intern','Intern'),
    ('junior','Junior'),
    ('mid','Mid'),
    ('senior', 'Senior'),
    ('architect', 'Architect'),
)

class Recipe(models.Model):
    title = models.CharField(max_length=150, unique=True, blank=False)
    description = models.TextField(max_length=1500, blank=False)
    imageUrl = models.CharField(max_length=400, blank=False)
    preparationTime = models.CharField(max_length=150, blank=False, default="")
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, default='mid')
    dateAdded = models.DateField(auto_now=True, blank=False, null=True)
    categories = models.ManyToManyField(Category)
    ingredients = models.ManyToManyField(RecipeIngredient)
    steps = models.ManyToManyField(Step)

    def no_of_rating(self):
        ratings = Rating.objects.filter(recipe=self)
        return len(ratings)
    
    def avg_rating(self):
        sum = 0
        ratings = Rating.objects.filter(recipe=self)
        for rating in ratings:
            sum += rating.stars
        if len(ratings) > 0:
            return sum / len(ratings)
        else:
            return 0

    def __str__(self):
        return self.title



class RecipeCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return  self.category.name + "  " + self.recipe.title


class Comment(models.Model): 
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, blank=True, null=True, default="") 
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, default="") 
    content = models.TextField(max_length=1500, blank=False, null=True)
    dateAdded = models.DateField(auto_now=True, blank=False, null=True)
    class Meta: 
        index_together = (('user', 'recipe'),)
        

class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, blank=False, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=True)
    stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    class Meta: 
        unique_together = (('user', 'recipe'),)
        index_together = (('user', 'recipe'),)

class Favorite(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, blank=False, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=True)
    class Meta: 
        unique_together = (('user', 'recipe'),)
        index_together = (('user', 'recipe'),)