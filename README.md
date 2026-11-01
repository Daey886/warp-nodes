# 🌐 WARP-Nodes · 8大国自动优选订阅中心

> 依托 Cloudflare Anycast 与国内探针真实测速数据，自动聚合生成 8 大国/地区精选 WireGuard 节点，每 6 小时自动更新发布。全面兼容 Mihomo (Clash Meta)、Sing-box、Shadowrocket、v2rayN 及各主流客户端。

[![Update WARP Subscriptions](https://github.com/Daey886/warp-nodes/actions/workflows/update.yml/badge.svg)](https://github.com/Daey886/warp-nodes/actions/workflows/update.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📌 支持地区与节点分布

每个地区精选 **4 个优质端点**（包含低延迟端点、防封锁备用端口与 IPv6 双栈端点），合计 **32 个高纯度节点**：

- 🇭🇰 **中国香港 (HK)** · 4 节点
- 🇯🇵 **日本 (JP)** · 4 节点
- 🇸🇬 **新加坡 (SG)** · 4 节点
- 🇺🇸 **美国 (US)** · 4 节点
- 🇬🇧 **英国 (GB)** · 4 节点
- 🇩🇪 **德国 (DE)** · 4 节点
- 🇰🇷 **韩国 (KR)** · 4 节点
- 🇨🇦 **加拿大 (CA)** · 4 节点

---

## 🚀 客户端订阅链接

### 1. Mihomo / Clash Meta / Clash Verge Rev（推荐）
- **完整开箱配置（自带 8 大国分流策略组 + 自动优选 + 广告拦截）**：
  ```
  https://raw.githubusercontent.com/Daey886/warp-nodes/main/dist/clash.yaml
  ```
  *CDN 加速链接*：
  ```
  https://fastly.jsdelivr.net/gh/Daey886/warp-nodes@main/dist/clash.yaml
  ```

- **纯 Proxy-Provider 节点池（供已有配置直接引用）**：
  ```
  https://raw.githubusercontent.com/Daey886/warp-nodes/main/dist/clash_providers.yaml
  ```

### 2. Sing-box
- **出站规则 JSON 格式**：
  ```
  https://raw.githubusercontent.com/Daey886/warp-nodes/main/dist/singbox.json
  ```

### 3. Loon 专属订阅 (标准 Proxy 格式)
- **直接导入 Loon 节点/订阅**：
  ```
  https://raw.githubusercontent.com/Daey886/warp-nodes/main/dist/loon.list
  ```
  *CDN 加速链接*：
  ```
  https://fastly.jsdelivr.net/gh/Daey886/warp-nodes@main/dist/loon.list
  ```

### 4. Shadowrocket (小火箭) / v2rayN
- **通用 Base64 WireGuard 格式订阅**：
  ```
  https://raw.githubusercontent.com/Daey886/warp-nodes/main/dist/sub.txt
  ```

### 4. 原始链接列表（直观查看）
- **单行 WireGuard URI 列表**：
  ```
  https://raw.githubusercontent.com/Daey886/warp-nodes/main/dist/nodes.txt
  ```

---

## 🛠️ 技术特性

1. **自动注册与授权**：
   - 接入 Cloudflare Client API 自动化注册独立账户，并完整保留关键字段 `reserved: [r1, r2, r3]`（Client ID），杜绝客户端握手被拒。
2. **避开封锁与 QoS**：
   - 摒弃已被国内运营商重点监控的默认 `2408` 端口，主力采用 `987, 878, 854, 500, 4500` 等非标端口及 IPv6 端点。
3. **真实探针回传**：
   - 数据源定时同步国内真实宽带探针丢包率 `<= 1.0%` 的测速池，拒绝海外机房自娱自乐的虚假测速。
4. **自动化 CI/CD**：
   - GitHub Actions 每 6 小时自动执行测试套件、抓取清洗并部署最新订阅。

---

## 📄 开源许可

本项目遵循 [MIT](LICENSE) 协议开源。
