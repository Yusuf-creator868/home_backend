# utils.py
from rest_framework_simplejwt.tokens import RefreshToken

def set_jwt_cookies(response, user):
    refresh = RefreshToken.for_user(user)

    response.set_cookie(
        key='access_token',
        value=str(refresh.access_token),
        httponly=True,
        secure=True,          # ✅ MUST be True on Vercel/Render (HTTPS)
        samesite='None',      # ✅ REQUIRED for cross-domain
        path='/'
    )

    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        httponly=True,
        secure=True,
        samesite='None',
        path='/'
    )

    return response