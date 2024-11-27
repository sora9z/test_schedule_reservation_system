# API 명세서

## 공통 사항

### 인증

- 회원가입(`POST /api/v1/users/`)과 로그인(`POST /api/v1/users/login`)을 제외한 모든 API는 JWT 인증이 필요합니다.
- JWT 토큰은 로그인 시 발급됩니다.

### 요청 헤더

```
Authorization: Bearer {access_token}
Content-Type: application/json
```

### 에러 응답

```json
{
  "detail": "에러 메시지"
}
```

### 상태 코드

- 200: 성공
- 201: 생성 성공
- 400: 잘못된 요청
- 401: 인증 실패
- 403: 권한 없음
- 404: 리소스를 찾을 수 없음
- 500: 서버 에러

## 사용자 API (User)

### 회원가입

- **엔드포인트**: POST /api/v1/users/
- **설명**: 새로운 사용자를 생성합니다
- **요청 본문**:
  ```json
  {
    "email": "string",
    "password": "string",
    "type": "ADMIN | USER"
  }
  ```
- **응답**: 201 Created
  ```json
  {
    "id": 0,
    "email": "string",
    "type": "ADMIN | USER"
  }
  ```

### 로그인

- **엔드포인트**: POST /api/v1/users/login
- **설명**: 사용자 로그인을 처리합니다
- **요청 본문**:
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **응답**: 200 OK
  ```json
  {
    "access_token": "string",
    "refresh_token": "string"
  }
  ```

## 예약 API (Reservation)

### 예약 생성

- **엔드포인트**: POST /api/v1/reservations/
- **설명**: 새로운 예약을 생성합니다
- **인증**: 필요
- **요청 본문**:
  ```json
  {
    "exam_date": "YYYY-MM-DD",
    "exam_start_time": "HH:MM:SS",
    "exam_end_time": "HH:MM:SS",
    "applicants": 0
  }
  ```
- **응답**: 201 Created
  ```json
  {
    "id": 0,
    "user_id": 0,
    "exam_date": "YYYY-MM-DD",
    "exam_start_time": "HH:MM:SS",
    "exam_end_time": "HH:MM:SS",
    "applicants": 0,
    "status": "PENDING | CONFIRMED | CANCELED"
  }
  ```

### 가능한 예약 시간 조회

- **엔드포인트**: GET /api/v1/reservations/available
- **설명**: 특정 날짜의 가능한 예약 시간을 조회합니다
- **쿼리 파라미터**:
  - date: YYYY-MM-DD
- **응답**: 200 OK
  ```json
  {
    "available_slots": [
      {
        "id": 0,
        "date": "YYYY-MM-DD",
        "start_time": "HH:MM:SS",
        "end_time": "HH:MM:SS",
        "remaining_capacity": 0
      }
    ]
  }
  ```

### 사용자 예약 목록 조회

- **엔드포인트**: GET /api/v1/reservations/
- **설명**: 현재 로그인한 사용자의 예약 목록을 조회합니다
- **인증**: 필요
- **응답**: 200 OK
  ```json
  {
    "reservations": [
      {
        "id": 0,
        "user_id": 0,
        "exam_date": "YYYY-MM-DD",
        "exam_start_time": "HH:MM:SS",
        "exam_end_time": "HH:MM:SS",
        "applicants": 0,
        "status": "PENDING | CONFIRMED | CANCELED"
      }
    ]
  }
  ```

### 예약 수정

- **엔드포인트**: PATCH /api/v1/reservations/{reservation_id}
- **설명**: 기존 예약을 수정합니다
- **인증**: 필요
- **요청 본문**:
  ```json
  {
    "exam_date": "YYYY-MM-DD",
    "exam_start_time": "HH:MM:SS",
    "exam_end_time": "HH:MM:SS",
    "applicants": 0
  }
  ```
- **응답**: 200 OK
  ```json
  {
    "is_success": true
  }
  ```

### 예약 삭제

- **엔드포인트**: DELETE /api/v1/reservations/{reservation_id}
- **설명**: 예약을 삭제합니다
- **인증**: 필요
- **응답**: 200 OK
  ```json
  {
    "is_success": true
  }
  ```

## 관리자 API (Admin)

### 예약 승인

- **엔드포인트**: PATCH /api/v1/admin/reservations/{reservation_id}/confirm
- **설명**: 관리자가 예약을 승인합니다
- **인증**: 필요 (관리자 권한)
- **응답**: 200 OK
  ```json
  {
    "is_success": true
  }
  ```

### 전체 예약 목록 조회

- **엔드포인트**: GET /api/v1/admin/reservations
- **설명**: 관리자가 모든 예약 목록을 조회합니다
- **인증**: 필요 (관리자 권한)
- **응답**: 200 OK
  ```json
  {
    "reservations": [
      {
        "id": 0,
        "user_id": 0,
        "exam_date": "YYYY-MM-DD",
        "exam_start_time": "HH:MM:SS",
        "exam_end_time": "HH:MM:SS",
        "applicants": 0,
        "status": "PENDING | CONFIRMED | CANCELED"
      }
    ]
  }
  ```
