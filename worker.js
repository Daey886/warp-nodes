/**
 * Cloudflare Worker - WARP-Nodes 边缘动态订阅分发引擎
 * Service Worker 格式 (兼容最强、极速冷启)
 */

const META_URL = "https://raw.githubusercontent.com/Daey886/warp-nodes/main/dist/meta.json";
const BACKUP_META_URL = "https://fastly.jsdelivr.net/gh/Daey886/warp-nodes@main/dist/meta.json";

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  try {
    const url = new URL(request.url);
    const cf = request.cf || {};

    const asn = cf.asn || 0;
    const org = (cf.asOrganization || "").toLowerCase();
    const country = cf.country || "CN";
    const city = cf.city || "Unknown";

    let isp = "通用网络";
    let ispTag = "MIX";
    
    // 识别运营商
    if ([4134, 4809, 23724].includes(asn) || org.includes("telecom") || org.includes("chinatelecom")) {
      isp = "中国电信";
      ispTag = "CT";
    } else if ([4837, 9929, 10099].includes(asn) || org.includes("unicom")) {
      isp = "中国联通";
      ispTag = "CU";
    } else if ([9808, 58453, 56040, 56041, 56042].includes(asn) || org.includes("mobile") || org.includes("chinamobile")) {
      isp = "中国移动";
      ispTag = "CM";
    } else if (org.includes("cbn") || org.includes("broadcast")) {
      isp = "中国广电";
      ispTag = "CBN";
    } else if (country !== "CN") {
      isp = `海外 (${country})`;
      ispTag = "OVERSEA";
    }

    // 状态接口
    if (url.pathname === "/" || url.pathname === "/status") {
      return new Response(JSON.stringify({
        status: "online",
        client_ip: request.headers.get("cf-connecting-ip"),
        client_asn: asn,
        detected_isp: isp,
        isp_tag: ispTag,
        region: `${country} - ${city}`,
        clash_subscription: `${url.origin}/clash`,
        notice: "请在 Clash / Mihomo 中订阅该链接，将根据网络自动下发最优端点"
      }, null, 2), {
        headers: { "content-type": "application/json; charset=utf-8" }
      });
    }

    // 拉取最新的 meta.json
    let meta = null;
    try {
      let resp = await fetch(META_URL, { cf: { cacheTtl: 600, cacheEverything: true } });
      if (!resp.ok) {
        resp = await fetch(BACKUP_META_URL, { cf: { cacheTtl: 600, cacheEverything: true } });
      }
      meta = await resp.json();
    } catch (e) {
      return new Response(`Error fetching node metadata: ${e.message}`, { status: 500 });
    }

    if (!meta || !meta.nodes || !meta.account) {
      return new Response("Invalid metadata structure", { status: 500 });
    }

    // 默认或指定 /clash 输出 Clash / Mihomo 配置
    const clashYaml = renderClashConfig(meta, isp, ispTag, asn);
    return new Response(clashYaml, {
      headers: {
        "content-type": "text/yaml; charset=utf-8",
        "content-disposition": `attachment; filename="warp-${ispTag.toLowerCase()}.yaml"`,
        "subscription-userinfo": "upload=0; download=0; total=2021623992320; expire=4102329600"
      }
    });

  } catch (err) {
    return new Response("Worker Exception: " + err.stack, { status: 500 });
  }
}

function renderClashConfig(meta, isp, ispTag, asn) {
  const account = meta.account;
  const regions = meta.regions;
  const nodes = meta.nodes;

  const proxiesList = [];
  const nodeNames = [];

  // 网络探针标识
  proxiesList.push(`  - name: "⚡ 网络识别: ${isp} (ASN${asn})"\n    type: wireguard\n    server: "${nodes[0].server}"\n    port: ${nodes[0].port}\n    ip: "${account.ip}"\n    ipv6: "${account.ipv6}"\n    private-key: "${account.private_key}"\n    public-key: "${account.public_key}"\n    reserved: [${account.reserved.join(', ')}]\n    mtu: 1280\n    persistent-keepalive: 25\n    remote-dns-resolve: true`);

  for (let n of nodes) {
    const cleanServer = n.server.replace(/[\[\]]/g, '');
    proxiesList.push(`  - name: "${n.name}"\n    type: wireguard\n    server: "${cleanServer}"\n    port: ${n.port}\n    ip: "${account.ip}"\n    ipv6: "${account.ipv6}"\n    private-key: "${account.private_key}"\n    public-key: "${account.public_key}"\n    reserved: [${account.reserved.join(', ')}]\n    mtu: 1280\n    persistent-keepalive: 25\n    remote-dns-resolve: true`);
    nodeNames.push(`"${n.name}"`);
  }

  const regionAutoNames = [];
  const regionGroupBlocks = [];

  for (let [code, metaReg] of Object.entries(regions)) {
    const regNodes = nodes.filter(n => n.region === code).map(n => `      - "${n.name}"`);
    const groupName = `${metaReg.flag} ${metaReg.name}`;
    regionAutoNames.push(`"${groupName}"`);

    regionGroupBlocks.push(`  - name: "${groupName}"\n    type: url-test\n    url: http://cp.cloudflare.com/generate_204\n    interval: 600\n    tolerance: 80\n    proxies:\n${regNodes.join('\n')}`);
  }

  return `# ==========================================
# WARP-Nodes 专属动态分流订阅
# 识别网络: ${isp} (ASN: ${asn})
# 更新时间: ${meta.updated_at}
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
${proxiesList.join('\n\n')}

proxy-groups:
  - name: "🚀 节点选择"
    type: select
    proxies:
      - "🖐️ 手动选择"
      - "♻️ 自动选择"
      - "⚡ 地区自动选择"
      - "🎯 全球直连"
${regionAutoNames.map(name => `      - ${name}`).join('\n')}

  - name: "🖐️ 手动选择"
    type: select
    proxies:
${nodeNames.map(name => `      - ${name}`).join('\n')}

  - name: "♻️ 自动选择"
    type: url-test
    url: http://cp.cloudflare.com/generate_204
    interval: 600
    tolerance: 100
    proxies:
${nodeNames.map(name => `      - ${name}`).join('\n')}

  - name: "⚡ 地区自动选择"
    type: url-test
    url: http://cp.cloudflare.com/generate_204
    interval: 600
    tolerance: 100
    proxies:
${regionAutoNames.map(name => `      - ${name}`).join('\n')}

  - name: "🤖 海外AI"
    type: select
    proxies:
      - "🇺🇸 美国"
      - "🇯🇵 日本"
      - "🇸🇬 新加坡"
      - "🇬🇧 英国"
      - "🚀 节点选择"
      - "🖐️ 手动选择"
      - "♻️ 自动选择"

  - name: "🎬 国际流媒体"
    type: select
    proxies:
      - "🚀 节点选择"
      - "🇸🇬 新加坡"
      - "🇯🇵 日本"
      - "🇺🇸 美国"
      - "🇹🇼 台湾"
      - "🇭🇰 香港"
      - "🖐️ 手动选择"
      - "♻️ 自动选择"

  - name: "💬 社交社区"
    type: select
    proxies:
      - "🚀 节点选择"
      - "🇭🇰 香港"
      - "🇯🇵 日本"
      - "🇸🇬 新加坡"
      - "🇺🇸 美国"
      - "🖐️ 手动选择"
      - "♻️ 自动选择"

  - name: "👨‍💻 开发者服务"
    type: select
    proxies:
      - "🚀 节点选择"
      - "🇺🇸 美国"
      - "🇯🇵 日本"
      - "🇸🇬 新加坡"
      - "🎯 全球直连"
      - "🖐️ 手动选择"

${regionGroupBlocks.join('\n\n')}

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
  - GEOSITE,google-gemini,🤖 海外AI
  - GEOSITE,youtube,🎬 国际流媒体
  - GEOSITE,netflix,🎬 国际流媒体
  - GEOSITE,spotify,🎬 国际流媒体
  - GEOSITE,telegram,💬 社交社区
  - GEOSITE,twitter,💬 社交社区
  - GEOSITE,discord,💬 社交社区
  - GEOSITE,reddit,💬 社交社区
  - GEOSITE,github,👨‍💻 开发者服务
  - GEOSITE,gitlab,👨‍💻 开发者服务
  - GEOSITE,google,🚀 节点选择
  - GEOSITE,geolocation-!cn,🚀 节点选择
  - GEOIP,CN,🎯 全球直连
  - MATCH,🚀 节点选择
`;
}
