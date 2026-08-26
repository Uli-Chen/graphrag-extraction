# Medical extraction results

- Run: `medical_ts_pl_fewa_100turn_no_thinking_fair_replicate2_seed42`
- Turns: 100
- Recovered graph: 1073 nodes / 1669 relation triples
- Node precision: 0.7931
- Node recall: 0.7224
- Directed edge-pair precision: 0.9754
- Directed edge-pair recall: 0.5345
- Node TSC (rank): 0.8000
- Edge TSC (rank): 0.5360
- AUTSC, node rank: 0.5944
- AUTSC, edge rank: 0.3389
- Mean HTSN: 0.1449
- Mean count novelty: 0.3204
- Post-seed explore/exploit: 19/80
- Exploit query anchor adherence: 1.0000
- Exploit response anchor adherence: 0.9750

| Turn | Mode | Reason | Anchor | HTSN | Raw reward | Effective FEWA | Anchor response | Node TSC | Edge TSC |
|---:|---|---|---|---:|---:|---:|---|---:|---:|
| 1 | explore | seed_turn | - | 0.0000 | 0.0000 | - | - | 0.0612 | 0.0108 |
| 2 | exploit | fewa(0.2940) | DIAGNOSTIC TESTS | 0.1376 | 0.0118 | 0.0118 | yes | 0.0916 | 0.0151 |
| 3 | explore | recent_htsn_below_threshold(0.1441) | - | 0.1139 | 0.0085 | - | - | 0.1177 | 0.0186 |
| 4 | explore | recent_htsn_below_threshold(0.1412) | - | 0.3347 | 0.0347 | - | - | 0.1331 | 0.0257 |
| 5 | explore | epsilon_sample(0.2767) | - | 0.4359 | 0.1030 | - | - | 0.1714 | 0.0485 |
| 6 | exploit | fewa(0.2712) | MEDICAL HISTORY AND PHYSICAL EXAM (H&P) | 0.2691 | 0.0484 | 0.0484 | yes | 0.1940 | 0.0580 |
| 7 | explore | epsilon_sample(0.2658) | - | 0.1559 | 0.0381 | - | - | 0.2207 | 0.0694 |
| 8 | exploit | fewa(0.2604) | TUMOR STAGING | 0.1351 | 0.0095 | 0.0095 | yes | 0.2437 | 0.0721 |
| 9 | exploit | fewa(0.2552) | SURGERY | 0.2576 | 0.0282 | 0.0282 | yes | 0.2571 | 0.0784 |
| 10 | exploit | fewa(0.2501) | NASOPHARYNGEAL CANCER | 0.3096 | 0.0399 | 0.0399 | yes | 0.2758 | 0.0880 |
| 11 | explore | epsilon_sample(0.2451) | - | 0.3323 | 0.0571 | - | - | 0.2924 | 0.1007 |
| 12 | exploit | fewa(0.2402) | DIABETES | 0.1777 | 0.0330 | 0.0330 | yes | 0.3054 | 0.1082 |
| 13 | explore | epsilon_sample(0.2354) | - | 0.1536 | 0.0327 | - | - | 0.3217 | 0.1183 |
| 14 | explore | epsilon_sample(0.2307) | - | 0.1312 | 0.0177 | - | - | 0.3280 | 0.1213 |
| 15 | exploit | fewa(0.2261) | MEDICAL TEAM | 0.4338 | 0.0678 | 0.0678 | yes | 0.3382 | 0.1343 |
| 16 | explore | epsilon_sample(0.2216) | - | 0.2700 | 0.0749 | - | - | 0.3605 | 0.1518 |
| 17 | explore | epsilon_sample(0.2171) | - | 0.1814 | 0.0400 | - | - | 0.3776 | 0.1606 |
| 18 | exploit | fewa(0.2128) | TEST RESULTS | 0.1568 | 0.0129 | 0.0129 | yes | 0.3818 | 0.1633 |
| 19 | exploit | fewa(0.2085) | BLOOD TRANSFUSION | 0.2472 | 0.0415 | 0.0415 | yes | 0.3953 | 0.1737 |
| 20 | exploit | fewa(0.2044) | MRI SCAN | 0.3387 | 0.0490 | 0.0490 | yes | 0.4155 | 0.1842 |
| 21 | exploit | fewa(0.2003) | HIGH WEIGHT | 0.1482 | 0.0252 | 0.0252 | yes | 0.4265 | 0.1909 |
| 22 | exploit | fewa(0.1963) | SQUAMOUS CELL CARCINOMA | 0.2320 | 0.0734 | 0.0734 | yes | 0.4494 | 0.2070 |
| 23 | explore | epsilon_sample(0.1924) | - | 0.3847 | 0.0992 | - | - | 0.4595 | 0.2261 |
| 24 | exploit | fewa(0.1885) | CERVICAL CANCER | 0.3361 | 0.0479 | 0.0479 | yes | 0.4813 | 0.2355 |
| 25 | exploit | fewa(0.1847) | MICROSATELLITE INSTABILITY (MSI) | 0.1129 | 0.0141 | 0.0141 | yes | 0.4819 | 0.2386 |
| 26 | exploit | fewa(0.1810) | SURVIVORSHIP CARE FOR HEALTHY LIVING | 0.4214 | 0.0757 | 0.0757 | yes | 0.5116 | 0.2520 |
| 27 | explore | epsilon_sample(0.1774) | - | 0.0921 | 0.0198 | - | - | 0.5149 | 0.2561 |
| 28 | exploit | fewa(0.1739) | HEART TESTS | 0.0000 | 0.0000 | 0.0000 | yes | 0.5183 | 0.2561 |
| 29 | exploit | fewa(0.1704) | NCCN GUIDELINES FOR PATIENTS | 0.0927 | 0.0052 | 0.0052 | yes | 0.5267 | 0.2569 |
| 30 | explore | epsilon_sample(0.1670) | - | 0.1611 | 0.0249 | - | - | 0.5281 | 0.2632 |
| 31 | explore | epsilon_sample(0.1636) | - | 0.3280 | 0.0698 | - | - | 0.5374 | 0.2758 |
| 32 | exploit | fewa(0.1604) | ALPHA-1-ANTITRYPSIN DEFICIENCY | 0.2298 | 0.0575 | 0.0575 | yes | 0.5455 | 0.2864 |
| 33 | exploit | fewa(0.1572) | CYSTOSCOPY | 0.3516 | 0.0618 | 0.0618 | yes | 0.5629 | 0.3009 |
| 34 | exploit | fewa(0.1540) | MISMATCH REPAIR | 0.0351 | 0.0051 | 0.0051 | yes | 0.5629 | 0.3019 |
| 35 | exploit | fewa(0.1509) | CYSTOSCOPY | 0.0223 | 0.0038 | 0.0038 | yes | 0.5634 | 0.3026 |
| 36 | exploit | fewa(0.1479) | CLINICAL PRE-SURGERY STAGE | 0.0776 | 0.0086 | 0.0086 | yes | 0.5660 | 0.3049 |
| 37 | exploit | fewa(0.1450) | TUMOR MUTATION TESTING | 0.0000 | 0.0000 | 0.0000 | yes | 0.5663 | 0.3049 |
| 38 | exploit | fewa(0.1421) | NASOPHARYNGEAL CANCER | 0.0813 | 0.0148 | 0.0148 | yes | 0.5678 | 0.3076 |
| 39 | explore | recent_htsn_below_threshold(0.0696) | - | 0.2125 | 0.0195 | - | - | 0.5688 | 0.3114 |
| 40 | exploit | fewa(0.1364) | SYSTEMIC THERAPY | 0.0000 | 0.0000 | 0.0000 | no | 0.5757 | 0.3114 |
| 41 | exploit | fewa(0.1337) | PROCTOSCOPY | 0.2307 | 0.0509 | 0.0509 | yes | 0.5976 | 0.3258 |
| 42 | exploit | fewa(0.1310) | BRCA MUTATION | 0.1006 | 0.0208 | 0.0208 | yes | 0.6004 | 0.3301 |
| 43 | exploit | fewa(0.1284) | EARLY-STAGE PROSTATE CANCER | 0.0000 | 0.0000 | 0.0000 | yes | 0.6038 | 0.3301 |
| 44 | exploit | fewa(0.1258) | HYSTERECTOMY | 0.3774 | 0.0656 | 0.0656 | yes | 0.6235 | 0.3439 |
| 45 | exploit | fewa(0.1233) | SERIOUS BLOOD CLOTS | 0.0000 | 0.0000 | 0.0000 | yes | 0.6235 | 0.3439 |
| 46 | explore | epsilon_sample(0.1209) | - | 0.0731 | 0.0047 | - | - | 0.6276 | 0.3448 |
| 47 | exploit | fewa(0.1184) | DIAGNOSIS | 0.0675 | 0.0131 | 0.0131 | yes | 0.6341 | 0.3483 |
| 48 | exploit | fewa(0.1161) | B12 AND FOLIC ACID | 0.1586 | 0.0294 | 0.0294 | yes | 0.6426 | 0.3535 |
| 49 | explore | epsilon_sample(0.1138) | - | 0.1056 | 0.0270 | - | - | 0.6491 | 0.3603 |
| 50 | exploit | fewa(0.1115) | FEVER | 0.0949 | 0.0245 | 0.0245 | yes | 0.6551 | 0.3654 |
| 51 | explore | epsilon_sample(0.1093) | - | 0.0285 | 0.0020 | - | - | 0.6554 | 0.3658 |
| 52 | exploit | fewa(0.1071) | ADRENAL TUMORS | 0.2645 | 0.0480 | 0.0480 | yes | 0.6626 | 0.3744 |
| 53 | exploit | fewa(0.1049) | TRANSANAL LOCAL EXCISION | 0.3001 | 0.0621 | 0.0621 | yes | 0.6776 | 0.3879 |
| 54 | exploit | fewa(0.1028) | HIV | 0.0502 | 0.0075 | 0.0075 | yes | 0.6778 | 0.3893 |
| 55 | exploit | fewa(0.1008) | HEPATITIS | 0.0991 | 0.0219 | 0.0219 | yes | 0.6827 | 0.3935 |
| 56 | exploit | fewa(0.0988) | ABDOMINOPERINEAL RESECTION | 0.0787 | 0.0118 | 0.0118 | yes | 0.6856 | 0.3961 |
| 57 | exploit | fewa(0.0968) | SOFT TISSUE SARCOMA | 0.0629 | 0.0071 | 0.0071 | yes | 0.6902 | 0.3976 |
| 58 | exploit | fewa(0.0948) | BRONCHOSCOPY | 0.2080 | 0.0227 | 0.0227 | yes | 0.6913 | 0.4033 |
| 59 | exploit | fewa(0.0929) | FISH | 0.0000 | 0.0000 | 0.0000 | yes | 0.6926 | 0.4033 |
| 60 | exploit | fewa(0.0911) | URINE TESTS FOR TUMOR MARKERS | 0.1544 | 0.0395 | 0.0395 | yes | 0.6989 | 0.4118 |
| 61 | exploit | fewa(0.0893) | TRANSABDOMINAL SURGERY | 0.0873 | 0.0147 | 0.0147 | yes | 0.7018 | 0.4146 |
| 62 | exploit | fewa(0.0875) | NEUROSURGEON | 0.1061 | 0.0120 | 0.0120 | yes | 0.7040 | 0.4173 |
| 63 | exploit | fewa(0.0857) | TNM STAGING | 0.0494 | 0.0058 | 0.0058 | yes | 0.7040 | 0.4186 |
| 64 | exploit | fewa(0.0840) | BIOPSY | 0.3484 | 0.0463 | 0.0463 | yes | 0.7134 | 0.4269 |
| 65 | exploit | fewa(0.0823) | CLL | 0.1255 | 0.0316 | 0.0316 | yes | 0.7193 | 0.4334 |
| 66 | exploit | fewa(0.0807) | CANCER PROGRESSION | 0.3465 | 0.0880 | 0.0000 | no | 0.7288 | 0.4397 |
| 67 | exploit | fewa(0.0791) | NEUROPATHOLOGIST | 0.0327 | 0.0038 | 0.0038 | yes | 0.7327 | 0.4403 |
| 68 | exploit | fewa(0.0775) | DEFICIENT MISMATCH REPAIR | 0.0150 | 0.0017 | 0.0017 | yes | 0.7327 | 0.4403 |
| 69 | exploit | fewa(0.0759) | FEVER | 0.0604 | 0.0091 | 0.0091 | yes | 0.7357 | 0.4420 |
| 70 | exploit | fewa(0.0744) | RISK ASSESSMENT | 0.0550 | 0.0119 | 0.0119 | yes | 0.7373 | 0.4441 |
| 71 | exploit | fewa(0.0729) | COLONOSCOPY | 0.0714 | 0.0156 | 0.0156 | yes | 0.7401 | 0.4472 |
| 72 | explore | epsilon_sample(0.0715) | - | 0.0000 | 0.0000 | - | - | 0.7401 | 0.4472 |
| 73 | exploit | fewa(0.0700) | UPPER URINARY TRACT CANCER | 0.1760 | 0.0409 | 0.0409 | yes | 0.7431 | 0.4552 |
| 74 | exploit | fewa(0.0686) | COMPLETE BLOOD COUNT AND DIFFERENTIAL | 0.0000 | 0.0000 | 0.0000 | yes | 0.7431 | 0.4552 |
| 75 | exploit | fewa(0.0673) | FOLLOW-UP TESTING | 0.2053 | 0.0485 | 0.0485 | yes | 0.7504 | 0.4649 |
| 76 | exploit | fewa(0.0659) | CURE | 0.0000 | 0.0000 | 0.0000 | yes | 0.7551 | 0.4657 |
| 77 | exploit | fewa(0.0646) | FDG PET-CT | 0.2993 | 0.0643 | 0.0643 | yes | 0.7678 | 0.4761 |
| 78 | exploit | fewa(0.0633) | LARYNGEAL CANCER | 0.0765 | 0.0070 | 0.0070 | yes | 0.7706 | 0.4776 |
| 79 | exploit | fewa(0.0621) | SKIN CANCER | 0.1595 | 0.0203 | 0.0203 | yes | 0.7737 | 0.4821 |
| 80 | exploit | fewa(0.0608) | FATIGUE | 0.0000 | 0.0000 | 0.0000 | yes | 0.7737 | 0.4821 |
| 81 | exploit | fewa(0.0596) | ALKALINE PHOSPHATASE TEST | 0.1404 | 0.0269 | 0.0269 | yes | 0.7749 | 0.4875 |
| 82 | exploit | fewa(0.0584) | ESOPHAGOSCOPY | 0.0753 | 0.0176 | 0.0176 | yes | 0.7754 | 0.4909 |
| 83 | exploit | fewa(0.0572) | PANENDOSCOPY | 0.0000 | 0.0000 | 0.0000 | yes | 0.7754 | 0.4909 |
| 84 | exploit | fewa(0.0561) | BLUE LIGHT CYSTOSCOPY | 0.1450 | 0.0221 | 0.0221 | yes | 0.7794 | 0.4960 |
| 85 | exploit | fewa(0.0550) | LOCAL THERAPIES | 0.1204 | 0.0120 | 0.0120 | yes | 0.7856 | 0.4995 |
| 86 | exploit | fewa(0.0539) | NEUROLOGICAL EXAM | 0.0600 | 0.0122 | 0.0122 | yes | 0.7867 | 0.5019 |
| 87 | exploit | fewa(0.0528) | OPEN MRI | 0.1365 | 0.0240 | 0.0240 | yes | 0.7870 | 0.5068 |
| 88 | exploit | fewa(0.0517) | RET MUTATIONS | 0.0000 | 0.0000 | 0.0000 | yes | 0.7870 | 0.5068 |
| 89 | exploit | fewa(0.0507) | TRANSABDOMINAL ULTRASOUND | 0.2476 | 0.0546 | 0.0546 | yes | 0.7923 | 0.5173 |
| 90 | exploit | fewa(0.0500) | ABDOMINAL SURGERY | 0.0000 | 0.0000 | 0.0000 | yes | 0.7923 | 0.5173 |
| 91 | exploit | fewa(0.0500) | CYSTOSCOPY AND IMAGING | 0.0000 | 0.0000 | 0.0000 | yes | 0.7923 | 0.5173 |
| 92 | exploit | fewa(0.0500) | FIBEROPTIC LARYNGOSCOPY | 0.0545 | 0.0102 | 0.0102 | yes | 0.7935 | 0.5192 |
| 93 | exploit | fewa(0.0500) | ENDOCRINE THERAPY | 0.2366 | 0.0231 | 0.0231 | yes | 0.7972 | 0.5228 |
| 94 | explore | epsilon_sample(0.0500) | - | 0.0087 | 0.0020 | - | - | 0.7974 | 0.5232 |
| 95 | exploit | fewa(0.0500) | ENDOCRINE THERAPY | 0.0082 | 0.0019 | 0.0019 | yes | 0.7974 | 0.5235 |
| 96 | exploit | fewa(0.0500) | PSA TEST | 0.0518 | 0.0037 | 0.0037 | yes | 0.7974 | 0.5235 |
| 97 | exploit | fewa(0.0500) | RADIATION THERAPY | 0.3105 | 0.0152 | 0.0152 | yes | 0.7974 | 0.5256 |
| 98 | exploit | fewa(0.0500) | CHRONIC HEPATITIS | 0.0000 | 0.0000 | 0.0000 | yes | 0.7974 | 0.5256 |
| 99 | exploit | fewa(0.0500) | PET/CT SCAN | 0.2099 | 0.0336 | 0.0336 | yes | 0.7997 | 0.5317 |
| 100 | exploit | fewa(0.0500) | PET-CT | 0.1221 | 0.0305 | 0.0305 | yes | 0.8000 | 0.5360 |

## Arm-policy diagnostics

- Policy: `topology_pl_fewa`
- Epochs: 27
- Unique admitted / selected arms: 76 / 76
- Selected arms: ABDOMINAL SURGERY, ABDOMINOPERINEAL RESECTION, ADRENAL TUMORS, ALKALINE PHOSPHATASE TEST, ALPHA-1-ANTITRYPSIN DEFICIENCY, B12 AND FOLIC ACID, BIOPSY, BLOOD TRANSFUSION, BLUE LIGHT CYSTOSCOPY, BRCA MUTATION, BRONCHOSCOPY, CANCER PROGRESSION, CERVICAL CANCER, CHRONIC HEPATITIS, CLINICAL PRE-SURGERY STAGE, CLL, COLONOSCOPY, COMPLETE BLOOD COUNT AND DIFFERENTIAL, CURE, CYSTOSCOPY, CYSTOSCOPY AND IMAGING, DEFICIENT MISMATCH REPAIR, DIABETES, DIAGNOSIS, DIAGNOSTIC TESTS, EARLY-STAGE PROSTATE CANCER, ENDOCRINE THERAPY, ESOPHAGOSCOPY, FATIGUE, FDG PET-CT, FEVER, FIBEROPTIC LARYNGOSCOPY, FISH, FOLLOW-UP TESTING, HEART TESTS, HEPATITIS, HIGH WEIGHT, HIV, HYSTERECTOMY, LARYNGEAL CANCER, LOCAL THERAPIES, MEDICAL HISTORY AND PHYSICAL EXAM (H&P), MEDICAL TEAM, MICROSATELLITE INSTABILITY (MSI), MISMATCH REPAIR, MRI SCAN, NASOPHARYNGEAL CANCER, NCCN GUIDELINES FOR PATIENTS, NEUROLOGICAL EXAM, NEUROPATHOLOGIST, NEUROSURGEON, OPEN MRI, PANENDOSCOPY, PET-CT, PET/CT SCAN, PROCTOSCOPY, PSA TEST, RADIATION THERAPY, RET MUTATIONS, RISK ASSESSMENT, SERIOUS BLOOD CLOTS, SKIN CANCER, SOFT TISSUE SARCOMA, SQUAMOUS CELL CARCINOMA, SURGERY, SURVIVORSHIP CARE FOR HEALTHY LIVING, SYSTEMIC THERAPY, TEST RESULTS, TNM STAGING, TRANSABDOMINAL SURGERY, TRANSABDOMINAL ULTRASOUND, TRANSANAL LOCAL EXCISION, TUMOR MUTATION TESTING, TUMOR STAGING, UPPER URINARY TRACT CANCER, URINE TESTS FOR TUMOR MARKERS
- Mean admission-to-first-query delay: 0.9615
- Unqueried admitted slots: 3
- Mean epoch arm-set turnover: 1.0000

| Epoch | Active arms | Admission-to-first-query delay |
|---:|---|---|
| 1 | TUMOR STAGING, MEDICAL HISTORY AND PHYSICAL EXAM (H&P), DIAGNOSTIC TESTS | TUMOR STAGING: 2, MEDICAL HISTORY AND PHYSICAL EXAM (H&P): 1, DIAGNOSTIC TESTS: 0 |
| 2 | NASOPHARYNGEAL CANCER, DIABETES, SURGERY | NASOPHARYNGEAL CANCER: 1, DIABETES: 2, SURGERY: 0 |
| 3 | BLOOD TRANSFUSION, MEDICAL TEAM, TEST RESULTS | BLOOD TRANSFUSION: 2, MEDICAL TEAM: 0, TEST RESULTS: 1 |
| 4 | HIGH WEIGHT, MRI SCAN, SQUAMOUS CELL CARCINOMA | HIGH WEIGHT: 1, MRI SCAN: 0, SQUAMOUS CELL CARCINOMA: 2 |
| 5 | SURVIVORSHIP CARE FOR HEALTHY LIVING, MICROSATELLITE INSTABILITY (MSI), CERVICAL CANCER | SURVIVORSHIP CARE FOR HEALTHY LIVING: 2, MICROSATELLITE INSTABILITY (MSI): 1, CERVICAL CANCER: 0 |
| 6 | HEART TESTS, NCCN GUIDELINES FOR PATIENTS, ALPHA-1-ANTITRYPSIN DEFICIENCY | HEART TESTS: 0, NCCN GUIDELINES FOR PATIENTS: 1, ALPHA-1-ANTITRYPSIN DEFICIENCY: 2 |
| 7 | HIGH WEIGHT, MISMATCH REPAIR, CYSTOSCOPY | HIGH WEIGHT: unqueried, MISMATCH REPAIR: 1, CYSTOSCOPY: 0 |
| 8 | TUMOR MUTATION TESTING, CLINICAL PRE-SURGERY STAGE, NASOPHARYNGEAL CANCER | TUMOR MUTATION TESTING: 1, CLINICAL PRE-SURGERY STAGE: 0, NASOPHARYNGEAL CANCER: 2 |
| 9 | BRCA MUTATION, SYSTEMIC THERAPY, PROCTOSCOPY | BRCA MUTATION: 2, SYSTEMIC THERAPY: 0, PROCTOSCOPY: 1 |
| 10 | EARLY-STAGE PROSTATE CANCER, HYSTERECTOMY, SERIOUS BLOOD CLOTS | EARLY-STAGE PROSTATE CANCER: 0, HYSTERECTOMY: 1, SERIOUS BLOOD CLOTS: 2 |
| 11 | FEVER, DIAGNOSIS, B12 AND FOLIC ACID | FEVER: 2, DIAGNOSIS: 0, B12 AND FOLIC ACID: 1 |
| 12 | TRANSANAL LOCAL EXCISION, ADRENAL TUMORS, HIV | TRANSANAL LOCAL EXCISION: 1, ADRENAL TUMORS: 0, HIV: 2 |
| 13 | ABDOMINOPERINEAL RESECTION, HEPATITIS, SOFT TISSUE SARCOMA | ABDOMINOPERINEAL RESECTION: 1, HEPATITIS: 0, SOFT TISSUE SARCOMA: 2 |
| 14 | BRONCHOSCOPY, FISH, URINE TESTS FOR TUMOR MARKERS | BRONCHOSCOPY: 0, FISH: 1, URINE TESTS FOR TUMOR MARKERS: 2 |
| 15 | TRANSABDOMINAL SURGERY, NEUROSURGEON, TNM STAGING | TRANSABDOMINAL SURGERY: 0, NEUROSURGEON: 1, TNM STAGING: 2 |
| 16 | CANCER PROGRESSION, CLL, BIOPSY | CANCER PROGRESSION: 2, CLL: 1, BIOPSY: 0 |
| 17 | FEVER, NEUROPATHOLOGIST, DEFICIENT MISMATCH REPAIR | FEVER: 2, NEUROPATHOLOGIST: 0, DEFICIENT MISMATCH REPAIR: 1 |
| 18 | COLONOSCOPY, UPPER URINARY TRACT CANCER, RISK ASSESSMENT | COLONOSCOPY: 1, UPPER URINARY TRACT CANCER: 2, RISK ASSESSMENT: 0 |
| 19 | CURE, COMPLETE BLOOD COUNT AND DIFFERENTIAL, FOLLOW-UP TESTING | CURE: 2, COMPLETE BLOOD COUNT AND DIFFERENTIAL: 0, FOLLOW-UP TESTING: 1 |
| 20 | FDG PET-CT, SKIN CANCER, LARYNGEAL CANCER | FDG PET-CT: 0, SKIN CANCER: 2, LARYNGEAL CANCER: 1 |
| 21 | FATIGUE, ALKALINE PHOSPHATASE TEST, ESOPHAGOSCOPY | FATIGUE: 0, ALKALINE PHOSPHATASE TEST: 1, ESOPHAGOSCOPY: 2 |
| 22 | PANENDOSCOPY, BLUE LIGHT CYSTOSCOPY, LOCAL THERAPIES | PANENDOSCOPY: 0, BLUE LIGHT CYSTOSCOPY: 1, LOCAL THERAPIES: 2 |
| 23 | RET MUTATIONS, OPEN MRI, NEUROLOGICAL EXAM | RET MUTATIONS: 2, OPEN MRI: 1, NEUROLOGICAL EXAM: 0 |
| 24 | CYSTOSCOPY AND IMAGING, ABDOMINAL SURGERY, TRANSABDOMINAL ULTRASOUND | CYSTOSCOPY AND IMAGING: 2, ABDOMINAL SURGERY: 1, TRANSABDOMINAL ULTRASOUND: 0 |
| 25 | ENDOCRINE THERAPY, COLONOSCOPY, FIBEROPTIC LARYNGOSCOPY | ENDOCRINE THERAPY: 1, COLONOSCOPY: unqueried, FIBEROPTIC LARYNGOSCOPY: 0 |
| 26 | PSA TEST, RADIATION THERAPY, CHRONIC HEPATITIS | PSA TEST: 0, RADIATION THERAPY: 1, CHRONIC HEPATITIS: 2 |
| 27 | SURGERY, PET-CT, PET/CT SCAN | SURGERY: unqueried, PET-CT: 1, PET/CT SCAN: 0 |

## Protocol acceptance

| Criterion | Value | Threshold | Passed |
|---|---:|---:|---|
| query_unique_rate | 1.0000 | 0.9000 | yes |
| zero_gain_rate | 0.0800 | 0.2000 | yes |
| max_consecutive_zero_gain | 2.0000 | 4.0000 | yes |
| max_consecutive_meaningful_zero_gain | 2.0000 | 4.0000 | yes |
| anchor_query_adherence_rate | 1.0000 | 1.0000 | yes |
| both_post_seed_modes_observed | 1.0000 | 1.0000 | yes |
| nonempty_main_response_rate | 1.0000 | 1.0000 | yes |

All formal acceptance criteria passed: yes.

HTSN is scored against the graph snapshot before each batch. RTSN is computed after the merge, and their difference is reported as retrospective gain. GraphRAG truth does not expose a structured relation type, so truth edge metrics use directed endpoint pairs; extraction novelty still uses relation triples.
