import os
import httpx
import dns.resolver
from dotenv import load_dotenv

load_dotenv()

NS = [ns.strip() for ns in os.getenv("DNS_SERVERS").split(',')]

def config_ns_resolv():
    resolv = dns.resolver.Resolver()
    resolv.nameservers = NS
    dns.resolver.default_resolver = resolv
    return resolv

def create_doh_connector():
    config_ns_resolv()
    
    return httpx.AsyncClient(
        timeout=30.0,
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        follow_redirects=True
    )