# test_schedule_reservation_system

목차

## 목차

1. [설계 및 고려사항](#설계-및-고려사항)
2. [프로젝트 구조](#프로젝트-구조)
3. [프로젝트 설정](#프로젝트-설정)
4. [요구사항](#요구사항)
5. [실행 방법](#실행-방법)
6. [API 명세](#API-명세)

## 설계 및 고려사항

1. 요구사항에 대한 가정

- 회원에 대한 요구사항
  - 회원 가입 및 로그인에 대한 요구사항이 없어 아래와 같이 구현하였습니다.
    - 회원가입 : email, password 를 받아 회원가입 기능을 구현하였습니다.
    - 로그인 : email, password 를 받아 로그인시 accessToken과 refreshToken을 반환하는 기능을 구현하였습니다.
    - 인증 : jwt 인증 전략을 사용하여 구현하였습니다.
- 예약에 대한 요구사항
  - 동 시간대에 최대 5만명 가능하다.
  - "동시간대"의 정의가 명확하지 않아 겹치는 시간대도 동시간대라고 간주하고 로직을 작성하였습니다. 시험을 위한 안정적인 시스템 자원 확보를 위해 이러한 정의를 사용하였습니다.

2. 설계 고려사항

- 예약을 이한 슬롯 개념을 도입하였습니다.
  - 시험 예약이 오전 9:00 ~ 오후 18:00 까지만 가능하다고 가정한다면, 매일 특정 간견(30분 또는 1시간) 단위로 슬롯을 생성하여 예약 가능 인원 및 시간을 관리하는 방향으로 설계하였습니다.
  - 슬롯 생성 로직을 구현하지 못하였지만 테스트를 위해 아래 SQL을 작성해두었습니다.
- 예약 가능 유무 확인을 위해 시간대 조회 성능을 위한 postgresql의 range type, gist index를 사용하였습니다.

  - 참고문서 : https://www.postgresql.org/docs/current/rangetypes.html
  - 고도화 방안 : 구현하지는 않았지만 레디스 등을 사용한 케싱 전략으로 성능개선이 가능할 것 같습니다.

- 시간대는 서버에서 utc로 변환하여 저장하였습니다. 이는 시간대가 다른 클라이언트에서 로컬 시간으로 입력받아 서버에서 변환하는 것이 더 효율적이라 판단하였습니다.
- 최대한 비즈니스를 담아내기 위해 유닛 테스트 코드를 작성하였습니다.
- 시간관계상 응답 미들웨어 및 통합 테스트 코드는 작성하지 못하였습니다.

3. 데이터베이스 스키마
   ![schema](schema.png)

## 프로젝트 구조

1. 프로젝트 구조

- 기본적인 layerd architecture 구조로 설계하였습니다.

  - 도메인이 user와 reservation 두 가지로 구성이 되기 때문에 간단한 구조로 설계하였습니다.

- repository와 model을 공통파일에 넣은 이유는 repository롸 model은 도메인에 종속적이지 않으며 여러 서비스에서 공통적으로 사용되기 때문입니다.

```
├── README.md
├── alembic # alembic 설정 파일
├── alembic.ini
├── app # 애플리케이션 파일
│   ├── api # 라우트 파일
│   ├── common # 공통 파일
│   ├── config.py # 설정 파일
│   ├── container.py # 컨테이너 파일(Dependency Container)
│   ├── main.py # 애플리케이션 진입점
│   ├── schemas # pydantic 스키마 파일
│   └── services # 서비스 파일
├── docker
├── poetry.lock
├── pyproject.toml
├── pytest.ini
└── tests
```

## 프로젝트 설정

- 파이썬 버전: 3.12.4
- 패키지 매니저: Poetry
- 데이터베이스: PostgreSQL
- 코드 포매팅: black
- 코드 포매팅 규칙: .flake8
- 커밋 메시지 규칙: .gitmessage.txt

## 요구사항

1. 예약 조회, 신청

- 고객은 예약 신청이 가능한 시간과 인원을 알 수 있습니다.
- 예약은 시험 시작 3일 전까지 신청 가능하며, 동 시간대에 최대 5만명까지 예약할 수 있습니다. 이때, 확정되지 않은 예약은 5만명의 제한에 포함되지 않습니다.
- 예약에는 시험 일정과 응시 인원이 포함되어야 합니다.
  - 예를 들어, 4월 15일 14시부터 16시까지 이미 3만 명의 예약이 확정되어 있을 경우, 예상 응시 인원이 2만명 이하인 추가 예약 신청이 가능합니다.
- 고객은 본인이 등록한 예약만 조회할 수 있습니다.
- 어드민은 고객이 등록한 모든 예약을 조회할 수 있습니다.

2. 예약 수정 및 확정

- 예약 확정: 고객의 예약 신청 후, 어드민이 이를 확인하고 확정을 통해 예약이 최종적으로 시험 운영 일정에 반영됩니다. 확정되지 않은 예약은 최대 인원 수 계산에 포함되지 않습니다.
- 고객은 예약 확정 전에 본인 예약을 수정할 수 있습니다.
- 어드민은 모든 고객의 예약을 확정할 수 있습니다.
- 어드민은 고객 예약을 수정할 수 있습니다.

3. 예약 삭제

- 고객은 확정 전에 본인 예약을 삭제할 수 있습니다.
- 어드민은 모든 고객의 예약을 삭제할 수 있습니다.

## 실행 방법

- Python 3.12 이상

1. 도커 컴포즈 실행

```
cd docker
docker compose up -p {project_name} up -d

# docker 컴포즈 종료
docker compose down
```

2. 의존성 설치

```

# poetry가 설치되어 있어야 합니다.
pip install poetry

# 의존성 설치
poetry install

# 가상환경 활성화
poetry shell

# 가상환경 활성화(수동 필요시)
source .venv/bin/activate

```

3. 데이터베이스 마이그레이션

- 초기 데이터 마이그레이션을 생성해두었습니다.

```
# 초기 데이터 마이그레이션 생성
alembic upgrade head

```

- 마이그레이션 파일 생성(없을시)

```
alembic revision --autogenerate -m "init"
alembic upgrade head
```

- 테스트를 위해 Slot 데이터를 생성하여야 합니다. 아래의 SQL을 참고하여 데이터를 생성해주세요
- [Slot 데이터 생성 SQL](sql/.sql)

4. 애플리케이션 실행

```

uvicorn app.main:app --reload

```

4. 테스트 방법

- 테스트를 위한 사용자를 생성해야합니다. API 명세를 참고 또는 아래의 커멘드로 생성할 수 있습니다.

```
curl -X POST "http://localhost:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{
           "email": "user@example.com",
           "password": "yourpassword",
           "type": "ADMIN"
         }'
```

- 테스트 코드 실행

```

pytest -v

```

## API 명세

- [Swagger UI](http://localhost:8000/docs)

- [API 명세서](doc/API.md)
