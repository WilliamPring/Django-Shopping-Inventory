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
    """
    Retrieve or post a cart.
    """
    def get(self, request, prodID, format=None):
        try:
            Cart.objects.filter(prod_id=prodID)
            cart = Cart.objects.all().filter(prod_id=prodID)
            serializer = CartSerializer(cart, many = True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({'error':'no cart found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, format=None):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            product = Product.objects.all().filter(prod_id=serializer.validated_data['prod_id'].prod_id)
            if product.count() < 1:
                return Response({'error': 'no such product'}, status=status.HTTP_404_NOT_FOUND)
            if product[0].in_stock == 0:
                return Response({'error': 'product is not in stock'}, status=status.HTTP_400_BAD_REQUEST)
            instance = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        errorMessage = ''
        if ('order_id' in serializer.errors):
            errorMessage += 'Issues with order ID '
        if ('prod_id' in serializer.errors):
            errorMessage += 'Issues with product ID'
        if errorMessage == '':
            errorMessage = serializer.errors
        return Response({'error':errorMessage}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        try:
            pass
        except Card.DoesNotExist:
            return Response({'error':'No card found'}, status=status.HTTP_404_NOT_FOUND)

class OrderAPIView(APIView):
    """
    Retrieve, insert, update or delete an order.
    """
    def get(self, request, orderID, format=None):
        try:
             Order.objects.get(order_id=orderID)
             #__iexact case insensitive
             order = Order.objects.all().filter(order_id=orderID)
             serializer = OrderSerializer(order, many = True)
             return Response(serializer.data, status=status.HTTP_200_OK)    
        except Order.DoesNotExist:
            return Response({'error':'no order found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, format=None):
        #regOrder = re.compile(r'^(0[1-9]|1[012][-](0[1-9]|[12][0-9]|3[01])[-]\d{2})$')
        regOrder = re.compile(r'^((\d{4})[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01]))$')
        serializer = OrderSerializer(data=request.data)         
        if serializer.is_valid():
            if ('order_id' in request.data):
                return Response({'error': 'no specify orderID'}, status=status.HTTP_400_BAD_REQUEST)
            # this check is redundant, serializer.is_valid() is going to check for date format regardless
            elif (regOrder.match(str(serializer.validated_data['order_date']))):
                instance = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'date should be in MM-DD-YY format'}, status=status.HTTP_400_BAD_REQUEST)   
        if ('cust_id' in serializer.errors):
            return Response({'error': "Issue with the customer ID"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    #order update

    def customerExists(self, customerID):
        customer = Customer.objects.all().filter(cust_id=customerID)
        if customer.count() < 1:
            return False
        else:
            return True

    def put(self, request, format=None):
        try:    
            req = json.loads( request.body.decode('utf-8') )
            if ('order_id' in req) and ('po_number' in req) and (req['order_id'] != '') and (req['po_number'] != ''):
                Order.objects.get(order_id=req['order_id'])
                if req['cust_id'] == '' and req['order_date'] == '':
                    customer = Order.objects.select_for_update().filter(order_id=req['order_id']).update(po_number = req["po_number"])
                elif req['cust_id'] != '' and req['order_date'] == '':
                    if not self.customerExists(req['cust_id']):
                        return Response({'error':'No customer found'}, status=status.HTTP_404_NOT_FOUND)
                    customer = Order.objects.select_for_update().filter(order_id=req['order_id']).update(po_number = req["po_number"], cust_id=req['cust_id'])
                elif req['cust_id'] == '' and req['order_date'] != '':
                    customer = Order.objects.select_for_update().filter(order_id=req['order_id']).update(po_number = req["po_number"], order_date=req['order_date'])
                else:
                    if not self.customerExists(req['cust_id']):
                        return Response({'error':'No customer found'}, status=status.HTTP_404_NOT_FOUND)
                    customer = Order.objects.select_for_update().filter(order_id=req['order_id']).update(po_number = req["po_number"], cust_id=req['cust_id'], order_date=req['order_date'])
                #if(customer <= 0):
                    #return Response(customer.data)
                return Response(req, status=status.HTTP_200_OK)
            else: 
                errorMessage = ""
                if ('order_id' not in req) or (req['order_id'] == ''):
                    errorMessage += "No order_id "
                if ('po_number' not in req) or (req['po_number'] == ''):
                    errorMessage +=  "No po_number "
                return Response({'error': errorMessage}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({'error':'No order found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, format=None):
        try:
            orderID = request.data['order_id']
            order = Order.objects.all().filter(order_id=orderID)
            if order.count() < 1:
                return Response({'error': 'no order found'}, status=status.HTTP_404_NOT_FOUND)
            event = Order.objects.get(order_id=orderID)
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except KeyError:
            return Response({'error': 'no order id provided'}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({'error':'no customer found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, format=None):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            if('cust_id' in request.data): 
                return Response({'error': 'no specify custID'}, status=status.HTTP_400_BAD_REQUEST)
            elif(self.r.match(serializer.validated_data['phone_number'])):
                instance = serializer.save()
            else:
                return Response({'error': 'phone format is not correct'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, format=None):
        req = json.loads( request.body.decode('utf-8') )
        if ('cust_id' in req) and ('first_name' in req) and ('last_name' in req):
            if req["phone_number"] == '':
                customer = Customer.objects.select_for_update().filter(cust_id=req["cust_id"]).update(first_name = req["first_name"], last_name = req["last_name"])
            else:
                if self.r.match(req['phone_number']):
                    customer = Customer.objects.select_for_update().filter(cust_id=req["cust_id"]).update(first_name = req["first_name"], last_name = req["last_name"], phone_number=req["phone_number"])
                else:
                    return Response({'error': 'Invalid phone number format'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(req, status=status.HTTP_200_OK)
            #if(customer <= 0):
            #    return Response(customer.data)
        else:
            errorMessage = ""
            if ('cust_id' not in req):
                errorMessage += "no cust_id "
            if ('first_name' not in req):
                errorMessage +=  "no first_name"
            if ('last_name' not in req):
                errorMessage +=  "no last_name"
            return Response({'error': errorMessage}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, name=None, format=None):
        try:
            lastName = request.data['last_name']
            customer = Customer.objects.all().filter(last_name=lastName)
            if customer.count() < 1:
                return Response({'error': 'no customer found'}, status=status.HTTP_404_NOT_FOUND)
            event = Customer.objects.get(last_name=lastName)
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except KeyError:
            return Response({'error': 'no last name provided'}, status=status.HTTP_400_BAD_REQUEST)

class ProductAPIView(APIView):
    """
    Retrieve, update or delete a product.
    """
    def get(self, request, prodName=None, soldout=None, format=None):
        try:
            if soldout is None and prodName is not None:
                Product.objects.get(prod_name=prodName)
                #__iexact case insensitive
                product = Product.objects.all().filter(prod_name__iexact=prodName)
                serializer = ProductSerializer(product, many = True)
                return Response(serializer.data)
            elif soldout is not None and prodName is None:
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
                    return Response({'error':'no product found'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error':'no product found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, format=None):
        req = json.loads(request.body.decode('utf-8'))
        if ('prod_id' in req) and ('prod_name' in req) and ('price' in req) and ('in_stock' in req) and ('prod_weight' in req):
            product = Product.objects.select_for_update().filter(prod_id=req['prod_id']).update(prod_name=req['prod_name'], price=req['price'], in_stock=req['in_stock'], prod_weight=req['prod_weight'])
            #if (product <= 0):
                #return Response(product.data)
            return Response(req, status=status.HTTP_200_OK)
        else:
            errorMessage = ''
            if ('prod_id' not in req):
                errorMessage += "no prodID "
            if ('prod_name' not in req):
                errorMessage += "no prod name "
            if ('price' not in req):
                errorMessage += "no price "
            if ('in_stock' not in req):
                errorMessage += "no in stock "
            if ('prod_weight' not in req):
                errorMessage += "no prod weight "
            return Response({'error': errorMessage}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            if ('prod_id' in request.data):
                return Response({'error': 'no specify prodID'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                instance = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        try:
            prodID = request.data['prod_id']
            product = Product.objects.all().filter(prod_id=prodID)
            if product.count() < 1:
                return Response({'error': 'no product with this id'}, status=status.HTTP_400_BAD_REQUEST)
            event = Product.objects.get(prod_id=prodID)
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except KeyError:
            return Response({'error': 'no prod id provided'}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({'error':'no customer found'}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({'error':'no order found'}, status=status.HTTP_404_NOT_FOUND)

class CustomerOrderPoAPIView(APIView):
    """
    Retrieve information about customer, order, and PO at the same time
    """

    def calculatePO(self, customer, order):
        carts = Cart.objects.all().filter(order_id=order[0].order_id)
        total = 0.0
        for element in carts:
            product = element.prod_id
            if product.in_stock > 0:
                total += product.price * element.quantity
        return total

    def get(self, request, name, poName=None, orderDate=None, first=True, format=None):
        try:
            if first:
                customer = Customer.objects.all().filter(first_name=name)
            else:
                customer = Customer.objects.all().filter(last_name=name)

            if customer.count() < 1:
                return Response({'error': 'no such customer'}, status=status.HTTP_404_NOT_FOUND)

            if poName is None and orderDate is not None:
                order = Order.objects.all().filter(order_date=orderDate, cust_id=customer[0].cust_id)
            else:
                order = Order.objects.all().filter(po_number=poName, cust_id=customer[0].cust_id)

            if order.count() < 1:
                return Response({'error': 'no such order for the given customer'}, status=status.HTTP_404_NOT_FOUND)

            serializer_customer = CustomerSerializer(customer, many=True)
            serializer_order = OrderSerializer(order, many=True)

            poValue = self.calculatePO(customer, order)

            serializer = [serializer_customer.data, serializer_order.data, [{'po' : poValue}]]
            return Response(serializer)
        except Customer.DoesNotExist:
            return Response({'error': 'no customer'}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({'error': 'no order'}, status=status.HTTP_404_NOT_FOUND)
