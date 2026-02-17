from rest_framework.decorators import api_view
from rest_framework.response import Response
from auth_app.serializers import AuthMeSerializer

@api_view(['GET'])
def auth_me(request):
    if request.user.is_authenticated:
        user = request.user
        data = AuthMeSerializer(user).data
        return Response(data)

    return Response({'detail' : "Unauthorized"}, status=403)