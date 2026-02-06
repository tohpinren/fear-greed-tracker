"""
Email Notification Module

Handles sending email notifications via SMTP when Fear and Greed indices
reach extreme greed thresholds.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


class EmailNotifier:
    """Handles email notifications via SMTP."""
    
    def __init__(self):
        """
        Initialize email notifier with configuration from environment variables.
        
        Required environment variables:
            SMTP_SERVER: SMTP server address (e.g., smtp.gmail.com)
            SMTP_PORT: SMTP port (e.g., 587)
            SMTP_USERNAME: Email address to send from
            SMTP_PASSWORD: SMTP password or app password
            NOTIFICATION_EMAIL: Email address to receive notifications
        """
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.notification_email = os.getenv("NOTIFICATION_EMAIL")
        
        if not all([self.smtp_server, self.smtp_username, self.smtp_password, self.notification_email]):
            raise ValueError(
                "Missing required email configuration. "
                "Set SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, and NOTIFICATION_EMAIL environment variables."
            )
    
    def _create_email_message(self, index_name: str, value: float, rating: str) -> MIMEMultipart:
        """
        Create email message with HTML and plain text content.
        
        Args:
            index_name: Name of the index
            value: Current index value
            rating: Current rating
            
        Returns:
            MIMEMultipart message object
        """
        subject = f"Alert: {index_name} - Extreme Greed Detected"
        
        html_body = f"""
        <html>
          <head></head>
          <body>
            <h2>Fear and Greed Index Alert</h2>
            <p><strong>{index_name}</strong> has reached <strong>Extreme Greed</strong> levels!</p>
            <table style="border-collapse: collapse; margin: 20px 0;">
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Index:</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{index_name}</td>
              </tr>
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Value:</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{value}</td>
              </tr>
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;"><strong>Rating:</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{rating.replace('_', ' ').title()}</td>
              </tr>
            </table>
            <p>This is an automated notification from your Fear and Greed Index Tracker.</p>
          </body>
        </html>
        """
        
        text_body = f"""
Fear and Greed Index Alert

{index_name} has reached Extreme Greed levels!

Index: {index_name}
Value: {value}
Rating: {rating.replace('_', ' ').title()}

This is an automated notification from your Fear and Greed Index Tracker.
        """
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.smtp_username
        message["To"] = self.notification_email
        
        text_part = MIMEText(text_body, "plain")
        html_part = MIMEText(html_body, "html")
        
        message.attach(text_part)
        message.attach(html_part)
        
        return message
    
    def send_notification(self, index_name: str, value: float, rating: str) -> None:
        """
        Send email notification when index reaches extreme greed.
        
        Args:
            index_name: Name of the index
            value: Current index value
            rating: Current rating
            
        Raises:
            smtplib.SMTPException: If email sending fails
        """
        message = self._create_email_message(index_name, value, rating)
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
        except smtplib.SMTPException as e:
            raise RuntimeError(f"Failed to send email notification: {e}") from e
