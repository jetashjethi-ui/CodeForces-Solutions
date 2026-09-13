# 🏆 Competitive Programming Solutions

Auto-synced from **LeetCode** & **Codeforces** → GitHub.

Every accepted submission is committed with its **original solve date**, so the GitHub contribution graph lights up green! 🟩

## 📂 Structure

```
├── LeetCode/          ← Accepted LeetCode solutions (with source code)
├── Codeforces/        ← Accepted Codeforces solutions (organized by contest)
├── sync.py            ← Sync script
└── .github/workflows/ ← GitHub Actions (runs every 6 hours)
```

## ⚙️ Setup

### 1. Add GitHub Secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret Name           | Value                                          |
|-----------------------|------------------------------------------------|
| `GIT_NAME`            | Your GitHub username                           |
| `GIT_EMAIL`           | Your GitHub verified email                     |
| `CF_HANDLE`           | Your Codeforces username                       |
| `LEETCODE_SESSION`    | Cookie from leetcode.com (see below)           |
| `LEETCODE_CSRFTOKEN`  | CSRF token cookie from leetcode.com (optional) |

### 2. Get Your LeetCode Session Cookie

1. Log into [leetcode.com](https://leetcode.com)
2. Press `F12` → **Application** tab → **Cookies** → `https://leetcode.com`
3. Copy the value of `LEETCODE_SESSION`
4. (Optional) Also copy `csrftoken`

### 3. Run It!

- **Automatic:** Runs every 6 hours via GitHub Actions
- **Manual:** Go to **Actions** tab → **Sync LeetCode & Codeforces** → **Run workflow**

## 🟩 Making GitHub Green

- Commits use the **exact timestamp** of when you solved each problem
- Uses your verified GitHub email so contributions are credited to you
- Works for both public and private repos (enable "Include private contributions" in GitHub profile settings)
