# app.py
from flask import Flask, request, jsonify
import dns.resolver
import socket

app = Flask(__name__)

DNSBL_PROVIDERS = [
    "zen.spamhaus.org",
    "bl.spamcop.net",
    "dnsbl.sorbs.net",
    "b.barracudacentral.org",
    "spam.dnsbl.sorbs.net"
]

def get_mx_ips(domain):
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        mx_hosts = [str(r.exchange).rstrip('.') for r in mx_records]
        mx_ips = []
        for host in mx_hosts:
            ip = socket.gethostbyname(host)
            mx_ips.append(ip)
        return mx_ips
    except Exception as e:
        return []

def reverse_ip(ip):
    return '.'.join(reversed(ip.split('.')))

def check_blacklists(ip):
    results = {}
    reversed_ip = reverse_ip(ip)
    for bl in DNSBL_PROVIDERS:
        query = f"{reversed_ip}.{bl}"
        try:
            dns.resolver.resolve(query, 'A')
            results[bl] = True
        except dns.resolver.NXDOMAIN:
            results[bl] = False
        except:
            results[bl] = "error"
    return results

@app.route('/check', methods=['GET'])
def check_domain():
    domain = request.args.get('domain')
    if not domain:
        return jsonify({"error": "Please provide a domain using ?domain=example.com"}), 400

    mx_ips = get_mx_ips(domain)
    if not mx_ips:
        return jsonify({"error": "No MX records or IPs found."}), 404

    full_result = {}
    for ip in mx_ips:
        full_result[ip] = check_blacklists(ip)

    return jsonify({"domain": domain, "mx_ips": mx_ips, "blacklist_results": full_result})

if __name__ == '__main__':
    app.run(debug=True)
