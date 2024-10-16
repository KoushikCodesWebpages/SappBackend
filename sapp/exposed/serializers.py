from accounts.models import Standard, Section, Subject
from rest_framework import serializers


class StandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Standard
        fields = ['id', 'name']


# SectionSerializer for section field in faculty and student models
class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['section_id', 'name']


# SubjectSerializer for handling subjects in FacultyDBSerializer
class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['subject_id', 'name']