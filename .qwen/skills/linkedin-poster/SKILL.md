---
name: linkedin-poster
description: |
  Automatically post on LinkedIn to generate business leads and sales.
  Uses Playwright for browser automation. Supports scheduled posts,
  content templates, and human-in-the-loop approval before posting.
---

# LinkedIn Poster

Automatically post content on LinkedIn to generate business leads.

## Setup

### 1. Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### 2. Create LinkedIn Session

```bash
python scripts/create-linkedin-session.py /path/to/vault
```

Scan QR code or log in to LinkedIn when browser opens.

### 3. Create Content Templates

Create `LinkedIn_Templates.md` in your vault:

```markdown
# LinkedIn Post Templates

## Template 1: Business Update
---
category: business_update
tags: [growth, milestone]
---
Excited to share that [ACHIEVEMENT]! 

This milestone represents [SIGNIFICANCE]. 

Thank you to our amazing team and clients who made this possible.

#Business #Growth #Milestone

## Template 2: Thought Leadership
---
category: thought_leadership
tags: [insights, industry]
---
Here's what I've learned about [TOPIC] after [EXPERIENCE]:

1. [INSIGHT_1]
2. [INSIGHT_2]
3. [INSIGHT_3]

What's your experience? Share in the comments!

#Leadership #Industry #Insights
```

## Usage

### Post Content

```bash
# Create a post (requires approval)
python scripts/linkedin_poster.py /path/to/vault post \
  --template "business_update" \
  --custom-vars "ACHIEVEMENT:Reached 100 clients,SIGNIFICANCE:hard work"

# Schedule a post
python scripts/linkedin_poster.py /path/to/vault schedule \
  --date "2026-03-05T09:00:00" \
  --content "Your post content here"

# List scheduled posts
python scripts/linkedin_poster.py /path/to/vault list
```

### Approval Workflow

1. **AI creates** post draft in `Pending_Approval/`:
   ```markdown
   ---
   type: approval_request
   action: linkedin_post
   scheduled: 2026-03-01T09:00:00
   ---
   
   ## Post Content
   
   Excited to share our latest milestone...
   
   Move to /Approved to post.
   ```

2. **Human reviews** and moves to `Approved/`

3. **Orchestrator posts** to LinkedIn

## Features

- **Templates**: Pre-approved content templates
- **Scheduling**: Post at optimal times
- **Auto-hashtags**: Relevant hashtags based on content
- **Image support**: Attach images to posts
- **Analytics**: Track post performance

## Best Practices

- Post during business hours (9 AM - 5 PM)
- Use 3-5 relevant hashtags
- Include engaging visuals
- Respond to comments within 24 hours
- Mix content types (updates, insights, celebrations)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login failed | Re-create session |
| Post not appearing | Check content length (< 3000 chars) |
| Rate limited | Wait 24 hours between posts |
