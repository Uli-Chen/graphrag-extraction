# Medical extraction results

- Run: `medical_ts_pl_fewa_50turn_v2`
- Turns: 50
- Recovered graph: 614 nodes / 910 relation triples
- Node precision: 0.9153
- Node recall: 0.4771
- Directed edge-pair precision: 0.9901
- Directed edge-pair recall: 0.2958
- Node TSC (rank): 0.5596
- Edge TSC (rank): 0.2990
- AUTSC, node rank: 0.3990
- AUTSC, edge rank: 0.1730
- Mean HTSN: 0.1782
- Mean count novelty: 0.4068
- Post-seed explore/exploit: 18/31
- Exploit query anchor adherence: 1.0000
- Exploit response anchor adherence: 0.8710

| Turn | Mode | Reason | Anchor | HTSN | Raw reward | Effective FEWA | Anchor response | Node TSC | Edge TSC |
|---:|---|---|---|---:|---:|---:|---|---:|---:|
| 1 | explore | seed_turn | - | 0.0000 | 0.0000 | - | - | 0.0629 | 0.0112 |
| 2 | exploit | fewa(0.2940) | DIAGNOSTIC TESTS | 0.0000 | 0.0000 | 0.0000 | yes | 0.0629 | 0.0112 |
| 3 | explore | recent_htsn_below_threshold(0.1441) | - | 0.3175 | 0.0583 | - | - | 0.1122 | 0.0260 |
| 4 | explore | epsilon_sample(0.2824) | - | 0.2030 | 0.0369 | - | - | 0.1549 | 0.0387 |
| 5 | explore | epsilon_sample(0.2767) | - | 0.3052 | 0.0888 | - | - | 0.2043 | 0.0589 |
| 6 | explore | epsilon_sample(0.2712) | - | 0.1733 | 0.0129 | - | - | 0.2202 | 0.0625 |
| 7 | exploit | fewa(0.2658) | MAMMOGRAM | 0.4304 | 0.0639 | 0.0639 | yes | 0.2380 | 0.0752 |
| 8 | exploit | fewa(0.2604) | TUMOR STAGING | 0.4046 | 0.0537 | 0.0537 | yes | 0.2575 | 0.0856 |
| 9 | exploit | fewa(0.2552) | NCCN CANCER CENTERS | 0.0000 | 0.0000 | 0.0000 | no | 0.2575 | 0.0856 |
| 10 | explore | epsilon_sample(0.2501) | - | 0.0856 | 0.0137 | - | - | 0.2754 | 0.0903 |
| 11 | exploit | fewa(0.2451) | SURGERY | 0.1124 | 0.0081 | 0.0081 | yes | 0.2813 | 0.0919 |
| 12 | explore | epsilon_sample(0.2402) | - | 0.3263 | 0.0523 | - | - | 0.2992 | 0.1018 |
| 13 | explore | epsilon_sample(0.2354) | - | 0.1765 | 0.0121 | - | - | 0.3078 | 0.1041 |
| 14 | exploit | fewa(0.2307) | COMPLETE BLOOD COUNT AND DIFFERENTIAL | 0.2313 | 0.0420 | 0.0420 | yes | 0.3271 | 0.1134 |
| 15 | explore | epsilon_sample(0.2261) | - | 0.0000 | 0.0000 | - | - | 0.3324 | 0.1143 |
| 16 | explore | epsilon_sample(0.2216) | - | 0.0813 | 0.0192 | - | - | 0.3478 | 0.1211 |
| 17 | exploit | fewa(0.2171) | TREATMENT | 0.0000 | 0.0000 | 0.0000 | no | 0.3501 | 0.1211 |
| 18 | explore | recent_htsn_below_threshold(0.1064) | - | 0.0000 | 0.0000 | - | - | 0.3575 | 0.1211 |
| 19 | explore | recent_htsn_below_threshold(0.1043) | - | 0.1403 | 0.0241 | - | - | 0.3647 | 0.1261 |
| 20 | explore | recent_htsn_below_threshold(0.1022) | - | 0.0000 | 0.0000 | - | - | 0.3650 | 0.1261 |
| 21 | explore | recent_htsn_below_threshold(0.1001) | - | 0.1922 | 0.0435 | - | - | 0.3826 | 0.1361 |
| 22 | explore | recent_htsn_below_threshold(0.0981) | - | 0.1919 | 0.0543 | - | - | 0.3923 | 0.1473 |
| 23 | exploit | fewa(0.1924) | BREAST CANCER | 0.4013 | 0.1027 | 0.1027 | yes | 0.4152 | 0.1651 |
| 24 | exploit | fewa(0.1885) | MEDICAL TEAM | 0.3261 | 0.0408 | 0.0000 | no | 0.4195 | 0.1725 |
| 25 | exploit | fewa(0.1847) | MAMMOGRAM SCREENING | 0.0979 | 0.0228 | 0.0228 | yes | 0.4266 | 0.1781 |
| 26 | exploit | fewa(0.1810) | HEPATITIS B AND HEPATITIS C SCREENING | 0.1028 | 0.0070 | 0.0070 | yes | 0.4266 | 0.1796 |
| 27 | explore | epsilon_sample(0.1774) | - | 0.0871 | 0.0156 | - | - | 0.4312 | 0.1829 |
| 28 | exploit | fewa(0.1739) | SPINE MRI | 0.3168 | 0.0631 | 0.0631 | yes | 0.4546 | 0.1952 |
| 29 | exploit | fewa(0.1704) | SURGICAL STAGING | 0.2510 | 0.0270 | 0.0270 | yes | 0.4660 | 0.2006 |
| 30 | exploit | fewa(0.1670) | CARDIOLOGIST | 0.2300 | 0.0418 | 0.0418 | yes | 0.4760 | 0.2089 |
| 31 | explore | epsilon_sample(0.1636) | - | 0.1013 | 0.0243 | - | - | 0.4775 | 0.2137 |
| 32 | exploit | fewa(0.1604) | LDH TEST | 0.0589 | 0.0093 | 0.0093 | yes | 0.4843 | 0.2151 |
| 33 | exploit | fewa(0.1572) | GENETIC TESTS | 0.3041 | 0.0594 | 0.0594 | yes | 0.4950 | 0.2276 |
| 34 | explore | epsilon_sample(0.1540) | - | 0.0000 | 0.0000 | - | - | 0.4953 | 0.2276 |
| 35 | explore | epsilon_sample(0.1509) | - | 0.0000 | 0.0000 | - | - | 0.4953 | 0.2276 |
| 36 | exploit | failed_explore_streak_cap(2) | B SYMPTOMS | 0.3175 | 0.0081 | 0.0081 | yes | 0.4975 | 0.2292 |
| 37 | exploit | fewa(0.1450) | MOHS SURGEON | 0.3347 | 0.0163 | 0.0163 | yes | 0.5034 | 0.2323 |
| 38 | exploit | fewa(0.1421) | HEPATITIS | 0.2511 | 0.0642 | 0.0642 | yes | 0.5145 | 0.2450 |
| 39 | exploit | fewa(0.1392) | DERMATOLOGIST | 0.3183 | 0.0733 | 0.0733 | yes | 0.5229 | 0.2597 |
| 40 | exploit | fewa(0.1364) | LYNCH SYNDROME | 0.2552 | 0.0424 | 0.0424 | yes | 0.5404 | 0.2700 |
| 41 | exploit | fewa(0.1337) | MEDICAL HISTORY | 0.1589 | 0.0394 | 0.0394 | yes | 0.5409 | 0.2779 |
| 42 | exploit | low_explore_success(0.000) | CLINICAL STAGING | 0.3115 | 0.0055 | 0.0055 | yes | 0.5409 | 0.2789 |
| 43 | exploit | low_explore_success(0.000) | TOMOSYNTHESIS | 0.0000 | 0.0000 | 0.0000 | yes | 0.5409 | 0.2789 |
| 44 | exploit | low_explore_success(0.000) | PELVIC MAGNETIC RESONANCE IMAGING | 0.1829 | 0.0029 | 0.0000 | no | 0.5409 | 0.2799 |
| 45 | exploit | fewa(0.1233) | CANCER CENTER | 0.2816 | 0.0204 | 0.0204 | yes | 0.5423 | 0.2817 |
| 46 | exploit | fewa(0.1209) | STAGE 3 RECTAL CANCER | 0.2941 | 0.0327 | 0.0327 | yes | 0.5452 | 0.2878 |
| 47 | exploit | fewa(0.1184) | DUCTAL CARCINOMA IN SITU | 0.0255 | 0.0012 | 0.0012 | yes | 0.5452 | 0.2880 |
| 48 | exploit | fewa(0.1161) | HOSPITAL | 0.0000 | 0.0000 | 0.0000 | yes | 0.5452 | 0.2880 |
| 49 | exploit | fewa(0.1138) | RECONSTRUCTIVE SURGERY | 0.1311 | 0.0082 | 0.0082 | yes | 0.5518 | 0.2897 |
| 50 | exploit | fewa(0.1115) | BIOPSY | 0.3992 | 0.0499 | 0.0499 | yes | 0.5596 | 0.2990 |

## Arm-policy diagnostics

- Policy: `topology_pl_fewa`
- Epochs: 11
- Unique admitted / selected arms: 33 / 31
- Selected arms: B SYMPTOMS, BIOPSY, BREAST CANCER, CANCER CENTER, CARDIOLOGIST, CLINICAL STAGING, COMPLETE BLOOD COUNT AND DIFFERENTIAL, DERMATOLOGIST, DIAGNOSTIC TESTS, DUCTAL CARCINOMA IN SITU, GENETIC TESTS, HEPATITIS, HEPATITIS B AND HEPATITIS C SCREENING, HOSPITAL, LDH TEST, LYNCH SYNDROME, MAMMOGRAM, MAMMOGRAM SCREENING, MEDICAL HISTORY, MEDICAL TEAM, MOHS SURGEON, NCCN CANCER CENTERS, PELVIC MAGNETIC RESONANCE IMAGING, RECONSTRUCTIVE SURGERY, SPINE MRI, STAGE 3 RECTAL CANCER, SURGERY, SURGICAL STAGING, TOMOSYNTHESIS, TREATMENT, TUMOR STAGING
- Mean admission-to-first-query delay: 0.9677
- Unqueried admitted slots: 2
- Mean epoch arm-set turnover: 1.0000

| Epoch | Active arms | Admission-to-first-query delay |
|---:|---|---|
| 1 | TUMOR STAGING, MAMMOGRAM, DIAGNOSTIC TESTS | TUMOR STAGING: 2, MAMMOGRAM: 1, DIAGNOSTIC TESTS: 0 |
| 2 | NCCN CANCER CENTERS, COMPLETE BLOOD COUNT AND DIFFERENTIAL, SURGERY | NCCN CANCER CENTERS: 0, COMPLETE BLOOD COUNT AND DIFFERENTIAL: 2, SURGERY: 1 |
| 3 | BREAST CANCER, MEDICAL TEAM, TREATMENT | BREAST CANCER: 1, MEDICAL TEAM: 2, TREATMENT: 0 |
| 4 | HEPATITIS B AND HEPATITIS C SCREENING, MAMMOGRAM SCREENING, SPINE MRI | HEPATITIS B AND HEPATITIS C SCREENING: 1, MAMMOGRAM SCREENING: 0, SPINE MRI: 2 |
| 5 | SURGICAL STAGING, LDH TEST, CARDIOLOGIST | SURGICAL STAGING: 0, LDH TEST: 2, CARDIOLOGIST: 1 |
| 6 | GENETIC TESTS, MOHS SURGEON, B SYMPTOMS | GENETIC TESTS: 0, MOHS SURGEON: 2, B SYMPTOMS: 1 |
| 7 | HEPATITIS, LYNCH SYNDROME, DERMATOLOGIST | HEPATITIS: 0, LYNCH SYNDROME: 2, DERMATOLOGIST: 1 |
| 8 | TOMOSYNTHESIS, CLINICAL STAGING, MEDICAL HISTORY | TOMOSYNTHESIS: 2, CLINICAL STAGING: 1, MEDICAL HISTORY: 0 |
| 9 | CANCER CENTER, STAGE 3 RECTAL CANCER, PELVIC MAGNETIC RESONANCE IMAGING | CANCER CENTER: 1, STAGE 3 RECTAL CANCER: 2, PELVIC MAGNETIC RESONANCE IMAGING: 0 |
| 10 | DUCTAL CARCINOMA IN SITU, HOSPITAL, RECONSTRUCTIVE SURGERY | DUCTAL CARCINOMA IN SITU: 0, HOSPITAL: 1, RECONSTRUCTIVE SURGERY: 2 |
| 11 | FAMILY MEMBERS, DIAGNOSIS, BIOPSY | FAMILY MEMBERS: unqueried, DIAGNOSIS: unqueried, BIOPSY: 0 |

## Protocol acceptance

| Criterion | Value | Threshold | Passed |
|---|---:|---:|---|
| query_unique_rate | 1.0000 | 0.9000 | yes |
| zero_gain_rate | 0.0800 | 0.2000 | yes |
| max_consecutive_zero_gain | 1.0000 | 4.0000 | yes |
| max_consecutive_meaningful_zero_gain | 2.0000 | 4.0000 | yes |
| anchor_query_adherence_rate | 1.0000 | 1.0000 | yes |
| both_post_seed_modes_observed | 1.0000 | 1.0000 | yes |
| nonempty_main_response_rate | 1.0000 | 1.0000 | yes |

All formal acceptance criteria passed: yes.

HTSN is scored against the graph snapshot before each batch. RTSN is computed after the merge, and their difference is reported as retrospective gain. GraphRAG truth does not expose a structured relation type, so truth edge metrics use directed endpoint pairs; extraction novelty still uses relation triples.
