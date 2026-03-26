> **English:** [VERSIONING_POLICY_EN.md](VERSIONING_POLICY_EN.md)

# Superconducting Magnet Stack Versioning Policy

## 목적

버전 숫자와 실제 구현 성숙도 사이의 기대치를 맞추기 위한 운영 규칙이다.
이 문서는 `README.md`의 해석 가이드를 더 공식화한다.

## 해석 원칙

- `0.x.y`는 연구/설계 스캐폴드 단계다.
- 현재 스택은 완성형 공정/실험 대체가 아니라, 설계 판단용 screening 엔진이다.
- 버전 상승은 "완성도 절대치"보다 "계약 안정성 + 기능 축 확장"을 우선 반영한다.

## 현재 릴리즈 해석

- `0.1.x`: 최소 contracts + readiness 판단 골격
- `0.2.x`: L4 `engine_ref` 연동과 CLI 운영 경로
- `0.3.x` ~ `0.5.x`: 연구 scaffold 확장(geometry/ac_loss/quench/joint/uniformity/fatigue/screening)
- `0.9.0`: 연구 확장 축이 넓어진 상태의 통합 버전 (완성형 production solver 의미 아님)

## 상향 기준 (권장)

- **Patch (`x.y.Z`)**: 문서 정합, 경미한 계산 보정, 테스트 보강
- **Minor (`x.Y.z`)**: 신규 연구 레이어/계약 확장, CLI/adapter 기능 확장
- **Major (`X.y.z`)**: 계약 파괴적 변경 또는 제품 포지셔닝 변경

## 버전과 기대치 문장 템플릿

릴리즈 노트/README에 아래 문장을 유지한다.

`이 버전은 연구/설계 스캐폴드 확장판이며, 고정밀 실험/공정 대체를 목표로 하지 않는다.`

