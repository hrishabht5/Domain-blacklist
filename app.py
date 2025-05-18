from flask import Flask, request, jsonify
import dns.resolver

app = Flask(__name__)

DNSBL_SERVERS = [
    "nordspam.dbl.spamhaus.org",
    "semfresh.rbl.spamhaus.org",
    "semuri.rbl.spamhaus.org",
    "semurired.rbl.spamhaus.org",
    "rhsbl.sorbs.net",
    "rhsbl-nomail.sorbs.net",
    "dbl.spamhaus.org",
    "multi.surbl.org",
    "0spam.fusionzero.com",
    "rbl.0spam.com",
    "mail-intelligence.abusix.net",
    "mail-intelligence-domain.abusix.net",
    "exploit.abusix.net",
    "anonmails.rbl.anonmails.de",
    "backscatterer.org",
    "b.barracudacentral.org",
    "blocklist.de",
    "calivent.rbl.spamhaus.org",
    "bogons.cymru.com",
    "tor.dan.me.uk",
    "torexit.dan.me.uk",
    "drmx.dnsbl.net.au",
    "drone.abuse.ch",
    "fabels.dnsbl.net.au",
    "hil.habeas.com",
    "hil2.habeas.com",
    "hostkarma.junkemailfilter.com",
    "dnsbl-1.uceprotect.net",
    "icmforbidden.rbl.uceprotect.net",
    "interserver.rbl.spamhaus.org",
    "jippg.net",
    "kemptbl.spameatingmonkey.net",
    "konstant.rbl.spamhaus.org",
    "lashback.rbl.spamhaus.org",
    "mailspike.bl.spameatingmonkey.net",
    "mailspike.z.spameatingmonkey.net",
    "msrbl.rbl.spamhaus.org",
    "msrbl.spamhaus.org",
    "netherrelays.rbl.spamhaus.org",
    "netherunsure.rbl.spamhaus.org",
    "nordspambl.spamhaus.org",
    "nosolicitado.rbl.spamhaus.org",
    "psbl.surriel.com",
    "rats.dnsbl.sorbs.net",
    "rats.noptr.sorbs.net",
    "rats.spam.sorbs.net",
    "rbl.jp",
    "s5h.net",
    "schulte.dnsbl.sorbs.net",
    "backscatter.dnsbl.sorbs.net",
    "blacklist.sem.com",
    "senderscore.rbl.spamhaus.org",
    "servicesnet.rbl.spamhaus.org",
    "spamcop.net",
    "zen.spamhaus.org",
    "spfbl.net",
    "suomispam.net",
    "swinog.spameatingmonkey.net",
    "triumf.ca",
    "truncate.dnsbl.sorbs.net",
    "uceprotect.net",
    "uceprotect2.net",
    "uceprotect3.net",
    "woodysmtp.dnsbl.sorbs.net",
    "zapbl.spamhaus.org"
]

def reverse_ip(ip):
    return '.'.join(ip.split('.')[::-1])

def check_blacklist(ip):
    reversed_ip = reverse_ip(ip)
    results = {}

    for dnsbl in DNSBL_SERVERS:
        query = f"{reversed_ip}.{dnsbl}"
        try:
            answers = dns.resolver.resolve(query, 'A')
            # If resolves, IP is listed
            results[dnsbl] = True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            results[dnsbl] = False
        except Exception as e:
            results[dnsbl] = f"Error: {str(e)}"
    return results

def resolve_domain(domain):
    try:
        answers = dns.resolver.resolve(domain, 'A')
        for rdata in answers:
            return rdata.to_text()
    except Exception:
        return None

@app.route('/check', methods=['GET'])
def check():
    domain = request.args.get('domain', '').strip()
    ip = request.args.get('ip', '').strip()

    if domain:
        ip = resolve_domain(domain)
        if not ip:
            return jsonify({"error": "Could not resolve domain"}), 400
    elif not ip:
        return jsonify({"error": "Provide either 'domain' or 'ip' query param"}), 400

    results = check_blacklist(ip)
    return jsonify({
        "ip": ip,
        "blacklist_results": results
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
