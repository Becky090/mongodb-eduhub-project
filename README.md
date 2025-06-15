# 📚 EduHub: MongoDB-Based E-Learning Platform

EduHub is a MongoDB-powered backend system designed to manage users, courses, enrollments, assignments, and analytics for an online education platform.

---

## 🛠️ Project Setup Instructions

### Prerequisites
- Python 3.8+
- MongoDB (local)
- Dependencies: Install with

```bash
pip install pymongo
```

### Setup
1. **Import libraries and create connection.**
  ```
  from pymongo import MongoClient
  ```

2. Launch MongoDB (local).
    ```
  client = MongoClient("mongodb://localhost:27017/")
  db = client["eduhub_db"]``` 

4. Interact using Jupyter or the provided Python scripts in `src/`.

---

## 🗂️ Database Schema Documentation

### 1. `users`
```json
{
  {
  "_id": "user1",
  "email": "kelsey22@example.net",
  "firstName": "Christopher",
  "lastName": "Davis",
  "role": "student",
  "dateJoined": {
    "$date": "2025-05-05T17:25:24.544Z"
  },
  "profile": {
    "bio": "Others represent strategy consider class that realize just.",
    "avatar": "https://placekitten.com/359/671",
    "skills": [
      "receive",
      "early",
      "history"
    ]
  },
  "isActive": true
}
  }

```

### 2. `courses`
```json
{
  "_id": "course1",
  "title": "Program Masterclass",
  "description": "Sense them consumer total value accept. Talk quality dark way. Skill future pretty edge.",
  "instructorId": "user26",
  "category": "Web Dev",
  "level": "intermediate",
  "duration": 33,
  "price": 100.15,
  "tags": [
    "weight",
    "wife",
    "picture",
    "especially"
  ],
  "createdAt": {
    "$date": "2025-06-14T13:09:17.913Z"
  },
  "updatedAt": {
    "$date": "2025-06-14T13:09:17.913Z"
  },
  "isPublished": true,
  "rating": 4.5

}
```

### 3. `enrollments`
```json
{
  "_id": "enroll18",
  "studentId": "user21",
  "courseId": "course3",
  "enrolledAt": {
    "$date": "2025-03-07T12:20:59.715Z"
  },
  "status": "completed"

}
```

### 4. `assignments`
```json
{
   "_id": "assign_course7_1",
  "courseId": "course7",
  "lessonId": null,
  "title": "Assignment for Art Masterclass",
  "description": "Detail public try measure. Management easy could recently red none.",
  "createdAt": {
    "$date": "2025-06-14T13:13:36.364Z"
  },
  "dueDate": {
    "$date": "2025-06-28T13:13:36.364Z"
  },
  "attachmentUrl": null,
  "grade": 58.09
}
```

### 5. `submissions`
```json
{
  "_id": "submit17",
  "assignmentId": "assign_course6_2",
  "studentId": "user18",
  "submittedAt": {
    "$date": "2025-06-02T14:09:07.145Z"
  },
  "contentUrl": "http://lewis.com/",
  "grade": 82.17,
  "feedback": "Meeting week final than.",
  "status": "graded"
}
```

### 5. `lessons`
```json
{
  "_id": "lesson_course1_1",
  "courseId": "course1",
  "title": "Raise meeting idea.",
  "content": "Provide method house listen ground political ever. Second as main billion ground space. Traditional account sell young.",
  "duration": 7,
  "videoUrl": "https://www.washington.biz/",
  "order": 1,
  "resources": [
    "https://harrington.com/search/main/mainregister.htm",
    "http://www.williamson-ray.com/tags/tagspost.html"
  ],
  "createdAt": {
    "$date": "2025-06-14T13:12:36.804Z"
  },
  "updatedAt": {
    "$date": "2025-06-14T13:12:36.804Z"
  }
}
```
---

## 🔍 Query Explanations

- **Read Queries**: Retrieve students, instructors, course info, enrollments, and assignments using filters and projections.
- **Update Queries**: Used `$set`, `$addToSet`, and `$inc` to update profile info, add tags, update grades.
- **Aggregation**: Performed grouping, lookup, and project stages for analytics like:
  - Average grades
  - Completion rates
  - Monthly enrollments
- **Delete Queries**: Implemented soft delete for users, and hard delete for enrollments and lessons.

All queries include appropriate error handling using `try-except` blocks.

---

## ⚡ Performance Analysis Results

### Indexed Fields
- `users.email` (unique)
- `courses.title`, `courses.category`
- `assignments.dueDate`
- `enrollments.studentId`, `enrollments.courseId`

### Optimization Example

| Query                          | Before Index | After Index |
|-------------------------------|--------------|-------------|
| `courses.find({"category": "Programming"})` | 4.49 ms      | 1.01 ms     |
| `users.find({"email": ...})`  | 3.87 ms      | 0.86 ms     |
| `assignments.find({"dueDate": ...})` | 2.98 ms      | 0.92 ms     |

Used `.explain("executionStats")` and Python `time.perf_counter()` for benchmarking.

---

## 🚧 Challenges Faced and Solutions

| Challenge | Solution |
|----------|----------|
| Enforcing schema rules in MongoDB | Used `$jsonSchema` validator on collections |
| Handling missing fields or wrong data types | Added robust error handling (`WriteError`, `DuplicateKeyError`) |
| Joining across collections in NoSQL | Used `$lookup` and `$unwind` in aggregation pipelines |
| Tracking performance gains | Measured using `explain()` and `time.perf_counter()` |
| Data duplication during insertions | Ensured unique `_id` usage and index enforcement |

---

## 📈 Advanced Analytics Implemented

- Top-performing students (average grade)
- Course completion rates
- Instructor analytics: revenue, average ratings
- Monthly enrollment trends
- Most popular course categories

