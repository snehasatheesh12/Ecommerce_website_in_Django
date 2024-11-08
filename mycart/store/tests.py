from django.test import TestCase

m=[{'product_name':'abc','price':200,'category':'bb'},
   {'product_name':'abc1','price':100,'category':'bb'},
   {'product_name':'abc2','price':400,'category':'bb1'},
   {'product_name':'abc3','price':180,'category':'bb1'}]

for i in m:
    if i['price']>180:
        print(i)
            
            
    