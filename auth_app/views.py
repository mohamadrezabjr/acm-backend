from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from auth_app.serializers import UserRegistrationSerializer
from auth_app.serializers import AuthMeSerializer
@api_view(['GET'])
def auth_me(request):
    if request.user.is_authenticated:
        user = request.user
        data = AuthMeSerializer(user).data
        return Response(data)

    return Response({'detail' : "Unauthorized"}, status=403)

class UserRegister(APIView):
    serializer_class = UserRegistrationSerializer
    def post(self, request):
        serialized_data = self.serializer_class(data = request.data)

        if serialized_data.is_valid():
            user = serialized_data.save()
            return Response({"detail" : "registration was successful"}, status=201)
        return Response({"detail" : "data is not valid for registration"}, status=400)