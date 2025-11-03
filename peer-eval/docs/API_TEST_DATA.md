# API Testing Guide with Sample Data

Use these sample JSON payloads to test each API endpoint in Swagger UI (http://localhost:8001/docs)

---

## 🔐 AUTHENTICATION APIs

### 1. POST /api/v1/auth/register - Register New User
```json
{
  "email": "student1@university.edu",
  "password": "SecurePass123!",
  "name": "Alice Johnson",
  "role": "student"
}
```

**More test users:**
```json
{
  "email": "instructor1@university.edu",
  "password": "InstructorPass123!",
  "name": "Dr. Sarah Smith",
  "role": "instructor"
}
```

```json
{
  "email": "bob@university.edu",
  "password": "BobPass123!",
  "name": "Bob Williams",
  "role": "student"
}
```

### 2. POST /api/v1/auth/login - Login
```json
{
  "email": "student1@university.edu",
  "password": "SecurePass123!"
}
```

### 3. POST /api/v1/auth/logout - Logout
No body required - just execute

### 4. GET /api/v1/auth/me - Get Current User
No body required - just execute

---

## 👥 USER MANAGEMENT APIs

### 5. POST /api/v1/users/ - Create User (Direct)
```json
{
  "email": "charlie@university.edu",
  "name": "Charlie Brown",
  "role": "student",
  "password": "Charlie123!"
}
```

**Create multiple students for testing:**
```json
{
  "email": "diana@university.edu",
  "name": "Diana Prince",
  "role": "student",
  "password": "Diana123!"
}
```

```json
{
  "email": "evan@university.edu",
  "name": "Evan Davis",
  "role": "student",
  "password": "Evan123!"
}
```

```json
{
  "email": "fiona@university.edu",
  "name": "Fiona Miller",
  "role": "student",
  "password": "Fiona123!"
}
```

### 6. GET /api/v1/users/ - List All Users
No body required - just execute

### 7. GET /api/v1/users/{user_id} - Get Specific User
Path parameter: `user_id` = 1 (or any id from list users)

### 8. PUT /api/v1/users/{user_id} - Update User
Path parameter: `user_id` = 1

Query parameters:
- `name`: "Alice Johnson Updated"
- `role`: "student"

### 9. DELETE /api/v1/users/{user_id} - Delete User
Path parameter: `user_id` = 5 (use an id you want to delete)

---

## 📁 PROJECT MANAGEMENT APIs

### 10. POST /api/v1/projects/ - Create Project
```json
{
  "title": "Software Engineering Mini Project",
  "description": "Develop a peer evaluation system for team projects",
  "instructor_id": 1,
  "start_date": "2025-09-01",
  "end_date": "2025-12-15",
  "status": "active"
}
```

**More project examples:**
```json
{
  "title": "Mobile App Development",
  "description": "Build a native mobile application for campus services",
  "instructor_id": 1,
  "start_date": "2025-11-01",
  "end_date": "2025-12-31",
  "status": "active"
}
```

```json
{
  "title": "Database Design Project",
  "description": "Design and implement a database for library management",
  "instructor_id": 1,
  "start_date": "2025-10-01",
  "end_date": "2025-11-30",
  "status": "active"
}
```

### 11. GET /api/v1/projects/ - List All Projects
No body required - just execute

### 12. GET /api/v1/projects/{project_id} - Get Project Details
Path parameter: `project_id` = 1

---

## 👨‍👩‍👧‍👦 TEAM MANAGEMENT APIs

### 13. POST /api/v1/teams/ - Create Team
```json
{
  "project_id": 1,
  "name": "Team Alpha",
  "member_ids": [2, 3, 4]
}
```

**More team examples:**
```json
{
  "project_id": 1,
  "name": "Team Beta",
  "member_ids": [5, 6, 7]
}
```

```json
{
  "project_id": 2,
  "name": "Mobile Masters",
  "member_ids": [2, 5, 8]
}
```

### 14. GET /api/v1/teams/ - List All Teams
No body required - just execute

---

## 📝 EVALUATION FORM APIs

### 15. POST /api/v1/forms/ - Create Evaluation Form
```json
{
  "project_id": 1,
  "title": "Midterm Peer Evaluation",
  "description": "Evaluate your team members' contributions at midterm",
  "max_score": 100,
  "criteria": [
    {
      "text": "Code Contribution - Quality and quantity of code written",
      "max_points": 30,
      "order_index": 0
    },
    {
      "text": "Communication - Clear and timely communication with team",
      "max_points": 20,
      "order_index": 1
    },
    {
      "text": "Collaboration - Working well with others, helping teammates",
      "max_points": 20,
      "order_index": 2
    },
    {
      "text": "Problem Solving - Finding solutions to technical challenges",
      "max_points": 15,
      "order_index": 3
    },
    {
      "text": "Reliability - Meeting deadlines and commitments",
      "max_points": 15,
      "order_index": 4
    }
  ]
}
```

**Another form example:**
```json
{
  "project_id": 1,
  "title": "Final Peer Evaluation",
  "description": "End-of-project evaluation of team performance",
  "max_score": 100,
  "criteria": [
    {
      "text": "Overall Technical Skills",
      "max_points": 40,
      "order_index": 0
    },
    {
      "text": "Teamwork and Leadership",
      "max_points": 30,
      "order_index": 1
    },
    {
      "text": "Communication and Documentation",
      "max_points": 30,
      "order_index": 2
    }
  ]
}
```

### 16. GET /api/v1/forms/ - List All Forms
No body required - just execute

---

## ⭐ EVALUATION SUBMISSION APIs

### 17. POST /api/v1/evaluations/ - Submit Evaluation
```json
{
  "form_id": 1,
  "evaluator_id": 2,
  "evaluatee_id": 3,
  "team_id": 1,
  "total_score": 85,
  "scores": [
    {
      "criterion_id": 1,
      "score": 25
    },
    {
      "criterion_id": 2,
      "score": 18
    },
    {
      "criterion_id": 3,
      "score": 19
    },
    {
      "criterion_id": 4,
      "score": 13
    },
    {
      "criterion_id": 5,
      "score": 10
    }
  ],
  "comments": "Excellent team member! Very helpful with debugging and always available for meetings."
}
```

**More evaluation examples:**
```json
{
  "form_id": 1,
  "evaluator_id": 2,
  "evaluatee_id": 4,
  "team_id": 1,
  "total_score": 78,
  "scores": [
    {
      "criterion_id": 1,
      "score": 22
    },
    {
      "criterion_id": 2,
      "score": 16
    },
    {
      "criterion_id": 3,
      "score": 17
    },
    {
      "criterion_id": 4,
      "score": 12
    },
    {
      "criterion_id": 5,
      "score": 11
    }
  ],
  "comments": "Good contribution overall. Could improve communication."
}
```

```json
{
  "form_id": 1,
  "evaluator_id": 3,
  "evaluatee_id": 2,
  "team_id": 1,
  "total_score": 92,
  "scores": [
    {
      "criterion_id": 1,
      "score": 28
    },
    {
      "criterion_id": 2,
      "score": 19
    },
    {
      "criterion_id": 3,
      "score": 20
    },
    {
      "criterion_id": 4,
      "score": 14
    },
    {
      "criterion_id": 5,
      "score": 11
    }
  ],
  "comments": "Outstanding team leader! Very organized and helpful."
}
```

### 18. GET /api/v1/evaluations/ - List Evaluations
No body required - just execute

---

## 📊 REPORTS APIs

### 19. GET /api/v1/reports/project/{project_id} - Project Report
Path parameter: `project_id` = 1

### 20. GET /api/v1/reports/team/{team_id} - Team Report
Path parameter: `team_id` = 1

---

## 🧪 EXAMPLE ENDPOINTS (Working with Supabase)

### 21. POST /api/v1/examples/users - Create User (Example)
Query parameters:
- `name`: "Test User"
- `email`: "test@example.com"

### 22. GET /api/v1/examples/users - List Users (Example)
No parameters required

### 23. GET /api/v1/examples/users/{user_id} - Get User (Example)
Path parameter: `user_id` = 1

### 24. PUT /api/v1/examples/users/{user_id} - Update User (Example)
Path parameter: `user_id` = 1

Query parameters:
- `name`: "Updated Test User"
- `email`: "updated@example.com"

### 25. DELETE /api/v1/examples/users/{user_id} - Delete User (Example)
Path parameter: `user_id` = 5

---

## 📝 COMPLETE TESTING WORKFLOW

### Step 1: Create Test Database Tables
First, run this SQL in Supabase SQL Editor:

```sql
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'student',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add sample instructor
INSERT INTO users (email, name, role) 
VALUES ('instructor@test.com', 'Dr. Smith', 'instructor')
ON CONFLICT (email) DO NOTHING;
```

### Step 2: Test User Creation
1. Open http://localhost:8001/docs
2. POST /api/v1/users/ with 4 students (Alice, Bob, Charlie, Diana)
3. GET /api/v1/users/ to verify - note their IDs

### Step 3: Create Project
1. POST /api/v1/projects/ with "Software Engineering Mini Project"
2. Use instructor_id = 1
3. Note the project_id returned

### Step 4: Create Teams
1. POST /api/v1/teams/ with Team Alpha (students 2, 3, 4)
2. Note the team_id returned

### Step 5: Create Evaluation Form
1. POST /api/v1/forms/ with 5 criteria
2. Note the form_id and all criterion_ids

### Step 6: Submit Evaluations
1. POST /api/v1/evaluations/ - Alice evaluates Bob
2. POST /api/v1/evaluations/ - Alice evaluates Charlie
3. POST /api/v1/evaluations/ - Bob evaluates Alice
4. Etc.

### Step 7: View Reports
1. GET /api/v1/reports/team/1 - See all scores
2. GET /api/v1/reports/project/1 - See project overview

---

## 💡 QUICK TEST COMMANDS (PowerShell)

```powershell
# Test health endpoint
Invoke-RestMethod http://localhost:8001/health

# Create a user
Invoke-RestMethod -Method POST -Uri "http://localhost:8001/api/v1/users/" `
  -ContentType "application/json" `
  -Body '{"email":"test@test.com","name":"Test User","role":"student","password":"pass123"}'

# List all users
Invoke-RestMethod http://localhost:8001/api/v1/users/

# Get specific user
Invoke-RestMethod http://localhost:8001/api/v1/users/1
```

---

## 🎯 Expected Results

After testing, you should have:
- ✅ 5+ users in database
- ✅ 1+ projects
- ✅ 1+ teams with members
- ✅ 1+ evaluation forms with criteria
- ✅ 3+ evaluation submissions
- ✅ Reports showing average scores

**All data visible in Supabase Table Editor!** 🚀
