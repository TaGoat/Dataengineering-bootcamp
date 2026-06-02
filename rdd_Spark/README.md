# RDD Spark Lab

This lab is about working with Spark RDDs to process employee data stored in HDFS.

## Dataset

The file `employees.txt` has 10 employee records in CSV format with these columns:

```
emp_id, name, department, job_title, salary, location, hire_date, performance_rating, years_exp
```

The data has some problems on purpose to practice filtering:
- Row 7 has a missing comma between job_title and salary (`Legal Counsel145000`), so it splits into 10 fields instead of 9
- There are empty lines in the middle of the file

## Setup

I copied the file into the itvlab Docker container and then uploaded it to HDFS:

```bash
docker cp employees.txt itvlab:/tmp/employees.txt
docker exec -it itvlab bash
hdfs dfs -mkdir -p /user/itvlab/rdd_lab
hdfs dfs -put -f /tmp/employees.txt /user/itvlab/rdd_lab/employees.txt
```

After that I verified it was there:

```bash
hdfs dfs -ls /user/itvlab/rdd_lab
```

```
-rw-r--r--   1 itversity supergroup   809  /user/itvlab/rdd_lab/employees.txt
```

## Tasks

The notebook `rdd.ipynb` solves 5 tasks using PySpark RDD operations:

**Task 1 - Parse text data into structured format**

Read the file from HDFS, removed the header and empty lines, then split each line by comma into a list.

**Task 2 - Count occurrences of each name**

Mapped each record to a (name, 1) pair and used reduceByKey to count. Every name appeared once.

**Task 3 - Filter invalid records**

Wrote a function that checks if a line has exactly 9 fields and if the numeric fields (emp_id, salary, rating, years_exp) can be parsed properly. Row 7 was caught as invalid because the missing comma gave it 10 fields instead of 9.

**Task 4 - Average salary per department**

Used only the valid records. Mapped each one to (department, (salary, 1)) and used reduceByKey to sum the salaries and counts, then divided to get the average.

Results:
- Engineering: $121,666
- IT: $115,000
- Finance: $105,000
- Sales: $97,500
- Marketing: $92,000
- HR: $88,000

**Task 5 - Employee count per department**

Mapped valid records to (department, 1) and used reduceByKey to count.

Results:
- Engineering: 3
- Sales: 2
- Marketing: 1
- Finance: 1
- IT: 1
- HR: 1

## Files

- `rdd.ipynb` - the Spark notebook with all tasks solved and output
- `employees.txt` - the dataset
- `README.md` - this file
