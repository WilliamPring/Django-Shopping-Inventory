from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CustomerSerializer, ProductSerializer
from .models import Customer, Product
from django.http import Http404
import json
# Create your views here.


class CustomerAPIView(APIView):
    """
    Retrieve, update or delete a customer.
    """
    def get(self, request, name, format=None):
        try:
             Customer.objects.get(first_name=name)
             customer = Customer.objects.all().filter(first_name=name)
             serializer = CustomerSerializer(customer, many = True)
             return Response(serializer.data)
        except Customer.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, format=None):
        req = json.loads( request.body.decode('utf-8') )
        if ('cust_id' in req) and ('first_name' in req) and ('last_name' in req):
            customer = Customer.objects.filter(cust_id=req["cust_id"])
            customer.first_name = req["first_name"]
            customer.last_name = req["last_name"]
            serializer = CustomerSerializer(customer, data=req, many=True)
            if serializer.is_valid():            
                print("Tha")
                serializer.save()
                return Response(serializer.data)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            pass    
        return Response(req, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, name, format=None):
        event = Customer.objects.get(last_name=name)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
 


@api_view(['GET', 'POST'])
def product_info(request, prodName):
     if request.method == 'GET':
        product = Product.objects.all().filter(prod_name=prodName)
        serializer = ProductSerializer(product, many = True)
        return Response(serializer.data)