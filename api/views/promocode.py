from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.serializers import PromoCodeCheckSerializer


class PromoCodeCheckView(APIView):
    """
    APIView для проверки промокода.
    """

    def post(self, request):
        serializer = PromoCodeCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
