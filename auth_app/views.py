from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

@api_view(['GET'])
def auth_me(request):
    if request.user.is_authenticated:
        user = request.user
        return Response({
            "id" : user.id,
            "phone" : user.phone,
        })
    return Response({'detail' : "Unauthorized"}, status=403)