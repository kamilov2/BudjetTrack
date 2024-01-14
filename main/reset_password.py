import telebot
import random
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Profile

bot = telebot.TeleBot('6066460877:AAEbu-NZMCVsL74RJc7VgZ3SRxB8IzQ6Klk')

@bot.message_handler(commands=['start'])
def start_command(message):
    handle_reset_password(message)

@bot.message_handler(func=lambda message: True)
def handle_reset_password(message):
    try:
        bot.send_message(message.chat.id, "Пожалуйста, введите свой адрес электронной почты:")
        bot.register_next_step_handler(message, handle_email)
    except Exception as e:
        print(f"Error in handle_reset_password: {e}")

def handle_email(message):
    try:
        email = message.text

        verification_code = str(random.randint(1000, 9999))

        profile, created = Profile.objects.get_or_create(email=email)
        profile.verification_code = verification_code
        profile.save()

        subject = 'Код сброса пароля'
        message_text = f'Ваш код подтверждения: {verification_code}'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = email

        send_mail(subject, message_text, from_email, [to_email])
        bot.send_message(message.chat.id, "Код подтверждения отправлен на ваш адрес электронной почты. Пожалуйста, проверьте вашу почту.")
        bot.send_message(message.chat.id, "Введите код подтверждения, полученный в вашем электронном письме:")
        bot.register_next_step_handler(message, handle_verification_code)
    except Exception as e:
        print(f"Error in handle_email: {e}")
        bot.reply_to(message, 'Что-то пошло не так. Попробуйте еще раз.')

def handle_verification_code(message):
    try:
        verification_code = message.text

        profile = get_object_or_404(Profile, verification_code=verification_code)

        bot.send_message(message.chat.id, "Подтверждение успешно! Введите новый пароль:")
        bot.register_next_step_handler(message, handle_new_password, profile.id)
    except Profile.DoesNotExist:
        bot.send_message(message.chat.id, "Неверный код подтверждения. Пожалуйста, попробуйте еще раз.")
    except Exception as e:
        print(f"Error in handle_verification_code: {e}")
        bot.reply_to(message, 'Что-то пошло не так. Попробуйте еще раз.')

def handle_new_password(message, profile_id):
    try:
        new_password = message.text

        profile = get_object_or_404(Profile, id=profile_id)
        user = profile.user
        user.set_password(new_password)
        user.save()

        profile.verification_code = ""
        profile.save()

        send_mail(
            'Подтверждение сброса пароля',
            'Ваш пароль успешно сброшен.',
            settings.DEFAULT_FROM_EMAIL,
            [profile.email],
            fail_silently=False,
        )

        bot.send_message(message.chat.id, "Пароль успешно обновлен!")
    except Exception as e:
        print(f"Error in handle_new_password: {e}")
        bot.reply_to(message, 'Что-то пошло не так. Попробуйте еще раз.')

bot.polling(none_stop=True)
