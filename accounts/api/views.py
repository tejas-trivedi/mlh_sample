import string
import secrets
from django.shortcuts import render
import random
import requests
import json
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import get_list_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect
from .forms import PasswordForm
from accounts.api.serializers import (
    CreateUserSerializer,
    UserLoginSerializer,
    GuestSignupSerializer,

)
from paytmpg import PaymentDetailsBuilder, Payment, UserInfo, EChannelId, Money, EnumCurrency, MerchantProperty
from paytmpg.pg.utils import SignatureUtil
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView, UpdateAPIView
)
from accounts.models import User, ACMMEMBER, GuestUser, Role, MembershipType
from paytm.models import Key, TransactToken


class CustomRegisterView(APIView):

    permission_classes = [AllowAny]
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        email_id = request.data.get("email_id")
        password = request.data.get("password")
        roles = request.data.get("roles")

        data = {"email_id": email_id, "password": password, "roles": [roles]}

        serializer = CreateUserSerializer(data=data)
        print(serializer)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = [
        AllowAny,
    ]

    def post(self, request):
        email_id = request.data.get("email_id")
        password = request.data.get("password")
        data = {"email_id": email_id, "password": password}
        # print(data)
        if email_id is None or password is None:
            serializer = UserLoginSerializer(data=data)
            if not serializer.is_valid():
                response = {"status": False, "detail": serializer.errors}
                return JsonResponse(response, safe=False)
        else:
            try:
                # CHECK IF PARTNER WITH ROLES as 5 exist
                user = User.objects.get(email_id=email_id)
                print(user)
                serializer = UserLoginSerializer()
                token = serializer.validate(attrs=data)
                # print(token)
                if not token:
                    response = {
                        "status": False,
                        "detail": "Please check your password and try again",
                    }
                    return JsonResponse(response, safe=False)
                else:
                    login(request, user)
                    response = {"status": True, "token": token}
                    return JsonResponse(response, safe=False)

            except User.DoesNotExist:
                return Response(
                    {"message": ["Register first"]}, status=status.HTTP_404_NOT_FOUND
                )


class UserLogoutView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, format=None):
        if request.user.auth_token.delete():
            return Response({"message": ["User logged out"]}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": ["Auth credentials not found"]},
                status=status.HTTP_404_NOT_FOUND,
            )


class ACMMemberRegisterView(APIView):

    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        member = request.user
        
        mid = Key.objects.all().values()
        print(mid)
        userrole = User.objects.get(email_id=request.user)
        print(userrole)
        userrole.roles.set('2')

        print(member)
        name = request.data.get("name")
        branch = request.data.get("branch")
        year = request.data.get("year")
        dob = request.data.get("dob")
        contact_number = request.data.get("contact_number")
        whatsapp_number = request.data.get("whatsapp_number")
        sap_id = request.data.get("sap_id")
        hostel_pg = request.data.get("hostel_pg")
        membership_type = request.data.get("membership_type")
        membership_type = MembershipType.objects.get(
            MEMBERSHIP=membership_type)
        validated_data = {"name": name, "member": member, "branch": branch, "year": year,
                          "dob": dob, "contact_number": contact_number,
                          "whatsapp_number": whatsapp_number, "sap_id": sap_id,
                          "hostel_pg": hostel_pg, "membership_type": membership_type,
                          }
        user = ACMMEMBER.objects.create(member=validated_data['member'], name=validated_data['name'], branch=validated_data['branch'], year=validated_data['year'],
                                        dob=validated_data[
            'dob'], contact_number=validated_data['contact_number'],
            whatsapp_number=validated_data['whatsapp_number'], sap_id=validated_data[
            'sap_id'], hostel_pg=validated_data['hostel_pg'],
            membership_type=validated_data['membership_type']
        )
        user.save()
        if user:
            amount = str(user.membership_type.price())
            order_id = str(get_random_alphanumeric_string(6)) + str(user.id)
            # print(order_id)
            merchantid = str(mid[0]['MID'])
            secretkey = mid[0]['secret_key']
            # print(merchantid,"-",secretkey)
            paytmParams = dict()
            paytmParams["body"] = {
                "requestType": "Payment",  # done
                "mid": merchantid,  # done
                "websiteName": "WEBSTAGING",  # done
                "orderId": order_id,  # done
                "callbackUrl": "https://merchant.com/callback",  # done
                "txnAmount": {
                    "value": amount,  # done
                    "currency": "INR",
                },
                "userInfo": {
                    "custId": "Member-0" + str(user.id),
                },
            }
            # print(paytmParams)
            checksum = SignatureUtil.generateSignature(
                json.dumps(paytmParams["body"]), secretkey)

            paytmParams["head"] = {
                "signature"	: checksum
            }
            # print(checksum)
            post_data = json.dumps(paytmParams)
            # for Staging
            url = "https://securegw-stage.paytm.in/theia/api/v1/initiateTransaction?mid={}&orderId={}".format(
                merchantid, order_id)
            # print(url)
            # for Production
            # url = "https://securegw.paytm.in/theia/api/v1/initiateTransaction?mid=YOUR_MID_HERE&orderId=ORDERID_98765"
            response = requests.post(url, data=post_data, headers={
                                     "Content-type": "application/json"}).json()
            print(response)
            if response['body']['resultInfo']['resultCode'] == '0000':
                order = TransactToken.objects.create(
                    user=member, amount=amount, order_id=order_id, signature=checksum, Txn_token=response['body']['txnToken'])
                order.save()
                if order:
                    responseData = dict()
                    responseData['body'] = {
                        'orderid': order_id,
                        'mid': merchantid,
                        'txnToken': response['body']['txnToken'],
                        'amount': amount,
                        'callbackurl': paytmParams['body']['callbackUrl']
                    }
                    return Response(responseData, status=status.HTTP_200_OK)
                return Response("Order Not Created", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response("Error", status=status.HTTP_400_BAD_REQUEST)


def get_random_alphanumeric_string(length):
    letters_and_digits = string.digits
    result_str = ''.join((random.choice(letters_and_digits)
                          for i in range(length)))
    return result_str


class GuestView(CreateAPIView):
    serializer_class = GuestSignupSerializer
    permission_classes = [
        AllowAny,
    ]

    def post(self, request, *args, **kwargs):
        guest_email = request.data.get('guest_email')
        guest = GuestUser.objects.filter(
            guest_email=guest_email).values('guest_id')
        if guest:
            guest_id = guest[0]['guest_id']
            responseData = {
                'Message': 'Verification mail Sent!',
            }
            token = secrets.token_hex(16)
            confirm_url = 'http://localhost:8000/accounts/pass/{}/{}/'.format(
                guest_id, token)
            print(confirm_url)
            send_mail('Welcome', 'This is a verification mail sent. Please click on the link below: {}'.format(
                confirm_url), 'test@gmail.com', [guest_email])
            return Response(responseData, status=status.HTTP_200_OK)
        guest_name = request.data.get('guest_name')
        guestlog = GuestUser.objects.create(
            guest_name=guest_name, guest_email=guest_email)
        guestlog.save()
        guest_id = guestlog.guest_id
        responseData = {
            "Guest id": guest_id,
        }
        token = secrets.token_hex(16)
        confirm_url = 'http://localhost:8000/accounts/pass/{}/{}/'.format(
            guest_id, token)
        print(confirm_url)
        send_mail('Welcome', 'This is a verification mail sent. Please click on the link below: {}'.format(
            confirm_url), 'test@gmail.com', [guest_email])
        return Response(responseData, status=status.HTTP_201_CREATED)


class CheckEmail(APIView):

    """
    """
    permission_classes = [AllowAny]  # [IsAuthenticated, ]

    def get(self, request, format=None):
        email = request.data.get("email")
        user = User.objects.filter(
            email_id=email).values('email_id')
        print(user)
        if user:
            email = user[0]['email_id']
            responseData = {
                'Email': email
            }
            return Response(responseData, status=status.HTTP_200_OK)
        guest = GuestUser.objects.filter(
            guest_email=email).values('guest_email')
        print(guest)
        if guest:
            email = guest[0]['guest_email']
            responseData = {
                'Email': email,
                'Message': "Please Verify your email address"
            }
            return Response(responseData, status=status.HTTP_401_UNAUTHORIZED)
        return Response("Try Again", status=status.HTTP_404_NOT_FOUND)


def form_pass(request, guest_id, randomstring):
    """
    working
    """
    guest = GuestUser.objects.filter(
        guest_id=guest_id).values('guest_email', 'guest_name')
    if guest:
        email = guest[0]['guest_email']
        name = guest[0]['guest_name']
        user = User.objects.filter(email_id=email)
        if user:
            return HttpResponse('Already Verified')
        print(guest)
        form = PasswordForm()
        if request.method == 'POST':
            form = PasswordForm(request.POST)
            if form.is_valid():
                roles = 3
                password = form.cleaned_data['password']
                guestuser = User.objects.create(
                    email_id=email, roles=roles, password=password)
                print(guestuser)
                guestuser.save()
                return HttpResponse("Verfied")
        return render(request, 'password.html', {'form': form, 'email': email, 'name': name})
    return HttpResponse("Link Expired")