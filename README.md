# Relationship between Educational Expenditure and Household Income in the US
The first project of SI 618 2021FA at University of Michigan School of Information

## Motivation
This project aims to figure out the relationship between the educational expenditures and the average household income in different states in the United States. Generally speaking, richer areas with high household income can spend more on education because they have more extra money addtion to satisfying the living needs. Besides, the people with higher household income usually have higher education levels, which might also promote their governments to spend more on education.
On the other hand, conversely speaking, it is also believed that higher investment in education leads to a higher education level, and thus results in higher income. Hence, if a government wants to increase people’s income and living standard, it may consider increasing the educational expenditures. However, does that work for every county or state? Are there some cases where the governments invest similar amount of capital but have different results? This is a key problem to research on which would help the government review the education spending plans and do some improvement.
This project mainly seeks to research on the following three questions:
1. Does states with higher household income tend to invest more money on education?
2. Does education investment result in high household income?
3. For the state with high education investment but low household income, inspect the previous two questions on the level of counties. What counties mainly cause that result? What might be the potential root reasons?

## Data Sources
I use two datasets in this project.
### US Educational Finances
The first dataset contains the educational revenues and expenditures of the elementary and high schools in different school districts of different states from 1992 to 2016. The data are available on Kaggle: [U.S. Educational Finances](https://www.kaggle.com/noriuk/us-educational-finances) and are in `csv` format.

### US Household Income Statistics
The second dataset contains the statistics (including mean, median,standard deviation, etc.) of US household income in different counties of different states. The statistics are all averages from 2011 to 2015. The data are captured in 2017 and available on Kaggle: [US Household Income Statistics](https://www.kaggle.com/goldenoakresearch/us-household-income-stats-geo-locations) and are in `csv` format.

## Data Manipulation
Fortunately, after retrieving all the useful data, none of them contains incomplete or missing fields.
### Step 1: Filter out useful data from the two raw datasets
I load the two raw datasets into SparkSQL and filter out useful information with SparkSQL. I use the names of states, school districts and the total expenditure of each states from the US Educational Finances dataset. Besides that, I also compute the average annual increase rate of the total expenditure of each states, which is done by the following query. 
```sql
select STATE, mean(expenditureIncreaseRate) as meanExpenditureIncreaseRate from (select STATE, 
(postExpenditure- preExpenditure)/preExpenditure as expenditureIncreaseRate, preYear, postYear 
from (select a.STATE, a.YEAR as preYear, b.YEAR as postYear, a.TOTAL_EXPENDITURE as preExpenditure, 
b.TOTAL_EXPENDITURE as postExpenditure from (select * from edu where YEAR < 2016) as a inner join 
(select * from edu where YEAR > 1992) as b where a.YEAR = b.YEAR-1 and a.STATE = b.STATE)) 
group by STATE order by STATE
```
Basically it involves a self join of the orignal dataset to match the adjacent two years together so that I can compute the annual increase rate of the total expenditure.
For the US Household Income Statistics dataset, I use the following query to extract the mean of median household income of each states.
```sql
select State_name as state, mean(Median) as meanMedian from income group by state order by state
```
It can be considered as a very simple MapReduce job. After all the filtering, I register the resulting Spark DataFrames to several Tables by `createOrReplaceTempView`.

### Step 2: Join the datasets on the state level
It is convenient to join the datasets on the state level because they all have the "states" fields. I use `inner join` to join them in case that there are some places like Puerto Rico that only exist in one of them. one example query is:
```sql
select * from incomeByState as a inner join eduByState2016 as b on a.state = b.STATE
```

### Step 3: Join the datasets on the county level
At the beginning, note that it is only valid to join datasets on the county level for a specified state, because there are same county names across different states. If someone joins the original two datasets directly on the county level, it would probably join couties from different states together. 
The US Educational Finances dataset only has "school_district" field, while the US Household Income Statistics dataset has the accurate "county" field. To join the datasets on the county level, I do the following:
1. Given a state, find all the names of counties in this state in the US Household Income Statistics dataset
2. For each names of counties, find all the names of school districts in this state that contain the name of a county from the US Educational Finances dataset
3. Map these school districts together with the county

I do in the above way because 
* The US Household Income Statistics dataset on Kaggle is only one part of the full dataset, as stated in their description. It takes about $8 to purchase the whole dataset. Hence, it does not contain the data of all counties.
* The naming pattern of school districts in the US Educational Finances dataset is regular. It usually contains the name of the county, census area, borough, municipio, parish or municipality it is in.
* There is no free, extratable dataset to map school districts to counties on the Internet. Even if there exists such dataset, it is also probable that the school districts are named differently.

The above procedure is implemented by a MapReduce job in Spark similar to homework 5. It involves a cross join to map all the key-value pairs of the two datasets together into one `RDD` object. Then I use the `RDD.map()` function to realize the special reducing job. The code is as follows
```python
cat_1 = q7_rdd.flatMap(cat_q7)
cat_2 = q8_rdd.flatMap(cat_q8).reduceByKey(lambda x, y: x+y)
joined_rdd = cat_1.cartesian(cat_2).flatMap(join_county).map(lambda x: (x[0][0], x[0][1], x[0][2], 
x[1][0], x[1][1]))
```
where the functions `cat_q7` and `cat_q8` reduce two datasets. After doing a cartesian product (the cross join) to the two reduced dataset, the `join_county` function reduce the resulting large dataset to match county and school districts together.

## Analysis and Visualization

### Problem 1: Does states with higher household income tend to invest more money on education?
To answer this question, I need to find how does the educational expenditure vary on different amount of household income. As for the household income, I choose to use the median values to reduce the effect of extremely large or small values. Because the household income is the average from 2011 to 2015, I extract the educational expenditures in 2016. Then I join these two extracted tables by the following query
```sql
select * from incomeByState as a inner join eduByState2016 as b on a.state = b.STATE
```
As a result, I draw a graph of **the total expenditures in 2016 of each state vs. the median household income of each states**.

![Figure 1](/Problem1.jpeg "Figure 1. 2016Expenditures vs. householdIncome")

From the above figure we can notice that there is a small but clear positive trend between these two variables. That means generally, we can say that higher household income results in higher educational expenditure. Besides, there are several outliers, like California, New York and Texas, which invest much more capital on education compared to other states. None of the three states, however, is in the highest income level. Though these three states "pull up" the overall regression line, we can still observe a slight positive relationship between these two variables.

### Problem 2: Does education investment result in high household income?
To answer this question, I need to find the annual increase rate of the education expenditure of each states. Because different states have different population, social environment and history conditions, it is meaningless to compare the exact quantity of education expenditures. Hence, I compute the average annual increase rate of the education expenditure of each states as stated in the **Data Manipulation** section (detailed code is also included there). I first compute the annual increase rates of each states from 1993 to 2016 and then I take the average of years. The statistic can be a normalized measurement of the expenditure investment of each states. Because the household income is the average income from 2011 to 2015, it is valuable to monitor the statistic range from 1993 to 2016--starting from about 20 years before 2011 and ending in about 2015. 20 years are also the length of time a person needed to grow up and finally obtain a bachelor degree. I plot a graph of **the median household income of all the counties of each states vs. the mean expenditure increase rate of each states**.

![Figure 2](/Problem2_02.jpeg "Figure 2. householdIncome vs. meanExpenditureIncreaseRate")

From the above figure we can notice that there is a small but clear positive trend between these two variables. That means generally, we can say that the more a state increases its educational expenditure, the more the household income in the end. We can also see that the three states specified in **Problem 1**: California, New York and Texas, lie near the regression line and two of them lie above the regression line. That means the exact large quantity of expenditures at least does not result in low household income. 
On the other hand, in the down-right corner of the graph, there are five states: Georgia, Kentucky, Oklahoma, Mississippi and Arkansas which focus on educational expenditures a lot, yet still resulting in a low income level. If I remove these five states, the graph changes into this:

![Figure 3](/Problem2_03.jpeg "Figure 3. householdIncome vs. meanExpenditureIncreaseRate altered")

We can find that without the effects of those five "outliers", the regression line is remarkbaly "pulled up". This fact motivates me to research on **Problem 3** below.

### Problem 3: For the state with high education investment but low household income, inspect the previous two questions on the level of counties. What counties mainly cause that result? What might be the potential root reasons?

To answer this problem, I pick the most extreme case--Oklahoma among the five states specified in **Problem 2**. Oklahoma has the highest average annual education expenditure increase rate, but a significantly low level of household income. After joining the datasets on the county level as stated in the **Data Manipulation** section (detailed code is also included there), I plot the two similar graphs as in **Problem 2** and **Problem 3**. The differences are that I compute all the statistics on the county level. They result in the two graphs below. The first one is of **the total expenditures in 2016 of each counties in Oklahoma vs. the median household income of each counties in Oklahoma**.

![Figure 4](/Problem3_01.jpeg "Figure 4. 2016ExpendituresOklahoma vs. householdIncomeOklahoma")

From the first graph we can find out two outliers. One is Comanche County, which is a rich region with extremely high household income. The other is Tulsa County, which has a normal household income but extremely high education expenditures. That may imply Tulsa County drags down the overall performance of Oklahoma.

The second one is of **the median household income of each counties in Oklahoma vs. the mean expenditure increase rate of each counties in Oklahoma**.

![Figure 5](/Problem3_03.jpeg "Figure 5. householdIncomeOklahoma vs. meanExpenditureIncreaseRateOklahoma")

From the second graph we can notice that except Tulsa County, Creek County, Cleveland County, Seminole County and Coal County all have very high average annual increase rate of education expenditures, but still stay on a kind of median level of household income. Are they the origins which drag down the performance of the whole states? The answer is no, because after removing these five counties, the graph change into this:

![Figure 6](/Problem3_04.jpeg "Figure 6. householdIncomeOklahoma vs. meanExpenditureIncreaseRateOklahoma altered")

It is very surprising that the trend of the whole states is a negative relationship between these two variables, which means the more a county increases its educational expenditure, the less the household income in the end. This trend is completely opposite to the one in the state level across the America. That means not the five counties specified above, but the whole state experiences something. 

After a short research on Oklahoma, I start to understand a little bit. Oklahoma is a state of agriculture. The most probable reason causing the above phenomenon could be people's leaving. The higher a person's academic degree is, the more eager he or she wants to leave Oklahoma and move into a big city. Most high academic degrees are more useful in a big city in modern society. People can find more suitable and well-paid jobs in big cities more efficiently.

## Challenges
1. Initially, it is hard to join the two datasets on the county level because there are only "school_district" field in the U.S. Educational Finances dataset. What I do is to print out the names of the school districts and try to observe some patterns. Finally I find that it is mostly regularly named, which makes it possible to do the join.
2. It is also challenging to construct a MapReduce job for the county-level join. It is impossible to use any join method to directly realize the goal because the keys are totally different. Hence, I do a cross join first to combine the two RDDs into one and then apply the RDD.map() function to do the reducing part.
3. There are also some challenges in the visualization part. I find it hard to add annotations to the outliers of each graphs. I use seaborn to plot the graph but I need to use pyplot to add annotations, which totally messes up the coordinates. I have to try some values by myself to find the right places to add annotations.

## Limitation
1. The household income data is not a full one, thus it does not include all the income data of all counties.
2. There is bias inroduced by the matching techniques of the counties and the school districts of a given state. Though the matching techniques work for most of the school districts, there are still some of them whose names do not contain any county's name.
3. School districts vary from 1992 to 2016, so there may exist some inconsistency when joining the datasets on the county level.

## Conclusion
The project finds out there in general exists a positive relationship between the household income of people and the education expenditures of the government. The exact quantities of education expenditures of each states are similar and there is a regression line with small but positive slope indicating that states with high household income have a small tendency to invest more on education. Besides, there are three states California, New York and Texas that invest a lot more on education than other states. 
In terms of the average annual increase rate of education expenditures, the positve relationship between the household income and that is much clearer. That means the more a state increases its educational expenditure, the more the household income in the end. However, there are five states Georgia, Kentucky, Oklahoma, Mississippi and Arkansas that has high average annual increase rate but stays on a low household income level.
Taking Okalahoma as an example, the relationship between the household income and the average annual increase rate of education expenditures is negative in all the couties except the rich Comanche County. That may be probably caused by people's leaving with high educational degree. Because Okalahoma is a state of agriculture, people who get better education are more reasonable to leave for big cities to maximize their skills.
