from rest_framework import generics, mixins
from rest_framework.permissions import IsAuthenticated
from main_app.permissions import IsAdmin, IsSuperUser
from auth_app.models import User
from admin_panel_app.serializers.users import UserListSerializer, UserDetailSerializer

class UserListRetrieveAPIView(mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              generics.GenericAPIView):

    permission_classes = (IsAuthenticated, IsAdmin, IsSuperUser)
    serializer_class = UserListSerializer
    queryset = User.objects.select_related("person")

    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            return self.retrieve(request, *args, **kwargs)
        return self.list(request, *args, **kwargs)

class UserDetailAPIView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsAdmin, IsSuperUser)
    serializer_class = UserDetailSerializer
    queryset = User.objects.select_related("person")