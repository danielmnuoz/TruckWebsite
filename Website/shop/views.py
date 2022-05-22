# Create your views here.
import requests
from django.shortcuts import render, get_object_or_404

from .models import Category
from .models import Product


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request,
                  'shop/product/list.html',
                  {'category': category,
                   'categories': categories,
                   'products': products})


def product_detail(request, id, slug):
    product = get_object_or_404(Product,
                                id=id,
                                slug=slug,
                                available=True)
    return render(request,
                  'shop/product/detail.html',
                  {'product': product})


# when a user clicks the catalog button, call this to access the api and build tables
# something wrong with this application? Has trouble with imports
def accessApi(request):
    # access api
    response = requests.get("https://openapi.etsy.com/v2/listings/active?api_key={h7ctibmsc63qthr5ozej14i4}")

    # pull from api to get products
    return render()
