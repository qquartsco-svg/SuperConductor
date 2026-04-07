> **한국어 (정본).** English: [README_EN.md](README_EN.md)

# Superconducting Magnet Stack

초전도체 전체를 한 번에 완성하려는 엔진이 아니라,
**초전도 자석의 설계·평가·readiness 판정**에 집중한 L1 독립 스택입니다.

Version: `1.0.0`

한 줄 정의:
**재료(Tc/Jc/Bc2) + 냉각 + 전자기/응력 + quench 위험을 하나의 Ω 판정으로 묶는 설계 커널**.

해석 가이드:
현재 `1.0.0`은 초전도 자석 연구/설계 foundation의 5계층이 정리된 안정 릴리스이며, 완성형 실험/공정 대체 엔진을 뜻하지 않는다.

상세 문서:

- 버전 정책: [docs/VERSIONING_POLICY.md](docs/VERSIONING_POLICY.md)
- 물리 프록시 한계: [docs/PHYSICS_PROXY_LIMITATIONS.md](docs/PHYSICS_PROXY_LIMITATIONS.md)
- quench 레이어 모델: [docs/QUENCH_LAYER_MODEL.md](docs/QUENCH_LAYER_MODEL.md)

## 설계 철학 정렬

- 00_BRAIN 철학대로 **물리 법칙 커널화 + 계층 확장**을 적용
- “재료 발견”이 아닌 “후보 재료 기반 설계평가”에 초점
- stdlib-only, 독립 패키지, 테스트 우선

## 이 스택이 하는 일 / 하지 않는 일

하는 일:

- 후보 재료/냉각/자석 설계를 입력으로 받아 readiness를 빠르게 스크리닝
- quench 위험을 포함한 설계 의사결정(진행/보류/재설계) 근거 제공
- `design_workspace`와 연결 가능한 `engine_ref` 출력 계약 제공

하지 않는 일:

- 새로운 초전도 물질 발견(DFT/실험 대체)
- 고정밀 다중물리 FEA/CFD/실험장비 대체
- 실제 생산 공정/품질 인증 툴체인 대체

## 레이어(초기)

- `contracts`: `MaterialCandidate`, `CryoProfile`, `MagnetDesign`, `QuenchRiskReport`, `BuildReadinessReport`
- `material`: `Tc/Jc/Bc2` 기반 derating + `omega_material`
- `thermal`: 냉각 마진 + `omega_thermal`
- `safety`: quench index + severity/recommendation
- `observer`: `omega_total` + verdict(`HEALTHY/STABLE/FRAGILE/CRITICAL`)
- `pipeline`: `run_magnet_design_assessment()`
- `engine_ref_adapter`: `superconducting.magnet.readiness` 입력 payload 실행
- `cli`: `sc-magnet-assess --input-json ... --json`

## 연구 확장 발판

이 스택은 아직 “초전도체 연구 전체”는 아니지만,
초전도 자석 연구로 나아가기 위한 다음 연구 축들을 기초 레이어로 올렸습니다.
이 확장 축은 `v0.3.0` 무렵의 기초 연구 스캐폴딩에서 시작해 현재 `1.0.0`까지 단계적으로 확장됐습니다.

- `coil_geometry`: 권선 길이, fill proxy, hoop load index
- `ac_loss`: 동적 sweep 조건에서의 AC loss screening
- `quench_propagation`: NZPV proxy, hotspot risk, dump window screening
- `joint_resistance`: 조인트 저항과 국소 발열 screening
- `field_uniformity`: 균일도 / fringe field proxy
- `mechanical_fatigue`: 반복 램프 하중과 fatigue risk screening
- `material_screening`: 후보 재료의 운영 margin / screening score
- `splice_topology`: splice 수와 topology penalty
- `ramp_profile`: 램프 속도와 동적 안정성 penalty
- `splice_matrix`: splice 행렬 복잡도와 전류 불균형 risk
- `ramp_dynamics`: 유도전압, 동적 heating, 안정 창(window) screening
- `material_ranking`: 같은 설계 조건에서 후보 재료군을 비교·랭킹하는 screening 레이어

## v1.0.0 5계층 구조

`1.0.0`의 핵심은 “초전도 현상 전체를 해결했다”가 아니라, **초전도 자석을 연구/설계 관점에서 안정적으로 읽는 5계층 foundation**이 코드로 정리됐다는 점입니다.

| 계층 | 모듈 | 역할 |
|---|---|---|
| Layer 1 — Physics Foundation | `material_database`, `critical_state`, `pinning`, `strain_effects` | 재료군, 임계상태, 보텍스 피닝, 변형률 derating |
| Layer 2 — Transient Dynamics | `quench_dynamics`, `protection_system` | RK4 quench 동역학, MIIT/dump resistor/protection screening |
| Layer 3 — Multi-Physics | `ac_loss_decomposition`, `multiphysics_engine` | AC loss 분해, 열·전자기·기계 proxy 통합 |
| Layer 4 — Research Tools | `sensitivity_analysis`, `uncertainty_quantification`, `fault_tolerance` | 민감도, 불확실성, 고장 허용성 |
| Layer 5 — Application Presets | `application_presets` | LHC/HL-LHC/SPARC/MRI/SMES 스타일 기준점 비교 |

이 계층은 고정밀 FEM/실험 장비를 대체하지 않습니다. 대신 MRF, Space Gate, Fusion, MRI, SMES 같은 상위 엔진이 “강한 자기장 인프라를 쓸 수 있는가”를 빠르게 스크리닝할 수 있게 하는 하부 readiness 언어입니다.

즉 현재 가장 자연스러운 확장 순서는:

1. 자석 형상/권선 구조
2. AC loss
3. quench propagation
4. joint resistance / field uniformity / fatigue
5. material screening / splice topology / ramp stability
6. splice matrix / ramp dynamics
7. material candidate ranking
8. critical-state / pinning / strain effects
9. quench dynamics / protection system
10. multiphysics / uncertainty / fault tolerance
11. application presets 기반 응용별 비교

## 설계 과정 (권장 워크플로)

1. **재료 정의**: `MaterialCandidate`에 `Tc/Jc/Bc2/anisotropy` 입력  
2. **운영점 정의**: `CryoProfile`에 작동온도/열부하/냉각용량 입력  
3. **자석 설계 정의**: `MagnetDesign`에 목표장/운영전류/단면/응력 입력  
4. **기본 판정**: `run_magnet_design_assessment()`로 readiness + quench 산출  
5. **연구 발판 확장**: AC loss/NZPV/joint/uniformity/fatigue/screening까지 순차 확장  
6. **L4 통합**: `superconducting.magnet.readiness` 노드로 상위 시나리오에 삽입  
7. **v1 계층 검사**: critical-state/pinning/strain/quench dynamics/protection/multiphysics/uncertainty/presets를 필요에 따라 보조 스크리닝으로 호출

## 핵심 개념 해설 (낯선 독자용)

- `Tc`: 초전도 상태가 유지되는 임계 온도 기준
- `Jc`: 단면당 허용 가능한 임계 전류 밀도
- `jc_a_per_mm2_77k` 필드 해석:
  - HTS 문맥에서 익숙한 기준값 이름을 사용하고 있다.
  - 본 스택에서는 재료군 간 비교를 위한 **reference Jc input**으로 읽는 것이 안전하다.
- `Bc2`: 자장 조건에서 초전도성이 무너지기 시작하는 임계 지표
- `quench`: 국소 정상전도 전이가 확산되며 발열이 커지는 위험 상태
- `Ω(omega)`: 설계 상태를 0~1로 요약한 건강도 지표
- `verdict`: `HEALTHY/STABLE/FRAGILE/CRITICAL` 4단계 판정

## 핵심 수식(설계용 단순 모델)

- `Jc_derated = Jc0 * (1 - T/Tc) * (1 - B/Bc2) / anisotropy`
- `omega_total = 0.4*omega_material + 0.35*omega_thermal + 0.25*omega_quench`
- `omega_quench = 1 - quench_index`

> 이 모델은 고정밀 실험 대체가 아니라, 초기 설계 트레이드오프 평가용입니다.

## Observer 의미

여기서 `observer`는 센서를 붙여 계속 상태를 수집하는 런타임 데몬이 아닙니다.
현재 구현의 `observer`는 아래 세 축을 관찰해 하나의 readiness 판정으로 묶는
**설계 관찰/집계 레이어**입니다.

- `material` 결과
- `thermal` 결과
- `safety(quench)` 결과

즉 이 스택의 `observer`는
“운영 중 자석을 계속 감시하는 계측 시스템”이라기보다,
**후보 설계안이 지금 단계에서 얼마나 build-ready 한가를 종합 판정하는 관찰자**
로 읽는 것이 정확합니다.

반대로 `pipeline`은 여러 평가 레이어를 실제 순서대로 호출해
하나의 결과 묶음으로 반환하는 **실행 오케스트레이션 레이어**입니다.
즉:

- `observer` = readiness 집계/판정
- `pipeline` = 평가 실행 흐름

## Quench 확장 구조

quench 관련 평가는 한 번에 끝나지 않고 다음 레이어로 확장된다.

1. base screening: `safety`의 `quench_index`
2. propagation: `quench_propagation`의 NZPV/hotspot proxy
3. local heating: `joint_resistance` 기반 접합부 발열 위험
4. dump/ramp window: `ramp_profile`, `ramp_dynamics`와 결합한 보호 여유 확인

즉 현재 구조는 quench를 단일 점수로만 처리하지 않고,
전파/국소발열/보호창으로 분해해 확장하도록 설계되어 있다.

## 빠른 시작

```python
from superconducting_magnet_stack import (
    MaterialCandidate, CryoProfile, MagnetDesign, run_magnet_design_assessment
)

material = MaterialCandidate("REBCO-like", tc_k=92.0, jc_a_per_mm2_77k=300.0, bc2_t=120.0, anisotropy=1.4)
cryo = CryoProfile(operating_temp_k=20.0, heat_load_w=12.0, cooling_capacity_w=30.0)
design = MagnetDesign(
    target_field_t=20.0,
    operating_current_a=600.0,
    conductor_cross_section_mm2=8.0,
    inductance_h=1.2,
    stored_energy_j=216000.0,
    stress_mpa=140.0,
)

readiness, quench = run_magnet_design_assessment(material, cryo, design)
print(readiness.verdict, readiness.omega_total)
print(quench.severity, quench.quench_index)
```

연구 확장 레이어까지 한 번에 보기:

```python
from superconducting_magnet_stack import run_research_foundation_assessment

reports = run_research_foundation_assessment(material, cryo, design, ac_sweep_hz=10.0)
readiness, quench, geometry, ac_loss, propagation = reports
print(geometry.hoop_load_index, ac_loss.loss_w_per_m, propagation.nzpv_m_per_s)
```

확장 연구 레이어까지 한 번에 보기:

```python
from superconducting_magnet_stack import run_extended_research_assessment

reports = run_extended_research_assessment(material, cryo, design, ac_sweep_hz=10.0)
readiness, quench, geometry, ac_loss, propagation, joint, uniformity, fatigue = reports
print(joint.joint_resistance_n_ohm, uniformity.field_uniformity_index, fatigue.fatigue_risk_index)
```

재료 연구 발판까지 한 번에 보기:

```python
from superconducting_magnet_stack import run_material_research_assessment

reports = run_material_research_assessment(material, cryo, design, ac_sweep_hz=10.0)
readiness, quench, geometry, ac_loss, propagation, joint, uniformity, fatigue, screening, splice, ramp, splice_matrix, ramp_dynamics = reports
print(screening.screening_score, splice.splice_count, ramp.ramp_rate_t_per_s)
print(splice_matrix.current_imbalance_risk_index, ramp_dynamics.stability_window_index)
```

후보 재료군 비교:

```python
from superconducting_magnet_stack import compare_material_candidates

candidates = [
    MaterialCandidate("CandidateA", tc_k=82.0, jc_a_per_mm2_77k=250.0, bc2_t=100.0, anisotropy=1.5),
    MaterialCandidate("CandidateB", tc_k=92.0, jc_a_per_mm2_77k=300.0, bc2_t=120.0, anisotropy=1.4),
]
ranking = compare_material_candidates(candidates, cryo, design)
print(ranking.best_candidate)
for item in ranking.ranking:
    print(item.rank, item.name, item.screening_score)
```

중요:

- `material_ranking`은 “절대적인 최적 재료 결정기”가 아닙니다.
- 현재 구현에서는 **같은 cryo/design 조건 아래에서 후보군을 screening score로 비교하는 보조 판단 레이어**로 읽는 것이 맞습니다.

CLI 후보군 비교:

```bash
cd _staging/Superconducting_Magnet_Stack
python3 -m superconducting_magnet_stack.cli \
  --input-json examples/material_compare_payload.json \
  --compare-materials \
  --json
```

## 테스트

```bash
cd _staging/Superconducting_Magnet_Stack
python3 -m pytest tests/ -q --tb=no
```

현재 로컬 점검 기준:

- 패키지 루트 내부: `99 passed`
- 패키지 루트 외부: `tests/conftest.py` 추가 후 수집 가능
- 범주:
  - core: contracts/material/thermal/safety/observer/pipeline/engine_ref/cli
  - foundation scaffold: geometry/ac_loss/quench_propagation
  - extended scaffold: joint/uniformity/fatigue
  - material scaffold: screening/splice/ramp/splice_matrix/ramp_dynamics/ranking
  - v1 physics/dynamics: material_database/critical_state/pinning/strain/quench_dynamics/protection
  - v1 research tools: multiphysics/uncertainty/sensitivity/fault_tolerance/application_presets

계약층 안전장치:

- `MaterialCandidate`, `CryoProfile`, `MagnetDesign` 는 이제 비물리적 입력을 계약층에서 바로 거절합니다.
- 예:
  - 빈 재료 이름
  - 음수 작동 온도
  - 0 이하 도체 단면적
- 이런 입력은 계산을 억지로 진행하지 않고 `ValueError` 로 멈춥니다.

## 변경 이력 / 무결성

- 변경 요약: [CHANGELOG.md](CHANGELOG.md)
- 무결성 설명: [BLOCKCHAIN_INFO.md](BLOCKCHAIN_INFO.md)
- 연속 기록 로그: [PHAM_BLOCKCHAIN_LOG.md](PHAM_BLOCKCHAIN_LOG.md)
- SHA-256 매니페스트: [SIGNATURE.sha256](SIGNATURE.sha256)

중요:

- 여기서 말하는 블록체인은 분산 합의형 네트워크를 뜻하지 않는다.
- 이 저장소에서는 **무결성과 변경 연속성 문서 패턴**을 뜻한다.
- 실제 검증은 SHA-256 매니페스트와 검증 스크립트로 수행한다.

검증:

```bash
python3 scripts/verify_signature.py
```

릴리스 게이트:

```bash
python3 scripts/release_check.py
```

서명 재생성:

```bash
python3 scripts/generate_signature.py
python3 scripts/verify_signature.py
```

## design_workspace 연결 (L4)

- 제안 `engine_ref`: `superconducting.magnet.readiness`
- 비교 `engine_ref`: `superconducting.magnet.material_ranking`
- payload 계약:
  - `material`: `name`, `tc_k`, `jc_a_per_mm2_77k`, `bc2_t`, `anisotropy?`
  - `cryo`: `operating_temp_k`, `heat_load_w`, `cooling_capacity_w`
  - `design`: `target_field_t`, `operating_current_a`, `conductor_cross_section_mm2`, `inductance_h`, `stored_energy_j`, `stress_mpa`

CLI:

```bash
cd _staging/Superconducting_Magnet_Stack
python3 -m superconducting_magnet_stack.cli --input-json examples/sample_payload.json --json
```

후보군 비교 CLI:

```bash
cd _staging/Superconducting_Magnet_Stack
python3 -m superconducting_magnet_stack.cli --input-json examples/material_compare_payload.json --compare-materials --json
```

## 확장 활용 시나리오

- **FusionCore 연계**: 고자장 자석 후보를 빠르게 스크리닝해 운영온도/응력 margin 비교
- **StarCraft/L4 연계**: 전력/열/메모리/HBM 시나리오 뒤에 자석 readiness 노드 삽입
- **교육/랩 프리디자인**: 실험 전 파라미터 민감도(온도/장/전류/응력) 사전 점검
- **의사결정 자동화**: `verdict`와 `quench_recommendation`을 게이트 룰에 연결

## GitHub 배포 가이드 (qquartsco-svg/SuperConductor, 처음 배포 시)

```bash
cd _staging/Superconducting_Magnet_Stack
git init
git add .
git commit -m "Release Superconducting Magnet Stack v1.0.0"
git branch -M main
git remote add origin https://github.com/qquartsco-svg/SuperConductor.git
git push -u origin main
```
