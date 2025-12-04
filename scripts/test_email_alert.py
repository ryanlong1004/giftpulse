#!/usr/bin/env python3
"""
Test script to trigger an email alert via Mailtrap.
This creates a test log entry that matches one of our monitoring rules.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import after path setup
from sqlalchemy import select  # noqa: E402
from app.core.database import get_db  # noqa: E402
from app.models.log import TwilioLog  # noqa: E402
from app.models.rule import MonitoringRule  # noqa: E402
from app.models.action import Action  # noqa: E402
from app.services.pattern_matcher import PatternMatcher  # noqa: E402
from app.services.action_handler import ActionHandler  # noqa: E402


async def create_test_log():
    """Create a test Twilio log that will trigger an alert."""
    async for db in get_db():
        # Create a test call log with error code that matches our rule
        test_log = TwilioLog(
            twilio_sid=f"TEST_CALL_{datetime.utcnow().timestamp()}",
            log_type="call",
            status="failed",
            error_code="30001",  # This matches "Failed Call Detection" rule
            from_number="+15551234567",
            to_number="+15559876543",
            raw_data={
                "direction": "outbound-api",
                "duration": "0",
                "price": "-0.00",
                "error_message": "Queue overflow",
            },
            created_at=datetime.utcnow(),
        )

        db.add(test_log)
        await db.commit()
        await db.refresh(test_log)

        print(f"✅ Created test log: {test_log.twilio_sid}")
        print(f"   - Type: {test_log.log_type}")
        print(f"   - Status: {test_log.status}")
        print(f"   - Error Code: {test_log.error_code}")

        return test_log


async def trigger_alert(test_log):
    """Match the test log against rules and trigger actions."""
    async for db in get_db():
        # Get all enabled rules
        result = await db.execute(
            select(MonitoringRule).where(
                MonitoringRule.enabled.is_(True),
                MonitoringRule.log_type == test_log.log_type
            )
        )
        rules = result.scalars().all()

        print(
            f"\n🔍 Checking {len(rules)} active rules for '{test_log.log_type}' logs..."
        )

        pattern_matcher = PatternMatcher()
        action_handler = ActionHandler()

        for rule in rules:
            print(f"\n📋 Rule: {rule.name}")
            print(f"   - Pattern Type: {rule.pattern_type}")
            print(f"   - Pattern Value: {rule.pattern_value}")

            # Check if log matches the rule
            if pattern_matcher.matches(test_log, rule):
                print("   ✅ MATCH! Triggering actions...")

                # Get actions for this rule
                result = await db.execute(
                    select(Action).where(
                        Action.rule_id == rule.id, Action.enabled.is_(True)
                    )
                )
                actions = result.scalars().all()

                print(f"   - Found {len(actions)} enabled action(s)")

                # Execute each action
                for action in actions:
                    print(f"\n   🔔 Executing {action.action_type} action...")
                    try:
                        await action_handler.handle(action, test_log, rule, db)
                        print(f"   ✅ {action.action_type} action completed!")

                        if action.action_type == "email":
                            recipients = action.config.get('recipients', [])
                            print(f"   📧 Email sent to: {recipients}")
                            print("   📧 Check your Mailtrap inbox!")
                    except Exception as e:
                        print(f"   ❌ Error executing action: {e}")
            else:
                print("   ❌ No match")


async def main():
    """Main test function."""
    print("=" * 60)
    print("🧪 GiftPulse Email Alert Test")
    print("=" * 60)
    print("\nThis test will:")
    print("1. Create a test Twilio call log with error code 30001")
    print("2. Match it against monitoring rules")
    print("3. Trigger email alerts to Mailtrap")
    print("\n" + "=" * 60 + "\n")

    try:
        # Create test log
        test_log = await create_test_log()

        # Trigger alert
        await trigger_alert(test_log)

        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)
        print("\n📧 Check your Mailtrap inbox at:")
        print("   https://mailtrap.io/inboxes")
        print("\n")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
