-- SQLZOO没有高亮显示，为增加辨识关键词大写；牛客网高亮很完善，为提高效率关键词小写

/* sqlzoo select-select
Find the continents where all countries have a population <= 25000000.
Then find the names of the countries associated with these continents.
Show name, continent and population.
*/
-- 1
SELECT name, continent, population FROM world
WHERE continent IN (
SELECT continent FROM world
GROUP BY continent HAVING MAX(population) <= 25000000
);
-- 2
SELECT name, continent, population
FROM (
    SELECT name, continent, population,
           MAX(population) OVER (PARTITION BY continent) as max_population
    FROM world
) continent_stats
WHERE max_population < 25000000
ORDER BY name;


/* sqlzoo self-join
Find the routes involving two buses that can go from Craiglockhart to Lochend.
Show the bus no. and company for the first bus, the name of the stop for the transfer,
and the bus no. and company for the second bus.
*/
SELECT r11.num, r11.company, s.name, r22.num, r22.company
FROM route r11
    JOIN route r12 ON r11.company=r12.company AND r11.num=r12.num
    JOIN stops s ON s.id=r12.stop,
    oute r21
    JOIN route r22 ON r21.company=r22.company AND r21.num=r22.num
WHERE
    r11.stop = (
        SELECT DISTINCT stop FROM route JOIN stops ON
        route.stop=stops.id WHERE stops.name='Craiglockhart')
    AND r12.stop = r21.stop
    AND
    r22.stop = (
        SELECT DISTINCT stop FROM route JOIN stops ON
        route.stop=stops.id WHERE stops.name='Lochend');


/* 牛客网 中等 日期相减，left join
请查询该酒店从6月12日开始连续入住多晚的客户信息？
要求输出：客户id、房间号、房间类型、
    连续入住天数（按照连续入住天数的升序排序，再按照房间号的升序排序，再按照客户id的降序排序）
*/
select
    c.user_id,
    g.room_id,
    g.room_type,
    DATEDIFF(c.checkout_time, c.checkin_time) as days
from
    guestroom_tb g left join checkin_tb c ON g.room_id=c.room_id
where
    DATEDIFF(c.checkout_time, c.checkin_time) > 1
order by days, g.room_id, c.user_id DESC;


/* 牛客网 中等 百分数计算、位数，distinct，不用join
请统计该商城每天用户从访问到下订单的转化率。
要求输出：日期，转化率（该日下订单人数/访问人数，以百分数形式输出并四舍五入保留1位小数）
注：输出结果按照日期升序排序
*/
select
    date(v.visit_time) as date,
    concat(round(100*(count(distinct o.user_id)/count(distinct v.user_id)), 1), '%') as cr
from
    order_tb o,
    visit_tb v
where
    date (visit_time) = date(order_time)
group by date(v.visit_time)
order by date;


/* 牛客网 困难 窗口函数，排序，减前项
你正在搭建一个用户活跃度的画像，其中一个与活跃度相关的特征是“最长连续登录天数”，
请用SQL实现“2023年1月1日-2023年1月31日用户最长的连续登录天数”
*/
select
    user_id,
    max(consec_days) as max_consec_days
from (
    select
        user_id,
        count(day_num) as consec_days
        from (
            select
                t1.user_id,
                date_sub(t1.fdate, interval(
                    dense_rank() over (partition by t1.user_id order by t1.fdate)) day
                ) as day_num
            from tb_dau t1
            where t1.fdate between '2023-01-01' and '2023-01-31'
        ) as t2
        group by user_id, day_num
) as t3
group by user_id;