from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    email = models.EmailField('email address', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return "{}".format(self.email)


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    NOVICE = 0
    BEGINNER = 1
    COMPETENT = 2
    PROFICIENT = 3
    EXPERT = 4
    LEVEL_CHOICES = [
        (NOVICE, 'novice'),
        (BEGINNER, 'beginner'),
        (COMPETENT, 'competent'),
        (PROFICIENT, 'proficient'),
        (EXPERT, 'expert'),
    ]

    SECONDS = 's'
    MINUTES = 'm'
    HOURS = 'h'
    DAYS = 'd'
    PREPARATION_TIME_UNIT_CHOICES = [
        (SECONDS, 'seconds'),
        (MINUTES, 'minutes'),
        (HOURS, 'hours'),
        (DAYS, 'days')
    ]
    user = models.ForeignKey(User, related_name='recipes', on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=150, unique=True)
    description = models.TextField(max_length=1500)
    imageUrl = models.CharField(max_length=400)
    preparationTime = models.FloatField(validators=[MinValueValidator(0)])
    preparationTimeUnit = models.CharField(max_length=1, choices=PREPARATION_TIME_UNIT_CHOICES)
    level = models.IntegerField(choices=LEVEL_CHOICES, default=COMPETENT)
    dateAdded = models.DateField(auto_now=True)
    categories = models.ManyToManyField(Category)

    def no_of_rating(self):
        ratings = Rating.objects.filter(recipe=self)
        return len(ratings)

    def avg_rating(self):
        m_sum = 0
        ratings = Rating.objects.filter(recipe=self)
        for rating in ratings:
            m_sum += rating.stars
        if len(ratings) > 0:
            return m_sum / len(ratings)
        else:
            return 0

    def __str__(self):
        return self.title


GRAM = 'g'
KILOGRAM = 'kg'
PIECE = 'piece'
TABLESPOON = 'tablespoon'
TEASPOON = 'teaspoon'
PINCH = 'pinch'
UNIT_CHOICES = [
    (GRAM, 'gram'),
    (KILOGRAM, 'kilogram'),
    (TABLESPOON, 'tablespoon'),
    (TEASPOON, 'teaspoon'),
    (PINCH, 'pinch'),
    (PIECE, 'piece')
]


class Unit(models.Model):
    full = models.CharField(max_length=50, unique=True)
    short = models.CharField(max_length=25, unique=True)

    def __str__(self):
        return self.full


class Ingredient(models.Model):
    name = models.CharField(max_length=150, unique=True)
    imageUrl = models.CharField(max_length=400, blank=True, null=True)
    quantity = models.FloatField(validators=[MinValueValidator(0)])
    unit = models.ForeignKey(Unit, related_name='ingredient_unit', on_delete=models.CASCADE)
    allowedUnits = models.ManyToManyField(Unit)
    kcal = models.PositiveIntegerField()
    isActive = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='ingredients', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(validators=[MinValueValidator(0)])
    unit = models.ForeignKey(Unit, related_name='recipe_unit', on_delete=models.CASCADE)

    def allowed_units(self):
        if self.pk is not None:
            return list(map(lambda u: u.full, self.ingredient.allowedUnits.all()))
        return "------"

    class Meta:
        unique_together = (('recipe', 'ingredient'),)

    def __str__(self):
        return self.ingredient.name + ' ' + str(self.quantity)


class Step(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='steps', on_delete=models.CASCADE)
    description = models.TextField(max_length=1500)
    order = models.IntegerField(validators=[MinValueValidator(1)])
    imageUrl = models.CharField(max_length=400, blank=True, null=True)

    class Meta:
        unique_together = (('recipe', 'order'),)

    def __str__(self):
        return self.description[0: 20]


class Comment(models.Model):
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(max_length=1500)
    dateAdded = models.DateField(auto_now_add=True)
    dateModified = models.DateField(auto_now=True)
    isActive = models.BooleanField(default=True)

    class Meta:
        index_together = (('user', 'recipe'),)


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = (('user', 'recipe'),)
        index_together = (('user', 'recipe'),)


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'recipe'),)
        index_together = (('user', 'recipe'),)
