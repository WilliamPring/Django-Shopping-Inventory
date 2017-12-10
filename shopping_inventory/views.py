from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CustomerSerializer, ProductSerializer, OrderSerializer, CartSerializer
from .models import Customer, Product, Order, Cart
from django.http import Http404
import json
import re
# Create your views here.


class CartAPIView(APIView):
    def get(self, request, prodID, format=None):
        try:
            Cart.objects.filter(prod_id=prodID)
            cart = Cart.objects.all().filter(prod_id=prodID)
            serializer = CartSerializer(cart, many = True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderAPIView(APIView):
    def get(self, request, orderID, format=None):
        try:
             Order.objects.get(order_id=orderID)
             #__iexact case insensitive
             order = Order.objects.all().filter(order_id=orderID)
             serializer = OrderSerializer(order, many = True)
             return Response(serializer.data, status=status.HTTP_200_OK)    
        except Order.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        #regOrder = re.compile(r'^(0[1-9]|1[012][-](0[1-9]|[12][0-9]|3[01])[-]\d{2})$')
        regOrder = re.compile(r'^((\d{4})[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01]))$')
        serializer = OrderSerializer(data=request.data)        
        if serializer.is_valid():
            if ('cust_id' not in request.data):
                return Response({'error': 'no specify custID'}, status=status.HTTP_400_BAD_REQUEST)
            elif (regOrder.match(str(serializer.validated_data['order_date']))):
                instance = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'date should be in MM-DD-YY format'}, status=status.HTTP_400_BAD_REQUEST)            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #order update
    def put(self, request, format=None):
        try:
            req = json.loads( request.body.decode('utf-8') )
            if ('order_id' in req) and ('po_number' in req):
                Order.objects.get(order_id=req['order_id'])
                customer = Order.objects.select_for_update().filter(order_id=req['order_id']).update(po_number = req["po_number"])
                if(customer <= 0):
                    return Response(customer.data)
                return Response(req, status=status.HTTP_200_OK)
            else: 
                errorMessage = ""
                if ('order_id' not in req):
                    errorMessage += "no order_id "
                if ('po_number' not in req):
                    errorMessage +=  "no po_number "
        except Order.DoesNotExist:
            raise Http404
    

class CustomerAPIView(APIView):
    """
    Retrieve, update or delete a customer.
    """
    #regex for phone number
    r = re.compile(r'\b\d{3}[-.]?\d{3}[-]\d{4}\b')
    def get(self, request, name, format=None):
        try:
             Customer.objects.get(first_name=name)
             #__iexact case insensitive
             customer = Customer.objects.all().filter(first_name__iexact=name)
             #expecting many
             serializer = CustomerSerializer(customer, many = True)
             return Response(serializer.data)
        except Customer.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            if('cust_id' in request.data): 
                return Response({'error': 'no specify custID'}, status=status.HTTP_400_BAD_REQUEST)
            elif(self.r.match(serializer.validated_data['phone_number'])):
                instance = serializer.save()
            else:
                return Response({'error': 'phone not correct'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, format=None):
        req = json.loads( request.body.decode('utf-8') )
        if ('cust_id' in req) and ('first_name' in req) and ('last_name' in req):
            customer = Customer.objects.select_for_update().filter(cust_id=req["cust_id"]).update(first_name = req["first_name"], last_name = req["last_name"])
            if(customer <= 0):
                return Response(customer.data)
        else:
            errorMessage = ""
            if ('cust_id' not in req):
                errorMessage += "no cust_id "
            if ('first_name' not in req):
                errorMessage +=  "no first_name"
            if ('last_name' not in req):
                errorMessage +=  "no last_name"
            return Response({'error': errorMessage}, status=status.HTTP_400_BAD_REQUEST)

        return Response(req, status=status.HTTP_200_OK)

    def delete(self, request, name, format=None):
        event = Customer.objects.get(last_name=name)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductAPIView(APIView):
    """
    Retrieve, update or delete a product.
    """
    def get(self, request, prodName, format=None):
        try:
             Product.objects.get(prod_name=prodName)
             #__iexact case insensitive
             product = Product.objects.all().filter(prod_name__iexact=prodName)
             serializer = ProductSerializer(product, many = True)
             return Response(serializer.data)
        except Product.DoesNotExist:
            raise Http404 

    def get(self, request, soldout, format=None):
        try:
            if soldout.lower() == "no":
                product = Product.objects.all().filter(in_stock__gt=0)
                serializer = ProductSerializer(product, many = True)
                return Response(serializer.data)
            elif soldout.lower() == "yes":
                product = Product.objects.all().filter(in_stock__lte=0)
                serializer = ProductSerializer(product, many = True)
                return Response(serializer.data)
            else:
                raise Product.DoesNotExist
        except Product.DoesNotExist:
            raise Http404 
    # def post(self, request, format=None):
    #     serializer = ProductSerializer(data=request.data)
    #     if serializer.is_valid():
    #         instance = serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerOrderAPIView(APIView):
    """
    Retrieve information about customer and order at the same time
    """
    def get(self, request, phone, orderDate, format=None):
        try:
            Customer.objects.get(phone_number=phone)
            Order.objects.get(order_date=orderDate)

            customer = Customer.objects.all().filter(phone_number=phone)
            order = Order.objects.all().filter(order_date=orderDate)

            serializer_customer = CustomerSerializer(customer, many= True)
            serializer_order = OrderSerializer(order, many= True)   

            serializer = [serializer_customer.data, serializer_order.data]
            return Response(serializer)
        except Customer.DoesNotExist:
            raise Http404
        except Order.DoesNotExist:
            raise Http404

class CustomerOrderPoAPIView(APIView):
    """
    Retrieve information about customer, order, and PO at the same time
    """
    def get(self, request, name, poName=None, first=True, format=None):
        try:
            if first:
                Customer.objects.get(first_name=name)
                customer = Customer.objects.all().filter(first_name=name)
            else:
                Customer.objects.get(last_name=name)
                customer = Customer.objects.all().filter(last_name=name)
            #Order.objects.get(po_number=poName)
            order = Order.objects.all().filter(po_number=poName)

            serializer_customer = CustomerSerializer(customer, many=True)
            serializer_order = OrderSerializer(order, many=True)

            serializer = [serializer_customer.data, serializer_order.data]
            return Response(serializer)
            #return Response()
        except Customer.DoesNotExist:
            raise Http404
        except Order.DoesNotExist:
            raise Http404
