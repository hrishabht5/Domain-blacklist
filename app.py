from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import dns.resolver
import dns.reversename

app = FastAPI()

IP_BLACKLISTS = [
    'zen.spamhaus.org',
    'b.barracudacentral.org',
    'bl.spamcop.net',
]

DOMAIN_BLACKLISTS = [
    'dbl.spamhaus.org',
    'multi.surbl.org',
]

class EmailRequest(BaseModel):
    email: EmailStr

def query_dnsbl(ip: str, blacklist: str) -> bool:
    reversed_ip = '.'.join(reversed(ip.split('.')))
    query = f"{reversed_ip}.{blacklist}"
    try:
        dns.resolver.resolve(query, 'A')
        return True
    except dns.resolver.NXDOMAIN:
        return False
    except Exception:
        return False

def query_domain_dnsbl(domain: str, blacklist: str) -> bool:
    query = f"{domain}.{blacklist}"
    try:
        dns.resolver.resolve(query, 'A')
        return True
    except dns.resolver.NXDOMAIN:
        return False
    except Exception:
        return False

def get_mx_ips(domain: str) -> list:
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        mx_hosts = [r.exchange.to_text(omit_final_dot=True) for r in answers]
        ips = []
        for mx in mx_hosts:
            a_answers = dns.resolver.resolve(mx, 'A')
            ips.extend([r.address for r in a_answers])
        return ips
    except Exception:
        return []

@app.post("/check_email")
async def check_email(data: EmailRequest):
    domain = data.email.split('@')[1]

    mx_ips = get_mx_ips(domain)
    if not mx_ips:
        raise HTTPException(status_code=400, detail="No MX records found for domain")

    domain_blacklisted = [bl for bl in DOMAIN_BLACKLISTS if query_domain_dnsbl(domain, bl)]

    ip_blacklisted = {}
    for ip in mx_ips:
        blacklists = [bl for bl in IP_BLACKLISTS if query_dnsbl(ip, bl)]
        if blacklists:
            ip_blacklisted[ip] = blacklists

    can_send_mail = not domain_blacklisted and not ip_blacklisted

    return {
        "domain": domain,
        "mx_ips": mx_ips,
        "domain_blacklisted": domain_blacklisted,
        "ip_blacklisted": ip_blacklisted,
        "can_send_mail": can_send_mail,
    }
