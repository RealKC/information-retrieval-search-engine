SELECT COUNT(*)
FROM yellowcab
WHERE tip_amount > 10;
SELECT DISTINCT VendorID
FROM yellowcab
WHERE passenger_count = 1
    OR passenger_count = 2;
SELECT COUNT(*)
FROM yellowcab
WHERE fare_amount > 15
    AND fare_amount < 20
    AND passenger_count = 1;
CREATE TABLE IF NOT EXISTS yellowcab_2 LIKE yellowcab;
INSERT yellowcab_2
SELECT *
FROM yellowcab;
CREATE INDEX idx_yc_tip ON yellowcab_2 (tip_amount);
CREATE INDEX idx_yc_passenger_count ON yellowcab_2 (passenger_count);
CREATE INDEX idx_yc_fare_amount ON yellowcab_2 (fare_amount);
SELECT COUNT(*)
FROM yellowcab_2;
DROP INDEX idx_yc_tip ON yellowcab_2;
DROP INDEX idx_yc_passenger_count ON yellowcab_2;
DROP INDEX idx_yc_fare_amount ON yellowcab_2;
CREATE TABLE IF NOT EXISTS yellowcab_3 LIKE yellowcab;
INSERT yellowcab_3
SELECT *
FROM yellowcab;
CREATE INDEX idx_yc_tip_pas ON yellowcab_2 (tip_amount, passenger_count);
