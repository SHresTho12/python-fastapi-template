from config import get_settings


def reset_password_mail(token):
    template = f"""
                <!DOCTYPE html>
                <html>
                <head>
                </head>
                <body>
                    <div style=" display: flex; align-items: center; justify-content: center; flex-direction: column;">
                        <h3> Reset Password </h3>
                        <br>
                        <p>Thanks for choosing Online money Transfer, please 
                        click on the link below to reset your password</p> 
                        <a style="margin-top:1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; background: #0275d8; color: white;"
                         # href="{get_settings().frontend_base_url}/auth/reset-password?token={token}">
                            Reset your password
                        <a>
                    </div>
                </body>
                </html>
            """
    return template
