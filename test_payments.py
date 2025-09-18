#!/usr/bin/env python3
"""
Test script for YooKassa payment integration
"""

import asyncio
import sys
from pathlib import Path

# Add bot directory to Python path
sys.path.append(str(Path(__file__).parent))

from bot.services.payment import PaymentService
from bot.database import db
from config import config

async def test_payment_creation():
    """Test payment creation"""
    print("🧪 Testing payment creation...")

    payment_service = PaymentService()

    # Test monthly subscription
    result = await payment_service.create_payment(
        user_id=123456789,
        subscription_type="monthly",
        amount=config.MONTHLY_PRICE,
        description="Тест месячной подписки"
    )

    if result:
        print(f"✅ Monthly payment created: {result['payment_id']}")
        print(f"💰 Amount: {result['amount']}₽")
        print(f"🔗 URL: {result['confirmation_url']}")
    else:
        print("❌ Failed to create monthly payment")

    # Test yearly subscription
    result = await payment_service.create_payment(
        user_id=123456789,
        subscription_type="yearly",
        amount=config.YEARLY_PRICE,
        description="Тест годовой подписки"
    )

    if result:
        print(f"✅ Yearly payment created: {result['payment_id']}")
        print(f"💰 Amount: {result['amount']}₽")
        print(f"🔗 URL: {result['confirmation_url']}")
    else:
        print("❌ Failed to create yearly payment")

async def test_webhook_processing():
    """Test webhook processing"""
    print("\n🧪 Testing webhook processing...")

    payment_service = PaymentService()

    # Mock successful payment webhook
    mock_webhook = {
        "event": "payment.succeeded",
        "object": {
            "id": "test_payment_id",
            "amount": {
                "value": "490.00",
                "currency": "RUB"
            },
            "metadata": {
                "user_id": "123456789",
                "subscription_type": "monthly"
            }
        }
    }

    result = await payment_service.process_webhook(mock_webhook)

    if result:
        print(f"✅ Webhook processed: {result['event']}")
        print(f"👤 User ID: {result['user_id']}")
        print(f"📋 Subscription: {result['subscription_type']}")
        print(f"💰 Amount: {result['amount']}₽")
    else:
        print("❌ Failed to process webhook")

async def test_database_operations():
    """Test database operations"""
    print("\n🧪 Testing database operations...")

    # Initialize database
    await db.init()

    # Test user creation
    test_user_id = 123456789
    await db.add_user(test_user_id, "testuser", "Test", "User")
    print(f"✅ Test user created: {test_user_id}")

    # Test subscription update
    import time
    subscription_end = time.time() + (30 * 24 * 60 * 60)  # 30 days from now

    result = await db.update_user_subscription(
        user_id=test_user_id,
        is_premium=True,
        subscription_type="monthly",
        subscription_end=subscription_end
    )

    if result:
        print("✅ Subscription updated successfully")

        # Verify the update
        user_info = await db.get_user(test_user_id)
        print(f"🔍 Premium status: {user_info.get('is_premium')}")
        print(f"⏰ Premium until: {user_info.get('premium_until')}")
    else:
        print("❌ Failed to update subscription")

async def test_price_configuration():
    """Test price configuration"""
    print("\n🧪 Testing price configuration...")

    payment_service = PaymentService()

    monthly_price = payment_service.get_subscription_price("monthly")
    yearly_price = payment_service.get_subscription_price("yearly")

    print(f"💰 Monthly price: {monthly_price}₽")
    print(f"💰 Yearly price: {yearly_price}₽")

    monthly_desc = payment_service.get_subscription_description("monthly")
    yearly_desc = payment_service.get_subscription_description("yearly")

    print(f"📋 Monthly description: {monthly_desc}")
    print(f"📋 Yearly description: {yearly_desc}")

    # Calculate savings
    yearly_monthly_equivalent = monthly_price * 12
    savings = yearly_monthly_equivalent - yearly_price
    savings_percent = (savings / yearly_monthly_equivalent) * 100

    print(f"💡 Yearly savings: {savings}₽ ({savings_percent:.1f}%)")

async def main():
    """Main test function"""
    print("🚀 Starting payment system tests...\n")

    # Check configuration
    if not config.YOOKASSA_SHOP_ID or not config.YOOKASSA_SECRET_KEY:
        print("⚠️  YooKassa credentials not configured")
        print("ℹ️  Some tests may fail or use mock data")

    try:
        await test_price_configuration()
        await test_database_operations()
        await test_webhook_processing()

        # Only test actual payment creation if credentials are configured
        if (config.YOOKASSA_SHOP_ID and config.YOOKASSA_SECRET_KEY and
            config.YOOKASSA_SHOP_ID != "your_shop_id" and
            config.YOOKASSA_SECRET_KEY != "your_secret_key"):
            await test_payment_creation()
        else:
            print("\n⚠️  Skipping payment creation test - credentials not configured")

        print("\n🎉 All tests completed!")

    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())