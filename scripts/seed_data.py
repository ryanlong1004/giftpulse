"""Seed script to populate database with example data."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import get_db_context
from app.models import MonitoringRule, Action, PatternType, ActionType


def seed_example_rules():
    """Seed database with example monitoring rules."""
    
    with get_db_context() as db:
        # Example 1: Error Code Detection
        rule1 = MonitoringRule(
            name="Failed Call Detection",
            description="Alert when calls fail with specific error codes",
            enabled=True,
            log_type="call",
            pattern_type=PatternType.ERROR_CODE,
            pattern_value="30001,30002,30003,30004,30005"
        )
        db.add(rule1)
        db.flush()
        
        action1_email = Action(
            rule_id=rule1.id,
            action_type=ActionType.EMAIL,
            config={
                "recipients": ["ops@example.com"],
                "subject": "Twilio Call Failure Alert",
                "body": "Call failed with error code {{ error_code }}"
            },
            enabled=True
        )
        db.add(action1_email)
        
        # Example 2: Threshold-based Detection
        rule2 = MonitoringRule(
            name="High Error Rate",
            description="Alert when 10+ errors occur in 5 minutes",
            enabled=True,
            log_type="error",
            pattern_type=PatternType.THRESHOLD,
            pattern_value="",
            threshold_count=10,
            threshold_window_minutes=5
        )
        db.add(rule2)
        db.flush()
        
        action2_email = Action(
            rule_id=rule2.id,
            action_type=ActionType.EMAIL,
            config={
                "recipients": ["oncall@example.com"],
                "subject": "High Twilio Error Rate Alert"
            },
            enabled=True
        )
        db.add(action2_email)
        
        # Example 3: Message Status Detection
        rule3 = MonitoringRule(
            name="SMS Delivery Failure",
            description="Alert on failed or undelivered SMS",
            enabled=True,
            log_type="message",
            pattern_type=PatternType.STATUS,
            pattern_value="failed,undelivered"
        )
        db.add(rule3)
        db.flush()
        
        action3_webhook = Action(
            rule_id=rule3.id,
            action_type=ActionType.WEBHOOK,
            config={
                "url": "https://hooks.example.com/twilio-alert",
                "method": "POST"
            },
            enabled=True
        )
        db.add(action3_webhook)
        
        db.commit()
        
        print("✅ Successfully seeded example monitoring rules and actions")
        print(f"   - Created {db.query(MonitoringRule).count()} rules")
        print(f"   - Created {db.query(Action).count()} actions")


if __name__ == "__main__":
    print("Seeding database with example data...")
    seed_example_rules()
