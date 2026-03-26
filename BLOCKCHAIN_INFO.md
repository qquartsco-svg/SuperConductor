# BLOCKCHAIN_INFO

## 목적

`Superconducting_Magnet_Stack`의 핵심 파일 무결성과 변경 연속성을 기록하기 위한 문서입니다.

이 저장소에서 "블록체인"은 분산 합의형 네트워크를 뜻하지 않습니다.
여기서는 아래 두 가지를 함께 가리키는 운영 표현입니다.

- `SIGNATURE.sha256` 기반 파일 무결성 검증
- `PHAM_BLOCKCHAIN_LOG.md` 기반 변경 연속성 기록

## 왜 필요한가

이 스택은 초전도 자석 연구/설계 발판 역할을 합니다.
즉 수치 모델이 거칠더라도,

- 어떤 파일이 현재 정본인지
- 어떤 버전 설명이 현재 코드와 맞는지
- 검토 시 파일이 변형되지 않았는지

는 명확해야 합니다.

## 현재 범위

현재 무결성 범위는 저장소 단위 확인입니다.

- 파일 존재 여부
- 파일 내용 SHA-256 해시 일치
- README / CHANGELOG / 버전 정합성 확인

아직 포함하지 않는 것:

- 외부 키 인프라
- 분산 합의
- 원격 서명 서비스
- 하드웨어 신뢰 루트

## 검증

```bash
python3 scripts/generate_signature.py
python3 scripts/verify_signature.py
```
