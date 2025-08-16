import os
from aiohttp import TCPConnector
from aiohttp.resolver import AsyncResolver
from dotenv import load_dotenv

load_dotenv()

NS = [ns.strip() for ns in os.getenv("DNS_SERVERS").split(',')]

def create_doh_connector():
    resolver = AsyncResolver(nameservers=NS)
    connector = TCPConnector(resolver=resolver,use_dns_cache=True)
    return connector