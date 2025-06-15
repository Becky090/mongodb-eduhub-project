BEFORE INDEXING

# 1. Course by category
``` q1_before = time_query(db, "courses", {"category": "Programming"}, label="Course by Category")```
# 2. Enrollment by student and course
```q2_before = time_query(db, "enrollments", {"studentId": "student123", "courseId": "course1"}, label="Enrollment Lookup")```

# 3. Assignment due next week
```
now = datetime.utcnow()
next_week = now + timedelta(days=7)
q3_before = time_query(db, "assignments", {"dueDate": {"$gte": now, "$lte": next_week}}, label="Upcoming Assignments")
```

# CREATING AN INDEX
```
db.courses.create_index([("category", 1)])
db.enrollments.create_index([("studentId", 1), ("courseId", 1)])
db.assignments.create_index([("dueDate", 1)])
```
# After Indexing
```
q1_after = time_query(db, "courses", {"category": "Programming"}, label="Course by Category")
q2_after = time_query(db, "enrollments", {"studentId": "student123", "courseId": "course1"}, label="Enrollment Lookup")
q3_after = time_query(db, "assignments", {"dueDate": {"$gte": now, "$lte": next_week}}, label="Upcoming Assignments")
```
PERFORMANCE ANALYSIS

📊 Course by Category
  - Before Index: 5.25 ms
  - After Index:  0.93 ms
  - Improvement:  4.32 ms

📊 Enrollment Lookup
  - Before Index: 1.02 ms
  - After Index:  0.57 ms
  - Improvement:  0.45 ms

📊 Upcoming Assignments
  - Before Index: 0.53 ms
  - After Index:  0.54 ms
  - Improvement:  -0.01 ms