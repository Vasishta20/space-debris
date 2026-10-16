# Bounded performance evidence

Run date: 2026-10-14. Host: local Windows execution. No full joined dataset was processed.

| Stage | Input/output | Elapsed seconds | Evidence |
|---|---:|---:|---|
| SATCAT ingest | 68,129 seen / 68,129 loaded / 0 rejected | 0.5079 | `pipeline-final.log` |
| EDA | 68,129 rows, four PNG charts | 1.2767 | `reports/eda/eda.json` and log |
| scikit-learn baseline | 68,129 rows, stratified 25% holdout | 2.6451 | `data/model_metrics.json` and log |
| SGP4 screening | 60 TLEs × 7 epochs, 1 candidate | 0.0169 | `data/screening.json` and log |
| Pipeline wall time | all bounded stages | approximately 7.1 | PowerShell command wall time |

The timings are single-run local measurements, not distributed Spark benchmarks. No partition-count experiment, throughput comparison, or multi-node claim is made. The Spark RDD evidence reports two local partitions for its deterministic fixture.

Parquet round-trip: 68,129 rows written/read with schema validation in 0.2917 seconds using PyArrow. PostgreSQL migration is a bounded data-load operation and is not presented as a pipeline timing benchmark.

## Review 3 validation and bounded Spark benchmark — 2026-10-15

The original joined CSV was scanned read-only with a single-pass `csv.reader`. It is not a distributed benchmark and produced:

| Check | Measured result |
|---|---:|
| Input size | 6,046,742,709 bytes |
| Data rows | 29,136,654 |
| Malformed rows | 0 |
| Invalid numeric values | 0 |
| Duplicate `(norad_id, epoch)` keys | 0 |
| Unique NORAD IDs | 31,937 |
| Scan elapsed | 203.910 seconds |

The existing six-record Scala RDD fixture was run with requested partitions 1, 2, and 4, then repeated once after compilation. All runs returned six valid records, category counts `(DEB,2);(PAY,3);(R/B,1)`, and altitude sum `3245.0 km`. Repeat wrapper times were 6.478 s, 6.290 s, and 6.512 s respectively. The first compile-inclusive run was 12.544 s, 6.577 s, and 6.854 s. These timings include local JVM/Maven/Spark startup and are not a speedup claim; the fixture is intentionally tiny and no full joined dataset was processed by Spark. Raw logs are under `reports/benchmarks/`.

The joined-file comparison with `data/satcat_clean.parquet` found 31,516 joined IDs in common, 421 joined-only IDs, and 36,613 Parquet-only IDs. These are different artifacts with different temporal/source scopes; no equality claim is made.

## Altitude-shell bounded comparison — 2026-10-15

The project-local shell implementation processed 420 propagated states (60 TLEs × 7 UTC epochs) in 0.019141 seconds and returned one candidate. The brute-force reference also returned one candidate; identities and distance/relative-velocity results matched exactly. This is a correctness/equivalence measurement on a small fixture, not a speedup claim: both methods were run in one process and no full joined dataset was processed.

## Staged shell scalability assessment — 2026-10-15

Using the existing C: Parquet altitude values to construct deterministic local state fixtures, the grouped legacy API and epoch-streaming API measured the following. Candidate identities matched in every case:

| Objects/epoch | Epochs | States | Shell comparisons/epoch | Brute-force pairs/epoch | Elapsed seconds | Peak traced allocation |
|---:|---:|---:|---:|---:|---:|---:|
| 60 | 7 | 420 | 261 | 1,770 | 0.0192 / 0.0163 | 0.29 / 0.06 MB |
| 240 | 7 | 1,680 | 5,416 | 28,680 | 0.1646 / 0.1489 | 1.07 / 0.15 MB |
| 960 | 7 | 6,720 | 114,990 | 460,320 | 2.9639 / 3.2356 | 4.06 / 0.89 MB |

Runtime and allocation columns are `legacy / streaming`; the streaming values are not guaranteed faster because both include Python fixture generation and interpreter overhead. Its main benefit is bounded working memory. The arithmetic estimate for 68,129 objects over seven epochs is 476,903 states and 2,320,746,256 brute-force pairs per epoch, or 16,245,223,792 total pair evaluations. No full-catalog job was launched. The streaming API has no spill or distributed partitioning; these measurements do not establish full-catalog feasibility or distributed scalability.

