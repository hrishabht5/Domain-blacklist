from fastapi import FastAPI, HTTPException, Query
import dns.resolver

app = FastAPI()

IP_BLACKLISTS = [
    'zen.spamhaus.org',
    'bl.spamcop.net',
    'b.barracudacentral.org',
    'psbl.surriel.com',
    'dnsbl-1.uceprotect.net',
]

DOMAIN_BLACKLISTS = [
    'dbl.spamhaus.org',
    'multi.surbl.org',
]

def query_dnsbl(ip: str, blacklist: str) -> str:
    reversed_ip = '.'.join(reversed(ip.split('.')))
    query = f"{reversed_ip}.{blacklist}"
    try:
        dns.resolver.resolve(query, 'A', lifetime=2)
        return "listed"
    except dns.resolver.NXDOMAIN:
        return "not listed"
    except Exception:
        return "error"

def query_domain_dnsbl(domain: str, blacklist: str) -> str:
    query = f"{domain}.{blacklist}"
    try:
        dns.resolver.resolve(query, 'A', lifetime=2)
        return "listed"
    except dns.resolver.NXDOMAIN:
        return "not listed"
    except Exception:
        return "error"

def get_mx_ips(domain: str) -> list:
    try:
        answers = dns.resolver.resolve(domain, 'MX', lifetime=2)
        mx_hosts = [r.exchange.to_text(omit_final_dot=True) for r in answers]
        ips = []
        for mx in mx_hosts:
            a_answers = dns.resolver.resolve(mx, 'A', lifetime=2)
            ips.extend([r.address for r in a_answers])
        return ips
    except Exception:
        return []

@app.get("/check_email")
async def check_email(email: str = Query(..., description="Email address to check")):
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email format")

    domain = email.split('@')[1]

    mx_ips = get_mx_ips(domain)
    if not mx_ips:
        raise HTTPException(status_code=400, detail="No MX records found for domain")

    # Check domain blacklists, map blacklist name to status string
    domain_blacklisted = {
        bl: query_domain_dnsbl(domain, bl) for bl in DOMAIN_BLACKLISTS
    }

    # Check each IP against IP blacklists, map IP to a dict of blacklist name → status string
    ip_blacklisted = {}
    for ip in mx_ips:
        ip_statuses = {bl: query_dnsbl(ip, bl) for bl in IP_BLACKLISTS}
        ip_blacklisted[ip] = ip_statuses

    # Overall mail send ability: False if any blacklist is 'listed'
    can_send_mail = not (
        any(status == "listed" for status in domain_blacklisted.values()) or
        any(status == "listed" for ip_bl in ip_blacklisted.values() for status in ip_bl.values())
    )

    return {
        "domain": domain,
        "mx_ips": mx_ips,
        "domain_blacklisted": domain_blacklisted,
        "ip_blacklisted": ip_blacklisted,
        "can_send_mail": can_send_mail,
    }
