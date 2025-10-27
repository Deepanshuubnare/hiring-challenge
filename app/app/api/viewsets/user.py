from rest_framework.response import Response
from app.serializers import input, output
from app.models.user import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from django.utils import timezone


class CreateUser(APIView):
    permission_classes = (AllowAny,)
    input_serializer_class = input.CreateUserInputSerializer
    output_serializer_class = output.UserOutputSerializer

    def post(self, request, *args, **kwargs):
        input_serializer = self.input_serializer_class(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # --- THIS IS THE FIX ---
            # We call `create` (not `create_user`) and pass all validated data.
            # The CustomUserManager's `create` method requires the password
            # and will handle the hashing automatically.
            user = User.objects.create(**input_serializer.validated_data)

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            output_serializer = self.output_serializer_class(user)
            return Response(
                {
                    'user': output_serializer.data,
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }, 
                status=status.HTTP_201_CREATED
            )
        

class LoginUser(APIView):
    permission_classes = (AllowAny,)
    input_serializer_class = input.LoginUserInputSerializer
    output_serializer_class = output.UserOutputSerializer

    def post(self, request, *args, **kwargs):
        input_serializer = self.input_serializer_class(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        
        phone_number = input_serializer.validated_data['phone_number']
        password = input_serializer.validated_data['password']

        try:
            # 1. IF USER EXISTS -> AUTHENTICATE
            user = User.objects.get(phone_number=phone_number)
            
            if not user.check_password(password):
                return Response(
                    {'error': 'Invalid password.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # User exists and password is correct
            user.last_login = timezone.now()
            user.save()
            status_code = status.HTTP_200_OK

        except User.DoesNotExist:
            # 2. IF USER DOES NOT EXIST -> CREATE NEW ACCOUNT
            
            # --- THIS IS THE FIX ---
            # We must pass the password to the `create` method,
            # just as we do in CreateUser, because the manager requires it.
            user = User.objects.create(
                phone_number=phone_number,
                first_name="User", # Add a placeholder name
                password=password  # Pass the password to the manager
            )
            
            # We no longer need user.set_password() or user.save()
            # because the `create` method handles it.
            
            status_code = status.HTTP_201_CREATED

        # Generate tokens for the user (either found or newly created)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        output_serializer = self.output_serializer_class(user)
        return Response(
            {
                'user': output_serializer.data,
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 
            status=status_code # Return 200 (OK) or 201 (Created)
        )

