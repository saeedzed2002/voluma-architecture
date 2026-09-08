# Container image provenance

The source-controlled container definitions pin the official multi-platform image
indexes reviewed for the Phase 6 baseline:

| Image | Pinned index digest |
| --- | --- |
| `node:24.20.0-bookworm-slim` | `sha256:ba849c60be29959425b8734d57b8b4b7d56f98edd9504c9af091d5281095a71e` |
| `python:3.14.7-slim-bookworm` | `sha256:416f0db2a2b561945630cef9877a7ea0581b27449eb9fd9df42f03e1b74b5b63` |
| `postgres:18.6` | `sha256:4ef4dbc939d61acea57712655ddb4b4ab27419c913f94cca0cd57cb3ea3c2280` |
| `redis:8.10.1` | `sha256:298e5b3bc566bade82f46ad5511777a4a07a294097ce16ada2f6a42be5239df5` |
| `nginx:1.30.4-alpine` | `sha256:dc5069ad14f19660b141b21236140b91656bf89bbc3e2417c70ae650cd66104c` |

Before every deployment, build the three VOLUMA images from the committed lockfiles,
run the required vulnerability scan, and record the resulting application image digest,
scanner version/database timestamp, findings, accepted exceptions, and release commit
in the private deployment record. Do not replace a digest with a tag or `latest`.
