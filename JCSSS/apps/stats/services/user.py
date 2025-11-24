from apps.users.models import CustomUser

def compute_user():
    
    return {
        "user_count": CustomUser.objects.count()
        }
