# Medical extraction results

- Run: `scratch_medical_ts_pl_fewa_100turn_seed42_20260822`
- Turns: 100
- Recovered graph: 898 nodes / 1635 relation triples
- Node precision: 0.8664
- Node recall: 0.6604
- Directed edge-pair precision: 0.9333
- Directed edge-pair recall: 0.5010
- Node TSC (rank): 0.7444
- Edge TSC (rank): 0.5074
- AUTSC, node rank: 0.5091
- AUTSC, edge rank: 0.2898
- Mean HTSN: 0.1527
- Mean count novelty: 0.3004
- Post-seed explore/exploit: 21/78
- Exploit query anchor adherence: 1.0000
- Exploit response anchor adherence: 0.9103

| Turn | Mode | Reason | Anchor | HTSN | Raw reward | Effective FEWA | Anchor response | Node TSC | Edge TSC |
|---:|---|---|---|---:|---:|---:|---|---:|---:|
| 1 | explore | seed_turn | - | 0.0000 | 0.0000 | - | - | 0.0612 | 0.0108 |
| 2 | exploit | fewa(0.2940) | DIAGNOSTIC TESTS | 0.1562 | 0.0214 | 0.0214 | yes | 0.0842 | 0.0155 |
| 3 | explore | epsilon_sample(0.2881) | - | 0.0574 | 0.0053 | - | - | 0.1096 | 0.0220 |
| 4 | explore | recent_htsn_below_threshold(0.1412) | - | 0.1909 | 0.0451 | - | - | 0.1658 | 0.0431 |
| 5 | explore | recent_htsn_below_threshold(0.1384) | - | 0.2775 | 0.0309 | - | - | 0.1769 | 0.0501 |
| 6 | exploit | fewa(0.2712) | MEDICAL HISTORY AND PHYSICAL EXAM (H&P) | 0.2304 | 0.0531 | 0.0531 | yes | 0.1997 | 0.0632 |
| 7 | explore | epsilon_sample(0.2658) | - | 0.3270 | 0.0549 | - | - | 0.2087 | 0.0733 |
| 8 | exploit | fewa(0.2604) | TUMOR STAGING | 0.3731 | 0.0532 | 0.0532 | yes | 0.2380 | 0.0837 |
| 9 | exploit | fewa(0.2552) | DIAGNOSTIC TESTING | 0.0481 | 0.0088 | 0.0000 | no | 0.2425 | 0.0857 |
| 10 | exploit | fewa(0.2501) | SIDE EFFECTS | 0.0692 | 0.0116 | 0.0116 | yes | 0.2432 | 0.0881 |
| 11 | explore | epsilon_sample(0.2451) | - | 0.0000 | 0.0000 | - | - | 0.2432 | 0.0881 |
| 12 | exploit | fewa(0.2402) | MEDICAL TEAM | 0.3261 | 0.0420 | 0.0000 | no | 0.2501 | 0.0959 |
| 13 | explore | epsilon_sample(0.2354) | - | 0.0000 | 0.0000 | - | - | 0.2534 | 0.0959 |
| 14 | explore | recent_htsn_below_threshold(0.1154) | - | 0.2445 | 0.0272 | - | - | 0.2660 | 0.1016 |
| 15 | explore | epsilon_sample(0.2261) | - | 0.0606 | 0.0125 | - | - | 0.2780 | 0.1069 |
| 16 | exploit | fewa(0.2216) | MEDICAL HISTORY | 0.1024 | 0.0232 | 0.0232 | yes | 0.2835 | 0.1112 |
| 17 | explore | epsilon_sample(0.2171) | - | 0.2638 | 0.0484 | - | - | 0.2943 | 0.1197 |
| 18 | explore | epsilon_sample(0.2128) | - | 0.2180 | 0.0392 | - | - | 0.3088 | 0.1269 |
| 19 | exploit | fewa(0.2085) | TARGETED THERAPY | 0.1827 | 0.0310 | 0.0310 | yes | 0.3131 | 0.1320 |
| 20 | exploit | fewa(0.2044) | BLACK PEOPLE | 0.4238 | 0.0141 | 0.0141 | yes | 0.3153 | 0.1343 |
| 21 | exploit | fewa(0.2003) | HEPATITIS C | 0.0703 | 0.0161 | 0.0161 | yes | 0.3217 | 0.1378 |
| 22 | exploit | fewa(0.1963) | MEDICAL PROVIDERS | 0.1239 | 0.0281 | 0.0281 | yes | 0.3352 | 0.1435 |
| 23 | exploit | fewa(0.1924) | SERIOUS BLOOD CLOTS | 0.1068 | 0.0215 | 0.0215 | yes | 0.3446 | 0.1486 |
| 24 | explore | epsilon_sample(0.1885) | - | 0.4591 | 0.1004 | - | - | 0.3660 | 0.1562 |
| 25 | exploit | fewa(0.1847) | CANCER STAGING | 0.1744 | 0.0225 | 0.0225 | yes | 0.3685 | 0.1583 |
| 26 | exploit | fewa(0.1810) | SUPPORTIVE CARE | 0.1547 | 0.0169 | 0.0169 | yes | 0.3690 | 0.1617 |
| 27 | exploit | fewa(0.1774) | LOW BLOOD CELL COUNTS | 0.2974 | 0.0604 | 0.0604 | yes | 0.3935 | 0.1755 |
| 28 | explore | epsilon_sample(0.1739) | - | 0.0757 | 0.0095 | - | - | 0.3951 | 0.1775 |
| 29 | exploit | fewa(0.1704) | ADVANCED-STAGE PROSTATE CANCER | 0.1006 | 0.0155 | 0.0155 | yes | 0.4039 | 0.1807 |
| 30 | exploit | fewa(0.1670) | GENETIC TEST | 0.2879 | 0.0489 | 0.0489 | yes | 0.4106 | 0.1915 |
| 31 | explore | epsilon_sample(0.1636) | - | 0.3565 | 0.0655 | - | - | 0.4253 | 0.2009 |
| 32 | explore | epsilon_sample(0.1604) | - | 0.3332 | 0.0462 | - | - | 0.4319 | 0.2094 |
| 33 | exploit | fewa(0.1572) | MISMATCH REPAIR | 0.0991 | 0.0149 | 0.0149 | yes | 0.4328 | 0.2126 |
| 34 | exploit | fewa(0.1540) | CLL | 0.2546 | 0.0681 | 0.0681 | yes | 0.4470 | 0.2260 |
| 35 | exploit | fewa(0.1509) | HEALTH CARE PROVIDER | 0.0244 | 0.0029 | 0.0029 | yes | 0.4506 | 0.2267 |
| 36 | exploit | fewa(0.1479) | LYNCH SYNDROME | 0.1411 | 0.0273 | 0.0273 | yes | 0.4519 | 0.2306 |
| 37 | exploit | fewa(0.1450) | CANCER TREATMENT | 0.3960 | 0.0526 | 0.0000 | no | 0.4674 | 0.2408 |
| 38 | exploit | fewa(0.1421) | TREATMENT | 0.0000 | 0.0000 | 0.0000 | yes | 0.4674 | 0.2408 |
| 39 | exploit | fewa(0.1392) | MEDICAL ONCOLOGIST | 0.1617 | 0.0073 | 0.0073 | yes | 0.4700 | 0.2418 |
| 40 | exploit | fewa(0.1364) | BLOOD TESTS | 0.2935 | 0.0688 | 0.0688 | yes | 0.4803 | 0.2545 |
| 41 | exploit | fewa(0.1337) | SUPPORT GROUPS | 0.1452 | 0.0408 | 0.0408 | yes | 0.4904 | 0.2608 |
| 42 | exploit | fewa(0.1310) | PET | 0.3464 | 0.0291 | 0.0000 | no | 0.5071 | 0.2649 |
| 43 | exploit | fewa(0.1284) | HEREDITARY GENE TESTING | 0.1077 | 0.0223 | 0.0223 | yes | 0.5089 | 0.2690 |
| 44 | exploit | fewa(0.1258) | DEEP VEIN THROMBOSIS | 0.0978 | 0.0227 | 0.0227 | yes | 0.5175 | 0.2732 |
| 45 | exploit | fewa(0.1233) | QUITTING SMOKING | 0.2931 | 0.0550 | 0.0550 | yes | 0.5191 | 0.2865 |
| 46 | explore | epsilon_sample(0.1209) | - | 0.0930 | 0.0165 | - | - | 0.5254 | 0.2903 |
| 47 | exploit | fewa(0.1184) | FAMILY HISTORY | 0.1437 | 0.0269 | 0.0269 | yes | 0.5259 | 0.2903 |
| 48 | exploit | fewa(0.1161) | COMPLETE BLOOD COUNT AND DIFFERENTIAL | 0.0741 | 0.0146 | 0.0146 | yes | 0.5281 | 0.2927 |
| 49 | explore | epsilon_sample(0.1138) | - | 0.0000 | 0.0000 | - | - | 0.5295 | 0.2927 |
| 50 | exploit | fewa(0.1115) | B SYMPTOMS | 0.0000 | 0.0000 | 0.0000 | yes | 0.5295 | 0.2927 |
| 51 | explore | epsilon_sample(0.1093) | - | 0.2431 | 0.0432 | - | - | 0.5319 | 0.3005 |
| 52 | exploit | fewa(0.1071) | ACUTE LYMPHOBLASTIC LEUKEMIA | 0.0212 | 0.0023 | 0.0023 | yes | 0.5322 | 0.3008 |
| 53 | exploit | fewa(0.1049) | HEART TESTS | 0.1027 | 0.0247 | 0.0247 | yes | 0.5372 | 0.3060 |
| 54 | exploit | fewa(0.1028) | TMB-H | 0.0182 | 0.0033 | 0.0033 | yes | 0.5388 | 0.3066 |
| 55 | exploit | fewa(0.1008) | GENETIC TESTS | 0.0000 | 0.0000 | 0.0000 | yes | 0.5388 | 0.3066 |
| 56 | exploit | fewa(0.0988) | RICHTER TRANSFORMATION | 0.0000 | 0.0000 | 0.0000 | yes | 0.5400 | 0.3066 |
| 57 | explore | recent_htsn_below_threshold(0.0484) | - | 0.0000 | 0.0000 | - | - | 0.5400 | 0.3066 |
| 58 | explore | recent_htsn_below_threshold(0.0474) | - | 0.3659 | 0.0622 | - | - | 0.5645 | 0.3192 |
| 59 | exploit | fewa(0.0929) | 4KSCORE | 0.2614 | 0.0510 | 0.0510 | yes | 0.5697 | 0.3282 |
| 60 | exploit | fewa(0.0911) | ULTRASOUND | 0.3776 | 0.0487 | 0.0487 | yes | 0.5803 | 0.3368 |
| 61 | exploit | fewa(0.0893) | BRCA MUTATION | 0.0000 | 0.0000 | 0.0000 | yes | 0.5803 | 0.3368 |
| 62 | exploit | fewa(0.0875) | FERTILITY PRESERVATION | 0.3397 | 0.0610 | 0.0610 | yes | 0.6006 | 0.3507 |
| 63 | exploit | fewa(0.0857) | TESTING FOR OVARIAN CANCER | 0.3327 | 0.0435 | 0.0435 | yes | 0.6027 | 0.3587 |
| 64 | exploit | fewa(0.0840) | NATURAL PREGNANCY | 0.1955 | 0.0428 | 0.0428 | yes | 0.6077 | 0.3679 |
| 65 | exploit | fewa(0.0823) | TISSUE TESTS | 0.1920 | 0.0247 | 0.0247 | yes | 0.6110 | 0.3725 |
| 66 | exploit | fewa(0.0807) | BIOPSY | 0.0787 | 0.0105 | 0.0105 | yes | 0.6206 | 0.3741 |
| 67 | exploit | fewa(0.0791) | BREAST DEVELOPMENT | 0.3219 | 0.0761 | 0.0761 | yes | 0.6355 | 0.3881 |
| 68 | exploit | fewa(0.0775) | CHECKPOINT INHIBITORS | 0.0000 | 0.0000 | 0.0000 | yes | 0.6355 | 0.3881 |
| 69 | exploit | fewa(0.0759) | FAMILY MEMBERS | 0.0000 | 0.0000 | 0.0000 | yes | 0.6355 | 0.3881 |
| 70 | exploit | fewa(0.0744) | CREATE A MEDICAL BINDER | 0.0143 | 0.0033 | 0.0033 | yes | 0.6376 | 0.3889 |
| 71 | exploit | fewa(0.0729) | NASOPHARYNGEAL CANCER STAGING | 0.3446 | 0.0545 | 0.0545 | yes | 0.6468 | 0.4000 |
| 72 | exploit | fewa(0.0715) | TUMOR TESTING | 0.0975 | 0.0097 | 0.0097 | yes | 0.6502 | 0.4025 |
| 73 | exploit | fewa(0.0700) | CHRONIC HEPATITIS B | 0.0000 | 0.0000 | 0.0000 | yes | 0.6502 | 0.4025 |
| 74 | explore | epsilon_sample(0.0686) | - | 0.0000 | 0.0000 | - | - | 0.6502 | 0.4025 |
| 75 | exploit | fewa(0.0673) | RADICAL TRACHELECTOMY | 0.3719 | 0.0581 | 0.0581 | yes | 0.6762 | 0.4151 |
| 76 | exploit | fewa(0.0659) | COLON CANCER | 0.2588 | 0.0521 | 0.0521 | yes | 0.6920 | 0.4257 |
| 77 | exploit | fewa(0.0646) | FERTILITY-SPARING TREATMENT | 0.0000 | 0.0000 | 0.0000 | yes | 0.6920 | 0.4257 |
| 78 | exploit | fewa(0.0633) | COMPUTED TOMOGRAPHY | 0.3238 | 0.0500 | 0.0000 | no | 0.6978 | 0.4347 |
| 79 | exploit | fewa(0.0621) | EXTRAFASCIAL HYSTERECTOMY | 0.1577 | 0.0286 | 0.0286 | yes | 0.7036 | 0.4406 |
| 80 | exploit | fewa(0.0608) | INFLAMMATION | 0.0000 | 0.0000 | 0.0000 | yes | 0.7036 | 0.4406 |
| 81 | exploit | fewa(0.0596) | RET MUTATIONS | 0.2330 | 0.0519 | 0.0519 | yes | 0.7036 | 0.4406 |
| 82 | exploit | fewa(0.0584) | EXTERNAL BEAM RADIATION THERAPY | 0.2595 | 0.0218 | 0.0000 | no | 0.7123 | 0.4452 |
| 83 | exploit | fewa(0.0572) | EARLY DETECTION | 0.1317 | 0.0316 | 0.0316 | yes | 0.7141 | 0.4519 |
| 84 | exploit | fewa(0.0561) | ALPHA-FETOPROTEIN (AFP) TEST | 0.1310 | 0.0292 | 0.0292 | yes | 0.7159 | 0.4580 |
| 85 | exploit | fewa(0.0550) | BONE MARROW BIOPSY | 0.2166 | 0.0224 | 0.0224 | yes | 0.7181 | 0.4633 |
| 86 | exploit | fewa(0.0539) | LI-FRAUMENI SYNDROME | 0.0766 | 0.0184 | 0.0184 | yes | 0.7221 | 0.4664 |
| 87 | exploit | fewa(0.0528) | ORGAN TRANSPLANT | 0.0000 | 0.0000 | 0.0000 | yes | 0.7221 | 0.4664 |
| 88 | exploit | fewa(0.0517) | NON-ALCOHOLIC FATTY LIVER DISEASE (NAFLD) | 0.0067 | 0.0016 | 0.0016 | yes | 0.7221 | 0.4664 |
| 89 | exploit | fewa(0.0507) | NAUSEA | 0.1055 | 0.0225 | 0.0225 | yes | 0.7235 | 0.4710 |
| 90 | exploit | fewa(0.0500) | RADIOLOGY | 0.2348 | 0.0468 | 0.0468 | yes | 0.7240 | 0.4797 |
| 91 | exploit | fewa(0.0500) | COMPUTED TOMOGRAPHY (CT) SCAN | 0.0616 | 0.0075 | 0.0075 | yes | 0.7243 | 0.4804 |
| 92 | exploit | fewa(0.0500) | ABDOMINAL AND PELVIC EXAM | 0.1901 | 0.0494 | 0.0494 | yes | 0.7339 | 0.4891 |
| 93 | exploit | fewa(0.0500) | TESTS | 0.0000 | 0.0000 | 0.0000 | no | 0.7352 | 0.4891 |
| 94 | exploit | fewa(0.0500) | DOCTOR | 0.1700 | 0.0402 | 0.0402 | yes | 0.7369 | 0.4971 |
| 95 | exploit | fewa(0.0500) | CHRONIC MYELOID LEUKEMIA | 0.0743 | 0.0193 | 0.0193 | yes | 0.7390 | 0.5005 |
| 96 | explore | epsilon_sample(0.0500) | - | 0.0000 | 0.0000 | - | - | 0.7390 | 0.5005 |
| 97 | exploit | fewa(0.0500) | DOCTOR | 0.0089 | 0.0019 | 0.0019 | yes | 0.7401 | 0.5009 |
| 98 | exploit | fewa(0.0500) | PROGNOSIS | 0.0335 | 0.0072 | 0.0072 | yes | 0.7401 | 0.5023 |
| 99 | exploit | fewa(0.0500) | PROLONGED CORRECTED QT INTERVAL | 0.0765 | 0.0105 | 0.0105 | yes | 0.7419 | 0.5042 |
| 100 | exploit | fewa(0.0500) | CARDIOLOGIST | 0.0738 | 0.0143 | 0.0143 | yes | 0.7444 | 0.5074 |

## Arm-policy diagnostics

- Policy: `topology_pl_fewa`
- Epochs: 26
- Unique admitted / selected arms: 77 / 77
- Selected arms: 4KSCORE, ABDOMINAL AND PELVIC EXAM, ACUTE LYMPHOBLASTIC LEUKEMIA, ADVANCED-STAGE PROSTATE CANCER, ALPHA-FETOPROTEIN (AFP) TEST, B SYMPTOMS, BIOPSY, BLACK PEOPLE, BLOOD TESTS, BONE MARROW BIOPSY, BRCA MUTATION, BREAST DEVELOPMENT, CANCER STAGING, CANCER TREATMENT, CARDIOLOGIST, CHECKPOINT INHIBITORS, CHRONIC HEPATITIS B, CHRONIC MYELOID LEUKEMIA, CLL, COLON CANCER, COMPLETE BLOOD COUNT AND DIFFERENTIAL, COMPUTED TOMOGRAPHY, COMPUTED TOMOGRAPHY (CT) SCAN, CREATE A MEDICAL BINDER, DEEP VEIN THROMBOSIS, DIAGNOSTIC TESTING, DIAGNOSTIC TESTS, DOCTOR, EARLY DETECTION, EXTERNAL BEAM RADIATION THERAPY, EXTRAFASCIAL HYSTERECTOMY, FAMILY HISTORY, FAMILY MEMBERS, FERTILITY PRESERVATION, FERTILITY-SPARING TREATMENT, GENETIC TEST, GENETIC TESTS, HEALTH CARE PROVIDER, HEART TESTS, HEPATITIS C, HEREDITARY GENE TESTING, INFLAMMATION, LI-FRAUMENI SYNDROME, LOW BLOOD CELL COUNTS, LYNCH SYNDROME, MEDICAL HISTORY, MEDICAL HISTORY AND PHYSICAL EXAM (H&P), MEDICAL ONCOLOGIST, MEDICAL PROVIDERS, MEDICAL TEAM, MISMATCH REPAIR, NASOPHARYNGEAL CANCER STAGING, NATURAL PREGNANCY, NAUSEA, NON-ALCOHOLIC FATTY LIVER DISEASE (NAFLD), ORGAN TRANSPLANT, PET, PROGNOSIS, PROLONGED CORRECTED QT INTERVAL, QUITTING SMOKING, RADICAL TRACHELECTOMY, RADIOLOGY, RET MUTATIONS, RICHTER TRANSFORMATION, SERIOUS BLOOD CLOTS, SIDE EFFECTS, SUPPORT GROUPS, SUPPORTIVE CARE, TARGETED THERAPY, TESTING FOR OVARIAN CANCER, TESTS, TISSUE TESTS, TMB-H, TREATMENT, TUMOR STAGING, TUMOR TESTING, ULTRASOUND
- Mean admission-to-first-query delay: 0.9870
- Unqueried admitted slots: 1
- Mean epoch arm-set turnover: 1.0000

| Epoch | Active arms | Admission-to-first-query delay |
|---:|---|---|
| 1 | TUMOR STAGING, MEDICAL HISTORY AND PHYSICAL EXAM (H&P), DIAGNOSTIC TESTS | TUMOR STAGING: 2, MEDICAL HISTORY AND PHYSICAL EXAM (H&P): 1, DIAGNOSTIC TESTS: 0 |
| 2 | MEDICAL TEAM, DIAGNOSTIC TESTING, SIDE EFFECTS | MEDICAL TEAM: 2, DIAGNOSTIC TESTING: 0, SIDE EFFECTS: 1 |
| 3 | BLACK PEOPLE, MEDICAL HISTORY, TARGETED THERAPY | BLACK PEOPLE: 2, MEDICAL HISTORY: 0, TARGETED THERAPY: 1 |
| 4 | HEPATITIS C, MEDICAL PROVIDERS, SERIOUS BLOOD CLOTS | HEPATITIS C: 0, MEDICAL PROVIDERS: 1, SERIOUS BLOOD CLOTS: 2 |
| 5 | SUPPORTIVE CARE, LOW BLOOD CELL COUNTS, CANCER STAGING | SUPPORTIVE CARE: 1, LOW BLOOD CELL COUNTS: 2, CANCER STAGING: 0 |
| 6 | GENETIC TEST, MISMATCH REPAIR, ADVANCED-STAGE PROSTATE CANCER | GENETIC TEST: 1, MISMATCH REPAIR: 2, ADVANCED-STAGE PROSTATE CANCER: 0 |
| 7 | HEALTH CARE PROVIDER, LYNCH SYNDROME, CLL | HEALTH CARE PROVIDER: 1, LYNCH SYNDROME: 2, CLL: 0 |
| 8 | TREATMENT, CANCER TREATMENT, MEDICAL ONCOLOGIST | TREATMENT: 1, CANCER TREATMENT: 0, MEDICAL ONCOLOGIST: 2 |
| 9 | BLOOD TESTS, SUPPORT GROUPS, PET | BLOOD TESTS: 0, SUPPORT GROUPS: 1, PET: 2 |
| 10 | DEEP VEIN THROMBOSIS, HEREDITARY GENE TESTING, QUITTING SMOKING | DEEP VEIN THROMBOSIS: 1, HEREDITARY GENE TESTING: 0, QUITTING SMOKING: 2 |
| 11 | FAMILY HISTORY, COMPLETE BLOOD COUNT AND DIFFERENTIAL, B SYMPTOMS | FAMILY HISTORY: 0, COMPLETE BLOOD COUNT AND DIFFERENTIAL: 1, B SYMPTOMS: 2 |
| 12 | TMB-H, ACUTE LYMPHOBLASTIC LEUKEMIA, HEART TESTS | TMB-H: 2, ACUTE LYMPHOBLASTIC LEUKEMIA: 0, HEART TESTS: 1 |
| 13 | 4KSCORE, GENETIC TESTS, RICHTER TRANSFORMATION | 4KSCORE: 2, GENETIC TESTS: 0, RICHTER TRANSFORMATION: 1 |
| 14 | BRCA MUTATION, FERTILITY PRESERVATION, ULTRASOUND | BRCA MUTATION: 1, FERTILITY PRESERVATION: 2, ULTRASOUND: 0 |
| 15 | TISSUE TESTS, NATURAL PREGNANCY, TESTING FOR OVARIAN CANCER | TISSUE TESTS: 2, NATURAL PREGNANCY: 1, TESTING FOR OVARIAN CANCER: 0 |
| 16 | BREAST DEVELOPMENT, CHECKPOINT INHIBITORS, BIOPSY | BREAST DEVELOPMENT: 1, CHECKPOINT INHIBITORS: 2, BIOPSY: 0 |
| 17 | FAMILY MEMBERS, NASOPHARYNGEAL CANCER STAGING, CREATE A MEDICAL BINDER | FAMILY MEMBERS: 0, NASOPHARYNGEAL CANCER STAGING: 2, CREATE A MEDICAL BINDER: 1 |
| 18 | CHRONIC HEPATITIS B, TUMOR TESTING, RADICAL TRACHELECTOMY | CHRONIC HEPATITIS B: 1, TUMOR TESTING: 0, RADICAL TRACHELECTOMY: 2 |
| 19 | COMPUTED TOMOGRAPHY, COLON CANCER, FERTILITY-SPARING TREATMENT | COMPUTED TOMOGRAPHY: 2, COLON CANCER: 0, FERTILITY-SPARING TREATMENT: 1 |
| 20 | EXTRAFASCIAL HYSTERECTOMY, RET MUTATIONS, INFLAMMATION | EXTRAFASCIAL HYSTERECTOMY: 0, RET MUTATIONS: 2, INFLAMMATION: 1 |
| 21 | EXTERNAL BEAM RADIATION THERAPY, ALPHA-FETOPROTEIN (AFP) TEST, EARLY DETECTION | EXTERNAL BEAM RADIATION THERAPY: 0, ALPHA-FETOPROTEIN (AFP) TEST: 2, EARLY DETECTION: 1 |
| 22 | ORGAN TRANSPLANT, BONE MARROW BIOPSY, LI-FRAUMENI SYNDROME | ORGAN TRANSPLANT: 2, BONE MARROW BIOPSY: 0, LI-FRAUMENI SYNDROME: 1 |
| 23 | RADIOLOGY, NON-ALCOHOLIC FATTY LIVER DISEASE (NAFLD), NAUSEA | RADIOLOGY: 2, NON-ALCOHOLIC FATTY LIVER DISEASE (NAFLD): 0, NAUSEA: 1 |
| 24 | COMPUTED TOMOGRAPHY (CT) SCAN, ABDOMINAL AND PELVIC EXAM, TESTS | COMPUTED TOMOGRAPHY (CT) SCAN: 0, ABDOMINAL AND PELVIC EXAM: 1, TESTS: 2 |
| 25 | DOCTOR, CHRONIC MYELOID LEUKEMIA, EXTRAFASCIAL HYSTERECTOMY | DOCTOR: 0, CHRONIC MYELOID LEUKEMIA: 1, EXTRAFASCIAL HYSTERECTOMY: unqueried |
| 26 | PROGNOSIS, PROLONGED CORRECTED QT INTERVAL, CARDIOLOGIST | PROGNOSIS: 0, PROLONGED CORRECTED QT INTERVAL: 1, CARDIOLOGIST: 2 |

## Protocol acceptance

| Criterion | Value | Threshold | Passed |
|---|---:|---:|---|
| query_unique_rate | 1.0000 | 0.9000 | yes |
| zero_gain_rate | 0.1000 | 0.2000 | yes |
| max_consecutive_zero_gain | 2.0000 | 4.0000 | yes |
| max_consecutive_meaningful_zero_gain | 3.0000 | 4.0000 | yes |
| anchor_query_adherence_rate | 1.0000 | 1.0000 | yes |
| both_post_seed_modes_observed | 1.0000 | 1.0000 | yes |
| nonempty_main_response_rate | 1.0000 | 1.0000 | yes |

All formal acceptance criteria passed: yes.

HTSN is scored against the graph snapshot before each batch. RTSN is computed after the merge, and their difference is reported as retrospective gain. GraphRAG truth does not expose a structured relation type, so truth edge metrics use directed endpoint pairs; extraction novelty still uses relation triples.
