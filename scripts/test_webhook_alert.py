#!/usr/bin/env python3
"""
Test script to trigger a webhook alert.
This creates a test log entry and sends a webhook notification.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import after path setup
from app.database import get_db_context  # noqa: E402
from app.models import Log, MonitoringRule, Action  # noqa: E402
from app.services.pattern_matcher import PatternMatcher  # noqa: E402
from app.actions.webhook import WebhookActionHandler  # noqa: E402


def create_test_log(db):
    """Create a test SMS log that will trigger an alert."""
    now = datetime.utcnow()
    test_log = Log(
        twilio_sid=f"TEST_SMS_{int(now.timestamp())}",
        log_type="message",
        timestamp=now,
        status="failed",
        error_code="30007",
        from_number="+15551234567",
        to_number="+15559876543",
        raw_data={
            "direction": "outbound-api",
            "price": "-0.00",
            "error_message": "Carrier violation",
        },
        created_at=now,
    )

    db.add(test_log)
    db.commit()
    db.refresh(test_log)

    print(f"✅ Created test log: {test_log.twilio_sid}")
    print(f"   - Type: {test_log.log_type}")
    print(f"   - Status: {test_log.status}")
    print(f"   - Error Code: {test_log.error_code}")

    return test_log


def create_webhook_action(db, rule_id, webhook_url):
    """Create a webhook action for testing."""
    webhook_action = Action(
        rule_id=rule_id,
        action_type="webhook",
        config={
            "url": webhook_url,
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
        },
        enabled=True,
    )
    db.add(webhook_action)
    db.commit()
    db.refresh(webhook_action)
    print("\n✅ Created webhook action for rule")
    return webhook_action


def trigger_alert(db, test_log, webhook_url):
    """Match the test log against rules and trigger webhook action."""
    # Get SMS failure rule
    rule = (
        db.query(MonitoringRule)
        .filter(
            MonitoringRule.enabled.is_(True),
            MonitoringRule.name == "SMS Delivery Failure",
        )
        .first()
    )

    if not rule:
        print("❌ SMS Delivery Failure rule not found!")
        return

    print(f"\n📋 Rule: {rule.name}")
    print(f"   - Pattern Type: {rule.pattern_type}")
    print(f"   - Pattern Value: {rule.pattern_value}")

    pattern_matcher = PatternMatcher()

    # Check if log matches the rule
    if pattern_matcher.check_log_against_rule(db, test_log, rule):
        print("   ✅ MATCH! Triggering webhook action...")

        # Check for existing webhook actions
        existing_actions = (
            db.query(Action)
            .filter(
                Action.rule_id == rule.id,
                Action.enabled.is_(True),
                Action.action_type == "webhook",
            )
            .all()
        )

        # Use existing or create new
        if existing_actions:
            actions = existing_actions
            print(f"   - Found {len(actions)} existing webhook action(s)")
        else:
            print("   - No webhook actions found, creating one...")
            new_action = create_webhook_action(db, rule.id, webhook_url)
            actions = [new_action]

        # Execute webhook action
        for action in actions:
            print(f"\n   🔔 Sending webhook to: {action.config.get('url', 'N/A')}")
            try:
                webhook_handler = WebhookActionHandler()
                result = webhook_handler.execute(action.config, test_log)

                if result.get("success"):
                    print("   ✅ Webhook sent successfully!")
                    print(f"   📡 Status Code: {result.get('status_code', 'N/A')}")
                    print("   📱 Check your Google Chat space!")
                else:
                    print(f"   ❌ Webhook failed: {result.get('error', 'Unknown')}")

            except Exception as e:
                print(f"   ❌ Error executing webhook: {e}")
                import traceback

                traceback.print_exc()
    else:
        print("   ❌ No match")


def main():
    """Main test function."""
    # Hardcoded webhook URL for testing
    webhook_url = (
        "https://chat.googleapis.com/v1/spaces/AAQA8c99S-4/messages?"
        "key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&"
        "token=HGqfJ1A19EVxEmsQ0GEBFcWwheszB8gE86ns9dqla1w"
    )
    
    print("=" * 60)
    print("🧪 GiftPulse Webhook Alert Test")
    print("=" * 60)
    print("\nThis test will:")
    print("1. Create a test Twilio SMS log with failed status")
    print("2. Match it against the SMS Delivery Failure rule")
    print("3. Send webhook notification")
    print(f"\nWebhook URL: {webhook_url[:50]}...")
    print("\n" + "=" * 60 + "\n")

    try:
        with get_db_context() as db:
            # Create test log
            test_log = create_test_log(db)

            # Trigger webhook alert
            trigger_alert(db, test_log, webhook_url)

        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)
        print("\n📱 Check your Google Chat space for the notification!")
        print("\n")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
