from django.core.mail import send_mail
 
def sendEmail(email, subject, content):
    try:
        send_mail(subject, content, 'luan.nguyenkhoa@asnet.com.vn', [email], fail_silently=False)
        print('successfully')   
    except :
        print('failed')



