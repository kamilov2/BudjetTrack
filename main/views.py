import logging
import traceback
import random
from django.shortcuts import render, get_object_or_404, get_list_or_404
from rest_framework.views import APIView
from rest_framework import generics, status
from django.conf import settings
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import authenticate, login, logout
from drf_yasg import openapi
from django.contrib.auth import update_session_auth_hash
from django.db.models import Sum
from datetime import datetime
from django.db.models import Count
from django.utils import timezone
from dateutil import parser
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db import transaction
from .serializers import *

logger = logging.getLogger(__name__)

class LimitAPIView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LimitSerializer

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="OK",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'profile': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'limit': openapi.Schema(type=openapi.TYPE_NUMBER),
                    },
                ),
            ),
            400: "Bad Request",
            500: "Internal Server Error",
        },
        operation_description="Retrieve or update user's limit.",
    )
    def get(self, request):
        try:
            with transaction.atomic():
                profile, created = Profile.objects.get_or_create(user=request.user)
                limit_instance, _ = Limit.objects.get_or_create(profile=profile)
                
                serializer = LimitSerializer(limit_instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Error {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

     

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="OK",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'profile': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'limit': openapi.Schema(type=openapi.TYPE_NUMBER),
                    },
                ),
            ),
            400: "Bad Request",
            500: "Internal Server Error",
        },
        operation_description="Update user's limit.",
    )
    def post(self, request):
        limit_value = request.data.get('limit')
        print(limit_value, "hello")

        try:
            with transaction.atomic():
                profile, created = Profile.objects.get_or_create(user=self.request.user)

                limit_instance = Limit.objects.filter(profile=profile).first()

                if limit_instance is None:
                    limit_instance = Limit(profile=profile, limit=0)
                
                if limit_value is not None:
                    limit_instance.limit = limit_value
                else:
                    limit_instance.limit = 0

                limit_instance.save()

                serializer = LimitSerializer(limit_instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f'Error: {e}')  
            return Response({'error': f'Error {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            201: openapi.Response(
                description="Created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'profile': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'user': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    },
                ),
            ),
            400: "Bad Request",
            500: "Internal Server Error",
        },
        operation_description="Register a new user.",
    )
    def post(self, request):
        """
        Register a new user.

        Parameters:
        - email (str): Email of the user.
        - password (str): Password of the user.

        Returns:
        - 201: Created with the details of the created user and profile.
        - 400: Bad Request if the request data is invalid.
        - 500: Internal Server Error if there is an issue with user authentication.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            if User.objects.filter(email=email).exists():
                return Response({'error': 'Bunday email royhatdan otgan.'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(username=email, email=email, password=password)
            profile = Profile.objects.create(user=user, email=email)

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                profile_serializer = ProfileSerializer(profile)
                return Response(profile_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Failed to authenticate user.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class CategoryAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'title': openapi.Schema(type=openapi.TYPE_STRING),
                            'emoji': openapi.Schema(type=openapi.TYPE_STRING),
                            'profile': openapi.Schema(type=openapi.TYPE_INTEGER),
                        },
                    ),
                ),
            ),
            400: "Bad Request",
            404: "Not Found",
        },
        operation_description="Get user's expense categories.",
    )
    def get(self, request):
        """
        Get user's expense categories.

        Returns:
        - 200: Success with a list of user's expense categories.
        - 400: Bad Request if the request is invalid.
        - 404: Not Found if the profile for the current user is not found.
        """
        profile = get_object_or_404(Profile, user=self.request.user)
        expense_category = get_list_or_404(ExpenseCategory, profile=profile)
        serializer = ExpenseCategorySerializer(expense_category, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={
            201: openapi.Response(
                description="Created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'title': openapi.Schema(type=openapi.TYPE_STRING),
                        'emoji': openapi.Schema(type=openapi.TYPE_STRING),
                        'profile': openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            400: "Bad Request",
            404: "Not Found",
        },
        operation_description="Create user's expense categories.",
    )
    def post(self, request):
        """
        Create user's expense categories.

        Parameters:
        - title (str): Title of the expense category.
        - emoji (str): Emoji representing the expense category.

        Returns:
        - 201: Created with the details of the created expense category.
        - 400: Bad Request if the request data is invalid.
        - 404: Not Found if the profile for the current user is not found.
        """
        try:
            profile = get_object_or_404(Profile, user=self.request.user)

            data = [request.data] if not isinstance(request.data, list) else request.data

            serializer = ExpenseCategorySerializer(data=data, many=True, context={'request': request})

            if serializer.is_valid():
                serializer.save(profile=profile)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Profile.DoesNotExist:
            return Response({"error": "Profile not found for the current user."}, status=status.HTTP_404_NOT_FOUND)

class UpdatePasswordAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: "Bad Request",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['old_password', 'new_password'],
        ),
        operation_description="Update user's password.",
    )
    def post(self, request):
        """
        Update user's password.

        Parameters:
        - old_password (str): Old password of the user.
        - new_password (str): New password to set for the user.

        Returns:
        - 200: Success with a message.
        - 400: Bad Request if the request data is invalid.
        """
        serializer = UpdatePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            if not user.check_password(old_password):
                return Response({'error': 'Incorrect old password.'}, status=400)

            user.set_password(new_password)
            user.save()

            update_session_auth_hash(request, user)

            return Response({'success': 'Password updated successfully.'}, status=200)
        else:
            return Response(serializer.errors, status=400)

class ExpenseAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get expense details for a specific date",
        manual_parameters=[
            openapi.Parameter(
                'date',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Date parameter in the format dd-mm-yyyy',
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successful response",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'date': openapi.Schema(type=openapi.TYPE_STRING),
                        'total_amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'expense_history': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'category__title': openapi.Schema(type=openapi.TYPE_STRING),
                                    'category__emoji': openapi.Schema(type=openapi.TYPE_STRING),
                                    'description': openapi.Schema(type=openapi.TYPE_STRING),
                                }
                            ),
                        ),
                    },
                ),
            ),
            400: "Bad Request",
            404: "Profile not found for the current user",
        },
    )
    def get(self, request):
        try:
            profile = get_object_or_404(Profile, user=self.request.user)

            date_str = self.request.query_params.get('date')
            if not date_str:
                return JsonResponse({"error": "Date parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                input_datetime = datetime.strptime(date_str, '%Y-%m-%d')    
                formatted_date = input_datetime.strftime('%b. %d, %Y')
                date = parser.parse(formatted_date).date()
            except ValueError:
                return JsonResponse({"error": "Invalid date format. Use 'yyyy-mm-dd'."}, status=status.HTTP_400_BAD_REQUEST)

            total_amount = Expense.objects.filter(profile=profile, reg_date=date).aggregate(Sum('amount'))['amount__sum'] or 0      

            expense_history = Expense.objects.filter(profile=profile, reg_date=date).values(
                'amount', 'category__title', 'category__emoji', 'description'
            ).order_by('-reg_date')

            return JsonResponse({
                'date': date_str,
                'total_amount': float(total_amount),
                'expense_history': list(expense_history),
            })

        except Profile.DoesNotExist:
            return JsonResponse({"error": "Profile not found for the current user."}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request):
        try:
            profile = get_object_or_404(Profile, user=self.request.user)

            category_id, description, amount = (
                request.data.get('category_id'),
                request.data.get('description', ''),
                request.data.get('amount')
            )

            if not category_id or not amount:
                return Response({"error": "category_id and amount are required fields."}, status=status.HTTP_400_BAD_REQUEST)

            category = get_object_or_404(ExpenseCategory, id=category_id)

            expense_data = {
                "profile": profile.id,
                "category": category.id,
                "amount": amount,
                "description": description,
            }

            serializer = ExpenseSerializer(data=expense_data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Profile.DoesNotExist:
            return Response({"error": "Profile not found for the current user."}, status=status.HTTP_404_NOT_FOUND)
        




class ExpenseCategoryTotalAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            current_month = timezone.now().month
            current_year = timezone.now().year

            expenses = Expense.objects.filter(
                profile=request.user.profile,
                reg_date__month=current_month,
                reg_date__year=current_year
            ).values('category__id', 'category__title', 'category__emoji').annotate(
                total_count=Count('id'), total_amount=Sum('amount'))

            results = []

            for expense in expenses:
                category_title = expense['category__title']
                category_emoji = expense['category__emoji']
                total_count = expense['total_count']
                total_amount = expense['total_amount']

                results.append({
                    'category_title': category_title,
                    'category_emoji': category_emoji,
                    'total_count': total_count,
                    'total_amount': total_amount,
                })

            total_category_amount = sum(expense['total_amount'] for expense in expenses)

            for result in results:
                result['total_category_amount'] = total_category_amount

            serializer = ExpenseCategoryTotalSerializer(results, many=True)

            return Response(serializer.data)
        except Exception as e:
            print("Exception:", e)
            print("Traceback:", traceback.format_exc())  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class AllExpenseAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            date_param = request.query_params.get('date')

            if date_param:
                try:
                    date_object = datetime.strptime(date_param, '%Y-%m-%d')
                    current_month = date_object.month
                    current_year = date_object.year
                except ValueError:
                    return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                current_month = timezone.now().month
                current_year = timezone.now().year

            expenses = Expense.objects.filter(
                profile=request.user.profile,
                reg_date__month=current_month,
                reg_date__year=current_year
            ).values('category__id', 'category__title', 'category__emoji').annotate(
                total_count=Count('id'), total_amount=Sum('amount'))

            results = []

            for expense in expenses:
                category_title = expense['category__title']
                category_emoji = expense['category__emoji']
                total_count = expense['total_count']
                total_amount = expense['total_amount']

                results.append({
                    'category_title': category_title,
                    'category_emoji': category_emoji,
                    'total_count': total_count,
                    'total_amount': total_amount,
                })

            total_category_amount = sum(expense['total_amount'] for expense in expenses)

            for result in results:
                result['total_category_amount'] = total_category_amount

            serializer = ExpenseCategoryTotalSerializer(results, many=True)

            return Response(serializer.data)
        except Exception as e:
            print("Exception:", e)
            print("Traceback:", traceback.format_exc())  
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class LogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]    
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="OK",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            401: "Unauthorized",
        },
        operation_description="Logout the authenticated user.",
    )
    def post(self, request):
        """
        Logout the authenticated user.

        Returns:
        - 200: OK with a detail message.
        - 401: Unauthorized if the user is not authenticated.
        """
        logout(request)
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="OK",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_STRING),
                        'csrf_token': openapi.Schema(type=openapi.TYPE_STRING),
                        'sessionid': openapi.Schema(type=openapi.TYPE_STRING),
                        'auth_token': openapi.Schema(type=openapi.TYPE_STRING),  
                    },
                ),
            ),
            400: "Bad Request",
            401: "Unauthorized",
        },
        operation_description="Authenticate user.",
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = authenticate(request, username=email)
            if user is None:
                return Response({"error":"Username yoqi parol notogri."})

                

            if user is not None:
                login(request, user)

                auth_token, created = Token.objects.get_or_create(user=user)

                response_data = {
                    'success': 'User authenticated successfully.',
                    'auth_token': auth_token.key, 
                }
                response = Response(response_data, status=status.HTTP_200_OK)
                return response
            else:
                return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
            

class PasswordResetAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        verification_code = str(random.randint(1000, 9999))
        user = authenticate(request, username=email)
        auth_token, created = Token.objects.get_or_create(user=user)

        try:
            profile, created = Profile.objects.get_or_create(email=email)
        except Profile.MultipleObjectsReturned:
            return Response({'error': _('Найдено несколько профилей для этого адреса электронной почты.')}, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response({'error': _('Профиль не найден для этого адреса электронной почты.')}, status=status.HTTP_404_NOT_FOUND)

        profile.verification_code = verification_code
        profile.save()

        subject = _('Код сброса пароля')
        message_text = _('Ваш код подтверждения: {0}').format(verification_code)
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = email

        try:
            send_mail(subject, message_text, from_email, [to_email])
        except Exception as e:
            stack_trace = traceback.format_exc()

            self.send_error_to_server(stack_trace, request.data)

            return Response(
                {'error': _('Не удалось отправить электронное письмо. Пожалуйста, попробуйте снова позже.'),
                 'stack_trace': stack_trace},  
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        response_data = {
            'status': 'ok',
            'message': _('Электронное письмо успешно отправлено.'),
            'token': auth_token.key  
        }
        return Response(response_data , status=status.HTTP_200_OK)