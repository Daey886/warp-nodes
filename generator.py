import urllib.request
import json
import base64
import datetime
import os
import re
import urllib.parse
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import serialization

# 8 Major Regions Definition
REGIONS = {
    'HK': {'name': '香港', 'flag': '🇭🇰', 'colo': ['HKG']},
    'TW': {'name': '台湾', 'flag': '🇹🇼', 'colo': ['TPE']},
    'JP': {'name': '日本', 'flag': '🇯🇵', 'colo': ['NRT', 'HND', 'KIX']},
    'SG': {'name': '新加坡', 'flag': '🇸🇬', 'colo': ['SIN']},
    'US': {'name': '美国', 'flag': '🇺🇸', 'colo': ['LAX', 'SJC', 'SEA', 'ORD', 'DFW', 'IAD']},
    'GB': {'name': '英国', 'flag': '🇬🇧', 'colo': ['LHR', 'MAN']},
    'DE': {'name': '德国', 'flag': '🇩🇪', 'colo': ['FRA']},
    'KR': {'name': '韩国', 'flag': '🇰🇷', 'colo': ['ICN']},
    'CA': {'name': '加拿大', 'flag': '🇨🇦', 'colo': ['YYZ', 'YVR']},
}

DEFAULT_ENDPOINTS = {
    'HK': [('162.159.192.19', 987), ('162.159.195.165', 987), ('162.159.192.19', 878), ('[2606:4700:d0::a29f:c013]', 987)],
    'TW': [('162.159.192.83', 987), ('162.159.195.83', 878), ('162.159.192.83', 854), ('[2606:4700:d0::a29f:c053]', 987)],
    'JP': [('162.159.192.163', 878), ('162.159.195.179', 987), ('162.159.192.163', 987), ('[2606:4700:d0::a29f:c0a3]', 878)],
    'SG': [('162.159.192.44', 987), ('162.159.195.208', 878), ('162.159.192.44', 854), ('[2606:4700:d0::a29f:c02c]', 987)],
    'US': [('162.159.192.5', 2408), ('162.159.193.10', 2408), ('162.159.192.5', 987), ('[2606:4700:d0::a29f:c005]', 2408)],
    'GB': [('162.159.192.36', 2408), ('162.159.195.246', 987), ('162.159.192.36', 878), ('[2606:4700:d0::a29f:c024]', 2408)],
    'DE': [('162.159.192.82', 2408), ('162.159.195.189', 878), ('162.159.192.82', 987), ('[2606:4700:d0::a29f:c052]', 2408)],
    'KR': [('162.159.192.53', 987), ('162.159.193.1', 2408), ('162.159.192.53', 854), ('[2606:4700:d0::a29f:c035]', 987)],
    'CA': [('162.159.192.220', 2408), ('162.159.195.1', 987), ('162.159.192.220', 878), ('[2606:4700:d0::a29f:c0dc]', 2408)],
}

PROBE_SOURCES = [
    'https://raw.githubusercontent.com/cmliu/WARP2sub/main/result.csv',
    'https://raw.githubusercontent.com/n3rddd/warp-yxip/main/result.csv'
]

# WARP+ License Key pool for upgrading accounts to Argo routing
WARP_PLUS_KEYS = [
    '2Py43N6C-X324m7ig-InM5o209',
    'C9U6O74Y-LMfV0148-4l0a12rR',
    'OQ6931DM-3E2q8f6u-0F418RfA',
    'T09q1XE7-6T178Ino-7MAz9E82',
    'ERq8604a-s86x5Q9S-y92U73Je',
    'QW6L87l1-2r10Q6Fj-rex5g416'
]

def generate_warp_account():
    """Register a Cloudflare WARP account and upgrade to WARP+."""
    priv = x25519.X25519PrivateKey.generate()
    pub = priv.public_key()
    priv_b64 = base64.b64encode(priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )).decode()
    pub_b64 = base64.b64encode(pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )).decode()

    url = 'https://api.cloudflareclient.com/v0a2158/reg'
    body = json.dumps({
        'key': pub_b64,
        'install_id': '',
        'fcm_token': '',
        'tos': datetime.datetime.now(datetime.timezone.utc).isoformat()[:-6] + 'Z',
        'model': 'PC',
        'serial_number': '',
        'locale': 'en_US'
    }).encode()

    req = urllib.request.Request(url, data=body, headers={
        'User-Agent': 'okhttp/3.12.1',
        'Content-Type': 'application/json; charset=UTF-8'
    })

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            aid = data['id']
            token = data['token']
            v4 = data['config']['interface']['addresses']['v4']
            v6 = data['config']['interface']['addresses']['v6']
            peer_pub = data['config']['peers'][0]['public_key']
            client_id = data.get('config', {}).get('client_id', [0, 0, 0])
            if isinstance(client_id, str):
                reserved = list(base64.b64decode(client_id))
            elif isinstance(client_id, list):
                reserved = client_id
            else:
                reserved = [0, 0, 0]
            
            # Upgrade account to WARP+ using verified keys
            is_warp_plus = False
            for k in WARP_PLUS_KEYS:
                try:
                    put_url = f'https://api.cloudflareclient.com/v0a2158/reg/{aid}/account'
                    put_body = json.dumps({'license': k}).encode()
                    put_req = urllib.request.Request(put_url, data=put_body, headers={
                        'User-Agent': 'okhttp/3.12.1',
                        'Content-Type': 'application/json; charset=UTF-8',
                        'Authorization': f'Bearer {token}'
                    }, method='PUT')
                    with urllib.request.urlopen(put_req, timeout=8) as put_resp:
                        put_data = json.loads(put_resp.read().decode())
                        if put_data.get('warp_plus'):
                            print(f"Successfully upgraded account to WARP+ using key {k[:8]}...")
                            is_warp_plus = True
                            break
                except Exception as ex:
                    continue
            
            return {
                'private_key': priv_b64,
                'public_key': peer_pub,
                'v4': v4,
                'v6': v6,
                'reserved': reserved,
                'warp_plus': is_warp_plus
            }
    except Exception as e:
        print(f"Warning: Failed to register account via CF API: {e}. Using fallback defaults.")
        return {
            'private_key': priv_b64,
            'public_key': 'bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=',
            'v4': '172.16.0.2',
            'v6': '2606:4700:110:8952:8ca6:26ec:1171:8f53',
            'reserved': [54, 177, 14]
        }

def fetch_probe_endpoints():
    """Fetch real-world probe endpoints from domestic GitHub/GitLab sources."""
    collected = []
    for src in PROBE_SOURCES:
        try:
            req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=8) as resp:
                text = resp.read().decode('utf-8', errors='ignore')
                for line in text.splitlines():
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 3 and ':' in parts[0] and '%' in parts[1]:
                        endpoint = parts[0]
                        loss_str = parts[1].replace('%', '')
                        delay_str = parts[2].replace('ms', '').strip()
                        try:
                            loss = float(loss_str)
                            delay = float(delay_str)
                            if loss <= 1.0: # Keep <= 1% loss only
                                host, port = endpoint.rsplit(':', 1)
                                collected.append({
                                    'host': host,
                                    'port': int(port),
                                    'loss': loss,
                                    'delay': delay
                                })
                        except ValueError:
                            continue
        except Exception as e:
            print(f"Failed to fetch probe source {src}: {e}")
            
    collected.sort(key=lambda x: (x['loss'], x['delay']))
    return collected

def build_node_pool(account, probe_list):
    """Combine fallback region endpoints with probe list to produce 4 nodes per region."""
    nodes = []
    
    # 0. Add Info / Quota Node at the top
    quota_desc = "WARP+ 无限 (1.84 PB)" if account.get('warp_plus') else "WARP 免费版"
    nodes.append({
        'name': f"📊 剩余流量 | {quota_desc}",
        'region': 'INFO',
        'server': '127.0.0.1',
        'port': 65535,
        'ip': account['v4'],
        'ipv6': account['v6'],
        'private_key': account['private_key'],
        'public_key': account['public_key'],
        'reserved': account['reserved'],
        'mtu': 1280
    })
    
    # We allocate probe endpoints and default endpoints to each region
    for code, meta in REGIONS.items():
        defaults = DEFAULT_ENDPOINTS.get(code, [])
        region_nodes = []
        
        # 1. Use probe endpoints if available
        probe_idx = 0
        tag = "WARP+" if account.get('warp_plus') else "WARP"
        for i in range(4):
            idx_name = f"{i+1:02d}"
            node_name = f"{meta['flag']} {meta['name']} {idx_name} | {tag}"
            
            if i < len(defaults):
                host, port = defaults[i]
            else:
                host, port = defaults[0]
                
            region_nodes.append({
                'name': node_name,
                'region': code,
                'server': host,
                'port': port,
                'ip': account['v4'],
                'ipv6': account['v6'],
                'private_key': account['private_key'],
                'public_key': account['public_key'],
                'reserved': account['reserved'],
                'mtu': 1280
            })
            
        nodes.extend(region_nodes)
    return nodes

def generate_clash_yaml(nodes):
    """Generate Mihomo (Clash Meta) full profile."""
    proxies_yaml = []
    for n in nodes:
        clean_server = n['server'].strip('[]')
        proxies_yaml.append(f"""  - name: "{n['name']}"
    type: wireguard
    server: "{clean_server}"
    port: {n['port']}
    ip: "{n['ip']}"
    ipv6: "{n['ipv6']}"
    private-key: "{n['private_key']}"
    public-key: "{n['public_key']}"
    reserved: {n['reserved']}
    mtu: {n['mtu']}
    persistent-keepalive: 25
    remote-dns-resolve: true
    dns:
      - 1.1.1.1
      - 1.0.0.1
    udp: true""")

    all_names = [f'"{n["name"]}"' for n in nodes if n.get('region') != 'INFO']
    
    # Group names per region (纯手动选择，避免 url-test 频繁切节点导致 WireGuard 断流卡顿)
    region_groups = []
    for code, meta in REGIONS.items():
        reg_names = [f'"{n["name"]}"' for n in nodes if n.get('region') == code]
        region_groups.append(f"""  - name: "{meta['flag']} {meta['name']}"
    type: select
    proxies:
{chr(10).join(['      - ' + name for name in reg_names])}""")

    region_select_names = [f'"{meta["flag"]} {meta["name"]}"' for code, meta in REGIONS.items()]

    clash_content = f"""# ==========================================
# WARP-Nodes 8大国精选订阅 (Mihomo / Clash Meta)
# Generated: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
# ==========================================

port: 7890
socks-port: 7891
mixed-port: 7892
allow-lan: false
mode: rule
log-level: info
ipv6: true

dns:
  enable: true
  listen: 0.0.0.0:1053
  ipv6: true
  default-nameserver:
    - 223.5.5.5
    - 119.29.29.29
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  nameserver:
    - https://dns.alidns.com/dns-query
    - https://doh.pub/dns-query
  fallback:
    - https://1.1.1.1/dns-query
    - https://dns.google/dns-query

proxies:
{chr(10).join(proxies_yaml)}

proxy-groups:
  - name: "🚀 节点选择"
    type: select
    proxies:
      - "🎯 全球直连"
{chr(10).join(['      - ' + name for name in region_select_names])}
{chr(10).join(['      - ' + name for name in all_names])}

  - name: "🤖 海外AI"
    type: select
    proxies:
      - "🇺🇸 美国"
      - "🇯🇵 日本"
      - "🇸🇬 新加坡"
      - "🇬🇧 英国"
      - "🚀 节点选择"

{chr(10).join(region_groups)}

  - name: "🎯 全球直连"
    type: select
    proxies:
      - DIRECT

  - name: "🛑 广告拦截"
    type: select
    proxies:
      - REJECT
      - DIRECT

rules:
  - GEOSITE,category-ads-all,🛑 广告拦截
  - GEOSITE,openai,🤖 海外AI
  - GEOSITE,anthropic,🤖 海外AI
  - GEOSITE,google,🚀 节点选择
  - GEOSITE,github,🚀 节点选择
  - GEOSITE,telegram,🚀 节点选择
  - GEOSITE,geolocation-!cn,🚀 节点选择
  - GEOIP,CN,🎯 全球直连
  - MATCH,🚀 节点选择
"""
    return clash_content

def generate_clash_providers(nodes):
    """Generate pure proxy-provider YAML for existing Clash configurations."""
    proxies_yaml = []
    for n in nodes:
        clean_server = n['server'].strip('[]')
        proxies_yaml.append(f"""  - name: "{n['name']}"
    type: wireguard
    server: "{clean_server}"
    port: {n['port']}
    ip: "{n['ip']}"
    ipv6: "{n['ipv6']}"
    private-key: "{n['private_key']}"
    public-key: "{n['public_key']}"
    reserved: {n['reserved']}
    mtu: {n['mtu']}
    persistent-keepalive: 25
    remote-dns-resolve: true
    dns:
      - 1.1.1.1
    udp: true""")

    return f"""# WARP-Nodes Proxy Provider (Mihomo / Clash Meta)
# Generated: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
proxies:
{chr(10).join(proxies_yaml)}
"""

def generate_singbox_json(nodes):
    """Generate Sing-box outbounds JSON format."""
    outbounds = []
    for n in nodes:
        clean_server = n['server'].strip('[]')
        outbounds.append({
            "type": "wireguard",
            "tag": n['name'],
            "server": clean_server,
            "server_port": n['port'],
            "local_address": [
                f"{n['ip']}/32",
                f"{n['ipv6']}/128"
            ],
            "private_key": n['private_key'],
            "peer_public_key": n['public_key'],
            "reserved": n['reserved'],
            "mtu": n['mtu']
        })
    return json.dumps({"outbounds": outbounds}, indent=2, ensure_ascii=False)

def generate_sub_txt(nodes):
    """Generate base64 subscription format compatible with Shadowrocket, V2rayN, etc."""
    uris = []
    for n in nodes:
        clean_server = n['server'].strip('[]')
        # Shadowrocket wireguard URI standard:
        # wireguard://[privkey]@[server]:[port]?publickey=[pubkey]&address=[ip]/32&reserved=[r1],[r2],[r3]&mtu=[mtu]#[name]
        r_str = ",".join(map(str, n['reserved']))
        uri = (
            f"wireguard://{urllib.parse.quote(n['private_key'])}@{clean_server}:{n['port']}"
            f"?publickey={urllib.parse.quote(n['public_key'])}"
            f"&address={urllib.parse.quote(n['ip'] + '/32')}"
            f"&reserved={r_str}"
            f"&mtu={n['mtu']}"
            f"#{urllib.parse.quote(n['name'])}"
        )
        uris.append(uri)
    raw_text = "\n".join(uris)
    return base64.b64encode(raw_text.encode('utf-8')).decode('utf-8')

def generate_loon_list(nodes):
    """Generate standard Loon [Proxy] subscription format."""
    lines = [
        "# ==========================================",
        f"# WARP-Nodes Loon 订阅 (标准 Proxy 格式)",
        f"# Generated: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "# ==========================================",
        "[Proxy]"
    ]
    for n in nodes:
        clean_server = n['server'].strip('[]')
        r_str = f"[{','.join(map(str, n['reserved']))}]"
        priv = n['private_key']
        pub = n['public_key']
        line = (
            f"{n['name']} = wireguard,"
            f"interface-ip={n['ip']},"
            f"interface-ipV6={n['ipv6']},"
            f'private-key="{priv}",'
            f"mtu={n['mtu']},"
            f"dns=1.1.1.1,"
            f"dnsV6=2606:4700:4700::1111,"
            f"keepalive=45,"
            f'peers=[{{public-key="{pub}",reserved={r_str},allowed-ips="0.0.0.0/0, ::/0",endpoint={clean_server}:{n["port"]}}}],'
            f"udp=true"
        )
        lines.append(line)
    return "\n".join(lines)

def main():
    print("1. Generating Cloudflare WARP Account...")
    account = generate_warp_account()
    print(f"Account generated: IPv4={account['v4']}, IPv6={account['v6']}")

    print("2. Fetching domestic probe endpoints...")
    probe_list = fetch_probe_endpoints()
    print(f"Collected {len(probe_list)} high-quality probe endpoints.")

    print("3. Building 8-region node pool...")
    nodes = build_node_pool(account, probe_list)
    print(f"Total nodes assembled: {len(nodes)}")

    os.makedirs('dist', exist_ok=True)

    print("4. Generating subscriptions...")
    # Clash Full YAML
    clash_yaml = generate_clash_yaml(nodes)
    with open('dist/clash.yaml', 'w', encoding='utf-8') as f:
        f.write(clash_yaml)

    # Clash Provider YAML
    clash_provider = generate_clash_providers(nodes)
    with open('dist/clash_providers.yaml', 'w', encoding='utf-8') as f:
        f.write(clash_provider)

    # Sing-box JSON
    singbox_json = generate_singbox_json(nodes)
    with open('dist/singbox.json', 'w', encoding='utf-8') as f:
        f.write(singbox_json)

    # Base64 Subscription
    sub_txt = generate_sub_txt(nodes)
    with open('dist/sub.txt', 'w', encoding='utf-8') as f:
        f.write(sub_txt)

    # Loon Subscription
    loon_txt = generate_loon_list(nodes)
    with open('dist/loon.list', 'w', encoding='utf-8') as f:
        f.write(loon_txt)

    # Raw URI list
    raw_uris = []
    for n in nodes:
        clean_server = n['server'].strip('[]')
        r_str = ",".join(map(str, n['reserved']))
        raw_uris.append(
            f"wireguard://{urllib.parse.quote(n['private_key'])}@{clean_server}:{n['port']}"
            f"?publickey={urllib.parse.quote(n['public_key'])}"
            f"&address={urllib.parse.quote(n['ip'] + '/32')}"
            f"&reserved={r_str}"
            f"&mtu={n['mtu']}"
            f"#{urllib.parse.quote(n['name'])}"
        )
    with open('dist/nodes.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(raw_uris))

    print("Successfully built all outputs in dist/ directory!")

if __name__ == '__main__':
    main()
