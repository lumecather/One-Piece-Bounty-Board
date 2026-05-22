# 🏴‍☠️ WANTED — Marine Bounty Board

**One Piece Bounty Board** — a web platform for creating and tracking wanted posters in the world of pirates. 
Role-based access, background tasks, and production-ready deployment.

📦 **Repository:** https://github.com/lumecather/One-Piece-Bounty-Board

---

## 📌 Table of Contents

1. [Game Mechanics](#game-mechanics)
2. [Role System & Permissions](#role-system--permissions)
3. [Post Management](#post-management)
4. [Auto Bounty Increase (Celery)](#auto-bounty-increase-celery)
5. [Admin Panel](#admin-panel)
6. [Tech Stack](#tech-stack)
7. [Local Development](#local-development)
8. [Deployment](#deployment)
9. [Note on Folder Names](#note-on-folder-names)

---

## 🎮 Game Mechanics

The project simulates a pirate world where:

- **Regular users** can browse wanted posters and comment
- **Organization members** can create wanted posters
- **Admins** have full control over everything
- **Bounties automatically increase** over time for active posters

---

## 👥 Role System & Permissions

### Available Roles

| Role | Can create posts | Can edit own posts | Can edit any post | Organization required |
|------|------------------|--------------------|--------------------|------------------------|
| **User (Pirate)** | ❌ No | ❌ No | ❌ No | No |
| **Hunter** | ❌ No | ❌ No | ❌ No | No |
| **pirate** | ❌ No | ❌ No | ❌ No | No |
| **Organization Member (Official)** | ✅ Yes | ✅ Yes | ❌ No | ✅ Yes |
| **Admin** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes (auto: "admins") |

### How Roles Work

1. **New users** register with role "User" by default
2. **Users can switch** between "Pirate" and "Hunter" freely in profile settings
3. **Organization Member** and **Admin** roles can only be assigned via admin panel
4. **Admins automatically get** `organization = "admins"`
5. **Organization members cannot change** their role or organization through the edit form — only admin can modify them

### Organization Logic

- Each user can belong to **one marine organization**
- **Posts created by organization members** automatically inherit the author's organization
- **Post visibility in profiles:** Users see posts from their own organization in a special section

---

### Creating a Post

Only **Hunters**, **Organization members**, and **Admins** can create posts.

**Required fields:**
- Title
- Content
- Bounty (in Berry/Belli)
- Image (wanted poster)

**Auto-filled fields:**
- Author (current user)
- Date (auto `now_add`)
- Organization (taken from author's profile)

### Editing a Post

- **Author** can edit their own posts
- **Admin** can edit any post (for moderation)
- **Organization members** can only edit posts within their organization

### Deleting a Post

- **Author** can delete own posts
- **Admin** can delete any post
- Deletion is **permanent** with no confirmation (fast one-click)

### Auto Bounty Increase

Each post can have a **BountyAuto** configuration:

- `enabled` — toggle auto‑increase on/off
- `percent` — increase percentage (default 5%, max 100%)
- `interval_days` — how often to increase (default 7 days)
- `last_run` — timestamp of last increase

**Logic:**  
Every Sunday at 9:00 AM, Celery task runs and increases bounties for all `enabled` posts.

---

## ⚙️ Auto Bounty Increase (Celery)

### How It Works

1. **Celery Beat** scheduler sends a task every Sunday at 09:00
2. **Celery Worker** executes `check_all_posts_bounties` task
3. For each post with `bounty_auto.enabled = True`:
   - Checks if `last_run` is None or > `interval_days`
   - Calculates new bounty:  
     `new_bounty = current_bounty + (current_bounty * percent / 100)`
   - Updates `last_run` to now
   - Saves the post

### Protection Against Integer Overflow

- PostgreSQL `bounty` field uses `BigIntegerField` (max ~9 billion)
- Task caps bounty at 2 billion to prevent overflow

---

## 🖥️ Admin Panel

> *"With great power comes great responsibility... and a lot of buttons."*

### 🔐 Access

Log in with your **superuser credentials**.  
*If you don't have one — create it:*

```bash
python manage.py createsuperuser
```
> then go to /admin page
## 👑 Admin Panel & User Management

### ⚙️ What You Can Manage


| Section | Description |
| :--- | :--- |
| **👥 Users** | Manage accounts, reset passwords, and tweak permissions. |
| **🏴‍☠️ Pirate Profiles** | Change roles, assign organizations, and control who's who. |
| **📜 Posts** | Edit or delete any wanted poster (change bounty, image, organization). |
| **💬 Comments** | Moderate the chaos — delete any comment if necessary. |
| **📈 Bounty Auto** | Configure auto‑increase settings per post. |

### 🎯 Assigning Roles via Admin Panel

1. Go to the **Pirate Profiles** section.
2. Find the pirate you want to upgrade (or downgrade 👀).
3. Change the **Role** field:
   * `Pirate` — Just a regular sailor.
   * `Hunter` — Cool title, no extra powers.
   * `Official` — Can create wanted posters *(requires organization)*.
   * `Admin` — Full control over everything.
4. *For Official:* Fill the **Organization** field (e.g., `"Marines"`, `"Bounty Hunters Guild"`).
5. Hit **Save**.

> 💡 **Pro tip:** Admins automatically get `organization = "admins"` via Django signal — no manual input needed.

### 🧙‍♂️ Admin Superpowers
*What Admins Can Do That Others Can't:*

* **Edit any post** (even if it belongs to another user).
* **Delete** any post or comment instantly.
* **Change roles** of any other user.
* **Assign organizations** to Official members.
* **Full oversight:** See and manage absolutely everything in the admin panel.

---

## ✨ Features

- 👤 **Role-based access** — Users, Officials, Admins.
- 📜 **Wanted Posters** — create, edit, auto‑increase bounty.
- 💬 **Comments** — authenticated users only, linked to profiles.
- 🖼️ **Pirate Profiles** — avatar, organization, role.
- ⚙️ **Background Tasks** — Celery + Redis for auto‑bounty updates.
- 🐳 **Docker Deployment** — fully containerized for VPS.

---

## 🛠️ Tech Stack

**Backend:**  
- Django 5 / Django REST Framework  
- PostgreSQL (production) / SQLite (local)  
- Celery + Redis  
- Gunicorn + Nginx (optional)  

**DevOps:**  
- Docker / Docker Compose  
- GitHub Actions (planned)  

**Other:**  
- Pillow (image resize & optimization)  
- Whitenoise (static files)  
- Django Debug Toolbar  

---

## 🚀 Local Development

### Prerequisites
- Python 3.11+
- PostgreSQL (or SQLite for quick start)
- Redis (for Celery)

Monitoring
Celery Flower is included in the plan but not yet configured.
Logs are available in Celery worker terminal.

---

> I also want to note that the folders are named noob or nob just for fun because at first I didn't intend it as a serious
project for a portfolio, but it turned out cool
