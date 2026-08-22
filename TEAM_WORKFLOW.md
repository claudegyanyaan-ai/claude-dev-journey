# Team Workflow — Claude Dev Journey

How the three of you keep your local folders in sync via the shared GitHub
repo, so anyone can pick up any project at any time.

Repo: **https://github.com/claudegyanyaan-ai/claude-dev-journey**
Chosen approach: everyone works directly on the `main` branch — pull before
you start, push when you stop. No branches, no Pull Requests. Works well
here because each of you owns a separate project folder (5, 6, 7), so the
three of you are very unlikely to touch the same file at the same time.

---

## Part 1 — One-time setup (do this once, in order)

### 1.1 Repo owner: add both teammates as collaborators

Right now the repo is public, which means anyone can **view** or **download**
it — but only people explicitly added as collaborators can **push changes
back**. Since both teammates need to push their own work, do this first:

1. Go to the repo on GitHub: `https://github.com/claudegyanyaan-ai/claude-dev-journey`
2. Click **Settings** (top menu of the repo, not your account settings).
3. In the left sidebar, click **Collaborators**.
4. Click **Add people**.
5. Type each teammate's GitHub username or the email they signed up with, and send the invite. Repeat for the second teammate.
6. Each teammate needs to check their email (or GitHub notifications) and **accept the invite** — they won't have push access until they do.

### 1.2 Each teammate: clone the repo to their own desktop

Once invited and accepted, each teammate runs this on their own machine
(pick any sensible folder — Desktop is fine, matching what you did):

```powershell
cd "C:\Users\<their name>\Desktop"
git clone https://github.com/claudegyanyaan-ai/claude-dev-journey.git "Claude dev journey"
```

This downloads the entire folder — all 4 completed projects, PLAN.md,
CLAUDE.md, everything — as a fully working local copy with full git history.
No manual copying of files needed.

### 1.3 Each person: set up their own environment for their project

**Important:** `.env` files (which hold your real Anthropic API key) are
intentionally **excluded from git** — that's a security feature, not an
oversight. This means each person must create their own `.env` locally; it
will never come through git, by design.

For whichever project you're assigned (5, 6, or 7 — once its folder exists),
follow that project's own README, which will walk through:
- Creating a virtual environment (`python -m venv .venv`) and activating it
- Installing dependencies (`pip install -r requirements.txt`)
- Copying `.env.example` to `.env` and filling in **your own** Anthropic API key (each person needs their own key from console.anthropic.com — don't share keys over chat/email)

---

## Part 2 — Daily workflow (every single work session)

This is the habit that keeps everyone in sync. Two rules, always in this order:

### Rule 1 — Pull before you start work

```powershell
cd "C:\Users\<you>\Desktop\Claude dev journey"
git pull
```

This downloads anyone else's changes since you last checked. Do this **every
time**, even if you don't think anyone else has pushed anything — it costs
nothing and prevents most problems before they happen.

### Rule 2 — Push when you stop (or after any meaningful chunk of progress)

```powershell
git add -A
git commit -m "short description of what you did"
git push
```

Don't sit on uncommitted work for days — the whole point of this setup is
that if someone has to step away, whatever they last pushed is what the
other two can pick up. Push often, even mid-project (not just at the very
end), especially before ending a session.

---

## Part 3 — Staying out of each other's way

Since each of you owns a separate project folder, you'll rarely touch the
same files. The main files that **are** shared and could clash if two people
edit them at the same time:

- Root `PROGRESS.md`
- `progress-dashboard.html`
- `PLAN.md` / `CLAUDE.md`

If you need to edit one of these, give the other two a quick heads-up first
(a message in your team chat is enough) so you don't overwrite each other's
edits.

### If you ever see the word "CONFLICT" in your terminal

This means git found two different versions of the same lines in the same
file and can't automatically decide which to keep. Don't guess or force
anything — stop, and either ask your mentor (bring the exact terminal output)
or ask a teammate who's more comfortable with git to help resolve it
together. This is a normal, fixable part of team git work, not a sign
something's broken.

---

## Part 4 — If someone leaves partway through a project

Because everyone pushes their work regularly (Rule 2 above), whatever was
last pushed to GitHub is always the "current" state. Any of the three of you
can pick up any project by simply:

```powershell
cd "C:\Users\<you>\Desktop\Claude dev journey"
git pull
```

That pulls the latest version of every project folder, including whatever
the person before you last pushed — no manual file-sharing needed.

---

## Quick reference — commands you'll use constantly

| What you want to do | Command |
|---|---|
| Get everyone else's latest changes | `git pull` |
| See what you've changed | `git status` |
| Stage all your changes | `git add -A` |
| Save a snapshot with a message | `git commit -m "message"` |
| Upload your commits to GitHub | `git push` |
| See project history | `git log --oneline` |
