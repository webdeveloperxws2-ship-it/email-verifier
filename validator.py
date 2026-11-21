import re
import smtplib
import dns.resolver
import requests
from email_validator import validate_email, EmailNotValidError

# --- YEH NAYA HISSA HAI ---
# DNS Resolver ko configure karein taake VPN ki wajah se MX record na mile
# Ye code system DNS ko ignore kar ke seedha Google/Cloudflare se poochega
resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']
resolver.timeout = 10
resolver.lifetime = 10
# ---------------------------

def check_syntax(email):
    try:
        validate_email(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False

def check_mx(domain):
    try:
        # Yahan humne 'dns.resolver.resolve' ki jagah 'resolver.resolve' use kiya hai
        answers = resolver.resolve(domain, 'MX')
        return True
    except Exception as e:
        # Error print karein taake pata chale asal masla kya hai
        print(f"MX Check Failed for {domain}: {e}")
        return False

def check_smtp(email, domain):
    try:
        # SMTP check ke liye bhi yahi custom resolver use karein
        mx_records = resolver.resolve(domain, 'MX')
        mx_host = str(sorted(mx_records, key=lambda r: r.preference)[0].exchange).rstrip('.')
        
        import socket
        with socket.create_connection((mx_host, 25), timeout=3) as sock:
            import smtplib
            server = smtplib.SMTP(timeout=5)
            server.connect(mx_host, 25)
            server.helo(server.local_hostname)
            server.mail('test@example.com')
            code, _ = server.rcpt(email)
            server.quit()
            return code == 250
    except Exception:
        return False

def is_disposable(email):
    try:
        # Apni Disify API key yahan dalein
        API_KEY = "sW4tuFjOfad0jrJVkSFRYfM7aut9sSQkkbAKcc8n"
        
        url = f"https://disify.com/api/email/{email}"
        headers = {"Authorization": f"Bearer {API_KEY}"}
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return False
        data = response.json()
        return data.get("disposable", False)
    except Exception:
        return False