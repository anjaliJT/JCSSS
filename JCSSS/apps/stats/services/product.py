from apps.products.models import Product

def compute_product():
    product_count = Product.objects.count()
    return {'product_count':product_count}