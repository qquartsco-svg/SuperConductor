> **English:** [QUENCH_LAYER_MODEL_EN.md](QUENCH_LAYER_MODEL_EN.md)

# Quench Layer Model

## 목적

quench 평가를 단일 점수가 아니라 레이어 구조로 이해하도록 정리한다.

## 레이어 구조

1. **Base Screening (`safety`)**
   - `quench_index`로 초기 위험도를 산출
   - `severity/recommendation`으로 즉시 조치 방향 제시

2. **Propagation Layer (`quench_propagation`)**
   - NZPV proxy 및 hotspot proxy로 전파 위험을 분해
   - 단순 위험도 이상의 동적 확산 성향을 확인

3. **Local Heating Layer (`joint_resistance`)**
   - 접합부 저항/발열 관점에서 국소 취약점 탐지
   - 동일 전류 조건에서 설계별 약점 비교

4. **Protection Window Layer (`ramp_profile`, `ramp_dynamics`)**
   - 램프 속도/유도전압/동적 heating을 함께 보고 보호 여유창(window) 점검
   - dump window 관련 설계 민감도를 확인

## 출력 해석

- 현재 구현은 보호계전기 대체가 아니라 설계 판단용 screening이다.
- 따라서 quench 관련 수치는 절대 안전 보증이 아니라 설계 후보 비교 지표로 써야 한다.

## 향후 확장

- 응용처별 보호 정책 프로파일 (Fusion/MRI/Lab)
- joint hotspot과 propagation coupling 강화
- dump resistor/energy extraction 모델 상세화

