query 1
```sql
SELECT COUNT(*) FROM yellowcab WHERE tip_amount > 10;
```
no indexes:  2.043 sec
1 col index: 0.204 sec
2 col index: 1.796 sec

query 2
```sql
SELECT DISTINCT VendorID
FROM yellowcab
WHERE passenger_count = 1 OR passenger_count = 2;
```
no indexes:  2.351 sec
1 col index: 2.833 sec
2 col index: 1.878 sec

querry 3:
```sql
SELECT COUNT(*)
FROM yellowcab
WHERE fare_amount > 15 AND fare_amount < 20 AND passenger_count = 1;
```
no indexes:  2.016 sec
1 col index: 0.165 sec
2 col index: 1.818 sec

1 col indexes:
```sql
CREATE INDEX idx_yc_tip ON yellowcab_2 (tip_amount);
CREATE INDEX idx_yc_passenger_count ON yellowcab_2 (passenger_count);
CREATE INDEX idx_yc_fare_amount ON yellowcab_2 (fare_amount);
```

2 col indexes:
```sql
CREATE INDEX idx_yc_tip_pas ON yellowcab_2 (tip_amount, passenger_count);
CREATE INDEX idx_yc_tip_fare ON yellowcab_2 (tip_amount, fare_amount);
CREATE INDEX idx_yc_pas_fare ON yellowcab_2 (passenger_count, fare_amount);
```
