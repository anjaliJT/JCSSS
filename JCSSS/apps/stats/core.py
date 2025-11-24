from .services import user, product, complain

def compute_product():
    """
    Computes products.
    """
    return{ "product": product.compute_product() }

def compute_user():
    """
    Computes users.
    """
    return{ "user": user.compute_user() }

def compute_complain(user):
    """
    Computes complains.
    """
    return{ "complain": complain.compute_active_complain(user) }

def compute_all_metrics(user_data):
    return {
        "product": product.compute_product(),
        "complain": complain.compute_active_complain(user_data),
        "users": user.compute_user(),
    }
