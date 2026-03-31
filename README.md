# SugarMind


## Solution Abstract: SugarMind

### Project: AI Reflection in Sugar Labs

When I started working on this project, the first thing I did was properly explore and understand the activities in Sugarizer. I went through them myself so I could understand how children actually interact with the platform and what would be the best way to build something meaningful on top of it. The main thing I kept in mind throughout was: **how will this actually make the experience better for the users?**

Since Sugar is mainly used by children aged **5–12 years**, I made sure that the model communicates in a tone that is simple, friendly, and suitable for that age group. When I think about my own childhood, I always enjoyed activities that made me think while still being fun. Sugar already does that really well, and adding a reflection agent ensures that children not only play but also actually learn from what they do.

I focused on providing something meaningful to the community through which children can learn and make the best of their experience.

👉 **Prototype:** *Sugar Mind* (add your link here)

---

## Workflow Visualization

### Workflow Explanation

The core of this system is the **master LLM**, which is fine-tuned on high-quality educational resources, including courses from Harvard University, aligned with concepts from **Educational Psychology**. This ensures that the model behaves like a professional educational psychologist and evaluates children’s responses in a meaningful and age-appropriate way.

Additionally:

* Audio and video pipelines are supported by specialized metrics
* These metrics help the model better understand and analyze user responses

---

### System Workflow

1. **Activity Selection**

   * The user selects an activity inside Sugarizer

2. **Data Retrieval**

   * The system retrieves the corresponding `.json` file from the Journal
   * This file contains all user interaction data

3. **Data Processing**

   * JSON is parsed to extract:

     * User actions
     * Progress
     * Key interaction data

4. **Context Building**

   * Extracted data is sent to the master LLM to build context

5. **User Interaction (SugarMind UI)**

   * User clicks the SugarMind icon
   * Chooses reflection type:

     * Emo Agent
     * Logic Agent
     * General Agent

6. **Input Methods**

   * **Text Input**

     * Evaluated directly by the LLM
   * **Video Input**

     * Uses child-focused engagement and expression metrics
   * **Audio Input**

     * Converted via speech-to-text
     * Evaluated using tone, confidence, and clarity

7. **Multimodal Processing**

   * Inputs are processed based on format
   * Prepared for unified analysis

8. **Response Generation**

   * Sent back to the master LLM
   * Generates:

     * Personalized feedback
     * Next reflective question

This unified approach ensures:

* Consistency
* Better context understanding
* More meaningful interaction

---

## Reflection Agents

The system follows a **three-agent architecture**, inspired by prior work and extended for better learning outcomes.

---

### 1. Emo Agent (Emotional Reflection)

Reflection is not just logical — **emotional growth is equally important**, especially for children.

**Purpose:**

* Encourage emotional expression
* Connect feelings with activities
* Support emotional development

**Behavior:**

* Asks questions about feelings and experiences
* Helps children reflect beyond outcomes

---

### 2. Logic Agent (Critical Thinking)

The Logic agent acts as a **friendly guide** based on educational psychology principles.

**Focus Areas:**

* Critical thinking
* Problem-solving
* Structured reasoning

**Behavior:**

* Encourages reflection on problem-solving approaches
* Helps children think about improvements

---

### 3. Gen Agent (General Reflection)

The Gen agent ensures **overall understanding and learning reinforcement**.

**Focus Areas:**

* What the child learned
* Concept reinforcement
* Simple reflective questioning

**Behavior:**

* Asks broad, easy-to-understand questions
* Confirms conceptual clarity

---

**Current folder directory :**
.
├── activity_json/
│   ├── 3D Volume Activity.json
│   └── Gears Activity (1).json
│
├── Prompts/
│   
│   └── Activity_description/
│       ├── __pycache__/
│       ├── Gears.py
│       └── three_d_Volume.py
│
├── Agents/
│  
│   ├── Emo_agent.py
│   ├── gen_agent.py
│   └── logic_agent.py
│
├── src/
│   ├── __pycache__/
│   
│   ├── Create_vector_store.py
│   ├── inference.py
│   └── video_analysis.py
│
├── Activity_description.lnk
├── get_activity_description.py
├── create_dataset.py
├── create_prompts_files.py
├── index.html
├── new.txt
├── sample_website.py
├── server.py
├── requirements.txt
├── README.md

## 🚀 How to Reproduce & Run Inference

Follow these steps to set up and run **SugarMind** locally:

### 1. Clone the Repository

```bash
git clone <your-repo-link>
cd <your-repo-folder>
```

---

### 2. Create Conda Environment (Python 3.12)

```bash
conda create -n sugarmind python=3.12 -y
conda activate sugarmind
```

---

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

---

### 4. Run the Application

```bash
python SugarMind.py
```

---

### 5. Open in Browser

After running, a **Gradio** link will appear in the terminal (usually like `http://127.0.0.1:7860`).

Open it in your browser to start using **SugarMind** 🎉


