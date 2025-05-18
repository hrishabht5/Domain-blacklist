from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import dns.resolver

app = FastAPI()

IP_BLACKLISTS = [
    'zen.spamhaus.org',
    'b.barracudacentral.org',
    'bl.spamcop.net',
    '0spam.fusionzero.com',
    'rbl.0spam.org',
    'black.mail.abusix.zone',
    'dbl.abusix.zone',
    'exploit.mail.abusix.zone',
    'backscatter.spameatingmonkey.net',
    'blocklist.de',
    'bogons.cymru.com',
    'tor.dan.me.uk',
    'drone.abuse.ch',
    'dronebl.org',
    'hil.habeas.com',
    'hil2.habeas.com',
    'hostkarma.junkemailfilter.com',
    'dnsbl.cobion.com',
    'dnsbl.icm.edu.pl',
    'dnsbl.imp.ch',
    'wormbl.imp.ch',
    'dnsbl.interserver.net',
    'ivmSIP.dnsbl.info',
    'ivmSIP24.dnsbl.info',
    'dnsbl.kempt.net',
    'bl.mailspike.net',
    'z.mailspike.net',
    'phishing.msrbl.net',
    'spam.msrbl.net',
    'dnsbl.njabl.org',
    'unsure.nether.net',
    'relays.nether.net',
    'bl.nordspam.com',
    'bl.nosolicitado.org',
    'psbl.surriel.com',
    'dyna.rbl.jp',
    'noptr.rbl.jp',
    'spam.rbl.jp',
    'rbl.jp',
    's5h.net',
    'schulte.org',
    'black.spameatingmonkey.net',
    'score.senderscore.com',
    'services.net',
    'dnsbl.spfbl.net',
    'rep.suomispam.net',
    'bl.swining.net',
    'rbl.triumf.ca',
    'truncate.gbudb.net',
    'dnsbl-1.uceprotect.net',
    'dnsbl-2.uceprotect.net',
    'dnsbl-3.uceprotect.net',
    'woodys.njabl.org',
    'zapbl.net',
]

DOMAIN_BLACKLISTS = [
    'dbl.spamhaus.org',
    'multi.surbl.org',
    'dbl.nordspam.com',
    'fresh.spameatingmonkey.net',
    'urired.spameatingmonkey.net',
    'rhsbl.badconf.rfc-ignorant.org',
    'rhsbl.nomail.rfc-ignorant.org',
]

class EmailRequest(BaseModel):
    email: EmailStr

def query_dnsbl(ip: str, blacklist: str) -> bool:
    reversed_ip = '.'.join(reversed(ip.split('.')))
    query = f"{reversed_ip}.{blacklist}"
    try:
        dns.resolver.resolve(query, 'A', lifetime=5)
        return True
    except dns.resolver.NXDOMAIN:
        return False
    except Exception:
        return False

def query_domain_dnsbl(domain: str, blacklist: str) -> bool:
    query = f"{domain}.{blacklist}"
    try:
        dns.resolver.resolve(query, 'A', lifetime=5)
        return True
    except dns.resolver.NXDOMAIN:
        return False
    except Exception:
        return False

def get_mx_ips(domain: str) -> list:
    try:
        answers = dns.resolver.resolve(domain, 'MX', lifetime=5)
        mx_hosts = [r.exchange.to_text(omit_final_dot=True) for r in answers]
        ips = []
        for mx in mx_hosts:
            try:
                a_answers = dns.resolver.resolve(mx, 'A', lifetime=5)
                ips.extend([r.address for r in a_answers])
            except Exception:
                continue
        return ips
    except Exception:
        return []

@app.post("/check_email")
async def check_email(data: EmailRequest):
    return await perform_check(data.email)

# Optional GET endpoint for browser/Pabbly testing
@app.get("/check_email")
async def check_email_get(email: str):
    return await perform_check(email)

async def perform_check(email: str):
    domain = email.split('@')[1]
    mx_ips = get_mx_ips(domain)

    if not mx_ips:
        raise HTTPException(status_code=400, detail="No MX records found for domain")

    domain_blacklisted = {
        bl: "LISTED" for bl in DOMAIN_BLACKLISTS if query_domain_dnsbl(domain, bl)
    }

    ip_blacklisted = {}
    for ip in mx_ips:
        blacklisted = {
            bl: "LISTED" for bl in IP_BLACKLISTS if query_dnsbl(ip, bl)
        }
        if blacklisted:
            ip_blacklisted[ip] = blacklisted

    can_send_mail = not domain_blacklisted and not ip_blacklisted

    return {
        "domain": domain,
        "mx_ips": mx_ips,
        "domain_blacklisted": domain_blacklisted,
        "ip_blacklisted": ip_blacklisted,
        "can_send_mail": can_send_mail,
    }
