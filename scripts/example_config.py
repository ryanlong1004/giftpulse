"""Example configuration for development/testing."""

# This file shows example configurations for monitoring rules and actions

example_error_code_rule = {
    "name": "Failed Call Detection",
    "description": "Alert when calls fail with specific Twilio error codes",
    "enabled": True,
    "log_type": "call",
    "pattern_type": "error_code",
    "pattern_value": "30001,30002,30003,30004,30005",
    "actions": [
        {
            "type": "email",
            "config": {
                "recipients": ["ops@example.com", "oncall@example.com"],
                "subject": "⚠️ Twilio Call Failure Alert - Error {{ error_code }}",
                "body": """
Alert: Call Failure Detected

Error Code: {{ error_code }}
Error Message: {{ error_message }}
Timestamp: {{ timestamp }}
From: {{ from_number }}
To: {{ to_number }}
Twilio SID: {{ twilio_sid }}

Please investigate this issue immediately.
                """,
            },
        },
        {
            "type": "webhook",
            "config": {
                "url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
            },
        },
    ],
}

example_threshold_rule = {
    "name": "High Error Rate Detection",
    "description": "Alert when 10+ errors occur within 5 minutes",
    "enabled": True,
    "log_type": "error",
    "pattern_type": "threshold",
    "pattern_value": "",  # Can specify additional filters like "error_code:30001,30002"
    "threshold_count": 10,
    "threshold_window_minutes": 5,
    "actions": [
        {
            "type": "email",
            "config": {
                "recipients": ["engineering@example.com"],
                "subject": "🚨 High Twilio Error Rate Alert",
                "body": """
URGENT: High Error Rate Detected

A threshold of 10 errors in 5 minutes has been exceeded.

This indicates a potential system-wide issue that requires immediate attention.

Please check the Twilio dashboard and application logs.
                """,
            },
        }
    ],
}

example_message_failure_rule = {
    "name": "SMS Delivery Failure",
    "description": "Alert on SMS delivery failures",
    "enabled": True,
    "log_type": "message",
    "pattern_type": "status",
    "pattern_value": "failed,undelivered",
    "actions": [
        {
            "type": "email",
            "config": {
                "recipients": ["sms-team@example.com"],
                "subject": "SMS Delivery Failure",
            },
        },
        {
            "type": "webhook",
            "config": {
                "url": "https://your-incident-management-system.com/webhooks/twilio",
                "method": "POST",
                "data": {"severity": "medium", "service": "twilio-sms"},
            },
        },
    ],
}

example_regex_rule = {
    "name": "Specific Error Message Detection",
    "description": "Alert on specific error messages using regex",
    "enabled": True,
    "log_type": "error",
    "pattern_type": "regex",
    "pattern_value": "(timeout|connection refused|network error)",
    "actions": [
        {
            "type": "email",
            "config": {
                "recipients": ["devops@example.com"],
                "subject": "Network-related Twilio Error Detected",
            },
        }
    ],
}
