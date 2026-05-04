#general
import os
from django.shortcuts import render
from .models import *
from .serializers import *
from django.core.mail import send_mail, get_connection
from .permissions import *
from django.template.loader import render_to_string
#rest
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)

        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class ForgotPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=400)

        token_obj = PasswordResetToken.objects.create(user=user)
        reset_link = f"https://shafins-lms-app-react.onrender.com/reset-password/{token_obj.token}"

        # temporarily return link in response instead of emailing
        return Response({
            "message": "Password reset link generated",
            "reset_link": reset_link
        })
    permission_classes = []

    def post(self, request):
        try:
            email = request.data.get("email")
            print("STEP 1 - EMAIL RECEIVED:", email)

            try:
                user = User.objects.get(email=email)
                print("STEP 2 - USER FOUND:", user.username)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=400)

            token_obj = PasswordResetToken.objects.create(user=user)
            print("STEP 3 - TOKEN CREATED:", token_obj.token)

            reset_link = f"https://shafins-lms-app-react.onrender.com/reset-password/{token_obj.token}"

            try:
                html_message = render_to_string('password_reset_email.html', {
                    'username': user.username,
                    'reset_link': reset_link,
                })
                print("STEP 4 - TEMPLATE RENDERED OK")
            except Exception as e:
                print("STEP 4 FAILED - TEMPLATE ERROR:", str(e))
                return Response({"error": "Template error"}, status=500)

            try:
                connection = get_connection(
                    backend='django.core.mail.backends.smtp.EmailBackend',
                    host='smtp.gmail.com',
                    port=587,
                    username=os.getenv('EMAIL_HOST_USER'),
                    password=os.getenv('EMAIL_HOST_PASSWORD'),
                    use_tls=True,
                    timeout=10
                )
                print("STEP 5 - CONNECTION CREATED")

                send_mail(
                    subject="Reset Your LMS Password",
                    message=f"Reset your password here: {reset_link}",
                    from_email=None,
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                    connection=connection,
                )
                print("STEP 6 - EMAIL SENT OK")
                return Response({"message": "Password reset email sent successfully"})

            except Exception as e:
                import traceback
                traceback.print_exc()
                print("STEP 5/6 FAILED - EMAIL ERROR:", str(e))
                return Response({"error": f"Email failed: {str(e)}"}, status=500)

        except Exception as e:
            import traceback
            traceback.print_exc()
            print("UNEXPECTED ERROR:", str(e))
            return Response({"error": "Unexpected error"}, status=500)
    permission_classes = []

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=400)

        token_obj = PasswordResetToken.objects.create(user=user)
        reset_link = f"https://shafins-lms-app-react.onrender.com/reset-password/{token_obj.token}"

        html_message = render_to_string('password_reset_email.html', {
            'username': user.username,
            'reset_link': reset_link,
        })

        try:
            # open connection with explicit timeout
            connection = get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                host='smtp.office365.com',
                port=587,
                username=os.getenv('EMAIL_HOST_USER'),
                password=os.getenv('EMAIL_HOST_PASSWORD'),
                use_tls=True,
                timeout=10  # fail after 10 seconds instead of hanging forever
            )

            send_mail(
                subject="Reset Your LMS Password",
                message=f"Reset your password here: {reset_link}",
                from_email=None,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
                connection=connection,
            )
            return Response({"message": "Password reset email sent successfully"})

        except Exception as e:
            print("EMAIL ERROR:", str(e))
            return Response({"error": f"Email failed: {str(e)}"}, status=500)
    
class ResetPasswordView(APIView):
    permission_classes = []

    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        try:
            token_obj = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response({"error": "Invalid token"}, status=400)

        if token_obj.is_expired():
            return Response({"error": "Token expired"}, status=400)

        user = token_obj.user
        user.set_password(new_password)
        user.save()

        # delete token after use
        token_obj.delete()

        return Response({"message": "Password reset successful"})
    
class AdminOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response({"message": "Hello Admin"})
    
class InstructorOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def get(self, request):
        return Response({"message": "Hello Instructor"})

class StudentOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        return Response({"message": "Hello Student"})