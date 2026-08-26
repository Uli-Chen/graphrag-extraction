# Medical GraphRAG formal results

These are the designated 100-query results against the same frozen medical
GraphRAG truth (1,178 nodes and 3,046 directed edge pairs). API thinking and
graph filtering were disabled in every run.

| Method | Recovered nodes | Matched nodes | Node P / R / F1 | Node TSC | Recovered edges | Matched edges | Edge P / R / F1 | Edge TSC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FEWA (3-seed mean) | 917.7 | 787.0 | .8587 / .6681 / .7511 | .7510 | 1,686.0 | 1,571.0 | .9315 / .5158 / .6637 | .5230 |
| AGEA (3-seed mean) | 907.7 | 782.7 | .8644 / .6644 / .7504 | .7427 | 1,646.7 | 1,520.7 | .9235 / .4992 / .6477 | .5052 |

`fewa_100turn_formal` is the official FEWA result aggregated over seeds 40,
41, and 42. The important former single-seed fair replicate is preserved as
`fewa_100turn_formal_1seed`. `agea_100turn_formal` is the official AGEA result
over the same three random seeds. Multi-seed root files contain aggregate
metrics and mean/std trajectories, while each `seed*/` directory preserves an
auditable compact run snapshot.

FEWA sample standard deviations for node P/R/F1/TSC are
.0303/.0118/.0055/.0186; the corresponding edge values are
.0140/.0276/.0257/.0280. AGEA sample standard deviations for node P/R/F1/TSC
are .0448/.0340/.0215/.0341; the corresponding edge values are
.0122/.0329/.0287/.0332.

Each standalone AGEA run used AGEA's native seed query, whereas all FEWA seeds
replayed the same frozen FEWA seed response. Both methods used the current
`DeepSeek-V4-Flash` model for live rounds. Therefore the comparison is
descriptive under the same budget and API switches, but the methods do not use
an identical first response. Both FEWA snapshots retain the frozen seed
response needed to reproduce their protocols.
