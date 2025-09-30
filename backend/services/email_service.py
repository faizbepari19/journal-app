import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Optional

class EmailService:
    """SendGrid email service for sending password reset emails"""
    
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY environment variable is required")
        
        # Remove quotes if they exist in the API key
        self.api_key = self.api_key.strip("'\"")
        
        self.client = SendGridAPIClient(api_key=self.api_key)
        self.from_email = 'faizbepari19@gmail.com'
        
    def send_password_reset_email(self, to_email: str, reset_token: str, username: str) -> bool:
        """
        Send password reset email to user
        
        Args:
            to_email: Recipient email address
            reset_token: Password reset token
            username: User's username for personalization
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Create reset link (you'll need to update the frontend URL)
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
            reset_link = f"{frontend_url}/reset-password?token={reset_token}"
            
            # HTML email content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Password Reset - Journal App</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🤖 Journal App</h1>
                        <h2>Password Reset Request</h2>
                    </div>
                    <div class="content">
                        <p>Hi {username},</p>
                        
                        <p>We received a request to reset your password for your Journal App account. If you didn't make this request, you can safely ignore this email.</p>
                        
                        <p>To reset your password, click the button below:</p>
                        
                        <a href="{reset_link}" class="button">Reset My Password</a>
                        
                        <p>Or copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; background: #eee; padding: 10px; border-radius: 4px;">{reset_link}</p>
                        
                        <p><strong>This link will expire in 1 hour for security reasons.</strong></p>
                        
                        <p>If you're having trouble clicking the button, copy and paste the URL above into your web browser.</p>
                        
                        <p>Best regards,<br>The Journal App Team</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated email. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            plain_content = f"""
            Hi {username},
            
            We received a request to reset your password for your Journal App account.
            
            To reset your password, visit this link:
            {reset_link}
            
            This link will expire in 1 hour for security reasons.
            
            If you didn't request this password reset, you can safely ignore this email.
            
            Best regards,
            The Journal App Team
            """
            
            # Create the email
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject='Reset Your Journal App Password',
                html_content=html_content,
                plain_text_content=plain_content
            )
            
            # Send the email
            response = self.client.send(message)
            
            # Check if email was sent successfully
            if response.status_code in [200, 202]:
                print(f"✅ Password reset email sent successfully to {to_email}")
                return True
            else:
                print(f"❌ Failed to send email. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending password reset email: {str(e)}")
            return False
    
    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """
        Send welcome email to new users (bonus feature)
        
        Args:
            to_email: Recipient email address
            username: User's username
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Welcome to Journal App</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .feature {{ margin: 15px 0; padding: 15px; background: white; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🤖 Welcome to Journal App!</h1>
                    </div>
                    <div class="content">
                        <p>Hi {username},</p>
                        
                        <p>Welcome to your new AI-powered journal! We're excited to help you capture your thoughts and memories with intelligent search capabilities.</p>
                        
                        <h3>🚀 Here's what you can do:</h3>
                        
                        <div class="feature">
                            <strong>📝 Write Entries:</strong> Capture your daily thoughts, experiences, and reflections
                        </div>
                        
                        <div class="feature">
                            <strong>🤖 AI Search:</strong> Ask questions like "What did I do last week?" or "How was I feeling in March?"
                        </div>
                        
                        <div class="feature">
                            <strong>📅 Smart Dates:</strong> Our AI understands "today", "yesterday", "last month" and more
                        </div>
                        
                        <p>Ready to start journaling? Log in to your account and create your first entry!</p>
                        
                        <p>Happy journaling!<br>The Journal App Team</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject='Welcome to Your AI-Powered Journal! 🤖',
                html_content=html_content
            )
            
            response = self.client.send(message)
            return response.status_code in [200, 202]
            
        except Exception as e:
            print(f"❌ Error sending welcome email: {str(e)}")
            return False

# Create singleton instance
email_service = EmailService()