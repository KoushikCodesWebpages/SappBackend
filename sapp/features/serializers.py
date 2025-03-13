from rest_framework import serializers


from accounts.models import Student, Faculty, SOAdmin
from accounts.serializers import AuthUserSerializer
from features.models import Announcement,Timetable,Attendance, AttendanceLock,CalendarEvent, Result, ResultLock, Assignment, Submission, Portion

class StudentProfileSerializer(serializers.ModelSerializer):
    user = AuthUserSerializer()  # Assuming this is your custom user serializer

    class Meta:
        model = Student
        fields = ['user', 'enrollment_number', 'standard', 'section', 'subjects','academic_year', 'attendance_percent','image','last_updated','student_code']

    def update(self, instance, validated_data):
        # Handle user update (username, email)
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        # Update the student profile data
        return super().update(instance, validated_data)

'''class FacultyNavbarSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Faculty
        fields = ['name']
'''
class FacultyProfileSerializer(serializers.ModelSerializer):
    user = AuthUserSerializer()

    class Meta:
        model = Faculty
        fields = ['user', 'faculty_id', 'department', 'specialization', 'coverage', 'class_teacher','image','last_updated']
    
    def update(self, instance, validated_data):
        # Handle user update (username, email)
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        # Update the student profile data
        return super().update(instance, validated_data)
    
    
class SOProfileSerializer(serializers.ModelSerializer):
    user = AuthUserSerializer()

    class Meta:
        model = SOAdmin
        fields = ['user','employee_id','school_name','image','last_updated']
    
    def update(self, instance, validated_data):
        # Handle user update (username, email)
        user_data = validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        # Update the student profile data
        return super().update(instance, validated_data)
    
    



class AttendanceLockSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLock
        fields = ['id', 'date', 'is_locked','last_updated']
        
class AttendanceSerializer(serializers.ModelSerializer):
    student = serializers.CharField(source='student.student_code')  # Display student_code in the response

    class Meta:
        model = Attendance
        fields = ['id', 'student', 'date', 'status','last_updated']

    def create(self, validated_data):
        # Extract the student_code from the validated data
        student_code = validated_data.get('student', None)

        if student_code:
            # Look up the Student object based on student_code
            try:
                student = Student.objects.get(student_code=student_code)
            except Student.DoesNotExist:
                raise serializers.ValidationError({"student": "Student with the provided student_code does not exist."})
            validated_data['student'] = student  # Set the student field to the actual Student object

        # Create the Attendance object with the student relation
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Extract the student_code from the validated data
        student_code = validated_data.get('student', None)

        if student_code:
            # Look up the Student object based on student_code
            try:
                student = Student.objects.get(student_code=student_code)
            except Student.DoesNotExist:
                raise serializers.ValidationError({"student": "Student with the provided student_code does not exist."})
            validated_data['student'] = student  # Set the student field to the actual Student object

        # Update the Attendance object with the new values
        return super().update(instance, validated_data)





class AnnouncementMainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'date', 'timings','last_updated']
        
class AnnouncementDetailedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = [
            'id',
            'title',
            'description',
            'date',
            'timings',
            'offline_or_online',
            'till',
            'last_updated'
        ]



class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = '__all__'




class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = '__all__'




class ResultLockSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)  # Include computed field

    class Meta:
        model = ResultLock
        fields = ['id', 'title', 'start_date', 'end_date','last_updated', 'is_active']  # Added `is_active`

class ResultSerializer(serializers.ModelSerializer):
    percentage = serializers.ReadOnlyField()  # Directly use model method

    class Meta:
        model = Result
        fields = ['id', 'result_lock', 'student', 'subject', 'marks', 'percentage','last_updated']

    def validate(self, data):
        """Use model's `clean()` method for validation instead of duplicating logic."""
        instance = Result(**data)  # Create an unsaved instance
        instance.clean()  # Call model's validation logic
        return data
    def get_percentage(self, obj):
        return obj.percentage()
            
            
  
            
class AssignmentMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'title','subject','completed','due_date','last_updated']
        
class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['faculty']
        
        


class StudentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id','assignment_title','student','image','document','mark','last_updated']
        read_only_fields = ['student']
        


   
   
        
class PortionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portion
        fields = ['id','standard','academic_year','subject','unit','title','description','reference','image','document','last_updated']