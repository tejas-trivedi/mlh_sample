import requests
from rest_framework.response import Response
from rest_framework import views
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from django.http import HttpResponse
import datetime
import json
from paytmpg import PaymentDetailsBuilder, Payment, UserInfo, EChannelId, Money, EnumCurrency, MerchantProperty
from paytmpg.pg.utils import SignatureUtil
from django.shortcuts import render
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from rest_framework import status
from rest_framework.views import APIView
from django.http import HttpResponse, HttpResponseRedirect
import random
from firebase_admin import db
import uuid
# Create your views here.
from acm.settings import FIREBASE_API_KEY, MERCHANT_ID, MERCHANT_KEY



class EventRegister(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        if firebase_admin._DEFAULT_APP_NAME not in firebase_admin._apps:
            cred = credentials.Certificate(
                'db.json')
            check = firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://url.com'
            })
        uid = request.data.get("uid")
        sap = request.data.get("sap")
        name = request.data.get("name")
        email = request.data.get('email')
        branch = request.data.get("branch")
        year = request.data.get("year")
        contact_number = request.data.get("contact_number")
        whatsapp_number = request.data.get("whatsapp_number")
        user_type = request.data.get("user_type")
        amount = request.data.get("amount")
        event_name = request.data.get("event_name")
        try:
            ref = db.reference('events_reg/{}/{}'.format(event_name, sap))
            refer = ref.get()
        except firebase_admin.exceptions.FirebaseError as ex:
            print('Error message:', ex)
            print('Error code:', ex.code)  # Platform-wide error code
            print('HTTP response:', ex.http_response)
        if refer == None:
            firebase_data = {
                "branch": branch,
                "contact": contact_number,
                "email": email,
                "name": name,
                "registrationTime": "",
                "sap": sap,
                "whatsappNo": whatsapp_number,
                "year": year,
                "amount": amount,
                "transaction_id": "",
                "user_type": user_type,
                "event_name": event_name
            }
            ref.update(firebase_data)

            merchantid = MERCHANT_ID
            secretkey = MERCHANT_KEY
            order_id = str(event_name + ":") + str(sap) + str(uuid)
            paytmParams = dict()
            paytmParams["body"] = {
                "requestType": "Payment",  # done
                "mid": merchantid,  # done
                "websiteName": "WEBSTAGING",  # done
                "orderId": order_id,  # done
                "callbackUrl": "https://securegw.paytm.in/theia/paytmCallback?ORDER_ID={}".format(order_id), 
                "txnAmount": {
                    "value": amount,  # done
                    "currency": "INR",
                },
                "userInfo": {
                    "custId": "Events-" + str(name),
                },
            }
            checksum = SignatureUtil.generateSignature(
                json.dumps(paytmParams["body"]), secretkey)
            paytmParams["head"] = {
                "signature"	: checksum
            }
            post_data = json.dumps(paytmParams)
            # for Staging
            #url = "https://securegw-stage.paytm.in/theia/api/v1/initiateTransaction?mid={}&orderId={}".format(
             #   merchantid, order_id)
            # for Production
            url = "https://securegw.paytm.in/theia/api/v1/initiateTransaction?mid=={}&orderId={}".format(merchantid, order_id)
            response = requests.post(url, data=post_data, headers={
                "Content-type": "application/json"}).json()
            if response['body']['resultInfo']['resultCode'] == '0000':
                responseData = dict()
                responseData['body'] = {
                    'orderid': order_id,
                    'mid': merchantid,
                    'txnToken': response['body']['txnToken'],
                    'amount': amount,   
                    'callbackurl': paytmParams['body']['callbackUrl']
                }
                return Response(responseData)
        event_detail = db.reference('acm_app_events/{}'.format(event_name))
        response_data = {
            "registered": True,
            "event": event_detail.get()
        }
        return Response(response_data, status=status.HTTP_200_OK)


class EventView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        response_data = "Hello"
        if firebase_admin._DEFAULT_APP_NAME not in firebase_admin._apps:
            cred = credentials.Certificate(
                'db.json')
            check = firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://url.com/'
            })
        # request the data
        uid = request.data.get("uid")
        event_name = request.data.get("event_name")
        # print(event_name)
        user = auth.get_user(uid)
        data = user._data
        # check whether a member or a anonymous
        if user.provider_data:
            pay_status = True
        else:
            pay_status = False
        # print(pay_status)
        # fetch details of the particular event
        event_detail = db.reference('acm_app_events/{}'.format(event_name))
        # print(event_detail.get('event_name'))
        event_type = event_detail.get('team')
        print(event_type[0]['team'])
        # print(event_detail.get('team'))
        if (event_type[0]['team'] == 'True'):
            print('Team event')

        #pay_status = True

        if pay_status:
            # this means he is a registred acm member
            sap_id = user.display_name
            amount = event_detail.get()['reg_amount_acm']
            # print(sap_id)
            try:
                # check if this user is already registered for this particular event or not
                #event_check = db.reference('events_reg/CSGO/{}'.format(sap_id))
                event_check = db.reference(
                    'events_reg/{}/{}'. format(event_name, sap_id))
                event_check = event_check.get()
                print(event_check)
            except firebase_admin.exceptions.FirebaseError as ex:
                print('Error message:', ex)
                print('Error code:', ex.code)  # Platform-wide error code
                print('HTTP response:', ex.http_response)
            if event_check == None:
                # if returned none that means not exist so fetch the details of that particular user and return it as a response
                detail = db.reference('acm_acmw_members/{}'.format(sap_id))
                print(detail.get())
                name = detail.get()['name']
                amount = event_detail.get()['reg_amount_acm']
                email = detail.get()['email']
                branch = detail.get()['branch']
                year = detail.get()['year']
                contact_number = detail.get()['contact']
                whatsapp_number = detail.get()['whatsappNo']
                user_detail = {
                    "event_registred": False,
                    "branch": branch,
                    "contact": contact_number,
                    "email": email,
                    "name": name,
                    "registrationTime": "",
                    "sap": sap_id,
                    "whatsappNo": whatsapp_number,
                    "year": year,
                    "amount": amount,
                    "transaction_id": "",
                    "type": "acm_member"
                }
                return Response(user_detail, status=status.HTTP_200_OK)
            # this means he has already registered for the event so return already registered and the event details
            response_data = {
                "event_registered": True,
                "event_date": event_detail.get()["date"],
                "event_name": event_detail.get()["event_name"],
                "amount": amount
            }
            return Response(response_data, status=status.HTTP_200_OK)
        amount = event_detail.get()['reg_amount_non_acm']
        # this means that he is a anonymous user and the front has tp render the form for the user to post that details in next view
        anonymous = {
            "amount": amount,
            "Anonymous": True
        }
        return Response(anonymous, status=status.HTTP_200_OK)