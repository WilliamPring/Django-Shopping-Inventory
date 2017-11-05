"""SOAAssign4 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
      url(r'^product/(?P<prodName>[\w|\W]+)$', views.product_info),
    url(r'^order/(?P<first>[0-9]+)$', views.customer_info),
"""
from django.conf.urls import url
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from shopping_inventory import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^customer/$', views.CustomerAPIView.as_view(),name ='customer'),
    url(r'^customer/(?P<name>\w+)/$', views.CustomerAPIView.as_view()),
    url(r'^product/(?P<prodName>\w+)/$', views.ProductAPIView.as_view()),
    url(r'^product/soldout/(?P<soldout>\w+)/$', views.ProductAPIView.as_view()),
    url(r'^order/(?P<orderID>\w+)/$', views.OrderAPIView.as_view()),
    url(r'^order/$', views.OrderAPIView.as_view(),name ='order'),
    url(r'^cart/$', views.CartAPIView.as_view(),name ='cart'),
    url(r'^cart/(?P<prodID>\w+)/$', views.CartAPIView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)