# Container image provenance

The source-controlled container definitions pin the official multi-platform image
indexes reviewed for the Phase 6 baseline:

| Image | Pinned index digest |
| --- | --- |
| `node:24.20.0-bookworm-slim` | `sha256:ba849c60be29959425b8734d57b8b4b7d56f98edd9504c9af091d5281095a71e` |
| `python:3.14.7-slim-bookworm` | `sha256:9ab8d9c8514b44f90cf0029dd42fdd7e9e211e639c8b995304cc04568dee900f` |
| `postgres:18.6` | `sha256:4ef4dbc939d61acea57712655ddb4b4ab27419c913f94cca0cd57cb3ea3c2280` |
| `redis:8.10.1` | `sha256:298e5b3bc566bade82f46ad5511777a4a07a294097ce16ada2f6a42be5239df5` |
| `nginx:1.30.4-alpine-slim` | `sha256:77da26c31397bf6694b4bf93275f5b40b0b120ba1b8f114264b603e592c561d6` |

Before every deployment, build the three VOLUMA images from the committed lockfiles,
run the required vulnerability scan, and record the resulting application image digest,
scanner version/database timestamp, findings, accepted exceptions, and release commit
in the private deployment record. Do not replace a digest with a tag or `latest`.
