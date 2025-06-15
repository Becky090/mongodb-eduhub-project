from pymongo import MongoClient, errors
from typing import List, Dict
from pymongo.database import Database
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pprint import pprint
import time

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["eduhub_db"]


def insert_one(collection_name, document):
    """
    Inserts a single document into the specified MongoDB collection.

    Args:
        collection_name (str): The name of the collection.
        document (dict): The document to insert.

    Returns:
        Inserted document ID or error message.
    """
    try:
        result = db[collection_name].insert_one(document)
        print(f"✅ Inserted into '{collection_name}' with _id: {result.inserted_id}")
        return result.inserted_id
    except errors.DuplicateKeyError as e:
        print(f"❌ Duplicate key error: {e}")
    except errors.PyMongoError as e:
        print(f"❌ Insert error: {e}")


# FUNCTIONS FOR TASK 3.2


def find_active_students(db: Database) -> List[Dict]:
    """Find all users who are active students."""
    return list(db.users.find({"role": "student", "isActive": True}))


def get_courses_with_instructors(db: Database) -> List[Dict]:
    """Retrieve course details along with instructor information."""
    pipeline = [
        {
            "$lookup": {
                "from": "users",
                "localField": "instructorId",
                "foreignField": "_id",
                "as": "instructor",
            }
        },
        {"$unwind": "$instructor"},
    ]
    return list(db.courses.aggregate(pipeline))


def get_courses_by_category(db: Database, category: str) -> List[Dict]:
    """Get all courses that belong to a specific category."""
    return list(db.courses.find({"category": category}))


def get_students_in_course(db, course_id):
    course = db.courses.find_one({"_id": course_id})
    if not course:
        return None, []

    pipeline = [
        {"$match": {"courseId": course_id}},
        {
            "$lookup": {
                "from": "users",
                "localField": "studentId",
                "foreignField": "_id",
                "as": "student",
            }
        },
        {"$unwind": "$student"},
        {
            "$project": {
                "_id": 0,
                "student._id": 1,
                "student.firstName": 1,
                "student.lastName": 1,
            }
        },
    ]

    enrollment_students = list(db.enrollments.aggregate(pipeline))
    students = [doc["student"] for doc in enrollment_students]

    return course["title"], students


def search_courses_by_title(db, keyword):
    return list(
        db.courses.find(
            {"title": {"$regex": keyword, "$options": "i"}}  # case-insensitive
        )
    )


# UPDATE FUNCTIONS
def update_document(db, collection_name, filter_query, update_data):
    """
    Generic update function for any collection and fields.

    Args:
        db: MongoDB database object.
        collection_name: string, name of the collection (e.g. "users", "courses").
        filter_query: dict, filter to match documents to update.
        update_data: dict, the update operations to perform (e.g. {"$set": {...}}).

    Returns:
        UpdateResult object.
    """
    collection = db[collection_name]
    result = collection.update_one(filter_query, update_data)
    return result


# DELETE FUNCTIONS


def soft_delete_user(db, user_id):
    result = db.users.update_one({"_id": user_id}, {"$set": {"isActive": False}})
    return result.modified_count


def delete_document(db, collection_name, filter_query):
    collection = db[collection_name]
    result = collection.delete_one(filter_query)
    return {"deleted_count": result.deleted_count}


# TASK 4.1: Complex Queries


def find_courses_in_price_range(db, min_price, max_price):
    courses = db.courses.find({"price": {"$gte": min_price, "$lte": max_price}})
    return list(courses)


def find_recent_users(db, months):
    cutoff_date = datetime.utcnow() - timedelta(days=30 * months)
    users = db.users.find({"dateJoined": {"$gte": cutoff_date}})
    return list(users)


def find_courses_by_tags(db, tags):
    courses = db.courses.find({"tags": {"$in": tags}})
    return list(courses)


def find_assignments_due_next_week(db):
    now = datetime.utcnow()
    next_week = now + timedelta(days=7)
    assignments = db.assignments.find({"dueDate": {"$gte": now, "$lte": next_week}})
    return list(assignments)


# Task 4.2: Aggregation Pipeline


def get_enrollment_stats(db):
    pipeline = [
        {"$group": {"_id": "$courseId", "totalEnrollments": {"$sum": 1}}},
        {
            "$lookup": {
                "from": "courses",
                "localField": "_id",
                "foreignField": "_id",
                "as": "course",
            }
        },
        {"$unwind": "$course"},
        {
            "$project": {
                "_id": 0,
                "courseId": "$_id",
                "courseTitle": "$course.title",
                "totalEnrollments": 1,
            }
        },
    ]
    return list(db.enrollments.aggregate(pipeline))


def get_avg_course_rating(db):
    pipeline = [{"$group": {"_id": None, "averageRating": {"$avg": "$rating"}}}]
    result = list(db.courses.aggregate(pipeline))
    return result[0]["averageRating"] if result else None


def group_courses_by_category(db):
    pipeline = [
        {
            "$group": {
                "_id": "$category",
                "count": {"$sum": 1},
                "courses": {"$push": "$title"},
            }
        },
        {"$project": {"_id": 0, "category": "$_id", "count": 1, "courses": 1}},
    ]
    return list(db.courses.aggregate(pipeline))


# Student Performance Analysis
# Average grade per student


def get_avg_grade_per_student(db):
    pipeline = [
        {"$match": {"grade": {"$ne": None}}},
        {"$group": {"_id": "$studentId", "averageGrade": {"$avg": "$grade"}}},
        {
            "$lookup": {
                "from": "users",
                "localField": "_id",
                "foreignField": "_id",
                "as": "student",
            }
        },
        {"$unwind": "$student"},
        {
            "$project": {
                "_id": 0,
                "studentId": "$_id",
                "firstName": "$student.firstName",
                "lastName": "$student.lastName",
                "averageGrade": {"$round": ["$averageGrade", 2]},
            }
        },
        {"$sort": {"averageGrade": -1}},
    ]
    return list(db.submissions.aggregate(pipeline))


# Completion rate by course


def get_completion_rate_by_course(db):

    enrollments = list(
        db.enrollments.aggregate(
            [{"$group": {"_id": "$courseId", "enrolled": {"$sum": 1}}}]
        )
    )

    submissions = list(
        db.submissions.aggregate(
            [
                {
                    "$lookup": {
                        "from": "assignments",
                        "localField": "assignmentId",
                        "foreignField": "_id",  # ← since assignmentId is actually _id
                        "as": "assignment",
                    }
                },
                {"$unwind": "$assignment"},
                {
                    "$group": {
                        "_id": {
                            "courseId": "$assignment.courseId",
                            "studentId": "$studentId",
                        }
                    }
                },
                {"$group": {"_id": "$_id.courseId", "submitted": {"$sum": 1}}},
            ]
        )
    )

    result = {}
    for e in enrollments:
        result[e["_id"]] = {"enrolled": e["enrolled"], "submitted": 0}

    for s in submissions:
        if s["_id"] in result:
            result[s["_id"]]["submitted"] = s["submitted"]

    return [
        {
            "courseId": course_id,
            "enrolled": data["enrolled"],
            "submitted": data["submitted"],
            "completionRate": (
                round((data["submitted"] / data["enrolled"]) * 100, 2)
                if data["enrolled"] > 0
                else 0
            ),
        }
        for course_id, data in result.items()
    ]


# Top-performing students
def get_top_performing_students(db, limit):
    pipeline = [
        {"$match": {"grade": {"$ne": None}}},
        {
            "$group": {
                "_id": "$studentId",
                "averageGrade": {"$avg": "$grade"},
                "submissionCount": {"$sum": 1},
            }
        },
        {"$sort": {"averageGrade": -1}},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "users",
                "localField": "_id",
                "foreignField": "_id",
                "as": "student",
            }
        },
        {"$unwind": "$student"},
        {
            "$project": {
                "studentId": "$_id",
                "averageGrade": {"$round": ["$averageGrade", 2]},
                "submissionCount": 1,
                "name": {"$concat": ["$student.firstName", " ", "$student.lastName"]},
            }
        },
    ]
    return list(db.submissions.aggregate(pipeline))


# Instructor Analytics
# Total students taught by each instructor


def get_total_students_per_instructor(db):
    pipeline = [
        {
            "$lookup": {
                "from": "enrollments",
                "localField": "_id",  # _id in courses
                "foreignField": "courseId",
                "as": "enrollments",
            }
        },
        {"$unwind": "$enrollments"},
        {
            "$group": {
                "_id": "$instructorId",
                "totalStudents": {"$addToSet": "$enrollments.studentId"},
            }
        },
        {
            "$project": {
                "instructorId": "$_id",
                "totalStudents": {"$size": "$totalStudents"},
                "_id": 0,
            }
        },
    ]
    return list(db.courses.aggregate(pipeline))


# Average course rating per instructor
def get_avg_rating_per_instructor(db):
    pipeline = [
        {"$match": {"rating": {"$ne": None}}},
        {"$group": {"_id": "$instructorId", "avgRating": {"$avg": "$rating"}}},
        {"$project": {"instructorId": "$_id", "avgRating": 1, "_id": 0}},
    ]
    return list(db.courses.aggregate(pipeline))


# Revenue generated per instructor
def get_revenue_per_instructor(db):
    pipeline = [
        {
            "$lookup": {
                "from": "enrollments",
                "localField": "_id",
                "foreignField": "courseId",
                "as": "enrollments",
            }
        },
        {"$unwind": "$enrollments"},
        {"$group": {"_id": "$instructorId", "revenue": {"$sum": "$price"}}},
        {"$project": {"instructorId": "$_id", "revenue": 1, "_id": 0}},
    ]
    return list(db.courses.aggregate(pipeline))


# Advanced Analytics


# Monthly enrollment trends
def get_monthly_enrollment_trends(db, months):

    start_date = datetime.utcnow() - relativedelta(months=months)

    pipeline = [
        {"$match": {"enrolledAt": {"$gte": start_date}}},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$enrolledAt"},
                    "month": {"$month": "$enrolledAt"},
                },
                "enrollments": {"$sum": 1},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}},
        {
            "$project": {
                "_id": 0,
                "year": "$_id.year",
                "month": "$_id.month",
                "enrollments": 1,
            }
        },
    ]
    return list(db.enrollments.aggregate(pipeline))


# Most popular course categories
def get_most_popular_categories(db):
    pipeline = [
        {
            "$lookup": {
                "from": "courses",
                "localField": "courseId",
                "foreignField": "_id",
                "as": "course",
            }
        },
        {"$unwind": "$course"},
        {"$group": {"_id": "$course.category", "enrollmentCount": {"$sum": 1}}},
        {"$sort": {"enrollmentCount": -1}},
    ]
    return list(db.enrollments.aggregate(pipeline))


# Student engagement metrics
def get_student_engagement_metrics(db):
    pipeline = [
        {
            "$group": {
                "_id": "$studentId",
                "assignmentsSubmitted": {"$sum": 1},
                "averageGrade": {"$avg": "$grade"},
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "_id",
                "foreignField": "_id",
                "as": "student",
            }
        },
        {"$unwind": "$student"},
        {
            "$project": {
                "_id": 0,
                "studentId": "$_id",
                "name": {"$concat": ["$student.firstName", " ", "$student.lastName"]},
                "assignmentsSubmitted": 1,
                "averageGrade": {"$round": ["$averageGrade", 2]},
            }
        },
    ]
    return list(db.submissions.aggregate(pipeline))


# Task 5.2: Query Optimization
def analyze_query_performance(db, collection_name, filter_query):
    explain_result = db.command(
        "explain",
        {"find": collection_name, "filter": filter_query},
        verbosity="executionStats",
    )
    pprint(explain_result["executionStats"])
    return explain_result


# Measure Query Time with Python Timing Functions
def time_query(db, collection_name, filter_query, label=""):
    collection = db[collection_name]
    start = time.time()
    result = list(collection.find(filter_query))
    end = time.time()
    duration_ms = round((end - start) * 1000, 2)
    return {"label": label, "count": len(result), "time_ms": duration_ms}


def print_comparison(before, after):
    print(f"\n📊 {before['label']}")
    print(f"  - Before Index: {before['time_ms']} ms")
    print(f"  - After Index:  {after['time_ms']} ms")
    print(f"  - Improvement:  {round(before['time_ms'] - after['time_ms'], 2)} ms")
