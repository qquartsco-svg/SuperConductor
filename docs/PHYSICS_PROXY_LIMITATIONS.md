> **English:** [PHYSICS_PROXY_LIMITATIONS_EN.md](PHYSICS_PROXY_LIMITATIONS_EN.md)

# Physics Proxy Limitations

## 목적

이 스택의 핵심 수식이 "고정밀 물리 해석기"가 아니라 "설계 초기 screening proxy"임을 명확히 기록한다.

## 핵심 제한

- `Jc_derated = Jc0 * (1 - T/Tc) * (1 - B/Bc2) / anisotropy`는 단순 근사식이다.
- 실제 재료의 `Jc(B,T,epsilon)` 거동은 훨씬 비선형이며 재료군별 편차가 크다.
- 따라서 본 식은 절대 성능 예측값이 아니라 후보 간 상대 비교 지표로 사용해야 한다.

## Omega 가중치 제한

- 현재 `omega_total = 0.4*material + 0.35*thermal + 0.25*quench`는 MVP 정책값이다.
- 응용처(Fusion/MRI/Lab Magnet)에 따라 가중치는 달라질 수 있다.
- 가중치 튜닝은 정책 프로파일로 분리하는 것이 권장된다.

## 권장 사용 방식

- 초기 설계안 후보를 빠르게 걸러내는 pre-screening
- 민감도 분석(온도/자장/전류/응력)에서 변화 방향 파악
- 고정밀 해석/실험 전에 설계 우선순위 좁히기

## 비권장 사용 방식

- 절대 임계치 보증
- 실험장비 보호 판단의 최종 근거
- 규제/품질 인증 문서의 단독 근거

