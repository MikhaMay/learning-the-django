from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import SimpleRouter
from store.views import BookViewSet, auth

router = SimpleRouter()
router.register(r'book', BookViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_django.urls', namespace='social')),  
    path('auth/', auth),
]

urlpatterns += router.urls
