from django.db import models
from accounts.models import *
from audit.models import *
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)  
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    parent = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="children")
    users = models.ManyToManyField(User, through="UserCategory", related_name="categories")

    def __str__(self):
        return str(self.name)



class Recommendation(models.Model):
    recommendation = models.CharField(max_length=500, unique=True)
    weight = models.IntegerField(default=0)
    categories = models.ManyToManyField(Category, blank=True) 

    def __str__(self):
        return str(self.recommendation)

class Question(models.Model):
    question = models.CharField(max_length=512)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    answerType = models.ForeignKey(
        "Question_type", on_delete=models.PROTECT, default=None, blank=True, null=True
    )
    min = models.FloatField(blank=True, null=True)
    max = models.FloatField(blank=True, null=True)
    time_start = models.TimeField(blank=True, null=True)
    time_end = models.TimeField(blank=True, null=True)
    weight = models.IntegerField(default=1, null=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    recommendations = models.ManyToManyField(Recommendation)

    def __str__(self):
        return str(self.question)

class Question_type(models.Model):
    type = models.CharField(max_length=36, default=None, null=True, blank=True)
    def __str__(self):
        return self.type

class UserCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_tracking = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "category")

    def __str__(self):
        return f"{self.user} - {self.category}"

class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField(default="null")

    def __str__(self):
        return f"{self.question.question} - {self.answer}"

class NodePosition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    node_id = models.CharField(max_length=255)
    x = models.FloatField()
    y = models.FloatField()

    class Meta:
        unique_together = ('user', 'node_id',)

    def __str__(self):
        return f"{self.user.username} - {self.node_id}"

