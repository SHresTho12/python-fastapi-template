from config import get_settings


def verification_mail(token):
    template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Python Version</title>
            <style>
                body {
    "font-family": Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }
                .container {
    "width": 100%;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #ffffff;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                .header {
    "text-align": center;
                    margin-bottom: 20px;
                }
                .header img {
    "max-width": 150px;
                }
                .content {
    "text-align": center;
                    margin-bottom: 20px;
                }
                .content h1 {
    "font-size": 24px;
                    color: #333;
                }
                .content p {
    "font-size": 16px;
                    color: #555;
                }
                .footer {
    "text-align": center;
                    font-size: 14px;
                    color: #777;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="https://cdn.vivasoftltd.com/wp-content/uploads/2024/03/Logo.svg" alt="Your Company Logo">
                </div>
                <div class="content">
                    <h1>Welcome to Vivasoft</h1>
                    <p>Thank you for signing up. Please verify your email address by clicking the button below:</p>
                    <a href="{get_settings().frontend_base_url}/auth/verification?token={token}" class="button">Verify Email</a>
                    <p>Your Python version is: {{ python_version }}</p>
                </div>
                <div class="footer">
                    <p>If you did not sign up for this account, you can ignore this email.</p>
                    <p>&copy; 2024 Vivasoft. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>

            """
    return template
