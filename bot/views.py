# from django.shortcuts import render
# from rest_framework import generics, status, response
# from rest_framework.permissions import IsAuthenticated
#
# from bot.management.commands.run_bot import Command
# from bot.models import TgUser
# from bot.serializers import TgUserVerificationSerializer
# from core.models import User
#
#
# class TgUserVerification(generics.CreateAPIView):
#     queryset = User
#     serializer_class = TgUserVerificationSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_object(self) -> User:
#         return self.request.user
#
#     def perform_update(self, serializer):
#         tg_client = Command.tg_client
#         verification_code = self.request.data["verification_code"]
#         tg_user = TgUser.objects.get(verification_code=verification_code)
#         user = self.get_object()
#         tg_user.user_id = user
#         tg_user.save()
#         user.verification_code = tg_user.verification_code
#         user.save()
#         tg_client.send_message(chat_id=tg_user.tg_chat_id, text=answer)
#         return response.Response("Verification completed successfully", status=status.HTTP_200_OK)
