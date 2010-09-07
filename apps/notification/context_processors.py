from notification.models import Notice

def notification(request):
    if request.user.is_authenticated():
        return {'notice_unseen_count': Notice.objects.unseen_count_for(request.user),}
    else:
        return {}

def notification_follow(request):
    if request.user.is_authenticated():
        return {'unseen_follow_count_for': Notice.objects.unseen_follow_count_for(request.user),}
    else:
        return {}
    
