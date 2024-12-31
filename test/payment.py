import stripe

# Set your secret key. Remember to switch to your live secret key in production.
stripe.api_key = "sk_test_your_secret_key"

try:
    payment_link = stripe.PaymentLink.create(
        line_items=[{
            'price': 'price_1234567890',  # Replace with your actual Price ID
            'quantity': 1,
        }],
        application_fee_amount=123,  # Optional: If you're using Stripe Connect
        subscription_data={
            'trial_period_days': 14  # Optional: If you want to offer a free trial
        }
    )

    print(f"Payment Link created: {payment_link.url}")

except stripe.error.StripeError as e:
    print(f"Error creating payment link: {str(e)}")
