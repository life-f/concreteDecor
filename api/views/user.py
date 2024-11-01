from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from api.serializers import CustomUserUpdateSerializer
from api.models import CustomUser


class CustomUserUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]  # Только авторизованные пользователи

    def get_object(self):
        # Получаем текущего авторизованного пользователя
        user = self.request.user
        # Проверка, что пользователь редактирует только свои данные
        try:
            return CustomUser.objects.get(id=user.id)
        except CustomUser.DoesNotExist:
            raise PermissionDenied("Вы не можете редактировать данные другого пользователя.")
