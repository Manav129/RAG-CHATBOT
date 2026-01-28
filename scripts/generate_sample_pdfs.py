# ============================================
# Script to Generate Sample PDF Documents
# ============================================
# This script creates sample company policy PDFs
# that our chatbot will use to answer questions.

from fpdf import FPDF
import os

# Create docs directory if it doesn't exist
os.makedirs("data/docs", exist_ok=True)


def create_pdf(filename: str, title: str, content: str):
    """
    Create a simple PDF document.
    
    Args:
        filename: Name of the PDF file (without path)
        title: Title shown at the top of the document
        content: Main text content of the document
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Set font for title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)  # Add some space
    
    # Set font for content
    pdf.set_font("Arial", "", 12)
    
    # Add content (multi_cell handles line wrapping)
    pdf.multi_cell(0, 8, content)
    
    # Save the PDF
    filepath = f"data/docs/{filename}"
    pdf.output(filepath)
    print(f"Created: {filepath}")


# ============================================
# Document 1: Refund Policy
# ============================================
refund_policy = """
REFUND POLICY - GOEL Electronics

1. GENERAL REFUND POLICY
All products purchased from GOEL Electronics can be returned within 30 days of purchase for a full refund. The item must be in original packaging and unused condition.

2. REFUND ELIGIBILITY
- Products must be returned within 30 days of delivery
- Items must be unused and in original packaging
- Original receipt or order confirmation is required
- Refunds are processed to the original payment method

3. REFUND PROCESS
Step 1: Contact our support team at support@GOEL Electronics.com or call 1-800-GOEL Electronics
Step 2: Provide your order number and reason for return
Step 3: Receive a Return Merchandise Authorization (RMA) number
Step 4: Ship the item back using the prepaid label we provide
Step 5: Refund is processed within 5-7 business days after we receive the item

4. NON-REFUNDABLE ITEMS
- Opened software or digital downloads
- Customized or personalized products
- Items marked as "Final Sale"
- Gift cards

5. PARTIAL REFUNDS
If an item is returned with missing parts or damage, a partial refund may be issued based on the condition assessment.

6. LATE RETURNS
Items returned after 30 days but within 60 days may be eligible for store credit only.

For any refund-related questions, contact our Customer Support team at support@GOEL Electronics.com or call 1-800-GOEL Electronics (1-800-832-4627).
"""

# ============================================
# Document 2: Shipping & Delivery
# ============================================
shipping_delivery = """
SHIPPING AND DELIVERY POLICY - GOEL Electronics

1. SHIPPING OPTIONS
We offer the following shipping methods:
- Standard Shipping (5-7 business days): FREE on orders over $50
- Express Shipping (2-3 business days): $9.99
- Next Day Delivery (1 business day): $19.99
- Same Day Delivery (select cities only): $29.99

2. ORDER PROCESSING TIME
All orders are processed within 1-2 business days. Orders placed after 2 PM EST are processed the next business day.

3. TRACKING YOUR ORDER
Once your order ships, you will receive an email with:
- Tracking number
- Carrier information (FedEx, UPS, or USPS)
- Estimated delivery date
You can also track your order at GOEL Electronics.com/track

4. DELIVERY ISSUES
If your package is:
- DELAYED: Check tracking status. Contact us if no update for 48 hours.
- DAMAGED: Take photos and contact us within 24 hours for replacement.
- LOST: File a claim through our support portal. We will investigate and reship.
- WRONG ITEM: Keep the item and contact us. We will send the correct item.

5. INTERNATIONAL SHIPPING
We ship to Canada, UK, and EU countries. International shipping takes 7-14 business days. Customs fees are the responsibility of the customer.

6. P.O. BOX DELIVERIES
We can ship to P.O. boxes for Standard Shipping only. Express and Next Day options require a physical address.

7. DELIVERY SIGNATURE
Orders over $500 require signature confirmation for security.

Contact shipping support: shipping@GOEL Electronics.com or 1-800-GOEL Electronics option 2.
"""

# ============================================
# Document 3: Payment Issues FAQ
# ============================================
payment_faq = """
PAYMENT ISSUES FAQ - GOEL Electronics

1. ACCEPTED PAYMENT METHODS
We accept:
- Credit Cards: Visa, MasterCard, American Express, Discover
- Debit Cards with Visa/MasterCard logo
- PayPal
- Apple Pay and Google Pay
- GOEL Electronics Gift Cards
- Affirm (Buy Now, Pay Later)

2. PAYMENT DECLINED - COMMON REASONS
Your payment may be declined due to:
- Insufficient funds in the account
- Incorrect card number, expiration date, or CVV
- Billing address doesn't match card records
- Card issuer blocked the transaction (call your bank)
- Daily spending limit reached
- Expired card

3. HOW TO FIX PAYMENT ISSUES
Step 1: Verify all card information is correct
Step 2: Ensure billing address matches your bank records
Step 3: Try a different payment method
Step 4: Contact your bank to authorize the transaction
Step 5: Clear browser cache and try again

4. DOUBLE CHARGED
If you see duplicate charges:
- Wait 24-48 hours - pending charges often drop automatically
- If charges persist, contact us with your order number
- We will investigate and refund duplicate charges within 3-5 business days

5. PAYMENT PENDING
Pending payments usually clear within 24 hours. If still pending after 48 hours, contact your bank first, then our support team.

6. PROMO CODE NOT WORKING
Check that:
- Code is not expired
- Minimum purchase requirement is met
- Code applies to items in your cart
- Code hasn't been used before (single-use codes)

7. REFUND NOT RECEIVED
Refunds take 5-7 business days to appear. Check with your bank if not received after 10 business days.

Payment Support: payments@GOEL Electronics.com or 1-800-GOEL Electronics option 3.
"""

# ============================================
# Document 4: Account & Login Help
# ============================================
account_help = """
ACCOUNT AND LOGIN HELP - GOEL Electronics

1. CREATING AN ACCOUNT
To create an account:
- Go to GOEL Electronics.com/signup
- Enter your email address
- Create a password (minimum 8 characters, include number and special character)
- Verify your email by clicking the link we send

2. FORGOT PASSWORD
To reset your password:
- Click "Forgot Password" on the login page
- Enter your email address
- Check your inbox for reset link (also check spam folder)
- Click the link and create a new password
- Link expires in 24 hours

3. ACCOUNT LOCKED
Your account may be locked after 5 failed login attempts.
To unlock:
- Wait 30 minutes and try again, OR
- Click "Forgot Password" to reset, OR
- Contact support with your registered email

4. CHANGE EMAIL ADDRESS
To update your email:
- Log into your account
- Go to Account Settings > Personal Information
- Enter new email address
- Verify the new email by clicking confirmation link

5. DELETE ACCOUNT
To delete your account:
- Log into your account
- Go to Account Settings > Privacy
- Click "Delete Account"
- Confirm deletion (this cannot be undone)
- Order history will be retained for legal purposes

6. TWO-FACTOR AUTHENTICATION (2FA)
We recommend enabling 2FA for security:
- Go to Account Settings > Security
- Click "Enable 2FA"
- Scan QR code with authenticator app (Google Authenticator, Authy)
- Enter the 6-digit code to confirm

7. ACCOUNT HACKED
If you suspect unauthorized access:
- Change your password immediately
- Enable 2FA
- Review recent orders for suspicious activity
- Contact support to report the issue

Account Support: accounts@GOEL Electronics.com or 1-800-GOEL Electronics option 4.
"""

# ============================================
# Document 5: Subscription Plans
# ============================================
subscription_terms = """
SUBSCRIPTION PLAN TERMS - GOEL Electronics

1. GOEL Electronics PLUS MEMBERSHIP
GOEL Electronics Plus is our premium membership program offering exclusive benefits.

MONTHLY PLAN: $9.99/month
ANNUAL PLAN: $79.99/year (save $40!)

2. MEMBERSHIP BENEFITS
- FREE Express Shipping on all orders
- 5% cashback on all purchases (as store credit)
- Early access to sales and new products
- Extended return window (60 days instead of 30)
- Priority customer support
- Exclusive member-only deals

3. BILLING AND RENEWAL
- Subscriptions auto-renew at the end of each billing period
- You will be charged on the same date each month/year
- Price changes are communicated 30 days in advance
- Payment method on file is charged automatically

4. CANCELLATION POLICY
- Cancel anytime from Account Settings > Subscription
- Monthly: Cancel before next billing date to avoid charges
- Annual: Cancel anytime, no refund for remaining months
- Benefits remain active until end of paid period

5. FREE TRIAL
- New members get a 14-day free trial
- Cancel before trial ends to avoid charges
- Only one free trial per customer/household

6. PAUSING MEMBERSHIP
You can pause your membership for up to 3 months:
- Go to Account Settings > Subscription > Pause Membership
- Select pause duration (1, 2, or 3 months)
- You won't be charged during pause
- Benefits are suspended during pause

7. STUDENT DISCOUNT
Students get 50% off! Verify student status at GOEL Electronics.com/student to get GOEL Electronics Plus for $4.99/month or $39.99/year.

Subscription Support: membership@GOEL Electronics.com or 1-800-GOEL Electronics option 5.
"""

# ============================================
# Document 6: Support Escalation Guide
# ============================================
escalation_guide = """
SUPPORT ESCALATION GUIDE - GOEL Electronics

1. SUPPORT CHANNELS
Contact us through:
- Email: support@GOEL Electronics.com (response within 24 hours)
- Phone: 1-800-GOEL Electronics (1-800-832-4627) - Mon-Fri 8AM-8PM EST
- Live Chat: Available on website 24/7
- Social Media: @GOEL ElectronicsSupport on Twitter/X

2. SUPPORT TICKET SYSTEM
When you contact us, a support ticket is created:
- You receive a Ticket ID (format: TKT-XXXXX)
- Use this ID to track your issue
- All communication is logged under this ticket
- Tickets are resolved within 48 hours for standard issues

3. ESCALATION LEVELS
LEVEL 1 - Initial Support (0-24 hours)
Basic inquiries, order status, simple troubleshooting

LEVEL 2 - Senior Support (24-48 hours)
Complex issues, refund disputes, technical problems

LEVEL 3 - Supervisor (48-72 hours)
Unresolved issues, complaints, policy exceptions

LEVEL 4 - Management (72+ hours)
Serious complaints, legal matters, executive review

4. WHEN TO REQUEST ESCALATION
You may request escalation if:
- Issue not resolved after 48 hours
- You received incorrect or contradictory information
- Request for exception to standard policy
- Significant financial loss due to our error

5. HOW TO ESCALATE
Simply say "I would like to escalate this issue" or:
- Reply to your support email with "ESCALATE" in subject
- Call and ask to speak with a supervisor
- Use ticket portal and click "Request Escalation"

6. PRIORITY SUPPORT
GOEL Electronics Plus members receive priority support:
- Dedicated support line: 1-800-GOEL Electronics option 9
- Faster response times (under 4 hours)
- Direct access to Level 2 support

7. COMPLAINT RESOLUTION
We take complaints seriously:
- All complaints are logged and reviewed
- You will receive acknowledgment within 24 hours
- Resolution or update within 72 hours
- Follow-up satisfaction survey sent after resolution

Emergency Support (order issues within 24 hours of delivery): 1-800-GOEL Electronics option 0.
"""

# ============================================
# Main: Generate all PDFs
# ============================================
if __name__ == "__main__":
    print("Generating sample PDF documents...")
    print("=" * 50)
    
    # Create each PDF
    create_pdf("Refund_Policy.pdf", "GOEL Electronics Refund Policy", refund_policy)
    create_pdf("Shipping_Delivery.pdf", "GOEL Electronics Shipping & Delivery", shipping_delivery)
    create_pdf("Payment_Issues_FAQ.pdf", "GOEL Electronics Payment FAQ", payment_faq)
    create_pdf("Account_Login_Help.pdf", "GOEL Electronics Account Help", account_help)
    create_pdf("Subscription_Plan_Terms.pdf", "GOEL Electronics Subscription Terms", subscription_terms)
    create_pdf("Support_Escalation_Guide.pdf", "GOEL Electronics Support Escalation", escalation_guide)
    
    print("=" * 50)
    print("All PDF documents created successfully!")
    print("Location: data/docs/")

