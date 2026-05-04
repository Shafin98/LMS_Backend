from django.shortcuts import render
from .models import *
from authapp.permissions import *
from .serializers import *

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Create your views here.

# ============================Course==========================================================
class CourseCreateView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def post(self, request):
        serializer = CourseCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        course = serializer.save()

        return Response({
            "message": "Course created",
            "course_id": course.id
        })
    
class CourseListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)

        return Response(serializer.data)
    
class CourseDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=404)

        serializer = CourseSerializer(course)
        return Response(serializer.data)
    
class CourseUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def put(self, request, pk):
        try:
            course = Course.objects.get(pk=pk, instructor=request.user)
        except Course.DoesNotExist:
            return Response({"error": "Not allowed"}, status=403)

        serializer = CourseCreateSerializer(course, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Course updated"})
    
class CourseDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def delete(self, request, pk):
        try:
            course = Course.objects.get(pk=pk, instructor=request.user)
        except Course.DoesNotExist:
            return Response({"error": "Not allowed"}, status=403)

        course.delete()
        return Response({"message": "Course deleted"})
    
# ============================Course==========================================================

class EnrollView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request):
        serializer = EnrollmentCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save()

        return Response({
            "message": "Enrolled successfully",
            "enrollment_id": enrollment.id
        })
    
class MyCoursesView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def get(self, request):
        courses = Course.objects.filter(instructor=request.user)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
    
class MyEnrollmentsView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        enrollments = Enrollment.objects.filter(student=request.user)
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    
class LessonCreateView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def post(self, request):
        course_id = request.data.get("course")

        if not Course.objects.filter(id=course_id, instructor=request.user).exists():
            return Response({"error": "You can only add lessons to your own courses"}, status=403)

        serializer = LessonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lesson = serializer.save()

        return Response({"message": "Lesson created", "id": lesson.id})
    
class LessonListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        lessons = Lesson.objects.filter(course_id=course_id).order_by("order")
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)
    
class LessonDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            lesson = Lesson.objects.get(pk=pk)
        except Lesson.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = LessonSerializer(lesson)
        return Response(serializer.data)
    
class DashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        # per-course enrollment stats
        course_stats = []
        for course in Course.objects.all():
            course_stats.append({
                "course": course.title,
                "enrollments": Enrollment.objects.filter(course=course).count()
            })

        # top 5 courses by enrollment
        top_courses = sorted(course_stats, key=lambda x: x["enrollments"], reverse=True)[:5]

        # per-instructor course count
        instructor_stats = []
        for instructor in User.objects.filter(role="instructor"):
            instructor_stats.append({
                "instructor": instructor.username,
                "courses": Course.objects.filter(instructor=instructor).count()
            })

        return Response({
            "total_courses": Course.objects.count(),
            "total_enrollments": Enrollment.objects.count(),
            "total_students": User.objects.filter(role="student").count(),
            "total_instructors": User.objects.filter(role="instructor").count(),
            "top_courses": top_courses,
            "instructor_stats": instructor_stats,
        })
    
class CategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = CourseCategory.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.role == 'admin':
            return Response({"error": "Only admins can create categories"}, status=403)
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)
