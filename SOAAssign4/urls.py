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
from shopping_inventory import views as views
from shopping_emporium import views as emporium_views
#from shopping_emporium import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #********************************************* shopping inventory
    # customer
    url(r'^inventory/customer/$', views.CustomerAPIView.as_view(),name ='customer'),
    #url(r'^customer/$', views.CustomerAPIView.as_view()),
    url(r'^inventory/customer/(?P<name>\w+)/$', views.CustomerAPIView.as_view()),
    # custome + order
    url(r'^inventory/customer-order/(?P<phone>(\w|[-])+)/(?P<orderDate>(\w|[-])+)/$', views.CustomerOrderAPIView.as_view()),
    # customer + order + po
    url(r'^inventory/customer-order-po/first/(?P<name>\w+)/$', views.CustomerOrderPoAPIView.as_view(), {'first': True}),
    url(r'^inventory/customer-order-po/last/(?P<name>\w+)/$', views.CustomerOrderPoAPIView.as_view(), {'first': False}),
    url(r'^inventory/customer-order-po/po/(?P<name>\w+)/(?P<poName>(\w|[-])+)/$', views.CustomerOrderPoAPIView.as_view(), {'first': True}),
    url(r'^inventory/customer-order-po/order/(?P<name>\w+)/(?P<orderDate>(\w|[-])+)/$', views.CustomerOrderPoAPIView.as_view(), {'first': False}),
    # product
    url(r'^inventory/product/(?P<prodName>\w+)/$', views.ProductAPIView.as_view()),
    url(r'^inventory/product/soldout/(?P<soldout>\w+)/$', views.ProductAPIView.as_view()),
    # order
    url(r'^inventory/order/(?P<orderID>\w+)/$', views.OrderAPIView.as_view()),
    url(r'^inventory/order/$', views.OrderAPIView.as_view(),name ='order'),
    # cart
    url(r'^inventory/cart/$', views.CartAPIView.as_view(),name ='cart'),
    url(r'^inventory/cart/(?P<prodID>\w+)/$', views.CartAPIView.as_view()),
    #********************************************** shopping emporium
    url(r'^emporium/$', emporium_views.MainView),
    url(r'^emporium/detail/(?P<type>\w+)/$', emporium_views.DetailView),
    url(r'^emporium/view/$', emporium_views.ViewView),
]

urlpatterns = format_suffix_patterns(urlpatterns)