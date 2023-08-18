from typing import Any

from rest_framework import generics, status, response
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import bad_request

from bot.models import TgUser
from bot.serializers import TgUserSerializer
from bot.tg.client import TgClient


class TgUserVerification(generics.UpdateAPIView):
    serializer_class = TgUserSerializer
    permission_classes = [IsAuthenticated]
    queryset = TgUser.objects.all()

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            tg_user = self.get_queryset().get(verification_code=request.data.get('verification_code'))
        except TgUser.DoesNotExist:
            raise bad_request

        tg_user.user = request.user
        tg_user.save()
        TgClient.send_message(chat_id=tg_user.chat_id, text='Bot verification completed successfully')

        return Response(TgUserSerializer(tg_user).data)
