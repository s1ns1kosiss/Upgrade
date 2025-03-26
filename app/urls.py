from django.urls import path
from .views import home, prodDetail

urlpatterns = [
    path('', home , name="home"),
    path('product/<int:id>', prodDetail, name='prodDetail'),
]