# Python Script: SSL Expiry Monitoring (ACM + External Certificates)
# External/legacy certificates: Monitored via direct SSL connection.
# ACM-managed certificates: Pulled via Boto3 to check expiry independently.
# Alerting: Sends emails to our team@email.com for any certificate expiring within the threshold.
# Independent monitoring layer: Even ACM-managed certificates are checked outside AWS automation to catch failed renewal, misconfiguration, or misattachment.
import ssl
import socket
import boto3
from datetime import datetime, timezone
from email.mime.text import MIMEText
import smtplib

# ---------- CONFIGURATION ----------

# Domains to check (external/legacy)
EXTERNAL_DOMAINS = [
    "example.com",
    "api.example.org",
    "legacy.company.net"
]

# ACM certificates to check (AWS Certificate Manager)
REGION = "us-east-1"
EXPIRY_THRESHOLD_DAYS = 15

# Email alert settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "alert@example.com"
SENDER_PASSWORD = "your_app_password"
RECEIVER_EMAIL = "devops-team@example.com"

# ---------- FUNCTIONS ----------

def get_ssl_expiry(domain):
    """Check external SSL certificate expiry"""
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=domain)
    conn.settimeout(5)
    conn.connect((domain, 443))
    cert = conn.getpeercert()
    conn.close()
    expiry_date = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
    return expiry_date

def get_acm_cert_expiry():
    """Check ACM-managed certificate expiry dates"""
    client = boto3.client('acm', region_name=REGION)
    response = client.list_certificates(CertificateStatuses=['ISSUED'])
    certs_expiry = []

    for cert_summary in response['CertificateSummaryList']:
        cert_arn = cert_summary['CertificateArn']
        cert_details = client.describe_certificate(CertificateArn=cert_arn)
        expiry_date = cert_details['Certificate']['NotAfter']
        domain_name = cert_details['Certificate']['DomainName']
        certs_expiry.append((domain_name, expiry_date))
    return certs_expiry

def send_email_alert(domain, days_left):
    """Send alert email for expiring certificate"""
    subject = f"⚠️ SSL Certificate Expiry Alert: {domain}"
    body = f"The SSL certificate for {domain} expires in {days_left} days. Please renew it soon."
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
    print(f"Email alert sent for {domain}")

# ---------- MAIN SCRIPT ----------

def main():
    print("🔍 Checking external SSL certificates...")
    for domain in EXTERNAL_DOMAINS:
        try:
            expiry = get_ssl_expiry(domain)
            days_left = (expiry - datetime.utcnow()).days
            print(f"{domain}: Expires on {expiry} ({days_left} days left)")
            if days_left < EXPIRY_THRESHOLD_DAYS:
                send_email_alert(domain, days_left)
        except Exception as e:
            print(f"❌ Failed to check {domain}: {e}")

    print("\n🔍 Checking ACM-managed SSL certificates...")
    try:
        acm_certs = get_acm_cert_expiry()
        for domain, expiry in acm_certs:
            days_left = (expiry - datetime.now(timezone.utc)).days
            print(f"{domain} (ACM): Expires on {expiry} ({days_left} days left)")
            if days_left < EXPIRY_THRESHOLD_DAYS:
                send_email_alert(domain, days_left)
    except Exception as e:
        print(f"❌ Failed to check ACM certificates: {e}")

    print("\n✅ SSL monitoring complete.")

if __name__ == "__main__":
    main()
