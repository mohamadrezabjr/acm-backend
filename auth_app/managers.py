from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password):
        if not email:
            raise ValueError("Error PhoneNumber")

        user = self.model(email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self , email, password):
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_admin = True
        user.is_creator = True
        user.save(using = self._db)
        return user