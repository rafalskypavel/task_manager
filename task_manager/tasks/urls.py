from django.urls import path
from .views import TaskViewSet

urlpatterns = [
    path('tasks/', TaskViewSet.as_view({
        'post': 'create',
        'get': 'list' # для фильтрации  в TaskViewSet есть filter_backends и filterset_fields
    }), name='task-list-create'),
    path('tasks/<int:pk>/', TaskViewSet.as_view({
        'get': 'retrieve',
        'patch': 'partial_update'
    }), name='task-detail'),
]