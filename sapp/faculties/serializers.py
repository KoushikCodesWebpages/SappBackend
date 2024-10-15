from rest_framework import serializers
from rest_framework import serializers
from accounts.models import Subject
from faculties.models import FacultyDB
from accounts.serializers import UserSerializer, SectionSerializer, SubjectSerializer


class FacultyDBSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    section = SectionSerializer(required=False, allow_null=True)  # Optional section
    subjects = SubjectSerializer(many=True)  # Faculty can teach multiple subjects

    class Meta:
        model = FacultyDB
        fields = ['id', 'user', 'image', 'name', 'address', 'reg_no', 'role', 'section', 'subject']  # Include section and subjects

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        subject_data = validated_data.pop('subjects')  # Pop subjects data
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        faculty = FacultyDB.objects.create(user=user, **validated_data)

        # Adding subjects to the faculty
        for subject in subject_data:
            subject_obj, created = Subject.objects.get_or_create(name=subject['name'])
            faculty.subjects.add(subject_obj)
        return faculty

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        subject_data = validated_data.pop('subjects', None)

        # Update user information
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        # Update faculty-specific fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update subjects (clear and re-add)
        if subject_data:
            instance.subjects.clear()
            for subject in subject_data:
                subject_obj, created = Subject.objects.get_or_create(name=subject['name'])
                instance.subjects.add(subject_obj)

        return instance