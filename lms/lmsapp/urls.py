from django.urls import path
from .views import *

urlpatterns = [
    path("courses/", CourseListView.as_view()),                  
    path("courses/create/", CourseCreateView.as_view()),         
    path("courses/<int:pk>/", CourseDetailView.as_view()),       
    path("courses/<int:pk>/update/", CourseUpdateView.as_view()),
    path("courses/<int:pk>/delete/", CourseDeleteView.as_view()),
    path("my-courses/", MyCoursesView.as_view()),

    path("enroll/", EnrollView.as_view()),                       
    path("my-enrollments/", MyEnrollmentsView.as_view()), 

    path("courses/<int:course_id>/lessons/", LessonListView.as_view()),
    path("lessons/<int:pk>/", LessonDetailView.as_view()),
    path("lessons/create/", LessonCreateView.as_view()),

    path("dashboard/", DashboardView.as_view()),
    path("categories/", CategoryView.as_view()),
]