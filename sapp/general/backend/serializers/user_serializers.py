

# UserSerializer remains the same



# Updated StudentsDBSerializer


# Updated FacultyDBSerializer with new fields

    
    
class ProfileSerializer(serializers.Serializer):
    student_profile = StudentsDBSerializer(required=False)  # Optional field for student profile
    faculty_profile = FacultyDBSerializer(required=False)  # Optional field for faculty profile

