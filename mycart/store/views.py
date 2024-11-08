from django.shortcuts import get_object_or_404, render
from .models import *
import time
from common.models import Category
from django.db.models import Q
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage


def shop(request, category_slug=None):
    context={}
    categories = None
    products = None
    product_count = 0
    page_product = None
    
    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_avilable=True)
        paginator=Paginator(products,2)
        page=request.GET.get('page')
        page_product=paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.filter(is_avilable=True)
        paginator=Paginator(products,6)
        page=request.GET.get('page')
        page_product=paginator.get_page(page)
        product_count = products.count()
   
    context = {
        
        'products': page_product,
        'product_count': product_count,
        'categories': categories,  
    }
    return render(request, 'product/product_page.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)
    except Exception as e:
        raise e
    products = Product.objects.filter(is_avilable=True)[:4]  
    context={'single_product':single_product,'product':products}
    return render(request,'product/product_detail.html',context)


def search(request):
    context = {'products': []}  
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count=products.count()
            context['products'] = products 
            context['product_count']=product_count
    return render(request, 'product/product_page.html', context)


