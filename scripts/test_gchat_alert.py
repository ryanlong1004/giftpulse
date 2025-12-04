#!/usr/bin/env python3
"""
Test script to trigger a Google Chat alert.
This creates a test log entry that matches a monitoring rule with Google Chat action.
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
from app.actions.google_chat import GoogleChatActionHandler  # noqa: E402


def create_test_log(db):
    """Create a test SMS log that will trigger an alert."""
    now = datetime.utcnow()
    # Create a test SMS log with failed status
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


def create_gchat_action(db, rule_id):
    """Create a Google Chat action for testing."""
    import os

    webhook_url = os.getenv("GOOGLE_CHAT_WEBHOOK")
    if not webhook_url:
        print("   ⚠️  GOOGLE_CHAT_WEBHOOK not set in environment!")
        return None

    gchat_action = Action(
        rule_id=rule_id,
        action_type="google_chat",
        config={
            "webhook_url": webhook_url,
            "message": "🚨 SMS Delivery Failed!\n"
            "Status: {{ status }}\n"
            "Error Code: {{ error_code }}\n"
            "From: {{ from_number }}\n"
            "To: {{ to_number }}",
        },
        enabled=True,
    )
    db.add(gchat_action)
    db.commit()
    db.refresh(gchat_action)
    print("\n✅ Created Google Chat action for rule")
    return gchat_action


def trigger_alert(db, test_log):
    """Match the test log against rules and trigger actions."""
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
        print("   ✅ MATCH! Triggering actions...")

        # Get Google Chat actions for this rule
        actions = (
            db.query(Action)
            .filter(
                Action.rule_id == rule.id,
                Action.enabled.is_(True),
                Action.action_type == "google_chat",
            )
            .all()
        )

        if not actions:
            print("   ⚠️  No Google Chat actions found, creating one...")
            new_action = create_gchat_action(db, rule.id)
            if new_action:
                actions = [new_action]
            else:
                print("   ❌ Failed to create Google Chat action")
                return

        print(f"   - Found {len(actions)} Google Chat action(s)")

        # Execute each action
        for action in actions:
            print("\n   🔔 Executing Google Chat action...")
            try:
                gchat_handler = GoogleChatActionHandler()
                result = gchat_handler.execute(action.config, test_log)
                print("   ✅ Google Chat notification sent!")
                print("   📱 Check your Google Chat space!")
                if result:
                    print(f"   Response: {result.get('status', 'N/A')}")
            except Exception as e:
                print(f"   ❌ Error executing action: {e}")
                import traceback

                traceback.print_exc()
    else:
        print("   ❌ No match")


def main():
    """Main test function."""
    print("=" * 60)
    print("🧪 GiftPulse Google Chat Alert Test")
    print("=" * 60)
    print("\nThis test will:")
    print("1. Create a test Twilio SMS log with failed status")
    print("2. Match it against the SMS Delivery Failure rule")
    print("3. Trigger Google Chat notification")
    print("\n" + "=" * 60 + "\n")

    try:
        with get_db_context() as db:
            # Create test log
            test_log = create_test_log(db)

            # Trigger alert
            trigger_alert(db, test_log)

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
