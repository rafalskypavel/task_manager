from typing import Dict, Any, Optional

from rest_framework import serializers
from django.utils import timezone

from .models import Task
from .services.task_validation import validate_status_or_raise, normalize_deadline_input, validate_telegram_user_id
from .services.task_crud import create_task, update_task
from .services.task_status import update_task_status


class TaskSerializer(serializers.ModelSerializer):
    deadline_local = serializers.SerializerMethodField(read_only=True)
    deadline_input = serializers.DateTimeField(
        write_only=True,
        required=False,
        input_formats=['%d.%m.%Y %H:%M', 'iso-8601']
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'deadline_input', 'deadline_local',
            'telegram_user_id', 'status', 'notification_sent', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'notification_sent', 'created_at', 'deadline', 'deadline_local']
        extra_kwargs = {
            'telegram_user_id': {'write_only': True},
            'deadline': {'required': False, 'write_only': True}
        }

    def validate_status(self, value: str) -> str:
        try:
            return validate_status_or_raise(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    def validate_deadline_input(self, value: Any) -> Any:
        try:
            return normalize_deadline_input(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    def validate_telegram_user_id(self, value: int) -> int:
        try:
            return validate_telegram_user_id(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    def get_deadline_local(self, obj: Task) -> Optional[str]:
        if obj.deadline:
            return timezone.localtime(obj.deadline).strftime('%d.%m.%Y %H:%M')
        return None

    def create(self, validated_data: Dict[str, Any]) -> Task:
        return create_task(validated_data)

    def update(self, instance: Task, validated_data: Dict[str, Any]) -> Task:
        return update_task(instance, validated_data)


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required=True)

    class Meta:
        model = Task
        fields = ['status']

    def validate_status(self, value: str) -> str:
        try:
            return validate_status_or_raise(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    def update(self, instance: Task, validated_data: Dict[str, Any]) -> Task:
        return update_task_status(instance, validated_data['status'])
