from rest_framework import serializers
from audit.models import *
from accounts.models import *

class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ['recommendation', 'weight']

class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question_type
        fields = ['type']

class QuestionSerializer(serializers.ModelSerializer):
    recommendations = RecommendationSerializer(many=True, read_only=True)
    answerType = QuestionTypeSerializer(read_only=True)

    class Meta:
        model = Question
        fields = ['question', 'answerType', 'min', 'max', 'time_start', 'time_end', 'weight', 'description', 'recommendations']

class categorySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, source='question_set')

    class Meta:
        model = Category
        fields = ['name', 'description', 'questions']
