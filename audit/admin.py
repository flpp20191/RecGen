from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Question_type)
admin.site.register(Recommendation)
admin.site.register(NodePosition)
admin.site.register(UserAnswer)
admin.site.register(UserCategory)

class SubthemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)


class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('recommendation', 'weight')
    search_fields = ('recommendation',)


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'category')
    search_fields = ('question',)
    list_filter = ('category',)