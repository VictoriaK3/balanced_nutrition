from django.core.mail import EmailMultiAlternatives

def send_welcome_email(user):
    subject = 'Добре дошъл в NutriPal!'
    from_email = None  # използва DEFAULT_FROM_EMAIL от settings.py
    to = [user.email]

    # Текстова версия (fallback)
    text_content = f"""Здравей, {user.username}!

Благодарим ти, че се регистрира в нашата платформа NutriPal.
Ако имаш въпроси, не се колебай да се свържеш с нас.

С уважение,
Екипът на NutriPal"""

    # HTML версия
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
      <div style="max-width: 600px; margin: auto; background-color: #ffffff;
                  border-radius: 10px; padding: 30px; box-shadow: 0 0 10px rgba(0,0,0,0.05);">
        <h2 style="color: #00c853; margin-top: 0;">Добре дошъл в NutriPal, {user.username}!</h2>
        <p style="font-size: 16px; color: #333;">
         Благодарим ти, че се присъедини към нас! 🎉  
         Радваме се, че вече си част от <strong>NutriPal</strong> — твоят приятел по пътя към по-балансиран живот.
        </p>
        <p style="font-size: 14px; color: #555;">
          Ако имаш въпроси или нужда от помощ, не се колебай да се свържеш с нас.
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        <p style="font-size: 13px; color: #999;">
          Това съобщение е изпратено автоматично. Моля, не отговаряй на него.<br>
          © 2025 NutriPal
        </p>
      </div>
    </body>
    </html>
    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
