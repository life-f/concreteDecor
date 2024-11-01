from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from api.serializers import ActivationSerializer

class ActivationView(generics.GenericAPIView):
    serializer_class = ActivationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Аккаунт успешно активирован!"}, status=status.HTTP_200_OK)
