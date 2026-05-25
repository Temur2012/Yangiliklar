from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Asosiy
    path('',                         views.home,           name='home'),
    path('news/<int:pk>/',           views.news_detail,    name='news_detail'),
    path('category/<slug:slug>/',    views.category_detail,name='category_detail'),
    path('search/',                  views.search,         name='search'),
    path('contact/',                 views.contact,        name='contact'),

    # Yangilik CRUD (superuser)
    path('news/create/',             views.news_create,    name='news_create'),
    path('news/<int:pk>/edit/',      views.news_edit,      name='news_edit'),
    path('news/<int:pk>/delete/',    views.news_delete,    name='news_delete'),

    # Izohlar
    path('news/<int:pk>/comment/',        views.add_comment,    name='add_comment'),
    path('comment/<int:pk>/delete/',      views.delete_comment, name='delete_comment'),

    # Accounts
    path('', include('accounts.urls')),
]

# Render serverida (DEBUG=False bo'lganda ham) rasmlar ishlashi uchun:
if settings.DEBUG or not settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)