from rest_framework import generics, mixins
from main_app.permissions import IsAdmin, IsSuperUser
from rest_framework.permissions import IsAuthenticated
from auth_app.models import User
from admin_panel_app.serializers.users import UserListSerializer

class UserListRetrieveAPIView(mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              generics.GenericAPIView):

    permission_classes = (IsAuthenticated, IsAdmin, IsSuperUser)
    serializer_class = UserListSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

