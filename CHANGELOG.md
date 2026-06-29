# Changelog

All notable changes to interior-space-layout-design are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/), and this
project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-06-29
### Added
- Full production Python harness (`src/interior_layout/`): intake, framework
  selector, 8-dimension scoring engine, improvement roadmap, feng shui overlay,
  quality gates, devil's-advocate review, synthesis, CLI.
- Standardized cluster output schema (`Deliverable` v1.0.0) and shared
  cross-skill contract (`cluster_contract.py` + `CLUSTER-INTEGRATION.md`).
- Self-improving knowledge pipeline (`knowledge_updater.py`): ArXiv API +
  optional crawl4ai, recency x relevance scoring, URL/DOI-hash dedup.
- Second knowledge brain seeded with 10 curated, cited entries.
- 7 end-to-end test scenarios + 25 pytest unit tests; all passing.
- README, LICENSE (MIT), pyproject, requirements, CI workflow, cron schedule.
