from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from api.models import Series
from api.serializers import SeriesSerializer

class SeriesDetailView(APIView):
    """
    API для получения информации о серии товаров и всех связанных товарах.
    """
    def get(self, request, id):
        series = get_object_or_404(Series, id=id)
        serializer = SeriesSerializer(series)
        return Response(serializer.data, status=status.HTTP_200_OK)
