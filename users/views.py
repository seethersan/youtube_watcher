from django.views import View
from django.http import JsonResponse
from gqlauth.models import UserStatus


class VerifyEmailView(View):
    def get(self, request, token=None, *args, **kwargs):
        status = None
        message = None
        if token:
            try:
                UserStatus.verify(token)
            except Exception as e:
                status = "error"
                message = str(e)
            else:
                status = "success"
                message = "Email verified successfully."
        else:
            status = "error"
            message = "Token not found."
        return JsonResponse({"status": status, "message": message})
