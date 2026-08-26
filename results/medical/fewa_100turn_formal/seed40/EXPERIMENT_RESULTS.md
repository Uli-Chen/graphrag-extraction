# Medical extraction results

- Run: `scratch_medical_ts_pl_fewa_100turn_seed40_20260822`
- Turns: 100
- Recovered graph: 973 nodes / 1766 relation triples
- Node precision: 0.8253
- Node recall: 0.6817
- Directed edge-pair precision: 0.9445
- Directed edge-pair recall: 0.5476
- Node TSC (rank): 0.7720
- Edge TSC (rank): 0.5553
- AUTSC, node rank: 0.5553
- AUTSC, edge rank: 0.3294
- Mean HTSN: 0.1901
- Mean count novelty: 0.3770
- Post-seed explore/exploit: 19/80
- Exploit query anchor adherence: 1.0000
- Exploit response anchor adherence: 0.9375

| Turn | Mode | Reason | Anchor | HTSN | Raw reward | Effective FEWA | Anchor response | Node TSC | Edge TSC |
|---:|---|---|---|---:|---:|---:|---|---:|---:|
| 1 | explore | seed_turn | - | 0.0000 | 0.0000 | - | - | 0.0612 | 0.0108 |
| 2 | exploit | fewa(0.2940) | CDC | 0.1338 | 0.0026 | 0.0026 | yes | 0.0629 | 0.0112 |
| 3 | explore | recent_htsn_below_threshold(0.1441) | - | 0.1504 | 0.0247 | - | - | 0.0964 | 0.0211 |
| 4 | exploit | fewa(0.2824) | CDC.GOV/TOBACCO | 0.5861 | 0.1534 | 0.1534 | yes | 0.1159 | 0.0375 |
| 5 | explore | epsilon_sample(0.2767) | - | 0.2281 | 0.0201 | - | - | 0.1358 | 0.0410 |
| 6 | exploit | fewa(0.2712) | TUMOR STAGING | 0.4012 | 0.0525 | 0.0525 | yes | 0.1667 | 0.0513 |
| 7 | exploit | fewa(0.2658) | PATIENT | 0.4739 | 0.0805 | 0.0805 | yes | 0.1964 | 0.0654 |
| 8 | exploit | fewa(0.2604) | METASTASIS | 0.2875 | 0.0225 | 0.0000 | no | 0.2144 | 0.0695 |
| 9 | explore | epsilon_sample(0.2552) | - | 0.4025 | 0.0597 | - | - | 0.2401 | 0.0796 |
| 10 | exploit | fewa(0.2501) | HPV CANCERS ALLIANCE | 0.3013 | 0.0430 | 0.0430 | yes | 0.2509 | 0.0881 |
| 11 | exploit | fewa(0.2451) | INFECTIONS | 0.0296 | 0.0025 | 0.0025 | yes | 0.2603 | 0.0894 |
| 12 | exploit | fewa(0.2402) | ACUTE LYMPHOBLASTIC LEUKEMIA | 0.3396 | 0.0312 | 0.0312 | yes | 0.2820 | 0.0950 |
| 13 | explore | epsilon_sample(0.2354) | - | 0.4133 | 0.0468 | - | - | 0.3021 | 0.1031 |
| 14 | exploit | fewa(0.2307) | AIDS | 0.2119 | 0.0356 | 0.0356 | yes | 0.3216 | 0.1126 |
| 15 | explore | epsilon_sample(0.2261) | - | 0.3064 | 0.0263 | - | - | 0.3287 | 0.1171 |
| 16 | exploit | fewa(0.2216) | CLINICAL TRIAL | 0.3221 | 0.0403 | 0.0403 | yes | 0.3423 | 0.1273 |
| 17 | exploit | fewa(0.2171) | GENETIC RISK TESTING | 0.4547 | 0.0906 | 0.0906 | yes | 0.3644 | 0.1448 |
| 18 | exploit | fewa(0.2128) | HEMATURIA | 0.2869 | 0.0684 | 0.0684 | yes | 0.3979 | 0.1608 |
| 19 | exploit | fewa(0.2085) | IMAGING TEST | 0.4237 | 0.0538 | 0.0538 | yes | 0.4043 | 0.1685 |
| 20 | explore | epsilon_sample(0.2044) | - | 0.3889 | 0.0471 | - | - | 0.4144 | 0.1778 |
| 21 | exploit | fewa(0.2003) | BIOMARKER TESTING | 0.3427 | 0.0736 | 0.0736 | yes | 0.4318 | 0.1923 |
| 22 | explore | epsilon_sample(0.1963) | - | 0.2699 | 0.0221 | - | - | 0.4403 | 0.1964 |
| 23 | exploit | fewa(0.1924) | MOLECULAR TESTING | 0.0402 | 0.0069 | 0.0069 | yes | 0.4408 | 0.1978 |
| 24 | explore | epsilon_sample(0.1885) | - | 0.3002 | 0.0457 | - | - | 0.4466 | 0.2059 |
| 25 | exploit | fewa(0.1847) | BREAST CANCER | 0.0865 | 0.0209 | 0.0000 | no | 0.4490 | 0.2101 |
| 26 | exploit | fewa(0.1810) | NCCN CANCER CENTERS | 0.0377 | 0.0024 | 0.0024 | yes | 0.4508 | 0.2105 |
| 27 | exploit | fewa(0.1774) | NARROW-BAND IMAGING | 0.3615 | 0.0459 | 0.0459 | yes | 0.4674 | 0.2196 |
| 28 | explore | epsilon_sample(0.1739) | - | 0.2967 | 0.0464 | - | - | 0.4830 | 0.2305 |
| 29 | exploit | fewa(0.1704) | GENETIC CANCER RISK TESTING | 0.0000 | 0.0000 | 0.0000 | yes | 0.4836 | 0.2305 |
| 30 | exploit | fewa(0.1670) | TESTING FOR BREAST CANCER | 0.1481 | 0.0295 | 0.0295 | yes | 0.4870 | 0.2360 |
| 31 | exploit | fewa(0.1636) | TESTING FOR BREAST CANCER | 0.0000 | 0.0000 | 0.0000 | yes | 0.4870 | 0.2360 |
| 32 | exploit | fewa(0.1604) | RADIATION THERAPY | 0.3094 | 0.0326 | 0.0326 | yes | 0.4939 | 0.2424 |
| 33 | exploit | fewa(0.1572) | HEMATOPATHOLOGIST | 0.2741 | 0.0401 | 0.0401 | yes | 0.5053 | 0.2506 |
| 34 | explore | epsilon_sample(0.1540) | - | 0.3007 | 0.0658 | - | - | 0.5164 | 0.2635 |
| 35 | exploit | fewa(0.1509) | NEUROPATHOLOGIST | 0.3442 | 0.0417 | 0.0417 | yes | 0.5249 | 0.2723 |
| 36 | exploit | fewa(0.1479) | BLOOD TESTS | 0.3634 | 0.0490 | 0.0490 | yes | 0.5326 | 0.2806 |
| 37 | exploit | fewa(0.1450) | NICOTINE WITHDRAWAL | 0.0123 | 0.0024 | 0.0024 | yes | 0.5326 | 0.2813 |
| 38 | exploit | fewa(0.1421) | MRI SCAN | 0.3902 | 0.0671 | 0.0671 | yes | 0.5410 | 0.2942 |
| 39 | exploit | fewa(0.1392) | HISTOLOGY | 0.2076 | 0.0235 | 0.0235 | yes | 0.5459 | 0.2980 |
| 40 | exploit | fewa(0.1364) | SMOKEFREE.GOV | 0.0000 | 0.0000 | 0.0000 | yes | 0.5459 | 0.2980 |
| 41 | exploit | fewa(0.1337) | HISTOLOGY | 0.0785 | 0.0090 | 0.0090 | yes | 0.5593 | 0.3005 |
| 42 | exploit | fewa(0.1310) | CHEMOTHERAPY | 0.2367 | 0.0259 | 0.0259 | yes | 0.5682 | 0.3054 |
| 43 | explore | epsilon_sample(0.1284) | - | 0.0844 | 0.0137 | - | - | 0.5705 | 0.3080 |
| 44 | exploit | fewa(0.1258) | COMBINATION REGIMEN | 0.2213 | 0.0160 | 0.0160 | yes | 0.5705 | 0.3111 |
| 45 | exploit | fewa(0.1233) | POLYPECTOMY | 0.1722 | 0.0303 | 0.0303 | yes | 0.5778 | 0.3194 |
| 46 | exploit | fewa(0.1209) | CERVICAL CANCER | 0.2347 | 0.0206 | 0.0206 | yes | 0.5868 | 0.3257 |
| 47 | explore | epsilon_sample(0.1184) | - | 0.2211 | 0.0194 | - | - | 0.5915 | 0.3290 |
| 48 | exploit | fewa(0.1161) | DUCTAL CARCINOMA IN SITU | 0.2916 | 0.0524 | 0.0524 | yes | 0.5976 | 0.3385 |
| 49 | explore | epsilon_sample(0.1138) | - | 0.0602 | 0.0056 | - | - | 0.6011 | 0.3400 |
| 50 | exploit | fewa(0.1115) | NPC STAGING | 0.0501 | 0.0067 | 0.0067 | yes | 0.6014 | 0.3420 |
| 51 | exploit | fewa(0.1093) | HPV | 0.0712 | 0.0081 | 0.0081 | yes | 0.6014 | 0.3429 |
| 52 | explore | epsilon_sample(0.1071) | - | 0.0000 | 0.0000 | - | - | 0.6014 | 0.3429 |
| 53 | exploit | fewa(0.1049) | HEREDITARY GENE TESTING | 0.1041 | 0.0203 | 0.0203 | yes | 0.6014 | 0.3470 |
| 54 | exploit | fewa(0.1028) | BLOOD UREA NITROGEN | 0.1365 | 0.0323 | 0.0323 | yes | 0.6079 | 0.3559 |
| 55 | exploit | fewa(0.1008) | OVARIAN CANCER | 0.1946 | 0.0167 | 0.0167 | yes | 0.6122 | 0.3590 |
| 56 | exploit | fewa(0.0988) | FATIGUE | 0.2237 | 0.0524 | 0.0524 | yes | 0.6200 | 0.3698 |
| 57 | exploit | fewa(0.0968) | CYTOLOGY | 0.0129 | 0.0022 | 0.0022 | yes | 0.6200 | 0.3705 |
| 58 | exploit | fewa(0.0948) | PLATINUM-BASED CHEMOTHERAPY | 0.2039 | 0.0227 | 0.0227 | yes | 0.6232 | 0.3764 |
| 59 | exploit | fewa(0.0929) | TECHNOLOGIST | 0.1577 | 0.0317 | 0.0317 | yes | 0.6264 | 0.3825 |
| 60 | exploit | fewa(0.0911) | HIGH-GRADE CANCER | 0.2014 | 0.0130 | 0.0130 | yes | 0.6303 | 0.3849 |
| 61 | explore | epsilon_sample(0.0893) | - | 0.3081 | 0.0614 | - | - | 0.6379 | 0.3955 |
| 62 | explore | epsilon_sample(0.0875) | - | 0.1803 | 0.0141 | - | - | 0.6403 | 0.3985 |
| 63 | exploit | fewa(0.0857) | PREGNANCY | 0.2586 | 0.0606 | 0.0606 | yes | 0.6534 | 0.4102 |
| 64 | exploit | fewa(0.0840) | TNM SCORES | 0.1119 | 0.0135 | 0.0135 | yes | 0.6539 | 0.4132 |
| 65 | exploit | fewa(0.0823) | BLACK MALES | 0.1605 | 0.0248 | 0.0248 | yes | 0.6645 | 0.4178 |
| 66 | exploit | fewa(0.0807) | FOLLOW-UP AND SURVEILLANCE | 0.3096 | 0.0647 | 0.0647 | yes | 0.6780 | 0.4299 |
| 67 | exploit | fewa(0.0791) | TESTING FOR NPC | 0.0829 | 0.0155 | 0.0155 | yes | 0.6780 | 0.4329 |
| 68 | exploit | fewa(0.0775) | SURVIVORSHIP CARE FOR HEALTHY LIVING | 0.0129 | 0.0015 | 0.0015 | yes | 0.6780 | 0.4332 |
| 69 | exploit | fewa(0.0759) | NEUROSURGEON | 0.0414 | 0.0093 | 0.0093 | yes | 0.6805 | 0.4350 |
| 70 | explore | epsilon_sample(0.0744) | - | 0.0518 | 0.0105 | - | - | 0.6828 | 0.4376 |
| 71 | exploit | fewa(0.0729) | GERMLINE MUTATION | 0.0842 | 0.0107 | 0.0107 | yes | 0.6849 | 0.4395 |
| 72 | exploit | fewa(0.0715) | EXTRAFASCIAL HYSTERECTOMY WITH LYMPH NODE EVALUATION | 0.3707 | 0.0572 | 0.0572 | yes | 0.7022 | 0.4523 |
| 73 | exploit | fewa(0.0700) | BREAST CANCER SCREENING | 0.0300 | 0.0038 | 0.0038 | yes | 0.7022 | 0.4530 |
| 74 | exploit | fewa(0.0686) | STAGE 1A1 CERVICAL CANCER | 0.1884 | 0.0291 | 0.0291 | yes | 0.7037 | 0.4598 |
| 75 | exploit | fewa(0.0673) | STAGE 1A1 CERVICAL CANCER | 0.0826 | 0.0085 | 0.0085 | yes | 0.7047 | 0.4612 |
| 76 | exploit | fewa(0.0659) | TREATMENT TEAM | 0.2083 | 0.0163 | 0.0000 | no | 0.7141 | 0.4650 |
| 77 | exploit | fewa(0.0646) | TESTING | 0.0000 | 0.0000 | 0.0000 | no | 0.7141 | 0.4650 |
| 78 | exploit | fewa(0.0633) | BREASTFEEDING | 0.0901 | 0.0153 | 0.0153 | yes | 0.7153 | 0.4688 |
| 79 | exploit | fewa(0.0621) | MRI | 0.1209 | 0.0262 | 0.0262 | yes | 0.7155 | 0.4698 |
| 80 | exploit | fewa(0.0608) | MULTIDISCIPLINARY CARE | 0.2488 | 0.0204 | 0.0204 | yes | 0.7186 | 0.4733 |
| 81 | exploit | fewa(0.0596) | LUMBAR PUNCTURE | 0.2111 | 0.0445 | 0.0445 | yes | 0.7236 | 0.4830 |
| 82 | exploit | fewa(0.0584) | BLADDER CANCER | 0.2619 | 0.0563 | 0.0563 | yes | 0.7318 | 0.4963 |
| 83 | exploit | fewa(0.0572) | PET SCAN | 0.3811 | 0.0499 | 0.0499 | yes | 0.7400 | 0.5055 |
| 84 | exploit | fewa(0.0561) | PRIMARY CNS LYMPHOMA IN THE EYES | 0.2771 | 0.0520 | 0.0520 | yes | 0.7430 | 0.5157 |
| 85 | exploit | fewa(0.0550) | DOCTOR | 0.2968 | 0.0580 | 0.0580 | yes | 0.7462 | 0.5265 |
| 86 | exploit | fewa(0.0539) | BONE MARROW ASPIRATE | 0.1254 | 0.0291 | 0.0291 | yes | 0.7488 | 0.5319 |
| 87 | exploit | fewa(0.0528) | HEMATOLOGIST | 0.0363 | 0.0072 | 0.0072 | yes | 0.7497 | 0.5332 |
| 88 | exploit | fewa(0.0517) | ENDORECTAL ULTRASOUND | 0.0000 | 0.0000 | 0.0000 | yes | 0.7517 | 0.5332 |
| 89 | exploit | fewa(0.0507) | CARCINOMA | 0.0000 | 0.0000 | 0.0000 | no | 0.7517 | 0.5332 |
| 90 | exploit | fewa(0.0500) | CANCER CARE TEAM | 0.4547 | 0.0480 | 0.0480 | yes | 0.7517 | 0.5346 |
| 91 | exploit | fewa(0.0500) | BASAL CELL SKIN CANCER | 0.2465 | 0.0284 | 0.0284 | yes | 0.7590 | 0.5408 |
| 92 | exploit | fewa(0.0500) | CERVICAL DYSPLASIA | 0.0169 | 0.0019 | 0.0019 | yes | 0.7590 | 0.5411 |
| 93 | exploit | fewa(0.0500) | FATIGUE | 0.0335 | 0.0083 | 0.0083 | yes | 0.7590 | 0.5428 |
| 94 | exploit | fewa(0.0500) | RECTAL CANCER | 0.0643 | 0.0118 | 0.0118 | yes | 0.7599 | 0.5449 |
| 95 | explore | epsilon_sample(0.0500) | - | 0.0000 | 0.0000 | - | - | 0.7619 | 0.5449 |
| 96 | exploit | fewa(0.0500) | DUCTAL CARCINOMA | 0.0000 | 0.0000 | 0.0000 | yes | 0.7619 | 0.5449 |
| 97 | explore | recent_htsn_below_threshold(0.0250) | - | 0.1255 | 0.0132 | - | - | 0.7643 | 0.5474 |
| 98 | exploit | fewa(0.0500) | EXTRAFASCIAL HYSTERECTOMY WITH LYMPH NODE EVALUATION | 0.1502 | 0.0285 | 0.0285 | yes | 0.7711 | 0.5537 |
| 99 | exploit | fewa(0.0500) | ADOLESCENT AND YOUNG ADULT | 0.0000 | 0.0000 | 0.0000 | yes | 0.7714 | 0.5537 |
| 100 | exploit | fewa(0.0500) | ONCOLOGY NURSE | 0.2036 | 0.0091 | 0.0091 | yes | 0.7720 | 0.5553 |

## Arm-policy diagnostics

- Policy: `topology_pl_fewa`
- Epochs: 27
- Unique admitted / selected arms: 76 / 75
- Selected arms: ACUTE LYMPHOBLASTIC LEUKEMIA, ADOLESCENT AND YOUNG ADULT, AIDS, BASAL CELL SKIN CANCER, BIOMARKER TESTING, BLACK MALES, BLADDER CANCER, BLOOD TESTS, BLOOD UREA NITROGEN, BONE MARROW ASPIRATE, BREAST CANCER, BREAST CANCER SCREENING, BREASTFEEDING, CANCER CARE TEAM, CARCINOMA, CDC, CDC.GOV/TOBACCO, CERVICAL CANCER, CERVICAL DYSPLASIA, CHEMOTHERAPY, CLINICAL TRIAL, COMBINATION REGIMEN, CYTOLOGY, DOCTOR, DUCTAL CARCINOMA, DUCTAL CARCINOMA IN SITU, ENDORECTAL ULTRASOUND, EXTRAFASCIAL HYSTERECTOMY WITH LYMPH NODE EVALUATION, FATIGUE, FOLLOW-UP AND SURVEILLANCE, GENETIC CANCER RISK TESTING, GENETIC RISK TESTING, GERMLINE MUTATION, HEMATOLOGIST, HEMATOPATHOLOGIST, HEMATURIA, HEREDITARY GENE TESTING, HIGH-GRADE CANCER, HISTOLOGY, HPV, HPV CANCERS ALLIANCE, IMAGING TEST, INFECTIONS, LUMBAR PUNCTURE, METASTASIS, MOLECULAR TESTING, MRI, MRI SCAN, MULTIDISCIPLINARY CARE, NARROW-BAND IMAGING, NCCN CANCER CENTERS, NEUROPATHOLOGIST, NEUROSURGEON, NICOTINE WITHDRAWAL, NPC STAGING, ONCOLOGY NURSE, OVARIAN CANCER, PATIENT, PET SCAN, PLATINUM-BASED CHEMOTHERAPY, POLYPECTOMY, PREGNANCY, PRIMARY CNS LYMPHOMA IN THE EYES, RADIATION THERAPY, RECTAL CANCER, SMOKEFREE.GOV, STAGE 1A1 CERVICAL CANCER, SURVIVORSHIP CARE FOR HEALTHY LIVING, TECHNOLOGIST, TESTING, TESTING FOR BREAST CANCER, TESTING FOR NPC, TNM SCORES, TREATMENT TEAM, TUMOR STAGING
- Mean admission-to-first-query delay: 0.9481
- Unqueried admitted slots: 4
- Mean epoch arm-set turnover: 1.0000

| Epoch | Active arms | Admission-to-first-query delay |
|---:|---|---|
| 1 | CDC.GOV/TOBACCO, CDC, TUMOR STAGING | CDC.GOV/TOBACCO: 1, CDC: 0, TUMOR STAGING: 2 |
| 2 | METASTASIS, HPV CANCERS ALLIANCE, PATIENT | METASTASIS: 1, HPV CANCERS ALLIANCE: 2, PATIENT: 0 |
| 3 | ACUTE LYMPHOBLASTIC LEUKEMIA, INFECTIONS, AIDS | ACUTE LYMPHOBLASTIC LEUKEMIA: 1, INFECTIONS: 0, AIDS: 2 |
| 4 | CLINICAL TRIAL, GENETIC RISK TESTING, HEMATURIA | CLINICAL TRIAL: 0, GENETIC RISK TESTING: 1, HEMATURIA: 2 |
| 5 | MOLECULAR TESTING, BIOMARKER TESTING, IMAGING TEST | MOLECULAR TESTING: 2, BIOMARKER TESTING: 1, IMAGING TEST: 0 |
| 6 | NARROW-BAND IMAGING, NCCN CANCER CENTERS, BREAST CANCER | NARROW-BAND IMAGING: 2, NCCN CANCER CENTERS: 1, BREAST CANCER: 0 |
| 7 | GENETIC CANCER RISK TESTING, METASTASIS, TESTING FOR BREAST CANCER | GENETIC CANCER RISK TESTING: 0, METASTASIS: unqueried, TESTING FOR BREAST CANCER: 1 |
| 8 | HEMATOPATHOLOGIST, NEUROPATHOLOGIST, RADIATION THERAPY | HEMATOPATHOLOGIST: 1, NEUROPATHOLOGIST: 2, RADIATION THERAPY: 0 |
| 9 | NICOTINE WITHDRAWAL, MRI SCAN, BLOOD TESTS | NICOTINE WITHDRAWAL: 1, MRI SCAN: 2, BLOOD TESTS: 0 |
| 10 | HISTOLOGY, SMOKEFREE.GOV, NCCN CANCER CENTERS | HISTOLOGY: 0, SMOKEFREE.GOV: 1, NCCN CANCER CENTERS: unqueried |
| 11 | POLYPECTOMY, CHEMOTHERAPY, COMBINATION REGIMEN | POLYPECTOMY: 2, CHEMOTHERAPY: 0, COMBINATION REGIMEN: 1 |
| 12 | DUCTAL CARCINOMA IN SITU, CERVICAL CANCER, NPC STAGING | DUCTAL CARCINOMA IN SITU: 1, CERVICAL CANCER: 0, NPC STAGING: 2 |
| 13 | HEREDITARY GENE TESTING, HPV, BLOOD UREA NITROGEN | HEREDITARY GENE TESTING: 1, HPV: 0, BLOOD UREA NITROGEN: 2 |
| 14 | CYTOLOGY, OVARIAN CANCER, FATIGUE | CYTOLOGY: 2, OVARIAN CANCER: 0, FATIGUE: 1 |
| 15 | PLATINUM-BASED CHEMOTHERAPY, HIGH-GRADE CANCER, TECHNOLOGIST | PLATINUM-BASED CHEMOTHERAPY: 0, HIGH-GRADE CANCER: 2, TECHNOLOGIST: 1 |
| 16 | TNM SCORES, BLACK MALES, PREGNANCY | TNM SCORES: 1, BLACK MALES: 2, PREGNANCY: 0 |
| 17 | SURVIVORSHIP CARE FOR HEALTHY LIVING, TESTING FOR NPC, FOLLOW-UP AND SURVEILLANCE | SURVIVORSHIP CARE FOR HEALTHY LIVING: 2, TESTING FOR NPC: 1, FOLLOW-UP AND SURVEILLANCE: 0 |
| 18 | GERMLINE MUTATION, EXTRAFASCIAL HYSTERECTOMY WITH LYMPH NODE EVALUATION, NEUROSURGEON | GERMLINE MUTATION: 1, EXTRAFASCIAL HYSTERECTOMY WITH LYMPH NODE EVALUATION: 2, NEUROSURGEON: 0 |
| 19 | BREAST CANCER SCREENING, STAGE 1A1 CERVICAL CANCER, PLATINUM-BASED CHEMOTHERAPY | BREAST CANCER SCREENING: 0, STAGE 1A1 CERVICAL CANCER: 1, PLATINUM-BASED CHEMOTHERAPY: unqueried |
| 20 | TESTING, TREATMENT TEAM, BREASTFEEDING | TESTING: 1, TREATMENT TEAM: 0, BREASTFEEDING: 2 |
| 21 | MRI, MULTIDISCIPLINARY CARE, LUMBAR PUNCTURE | MRI: 0, MULTIDISCIPLINARY CARE: 1, LUMBAR PUNCTURE: 2 |
| 22 | PRIMARY CNS LYMPHOMA IN THE EYES, BLADDER CANCER, PET SCAN | PRIMARY CNS LYMPHOMA IN THE EYES: 2, BLADDER CANCER: 0, PET SCAN: 1 |
| 23 | HEMATOLOGIST, DOCTOR, BONE MARROW ASPIRATE | HEMATOLOGIST: 2, DOCTOR: 0, BONE MARROW ASPIRATE: 1 |
| 24 | ENDORECTAL ULTRASOUND, CANCER CARE TEAM, CARCINOMA | ENDORECTAL ULTRASOUND: 0, CANCER CARE TEAM: 2, CARCINOMA: 1 |
| 25 | BASAL CELL SKIN CANCER, FATIGUE, CERVICAL DYSPLASIA | BASAL CELL SKIN CANCER: 0, FATIGUE: 2, CERVICAL DYSPLASIA: 1 |
| 26 | EXTRAFASCIAL HYSTERECTOMY WITH LYMPH NODE EVALUATION, DUCTAL CARCINOMA, RECTAL CANCER | EXTRAFASCIAL HYSTERECTOMY WITH LYMPH NODE EVALUATION: 2, DUCTAL CARCINOMA: 1, RECTAL CANCER: 0 |
| 27 | PERFORMANCE STATUS ASSESSMENT, ADOLESCENT AND YOUNG ADULT, ONCOLOGY NURSE | PERFORMANCE STATUS ASSESSMENT: unqueried, ADOLESCENT AND YOUNG ADULT: 0, ONCOLOGY NURSE: 1 |

## Protocol acceptance

| Criterion | Value | Threshold | Passed |
|---|---:|---:|---|
| query_unique_rate | 1.0000 | 0.9000 | yes |
| zero_gain_rate | 0.0500 | 0.2000 | yes |
| max_consecutive_zero_gain | 1.0000 | 4.0000 | yes |
| max_consecutive_meaningful_zero_gain | 2.0000 | 4.0000 | yes |
| anchor_query_adherence_rate | 1.0000 | 1.0000 | yes |
| both_post_seed_modes_observed | 1.0000 | 1.0000 | yes |
| nonempty_main_response_rate | 1.0000 | 1.0000 | yes |

All formal acceptance criteria passed: yes.

HTSN is scored against the graph snapshot before each batch. RTSN is computed after the merge, and their difference is reported as retrospective gain. GraphRAG truth does not expose a structured relation type, so truth edge metrics use directed endpoint pairs; extraction novelty still uses relation triples.
