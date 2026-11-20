# Network Automation Lab

Multi-vendor EVPN-VXLAN fabric built with Containerlab: an FRRouting spine and two Nokia SR Linux leaves, with a Linux host behind each leaf. The fabric is first configured by hand (to understand every step) and then automated with Ansible and Python.

> **Status:** work in progress. See the roadmap below.

## Topology

| Node | Role | Image |
|---|---|---|
| `spine1` | Underlay spine (eBGP) | `frrouting/frr` |
| `leaf1`, `leaf2` | VXLAN leaves (underlay + EVPN overlay) | `ghcr.io/nokia/srlinux` |
| `h1`, `h2` | Hosts in the same L2 segment | `alpine` |

## Addressing plan

| Node | AS | Loopback | Uplink to spine |
|---|---|---|---|
| spine1 | 65000 | 10.255.0.1/32 | 10.0.1.0/31 (to leaf1), 10.0.2.0/31 (to leaf2) |
| leaf1 | 65001 | 10.255.0.11/32 | 10.0.1.1/31 |
| leaf2 | 65002 | 10.255.0.12/32 | 10.0.2.1/31 |

L2 segment: VNI 111 / EVI 111 (`mac-vrf-1`), route target `target:100:111`. Hosts: `h1` 192.168.100.1/24, `h2` 192.168.100.2/24.

## Design

- **Underlay:** eBGP between the spine and each leaf, advertising only the loopbacks.
- **Overlay:** EVPN-VXLAN, with eBGP multihop sessions between the leaf loopbacks. The spine only provides IP transport.

## Usage

```bash
sudo containerlab deploy -t fabric.clab.yml
# manual configuration: see manual/*.cli
docker exec clab-fabric-h1 ip addr add 192.168.100.1/24 dev eth1
docker exec clab-fabric-h2 ip addr add 192.168.100.2/24 dev eth1
docker exec clab-fabric-h1 ping -c 4 192.168.100.2
sudo containerlab destroy -t fabric.clab.yml --cleanup
```

Requires Docker and Containerlab (WSL2 on Windows works). The two SR Linux nodes use about 3 GB of RAM.

## Roadmap

- [x] Base topology (FRR spine, SR Linux leaves, hosts)
- [x] Manual BGP underlay
- [x] Manual EVPN-VXLAN overlay
- [ ] Automation with Ansible (data model, templates) and Python validation
- [ ] CI: lint, deploy the lab, apply and validate