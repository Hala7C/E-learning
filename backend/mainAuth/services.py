from django.contrib.auth import get_user_model
import pyotp
import requests 
import qrcode
import qrcode.image.svg
import base64
from io import BytesIO

User=get_user_model()

def getUserService(request):
    """
    Get the user with a particular user_id
    """
    try:
        data = request.data
        user_id = data.get('id', None)
        user = User.objects.get(id = user_id)
        return user
    except:
        return None

def getQRCodeService(user):
    """
    Generate the QR Code image, save the otp_base32 for the user
    """
    otp_base32 = pyotp.random_base32()
    otp_auth_url = pyotp.totp.TOTP(otp_base32).provisioning_uri(
    name=user.first_name.lower(), issuer_name="localhost.com")

    user.otp_base32 = otp_base32
    user.save()
    qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
    qr.add_data(otp_auth_url)
    qr.make(fit=True)
    qr_code_image = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    buffered = BytesIO()
    qr_code_image.save(buffered, format="PNG")
    qr_image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    qr=f"data:image/png;base64,{ qr_image_base64 }"
    return qr

def getLoginUserService(request):
    """
    Return the user id
    """
    data = request.data
    username = data.get('email', None)
    password = data.get('password', None)
    try:
        user = User.objects.get(username = username, password = password)
        return user
    except:
        return None
import time    
def getOTPValidityService(user, otp):
    """
    Verify the OTP
    """
    totp = pyotp.TOTP(user.otp_base32)
    print(totp.now())
    print(otp)
    if not totp.verify(otp):
        return False
    user.logged_in = True
    user.save()
    return True