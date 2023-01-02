from django.urls import path
from .views import CustomUserLoginView, CustomUserRegistrationView, upload_image


app_name = "jwt_app"

urlpatterns = [
    path('upload_image/', upload_image, name="upload-image"), 
    path('custom_user_registration/', CustomUserRegistrationView.as_view(), name="custom-user-registration"),
    path('custom_user_login/', CustomUserLoginView.as_view(), name="custom-user-login"),
]