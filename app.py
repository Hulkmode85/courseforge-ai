import os
from flask import Flask, request, render_template_string
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

FORM_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CourseForge AI - Course Creator</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#0a0a0a;color:#e0e0e0;min-height:100vh}
.container{max-width:800px;margin:0 auto;padding:40px 20px}
h1{font-size:2rem;background:linear-gradient(135deg,#f59e0b,#ef4444);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px}
p.sub{color:#888;margin-bottom:30px}
form{background:#151515;border:1px solid #222;border-radius:12px;padding:30px}
label{display:block;margin-bottom:6px;color:#aaa;font-size:.9rem}
input,textarea,select{width:100%;padding:12px;background:#0a0a0a;border:1px solid #333;border-radius:8px;color:#fff;font-size:1rem;margin-bottom:20px}
textarea{height:120px;resize:vertical}
button{width:100%;padding:14px;background:linear-gradient(135deg,#f59e0b,#ef4444);border:none;border-radius:8px;color:#fff;font-size:1.1rem;cursor:pointer;font-weight:600}
button:hover{opacity:.9}
.loading{display:none;text-align:center;padding:20px;color:#f59e0b}
</style>
</head>
<body>
<div class="container">
<h1>CourseForge AI</h1>
<p class="sub">Generate a complete online course outline in seconds</p>
<form method="POST" action="/generate" onsubmit="document.getElementById('load').style.display='block'">
<label>Course Topic</label>
<input type="text" name="topic" placeholder="e.g. Digital Marketing for Small Businesses" required>
<label>Target Audience</label>
<input type="text" name="audience" placeholder="e.g. Small business owners with no marketing experience">
<label>Your Expertise / Key Points to Cover</label>
<textarea name="expertise" placeholder="Describe your knowledge area and any specific topics you want included..." required></textarea>
<label>Course Level</label>
<select name="level">
<option value="beginner">Beginner</option>
<option value="intermediate">Intermediate</option>
<option value="advanced">Advanced</option>
</select>
<label>Desired Course Length</label>
<select name="length">
<option value="mini">Mini Course (4-6 lessons)</option>
<option value="standard">Standard (8-12 lessons)</option>
<option value="comprehensive">Comprehensive (15-20 lessons)</option>
</select>
<button type="submit">Generate Course Outline</button>
</form>
<div id="load" class="loading">Building your course... 30-60 seconds...</div>
</div>
</body>
</html>
"""

RESULT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Course Outline - CourseForge AI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#0a0a0a;color:#e0e0e0;min-height:100vh}
.container{max-width:900px;margin:0 auto;padding:40px 20px}
h1{font-size:1.8rem;background:linear-gradient(135deg,#f59e0b,#ef4444);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:20px}
.section{background:#151515;border:1px solid #222;border-radius:12px;padding:20px;margin-bottom:20px}
.section h3{color:#f59e0b;margin-bottom:10px}
.content{line-height:1.8;white-space:pre-wrap}
.copy-btn{display:inline-block;margin:10px 10px 20px 0;padding:12px 24px;background:linear-gradient(135deg,#f59e0b,#ef4444);border:none;border-radius:8px;color:#fff;cursor:pointer;font-size:1rem;font-weight:600}
.copy-btn:hover{opacity:.9}
a{color:#f59e0b;text-decoration:none}
</style>
</head>
<body>
<div class="container">
<h1>{{ topic }} - Course Outline</h1>
<button class="copy-btn" onclick="let t='';document.querySelectorAll('.content').forEach(c=>t+=c.innerText+'\\n\\n');navigator.clipboard.writeText(t);this.textContent='All Copied!'">Copy Full Outline</button>

<div class="section">
<h3>Course Overview & Marketing Description</h3>
<div class="content">{{ overview }}</div>
</div>
<div class="section">
<h3>Module & Lesson Outline</h3>
<div class="content">{{ modules }}</div>
</div>
<div class="section">
<h3>Quiz Questions & Assignments</h3>
<div class="content">{{ quizzes }}</div>
</div>
<div class="section">
<h3>Marketing Description</h3>
<div class="content">{{ marketing }}</div>
</div>
<br><a href="/">&larr; Create Another Course</a>
</div>
</body>
</html>
"""

@app.route("/")
def index():
    return FORM_PAGE

@app.route("/generate", methods=["POST"])
def generate():
    topic = request.form.get("topic", "")
    audience = request.form.get("audience", "")
    expertise = request.form.get("expertise", "")
    level = request.form.get("level", "beginner")
    length = request.form.get("length", "standard")

    length_map = {"mini": "4-6", "standard": "8-12", "comprehensive": "15-20"}
    lesson_count = length_map.get(length, "8-12")

    prompt = f"""Create a complete online course outline.

Topic: {topic}
Target Audience: {audience}
Expertise/Key Points: {expertise}
Level: {level}
Target Lessons: {lesson_count}

Generate the following sections, clearly labeled:

OVERVIEW:
Write a compelling course overview (2-3 paragraphs): what students will learn, prerequisites, expected outcomes.

MODULES:
Create a detailed module-by-module outline with:
- Module title
- Module description (1 sentence)
- Individual lessons within each module (title + 1-sentence description)
- Learning objectives per module

QUIZZES:
For each module, create:
- 2-3 multiple choice quiz questions (with correct answer marked)
- 1 practical assignment/exercise

MARKETING:
Write a course sales page description including:
- Headline
- 5 key benefits/bullet points
- "This course is for you if..." section
- "By the end of this course you will..." section"""

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    text = msg.content[0].text
    overview = modules = quizzes = marketing = ""

    try:
        if "OVERVIEW:" in text:
            parts = text.split("OVERVIEW:", 1)[1]
            if "MODULES:" in parts:
                overview, parts = parts.split("MODULES:", 1)
                overview = overview.strip()
                if "QUIZZES:" in parts:
                    modules, parts = parts.split("QUIZZES:", 1)
                    modules = modules.strip()
                    if "MARKETING:" in parts:
                        quizzes, marketing = parts.split("MARKETING:", 1)
                        quizzes = quizzes.strip()
                        marketing = marketing.strip()
                    else:
                        quizzes = parts.strip()
                else:
                    modules = parts.strip()
        else:
            overview = text
    except:
        overview = text

    return render_template_string(RESULT_PAGE,
        topic=topic, overview=overview, modules=modules,
        quizzes=quizzes, marketing=marketing)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
