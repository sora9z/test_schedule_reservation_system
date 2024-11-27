DO $$
DECLARE
    start_time TIME := '09:00'; -- UTC 기준 시작 시간
    end_time TIME := '18:00';   -- UTC 기준 종료 시간
    cur_time TIME := '09:00';
    slot_interval INTERVAL := '30 minutes';
    slot_date DATE := '2024-11-30'; -- 슬롯 날짜 (UTC)
    range_start TIMESTAMPTZ;
    range_end TIMESTAMPTZ;
    default_capacity INTEGER := 50000; -- remaining_capacity 기본값
BEGIN
    -- 세션 시간대를 UTC로 설정
    SET TIMEZONE TO 'UTC';

    WHILE cur_time < end_time LOOP
        -- 시작 및 종료 시간 범위를 UTC로 변환하여 생성
        range_start := (slot_date::TEXT || ' ' || cur_time::TEXT || '+00')::TIMESTAMPTZ;
        range_end := (slot_date::TEXT || ' ' || (cur_time + slot_interval)::TEXT || '+00')::TIMESTAMPTZ;

        -- 동적 SQL 실행
        EXECUTE '
            INSERT INTO slots (date, start_time, end_time, time_range, remaining_capacity, created_at, updated_at) 
            VALUES ($1, $2, $3, TSTZRANGE($4, $5, ''[]''), $6, now(), now())
        ' USING slot_date, cur_time, cur_time + slot_interval, range_start AT TIME ZONE 'UTC', range_end AT TIME ZONE 'UTC', default_capacity;

        -- 다음 슬롯 시간으로 이동
        cur_time := cur_time + slot_interval;
    END LOOP;
END $$;
