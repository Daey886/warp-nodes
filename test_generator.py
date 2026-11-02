import unittest
import os
import json
import base64
import yaml
from generator import (
    REGIONS,
    DEFAULT_ENDPOINTS,
    build_node_pool,
    generate_clash_yaml,
    generate_clash_providers,
    generate_singbox_json,
    generate_sub_txt,
)

class TestWarpGenerator(unittest.TestCase):
    def setUp(self):
        self.mock_account = {
            'private_key': 'mock_priv_key_example=',
            'public_key': 'bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=',
            'v4': '172.16.0.2',
            'v6': '2606:4700:110:88d6:7c4d:b582:9dc1:7a2c',
            'reserved': [54, 177, 14]
        }
        self.mock_probe_list = [
            {'host': '162.159.192.19', 'port': 987, 'loss': 0.0, 'delay': 140.0},
            {'host': '162.159.195.165', 'port': 878, 'loss': 0.0, 'delay': 150.0},
        ]

    def test_node_pool_regions_and_counts(self):
        nodes = build_node_pool(self.mock_account, self.mock_probe_list)
        # 1 info node + 36 region nodes = 37 total
        self.assertEqual(len(nodes), 37, "Total nodes should be 37 (1 info node + 9 regions * 4 nodes)")
        self.assertTrue(nodes[0]['name'].startswith("📊 剩余流量"))
        
        region_counts = {}
        for n in nodes:
            r = n['region']
            if r == 'INFO':
                continue
            region_counts[r] = region_counts.get(r, 0) + 1
            self.assertEqual(len(n['reserved']), 3, "Reserved client_id must have 3 integers")
            self.assertEqual(n['ip'], '172.16.0.2')
            self.assertTrue(n['private_key'])
            self.assertTrue(n['public_key'])

        self.assertEqual(len(region_counts), 9, "Should cover exactly 9 regions")
        for code, count in region_counts.items():
            self.assertEqual(count, 4, f"Region {code} should have 4 nodes")

    def test_clash_yaml_structure(self):
        nodes = build_node_pool(self.mock_account, self.mock_probe_list)
        yaml_content = generate_clash_yaml(nodes)
        self.assertIn("🤖 海外AI", yaml_content)
        self.assertNotIn("🎬 国际流媒体", yaml_content)
        self.assertNotIn("💬 社交社区", yaml_content)
        self.assertNotIn("👨‍💻 开发者服务", yaml_content)
        self.assertIn("🎯 全球直连", yaml_content)
        self.assertIn("hidden: true", yaml_content)
        self.assertIn("🖐️ 手动选择", yaml_content)
        self.assertNotIn("🌐 地区手动选择", yaml_content)
        self.assertIn("♻️ 自动选择", yaml_content)
        self.assertIn("⚡ 地区自动选择", yaml_content)
        self.assertIn("persistent-keepalive: 25", yaml_content)
        self.assertIn("proxies:", yaml_content)
        self.assertIn("proxy-groups:", yaml_content)
        
        # Parse with PyYAML to verify syntax
        data = yaml.safe_load(yaml_content)
        self.assertEqual(len(data['proxies']), 37)
        group_names = [g['name'] for g in data['proxy-groups']]
        self.assertIn("🚀 节点选择", group_names)
        self.assertIn("🖐️ 手动选择", group_names)
        self.assertNotIn("🌐 地区手动选择", group_names)
        self.assertIn("♻️ 自动选择", group_names)
        self.assertIn("⚡ 地区自动选择", group_names)
        self.assertIn("🤖 海外AI", group_names)
        self.assertIn("🛑 广告拦截", group_names)
        self.assertIn("🎯 全球直连", group_names)
        hidden_groups = [g['name'] for g in data['proxy-groups'] if g.get('hidden') is True]
        self.assertEqual(set(hidden_groups), {
            "🇭🇰 香港", "🇹🇼 台湾", "🇯🇵 日本", "🇸🇬 新加坡", "🇺🇸 美国",
            "🇬🇧 英国", "🇩🇪 德国", "🇰🇷 韩国", "🇨🇦 加拿大",
        })
        self.assertEqual(group_names.count("🎯 全球直连"), 1)

    def test_singbox_json(self):
        nodes = build_node_pool(self.mock_account, self.mock_probe_list)
        sb_json = generate_singbox_json(nodes)
        data = json.loads(sb_json)
        self.assertIn("outbounds", data)
        self.assertEqual(len(data['outbounds']), 37)
        self.assertEqual(data['outbounds'][0]['type'], 'wireguard')

    def test_sub_txt_base64(self):
        nodes = build_node_pool(self.mock_account, self.mock_probe_list)
        b64 = generate_sub_txt(nodes)
        decoded = base64.b64decode(b64).decode('utf-8')
        uris = decoded.splitlines()
        self.assertEqual(len(uris), 37)
        self.assertTrue(uris[0].startswith("wireguard://"))
        self.assertIn("reserved=", uris[0])

    def test_loon_list(self):
        nodes = build_node_pool(self.mock_account, self.mock_probe_list)
        from generator import generate_loon_list
        loon_text = generate_loon_list(nodes)
        self.assertIn("[Proxy]", loon_text)
        self.assertIn("interface-ip=172.16.0.2", loon_text)
        self.assertIn("reserved=[54,177,14]", loon_text)
        self.assertIn("wireguard,", loon_text)

    def test_meta_json_structure(self):
        with open('dist/meta.json') as f:
            data = json.load(f)
        self.assertEqual(data['account']['ip'], '172.16.0.2')
        self.assertTrue(len(data['nodes']) >= 36)


if __name__ == '__main__':
    unittest.main()
