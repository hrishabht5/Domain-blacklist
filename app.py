from flask import Flask, request, jsonify
import dns.resolver

app = Flask(__name__)

DNSBL_SERVERS = [
    "zen.spamhaus.org",
    "bl.spamcop.net",
    "b.barracudacentral.org",
    "dnsbl.sorbs.net",
    "psbl.surriel.com",
    "cbl.abuseat.org"
]

def reverse_ip(ip):
    return '.'.join(ip.split('.')[::-1])

def is_listed(ip):
    reversed_ip = reverse_ip(ip)
    blacklist_results = {}

    for dnsbl in DNSBL_SERVERS:
        query = f"{reversed_ip}.{dnsbl}"
        try:
            answers = dns.resolver.resolve(query, 'A')
            # If resolves, IP is listed
            blacklist_results[dnsbl] = True
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            blacklist_results[dnsbl] = False
        except Exception as e:
            blacklist_results[dnsbl] = f"Error: {str(e)}"
    return blacklist_results

def resolve_domain(domain):
    try:
        answers = dns.resolver.resolve(domain, 'A')
        for rdata in answers:
            return rdata.to_text()
    except Exception as e:
        return None

@app.route('/check', methods=['GET'])
def check():
    domain = request.args.get('domain')
    ip = request.args.get('ip')

    if not domain and not ip:
        return jsonify({"error": "Provide either domain or ip parameter"}), 400

    if domain:
        ip = resolve_domain(domain)
        if not ip:
            return jsonify({"error": "Could not resolve domain"}), 400

    result = is_listed(ip)
    return jsonify({"ip": ip, "blacklist": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
