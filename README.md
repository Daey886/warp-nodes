# 🌐 WARP-Nodes · 9大地区精选订阅中心

> 依托 Cloudflare Anycast 与国内探针真实测速数据，自动聚合生成 9 大地区精选 WARP+ WireGuard 节点，每 6 小时自动更新发布。全面兼容 Loon、Mihomo (Clash Meta)、Sing-box、Shadowrocket、v2rayN 及各主流客户端。

[![Update WARP Subscriptions](https://github.com/Daey886/warp-nodes/actions/workflows/update.yml/badge.svg)](https://github.com/Daey886/warp-nodes/actions/workflows/update.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📌 支持地区与节点分布

每个地区精选 **4 个优质端点**（包含低延迟端点、防封锁备用端口与 IPv6 双栈端点），合计 **36 个高纯度 WARP+ 节点**：

- 🇭🇰 **中国香港 (HK)** · 4 节点
- 🇹🇼 **中国台湾 (TW)** · 4 节点
- 🇯🇵 **日本 (JP)** · 4 节点
- 🇸🇬 **新加坡 (SG)** · 4 节点
- 🇺🇸 **美国 (US)** · 4 节点
- 🇬🇧 **英国 (GB)** · 4 节点
- 🇩🇪 **德国 (DE)** · 4 节点
- 🇰🇷 **韩国 (KR)** · 4 节点
- 🇨🇦 **加拿大 (CA)** · 4 节点

---

## 🚀 客户端订阅使用指南

本项目提供两种使用方式：**方式 1 静态直链（开箱即用）** 与 **方式 2 Cloudflare Worker 动态智能分发（千人千面，速度极致）**。

---

### 🌟 方式 1：静态直链订阅（最快上手，零配置）

直接将下方链接复制并添加到你的代理客户端订阅中即可：

#### 1. Mihomo / Clash Meta / Clash Verge Rev
- **完整开箱配置（全套策略组：手动/自动全层级 + 9大地区独立低震荡优选 + AI/流媒体/社交/开发业务分流 + 广告拦截）**：
  ```text
  https://fastly.jsdelivr.net/gh/Daey886/warp-nodes@main/dist/clash.yaml
  ```
  *(国内高速 CDN 镜像，无需挂代理即可极速拉取；备用 GitHub Raw：`https://raw.githubusercontent.com/Daey886/warp-nodes/main/dist/clash.yaml`)*

- **纯 Proxy-Provider 节点池（供已有配置直接外部引用）**：
  ```text
  https://fastly.jsdelivr.net/gh/Daey886/warp-nodes@main/dist/clash_providers.yaml
  ```

#### 2. Sing-box
- **出站规则 JSON 格式**：
  ```text
  https://fastly.jsdelivr.net/gh/Daey886/warp-nodes@main/dist/singbox.json
  ```

#### 3. Loon 专属订阅 (标准 Proxy 格式)
- **直接导入 Loon 节点/订阅**：
  ```text
  https://fastly.jsdelivr.net/gh/Daey886/warp-nodes@main/dist/loon.list
  ```

#### 4. Shadowrocket (小火箭) / v2rayN
- **通用 Base64 WireGuard 格式订阅**：
  ```text
  https://fastly.jsdelivr.net/gh/Daey886/warp-nodes@main/dist/sub.txt
  ```

---

### ⚡ 方式 2：Cloudflare Worker 动态分发（千人千面，智能感知网络）

#### 官方在线动态订阅服务
现已上线官方边缘动态节点分发节点，自动识别你的宽带运营商（电信 / 移动 / 联通 / 广电 / 海外）并下发最优端点：

- **动态 Clash / Mihomo 订阅地址**：
  ```text
  https://warp.baey.top/clash
  ```
- **边缘网络诊断与状态查看**：
  ```text
  https://warp.baey.top/status
  ```

#### 自行私有部署（可选）
如果你希望使用自己的私有域名，使用仓库根目录下的 [`worker.js`](worker.js) 部署到 Cloudflare Workers 即可：
1. 在 Cloudflare Dashboard 创建一个 Worker（如命名为 `warp-nodes`）；
2. 粘贴 [`worker.js`](worker.js) 源码并点击 Deploy；
3. 为 Worker 绑定你的自定义域名（例如 `warp.yourdomain.com`）；
4. 客户端订阅链接即为：`https://warp.yourdomain.com/clash`。

---

### ⚖️ 方式 1 与 方式 2 的核心区别

| 对比维度 | 方式 1：静态直链（jsDelivr / GitHub） | 方式 2：Cloudflare Worker 动态引擎 |
| :--- | :--- | :--- |
| **工作原理** | 下载 GitHub 每 6 小时构建好的固定 `clash.yaml` | 客户端请求时，Worker 实时读取你的 ASN 动态拼装专属配置 |
| **网络适配能力** | **全国一锅端**。不管电信移动联通，拿到的 36 个 IP 完全相同 | **千人千面**。自动识别电信/移动/联通，给最优路由与端点标签 |
| **高峰期体验** | 部分运营商遇到晚高峰跨网 QoS 时可能降速或丢包 | 电信走美西、移动走港新、联通走欧陆，避开跨网拥堵 |
| **上手门槛** | 零门槛，复制直链粘贴即用 | 现成官方链接 `https://warp.baey.top/clash` 同样开箱即用 |
| **稳定性** | 依赖公共 CDN 镜像 | 独立域名解析与 Cloudflare 边缘计算，链接稳定持久 |

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
