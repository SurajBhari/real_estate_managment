import pyotp

# Please note that this is not the actual secret key that is being used.
def validate_otp(otp):
    x = pyotp.TOTP("JBSWY3DPEHPK3PXP").now()
    return x == str(otp)