from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics

from api.models import Order
from api.serializers import OrderCreateSerializer, OrderSerializer


class OrdersView(generics.ListAPIView):
    """
    Представление для получения списка заказов текущего пользователя.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Возвращаем заказы только текущего пользователя
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class CreateOrderView(APIView):
    """
    APIView для заказов.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)

        order = serializer.create_order(
            user=request.user,
            validated_data=serializer.validated_data
        )

        return Response({"message": "Заказ успешно создан", "order_id": order.id}, status=status.HTTP_201_CREATED)
