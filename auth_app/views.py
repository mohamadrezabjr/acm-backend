from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def auth_me(request):
    if request.user.is_authenticated:
        user = request.user
        return Response({
            "id" : user.id,
            "phone" : user.phone,
            "role" : user.role,
            "first_name" : user.person.first_name,
            "last_name" : user.person.last_name,
            "bio" : user.person.bio,
            "student_id" : user.person.student_id
        })

    return Response({'detail' : "Unauthorized"}, status=403)