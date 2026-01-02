# 특허 선행기술 조사 결과

**조사 일시**: 2026-01-02 08:52:17

## 조사 대상 특허

**제목**: 추적불가능한 생체인증 기술 및 시스템

**초록**: 본 발명은 사용자의 생체정보를 이용하여 인증을 수행하되, 생체정보 자체를 저장하거나 전송하지 않음으로써 개인정보 추적 및 역추적이 불가능한 생체인증 기술에 관한 것이다. 구체적으로, 사용자의 지문, 얼굴, 홍채 등의 생체정보로부터 임시 토큰을 생성하고, 이를 영지식 증명(Zero-Knowledge Proof) 기법과 결합하여 생체정보 원본 없이도 본인 확인이 가능하도록 한다. 또한 블록체인 기반 분산 저장 구조를 통해 중앙 서버의 데이터 유출 위험을 원천 차단하며, 매 인증마다 다른 일회용 생체 토큰을 생성하여 재사용 공격을 방지한다. 이를 통해 생체정보 유출 시에도 타 시스템에서의 악용이 불가능하고, 사용자의 인증 이력 추적이 불가능한 완전한 프라이버시 보장형 생체인증 시스템을 구현한다.

**키워드**: 추적불가능, 생체인증, 영지식증명, Zero-Knowledge Proof, zk-SNARK, zk-STARK, 블록체인, 분산저장, 프라이버시, 일회용 토큰

## 발견된 선행기술 (상위 10건)

### 1. Zero-Knowledge Proof System for Identity Verification

- **특허번호**: US10567890
- **유사도**: 9.73%
- **출처**: USPTO
- **URL**: [https://patents.google.com/patent/US10567890](https://patents.google.com/patent/US10567890)

**초록**: 영지식 증명을 이용한 신원 확인 시스템이나, 생체정보가 아닌 일반 신원정보(ID, 비밀번호)를 대상으로 한다. zk-SNARK 프로토콜을 사용하지만 생체인증과는 결합되지 않았다.

### 2. Blockchain-Based Biometric Data Management System

- **특허번호**: KR1020210087654
- **유사도**: 8.86%
- **출처**: KIPRIS
- **URL**: [https://patents.google.com/patent/KR1020210087654](https://patents.google.com/patent/KR1020210087654)

**초록**: 블록체인을 이용한 생체정보 관리 시스템으로, 사용자의 생체정보를 블록체인에 저장한다. 분산저장을 통해 데이터 무결성을 보장하나, 생체정보 원본을 해싱하여 저장하므로 일회용 토큰 방식은 아니다.

### 3. Privacy-Preserving Biometric Authentication Using Homomorphic Encryption

- **특허번호**: US10234567
- **유사도**: 7.58%
- **출처**: USPTO
- **URL**: [https://patents.google.com/patent/US10234567](https://patents.google.com/patent/US10234567)

**초록**: 본 발명은 동형암호(Homomorphic Encryption)를 이용한 프라이버시 보장형 생체인증 방법에 관한 것이다. 생체정보를 암호화한 상태에서 비교 연산을 수행하여 복호화 없이 인증을 완료한다. 그러나 영지식 증명 기법은 사용하지 않으며, 블록체인 대신 중앙 서버를 사용한다.

### 4. Multi-Modal Biometric Authentication with Template Protection

- **특허번호**: KR1020200123456
- **유사도**: 6.98%
- **출처**: KIPRIS
- **URL**: [https://patents.google.com/patent/KR1020200123456](https://patents.google.com/patent/KR1020200123456)

**초록**: 다중 생체정보(지문, 얼굴, 홍채)를 결합한 인증 시스템으로 템플릿 보호 기능을 제공한다. 그러나 매 인증마다 동일한 템플릿을 사용하므로 추적 가능성이 존재한다.

### 5. Decentralized Identity Management Using Blockchain

- **특허번호**: US10789012
- **유사도**: 5.66%
- **출처**: USPTO
- **URL**: [https://patents.google.com/patent/US10789012](https://patents.google.com/patent/US10789012)

**초록**: 블록체인 기반 탈중앙화 신원 관리 시스템이다. 사용자 신원정보를 블록체인에 저장하고 분산 검증을 수행하나, 생체인증 특화 기능은 없다.

### 6. Cancelable Biometric Template Generation Method

- **특허번호**: US10456789
- **유사도**: 4.95%
- **출처**: USPTO
- **URL**: [https://patents.google.com/patent/US10456789](https://patents.google.com/patent/US10456789)

**초록**: Cancelable Biometric 기법을 이용하여 생체정보 템플릿을 생성한다. 유출 시 템플릿을 폐기하고 새로운 템플릿을 발급할 수 있으나, 영지식 증명이나 일회용 토큰 방식은 사용하지 않는다.

### 7. One-Time Password Generation from Biometric Data

- **특허번호**: US10890123
- **유사도**: 3.44%
- **출처**: USPTO
- **URL**: [https://patents.google.com/patent/US10890123](https://patents.google.com/patent/US10890123)

**초록**: 생체정보를 이용한 일회용 비밀번호(OTP) 생성 방법이다. 생체정보로부터 일회성 값을 생성하나, 영지식 증명이나 블록체인 기술은 사용하지 않는다.

### 8. Fuzzy Vault Scheme for Fingerprint Authentication

- **특허번호**: US10678901
- **유사도**: 3.22%
- **출처**: USPTO
- **URL**: [https://patents.google.com/patent/US10678901](https://patents.google.com/patent/US10678901)

**초록**: Fuzzy Vault 기법을 이용한 지문 인증 방법이다. 생체정보의 변동성을 허용하면서도 보안을 유지하나, 일회용 토큰 방식이나 영지식 증명은 사용하지 않는다.

### 9. Secure Biometric Template Storage Using Secret Sharing

- **특허번호**: KR1020190098765
- **유사도**: 2.86%
- **출처**: KIPRIS
- **URL**: [https://patents.google.com/patent/KR1020190098765](https://patents.google.com/patent/KR1020190098765)

**초록**: 비밀분산(Secret Sharing) 기법을 이용한 생체 템플릿 저장 방법이다. 템플릿을 여러 조각으로 나누어 분산 저장하나, 영지식 증명이나 일회용 토큰은 미포함이다.

### 10. Privacy-Enhanced Face Recognition Using Differential Privacy

- **특허번호**: US10901234
- **유사도**: 2.52%
- **출처**: USPTO
- **URL**: [https://patents.google.com/patent/US10901234](https://patents.google.com/patent/US10901234)

**초록**: 차등 프라이버시(Differential Privacy)를 적용한 얼굴 인식 시스템이다. 노이즈 추가를 통해 프라이버시를 보호하나, 영지식 증명이나 일회용 토큰은 사용하지 않는다.

## 통계

- **총 발견 특허 수**: 10건
- **평균 유사도**: 5.58%
- **고유사도 특허** (>50%): 0건
