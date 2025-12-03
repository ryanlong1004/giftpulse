"""Email action handler."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from jinja2 import Template

from app.actions.base import BaseActionHandler
from app.models import Log
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmailActionHandler(BaseActionHandler):
    """Handler for sending email notifications."""
    
    def __init__(self):
        """Initialize email handler."""
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.smtp_from = settings.smtp_from
        self.smtp_use_tls = settings.smtp_use_tls
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate email configuration.
        
        Args:
            config: Configuration with 'recipients' and 'subject'
        
        Returns:
            True if valid
        """
        if 'recipients' not in config:
            logger.error("Email config missing 'recipients'")
            return False
        
        if not isinstance(config['recipients'], list):
            logger.error("Email 'recipients' must be a list")
            return False
        
        if not config['recipients']:
            logger.error("Email 'recipients' list is empty")
            return False
        
        return True
    
    def _render_template(
        self,
        template_str: str,
        log: Log
    ) -> str:
        """
        Render email template with log data.
        
        Args:
            template_str: Template string
            log: Log data
        
        Returns:
            Rendered template
        """
        template = Template(template_str)
        return template.render(
            log=log,
            twilio_sid=log.twilio_sid,
            log_type=log.log_type.value,
            timestamp=log.timestamp,
            status=log.status,
            error_code=log.error_code,
            error_message=log.error_message,
            from_number=log.from_number,
            to_number=log.to_number,
        )
    
    def _create_default_body(self, log: Log) -> str:
        """
        Create default email body.
        
        Args:
            log: Log data
        
        Returns:
            Email body text
        """
        body = f"""
GiftPulse Twilio Log Alert

Log Type: {log.log_type.value}
Timestamp: {log.timestamp}
Twilio SID: {log.twilio_sid}
Status: {log.status or 'N/A'}

"""
        
        if log.error_code:
            body += f"Error Code: {log.error_code}\n"
        
        if log.error_message:
            body += f"Error Message: {log.error_message}\n"
        
        if log.from_number:
            body += f"From: {log.from_number}\n"
        
        if log.to_number:
            body += f"To: {log.to_number}\n"
        
        body += "\nThis is an automated alert from GiftPulse Monitor."
        
        return body
    
    def execute(self, config: Dict[str, Any], log: Log) -> Dict[str, Any]:
        """
        Send email notification.
        
        Args:
            config: Email configuration
            log: Log that triggered the action
        
        Returns:
            Execution result
        """
        if not self.validate_config(config):
            return {
                'success': False,
                'error': 'Invalid configuration'
            }
        
        try:
            recipients: List[str] = config['recipients']
            subject = config.get('subject', 'Twilio Log Alert')
            
            # Render subject if it's a template
            if '{{' in subject:
                subject = self._render_template(subject, log)
            
            # Get or create body
            if 'body' in config:
                body = self._render_template(config['body'], log)
            else:
                body = self._create_default_body(log)
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_from
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            logger.info(f"Sending email to {recipients}")
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {recipients}")
            
            return {
                'success': True,
                'recipients': recipients,
                'subject': subject
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
