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
#import logging
# Create your views here.


#logger = logging.getLogger(__name__)

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
            req = json.loads(request.body.decode('utf-8'))
            if ('order_id' in req) and (req['order_id'] != '') and ('prod_id' in req) and (req['prod_id'] != ''):
                if ('quantity' in req) and (req['quantity'] != ''):
                    cart = Cart.objects.select_for_update().filter(order_id=req['order_id'], prod_id=req['prod_id']).update(quantity=req['quantity'])
                    return Response(req, status=status.HTTP_200_OK)
                return Response(req, status=status.HTTP_204_NO_CONTENT)
            else:
                errorMessage = ''
                if ('order_id' not in req) or (req['order_id'] == ''):
                    errorMessage += "No order_id "
                if ('prod_id' not in req) or (req['prod_id'] == ''):
                    errorMessage += "No prod_id "
                return Response({'error': errorMessage}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({'error':'No card found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({'error':'Invalid input value'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        try:
            orderID = request.data['order_id']
            prodID = request.data['prod_id']
            cart = Cart.objects.all().filter(order_id=orderID, prod_id=prodID)
            if cart.count() < 1:
                return Response({'error': 'No cart found'}, status=status.HTTP_404_NOT_FOUND)
            event = Cart.objects.get(order_id=orderID, prod_id=prodID)
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except KeyError:
            return Response({'error': 'No IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({'error': 'No customer found'}, status=status.HTTP_404_NOT_FOUND)
            event = Customer.objects.get(last_name=lastName)
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except KeyError:
            return Response({'error': 'No last name provided'}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response({'error': 'No product with this id'}, status=status.HTTP_400_BAD_REQUEST)
            event = Product.objects.get(prod_id=prodID)
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except KeyError:
            return Response({'error': 'No prod id provided'}, status=status.HTTP_400_BAD_REQUEST)

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
        totalPiece = 0.0
        totalWeight = 0
        for element in carts:
            product = element.prod_id
            if product.in_stock > 0:
                total += product.price * element.quantity
                totalWeight += product.prod_weight * element.quantity
                totalPiece += element.quantity
        return total, totalPiece, totalWeight

    def get(self, request, orderID=None, custID=None, lastName=None, firstName=None, poNumber=None, orderDate=None, format=None):
        try:
            tax = '13'

            if custID != '':
                customer = Customer.objects.all().filter(cust_id=custID)
            else:
                if firstName == '' and lastName == '':
                    return Response({'error':'no customer info provided'}, status=status.HTTP_400_BAD_REQUEST)
                elif firstName == '' and lastName != '':
                    customer = Customer.objects.all().filter(last_name=lastName)
                elif firstName != '' and lastName == '':
                    customer = Customer.objects.all().filter(first_name=firstName)
                else:
                    customer = Customer.objects.all().filter(first_name=firstName, last_name=lastName)
            if customer.count() < 1:
                return Response({'error':'No customer with such parameters'}, status=status.HTTP_404_NOT_FOUND)

            if custID == '':
                custID = customer[0].cust_id

            if orderID !='':
                order = Order.objects.all().filter(order_id=orderID, cust_id=custID)
            else:
                if poNumber == '' and orderDate == '':
                    return Response({'error':'no order info provided'}, status=status.HTTP_400_BAD_REQUEST)
                elif poNumber != '' and orderDate == '':
                    order = Order.objects.all().filter(po_number=poNumber, cust_id=custID)
                elif poNumber == '' and orderDate != '':
                    order = Order.objects.all().filter(order_date=orderDate, cust_id=custID)
                else:
                    order = Order.objects.all().filter(order_date=orderDate, po_number=poNumber, cust_id=custID)
            if order.count() < 1:
                return Response({'error':'No order with such parameters'}, status=status.HTTP_404_NOT_FOUND)

            product = Product.objects.none()
            quantityList = []
            tempList = []
            # bulding temp list with products from each cart
            for oneOrder in order:
                cart = Cart.objects.all().filter(order_id=oneOrder.order_id)
                for oneCart in cart:
                    if oneCart.prod_id.in_stock > 0:
                        tempList.append(oneCart.prod_id)
                        quantityList.append(oneCart.quantity)
            # adding all products from the temp list to an empty Query set of Products
            products = product | tempList

            serializerCustomer = CustomerSerializer(customer, many=True)
            #serializerOrder = OrderSerializer(order, many=True)
            serializerOrder = OrderSerializer(order[0], many=False)
            serializerProduct = ProductSerializer(products, many=True)

            poValue, poPiece, poWeight = self.calculatePO(customer, order)
            measurementsList = {
                'subtotal': poValue,
                'tax': '{0:.2f}'.format(poValue * (int(tax) / 100)),
                'total': '{0:.2f}'.format(poValue * (1 + int(tax) / 100)),
                'pieces': poPiece,
                'weight': poWeight
            }
            serializer = [{'customer' :serializerCustomer.data}, {'order': serializerOrder.data}, {'products' : serializerProduct.data}, {'quantities': quantityList}, {'measurements':measurementsList}]

            return Response(serializer)
        except Customer.DoesNotExist:
            return Response({'error':'no customer found'}, status=status.HTTP_404_NOT_FOUND)
        except Order.DoesNotExist:
            return Response({'error':'no order found'}, status=status.HTTP_404_NOT_FOUND)

