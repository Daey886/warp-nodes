# WARP-Nodes

> 一个用于生成 Cloudflare WARP / WARP+ WireGuard 订阅的开源工具。项目负责生成配置、策略组和多客户端格式，不承诺提供真实地区服务器、固定出口地区或稳定的视频线路。

[![Update WARP Subscriptions](https://github.com/Daey886/warp-nodes/actions/workflows/update.yml/badge.svg)](https://github.com/Daey886/warp-nodes/actions/workflows/update.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 项目定位

WARP-Nodes 将 Cloudflare WARP 的 WireGuard 参数和 Cloudflare Anycast 接入端点组装成客户端订阅，输出 Mihomo / Clash Meta、Sing-box、Loon、Shadowrocket 和 v2rayN 等格式。

它不是 VPS 节点池，也不是拥有香港、日本、美国等独立出口服务器的代理服务。配置中的地区名称主要用于策略组和端点标签；Cloudflare WARP 的实际出口和网络路径由 Cloudflare 动态决定，标签不等于实际出口地区。

项目适合：

- 临时备用出口；
- 测试不同 WARP 接入端点；
- 将 WireGuard 参数转换成常用客户端格式；
- 为已有代理配置提供 WARP 备用节点；
- 研究自动生成订阅和策略组。

项目不保证：

- 每个标注地区都对应真实的当地出口；
- 所有端点长期可用；
- 视频、直播或大流量传输稳定；
- TCP 端口可连接就一定能完成 WireGuard 握手；
- 一次 HTTP 204 成功就代表长期稳定；
- 公共测速 CSV 的结果在所有运营商和时段都有效。

---

## 当前生成内容

默认配置按 9 个地区标签组织，每个地区生成 4 个端点，共 36 个 WireGuard 条目；另外包含一个信息条目，因此生成文件通常包含 37 个代理条目：

- 🇭🇰 香港（HK）
- 🇹🇼 台湾（TW）
- 🇯🇵 日本（JP）
- 🇸🇬 新加坡（SG）
- 🇺🇸 美国（US）
- 🇬🇧 英国（GB）
- 🇩🇪 德国（DE）
- 🇰🇷 韩国（KR）
- 🇨🇦 加拿大（CA）

这些是配置标签，不是对 Cloudflare 实际出口位置的承诺。端点可用性会受到运营商、网络时段、UDP 连通性、Cloudflare 路由和 WARP 账户状态影响。

---

## 订阅文件

仓库的 `dist/` 目录包含由 `generator.py` 生成的文件：

### Mihomo / Clash Meta

完整配置，包含节点、地区分组、手动选择、自动测速、海外 AI、流媒体、社交、开发者服务和广告拦截等策略组：

```text
https://fastly.jsdelivr.net/gh/Daey886/warp-nodes@main/dist/clash.yaml
```

GitHub Raw 备用地址：

```text
https://raw.githubusercontent.com/Daey886/warp-nodes/main/dist/clash.yaml
```

纯节点池：

```text
https://fastly.jsdelivr.net/gh/Daey886/warp-nodes@main/dist/clash_providers.yaml
```

### Sing-box

```text
https://fastly.jsdelivr.net/gh/Daey886/warp-nodes@main/dist/singbox.json
```

### Loon

```text
https://fastly.jsdelivr.net/gh/Daey886/warp-nodes@main/dist/loon.list
```

### Shadowrocket / v2rayN

```text
https://fastly.jsdelivr.net/gh/Daey886/warp-nodes@main/dist/sub.txt
```

订阅文件由 GitHub Actions 定期重新生成。生成成功不等于所有节点都通过了当前网络下的真实代理流量验证；使用者应在自己的线路上测试 WireGuard 握手、HTTP 请求和持续流量表现。

---

## Cloudflare Worker 动态分发

仓库保留 `worker.js` 作为可选的 Cloudflare Worker 部署模板。Worker 可以根据请求携带的 Cloudflare ASN、运营商组织和国家信息，动态生成一份订阅配置。

这个方案的意义是：

- 让不同网络环境的访问者获得不同的配置标签；
- 将订阅入口放在自己的 Worker 自定义域名下；
- 在 Worker 层读取仓库中的 `dist/meta.json`，按请求动态拼装 Clash 配置。

但 Worker 不能改变 WARP 的底层网络事实：

- Worker 不能保证某个 Anycast IP 对应某个国家；
- Worker 不能凭 ASN 直接证明某个端点对该运营商一定最快；
- Worker 本身不等于节点健康检查系统；
- Worker 不应把未经过真实 WireGuard 和代理流量验证的端点包装成“最优节点”。

### 当前在线状态

仓库曾经使用过 `warp.baey.top` 作为在线 Worker 入口，但该实例和 DNS 记录已经删除。当前没有由本仓库维护的官方动态订阅地址。

如需自行部署：

1. 在 Cloudflare Workers 创建自己的 Worker；
2. 部署仓库根目录的 `worker.js`；
3. 绑定自己的 Worker 域名或自定义域名；
4. 使用自己的域名加 `/clash` 作为动态订阅地址；
5. 部署后自行验证 `/status`、`/clash`、Worker 路由和订阅内容。

不要直接把已经删除的 `warp.baey.top` 当作可用地址。

---

## 静态订阅与 Worker 订阅

| 方式 | 实际作用 | 限制 |
| --- | --- | --- |
| GitHub / jsDelivr 静态订阅 | 提供已经生成的固定配置 | 所有访问者拿到同一批配置，依赖端点当前状态 |
| 自建 Cloudflare Worker | 按请求环境动态生成配置 | 只能改变分发逻辑，不能保证 WARP 出口地区或线路质量 |

Worker 是订阅分发层，不是新的代理传输层。两种方式最终使用的仍然是 WARP WireGuard 端点。

---

## 端点来源与实际筛选

`generator.py` 包含固定的默认端点，也可以读取公开测速 CSV 作为候选来源。公开测速结果只能作为候选参考，不能视为长期稳定保证。

可靠的节点验收应至少包含：

1. WireGuard UDP 握手；
2. 通过该节点发出真实 HTTP 请求；
3. 多次、分时段重复测试；
4. 持续流量下的丢包、抖动、重传和吞吐观察。

TCP 端口探测不能替代 WireGuard 测试；一次延迟测试也不能替代视频或持续下载测试。

---

## 自动化流程

`.github/workflows/update.yml` 由 GitHub Actions 定期运行，并支持手动触发：

1. 检出仓库；
2. 安装 Python 依赖；
3. 运行 `test_generator.py`；
4. 运行 `generator.py`；
5. 将有变化的 `dist/` 文件提交回 `main`。

当前工作流验证的是生成器测试和订阅文件生成，不等价于对全部端点完成端到端可用性验收。

---

## 本地生成

```bash
pip install cryptography pyyaml
python3 -m unittest test_generator.py
python3 generator.py
```

生成结果位于 `dist/`。

---

## 安全说明

不要把真实的 WireGuard 私钥、WARP 账户令牌、许可证密钥或其他账户凭据提交到公开仓库。公开订阅中的凭据一旦泄露，应立即废弃并重新生成账户或密钥。

本项目不提供账号共享、节点可用性承诺或商业代理服务。

---

## 开源许可

本项目遵循 [MIT License](LICENSE)。
