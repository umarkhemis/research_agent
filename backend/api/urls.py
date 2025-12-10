from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'papers', views.PaperViewSet, basename='paper')
router.register(r'literature-reviews', views.LiteratureReviewViewSet, basename='literature-review')
router.register(r'search-history', views.SearchHistoryViewSet, basename='search-history')
router.register(r'notes', views.ProjectNoteViewSet, basename='note')
router.register(r'export', views.ExportViewSet, basename='export')
router.register(r'statistics', views.StatisticsViewSet, basename='statistics')

urlpatterns = [
    path('', include(router.urls)),
]
