from typing import List
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Task
from .serializers import TaskSerializer, TaskStatusUpdateSerializer
from django.utils import timezone
from datetime import timedelta


class TaskViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch']  # Только разрешённые методы
    queryset = Task.objects.all().only(
        'id',  # Для всех операций (GET/PATCH)
        'title',  # Для создания/просмотра задачи (POST/GET)
        'description',  # Для создания/просмотра задачи (POST/GET)
        'deadline',  # Для проверки в Celery + вывод в API
        'telegram_user_id',  # Для фильтрации (?telegram_user_id=) и Celery
        'status',  # Для PATCH /tasks/<id>/ (обновление статуса)
    )
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend] # Только фильтрация по telegram_user_id
    filterset_fields: List[str] = ['telegram_user_id', 'status']  # Именно это поле позволяет фильтровать
    lookup_field = 'pk'

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return TaskStatusUpdateSerializer  # Только статус
        return TaskSerializer  # Все поля для GET/POST

    # обновление статуса задачи
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if set(request.data.keys()) != {'status'}:
            return Response(
                {"error": "Only 'status' field is allowed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(  # Автоматически выберет TaskStatusUpdateSerializer
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)  # Вернёт только {"status": "done"}


    @action(detail=False, methods=['get'])
    def deadline_soon(self, request):
        """Дополнительный endpoint для Celery чтобы находить задачи с приближающимся дедлайном"""
        soon_deadline = timezone.now() + timedelta(minutes=10)
        tasks = Task.objects.filter(
            deadline__lte=soon_deadline,
            deadline__gte=timezone.now(),
            status=Task.Status.UNDONE
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

