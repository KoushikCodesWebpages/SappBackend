from rest_framework import serializers
from django.contrib.auth.models import User
from backend.models.base_models import Standard, Section
from backend.models.user_models import FacultyDB, StudentsDB, Subject

# UserSerializer remains the same
class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],  # Set email as the username
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user


# StandardSerializer remains unchanged
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


# Updated StudentsDBSerializer
from rest_framework import serializers
class StudentsDBSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    standard = StandardSerializer()  # Nested serializer for standard
    section = SectionSerializer()    # Nested serializer for section
    title = serializers.SerializerMethodField()  # Use SerializerMethodField to get the username

    class Meta:
        model = StudentsDB
        fields = ['id', 'user', 'image', 'standard', 'section', 'title', 'description']  # Ensure all relevant fields are included

    def get_title(self, obj):
        return obj.user.username  # Return the username as the title

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def create(self, validated_data):
        user_data = validated_data.pop('user')  # Pop user data from the validated data
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)

        # Create the student instance with the user instance
        student = StudentsDB.objects.create(user=user, **validated_data)
        
        # Set the title to the username and save
        student.title = user.username  
        student.save()  # Save the student instance to persist the title

        return student


# Updated FacultyDBSerializer with new fields
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
    
    
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    standard = StandardSerializer(required=False)
    section = SectionSerializer(required=False)
    title = serializers.CharField(source='title', required=False)  # Directly map to the title field in the model
    description = serializers.CharField(required=False)

    class Meta:
        fields = ['id', 'user', 'image', 'standard', 'section', 'title', 'description']

    def update(self, instance, validated_data):
        # Determine whether the instance is a student or faculty
        if isinstance(instance, StudentsDB):
            self.Meta.model = StudentsDB
        elif isinstance(instance, FacultyDB):
            self.Meta.model = FacultyDB
        else:
            raise serializers.ValidationError("Invalid instance type.")

        # Update user details
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        # Update other fields in the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

