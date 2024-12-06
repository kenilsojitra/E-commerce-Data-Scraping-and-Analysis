from django.contrib import admin
from django.urls import path
from app import views
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('result/', views.result, name='result'), 
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('history/', views.history, name='history'),
    path('download_csv/<str:filename>/', views.download_csv, name='download_csv'),
    path('view_csv/<str:file_name>/', views.view_csv, name='view_csv'),
    path('rename/', views.rename_file, name='rename_file'),
    path('delete/', views.delete_file, name='delete_file'),
    # path('analysis/', views.analysis, name='analysis'),
    path('upload_csv/', views.upload_csv, name='upload_csv'), 
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.LogoutPage, name='logout'),  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

