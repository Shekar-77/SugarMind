b = [
    "3D Volume",
    "Xmas Lights",
    "Dollar Street",
    "Tangram",
    "Vote",
    "MindMath",
    "Sprint Math",
    "Curriculum",
    "Chess",
    "Fraction",
    "Falabracman",
    "Exerciser",
    "Gears",
    "Maze Web",
    "Paint",
    "TamTam Micro",
    "Memorize",
    "Physics JS",
    "Calculate",
    "Turtle Blocks JS",
    "Clock Web",
    "Story",
    "Speak",
    "Moon",
    "Record"
]

a = [
    '''def three_d_volume_description():
    return """This activity helps learners understand the concept of volume in three-dimensional objects.\n
Users interact with different 3D shapes and observe how length, width, and height contribute to volume.\n
It encourages spatial visualization by allowing manipulation of shapes.\n
Learners gain a practical understanding of volume calculation through exploration.\n"""''',

    '''def xmas_lights_description():
    return """This activity introduces patterns, sequences, and basic logic through a playful interface.\n
Users create blinking light patterns and control timing and repetition.\n
It helps learners recognize cycles and predict outcomes.\n
The activity promotes creative thinking and pattern recognition.\n"""''',

    '''def dollar_street_description():
    return """This activity builds global awareness and social understanding.\n
Learners explore how families around the world live at different income levels.\n
Real-life images and stories are used to compare housing, food, and daily activities.\n
It encourages empathy and critical thinking about economic diversity.\n"""''',

    '''def tangram_description():
    return """This activity develops spatial reasoning and problem-solving skills.\n
Users arrange geometric pieces to form specific shapes.\n
It challenges learners to think about rotation, symmetry, and composition.\n
The activity strengthens visual logic and creativity.\n"""''',

    '''def vote_description():
    return """This activity introduces the concept of democratic decision-making.\n
Users create polls, cast votes, and view results.\n
It demonstrates how individual choices contribute to group outcomes.\n
Learners understand fairness, participation, and collective decision processes.\n"""''',

    '''def mindmath_description():
    return """This activity focuses on improving mental calculation skills.\n
Learners solve arithmetic problems without using calculators.\n
The activity emphasizes accuracy and logical thinking.\n
It helps build confidence in basic math through repeated practice.\n"""''',

    '''def sprint_math_description():
    return """This activity improves speed and accuracy in arithmetic.\n
Learners answer math questions under strict time limits.\n
It encourages quick thinking and focus.\n
The activity helps develop fluency in basic mathematical operations.\n"""''',

    '''def curriculum_description():
    return """This activity provides structured access to educational content.\n
Learners follow guided lessons and learning paths.\n
It helps organize activities by subject or skill level.\n
The activity supports systematic and self-paced learning.\n"""''',

    '''def chess_description():
    return """This activity teaches strategic thinking and planning.\n
Learners play chess while understanding rules and piece movements.\n
It encourages foresight, patience, and logical reasoning.\n
The game helps develop decision-making skills.\n"""''',

    '''def fraction_description():
    return """This activity helps learners understand fractions visually.\n
Users interact with fraction-based puzzles and representations.\n
It connects numerical values with visual models.\n
The activity strengthens conceptual understanding of fractions.\n"""''',

    '''def falabracman_description():
    return """This activity focuses on vocabulary building and spelling.\n
Learners play word-based games that challenge language skills.\n
It promotes recognition of correct word forms.\n
The activity improves reading and spelling through engagement.\n"""''',

    '''def exerciser_description():
    return """This activity promotes awareness of physical fitness.\n
Users follow guided movements and exercises.\n
It encourages healthy habits and body awareness.\n
The activity links learning with physical activity.\n"""''',

    '''def gears_description():
    return """This activity explains mechanical motion and gear systems.\n
Learners connect gears and observe changes in speed and direction.\n
It demonstrates cause-and-effect relationships.\n
The activity builds basic engineering understanding.\n"""''',

    '''def maze_web_description():
    return """This activity develops logical thinking and navigation skills.\n
Users solve mazes by planning paths.\n
It encourages trial-and-error learning.\n
The activity strengthens problem-solving abilities.\n"""''',

    '''def paint_description():
    return """This activity encourages creative expression through digital drawing.\n
Users draw, color, and design freely.\n
It supports imagination and artistic exploration.\n
The activity helps develop fine motor and creative skills.\n"""''',

    '''def tamtam_micro_description():
    return """This activity introduces music and sound exploration.\n
Learners create rhythms and experiment with beats.\n
It helps understand musical patterns.\n
The activity encourages creativity through sound.\n"""''',

    '''def memorize_description():
    return """This activity improves memory and concentration skills.\n
Users match symbols or images by recall.\n
It strengthens attention and short-term memory.\n
The activity encourages focus through gameplay.\n"""''',

    '''def physics_js_description():
    return """This activity introduces basic physics concepts through simulations.\n
Learners interact with forces, motion, and objects.\n
It allows experimentation in a safe environment.\n
The activity builds conceptual understanding of physics.\n"""''',

    '''def calculate_description():
    return """This activity supports mathematical problem solving.\n
Users perform arithmetic and advanced calculations.\n
It helps verify answers and explore numeric relationships.\n
The activity acts as a learning aid for math.\n"""''',

    '''def turtle_blocks_js_description():
    return """This activity introduces programming through visual blocks.\n
Learners create drawings and patterns using commands.\n
It teaches sequencing and logic.\n
The activity builds foundational coding skills.\n"""''',

    '''def clock_web_description():
    return """This activity helps learners understand time concepts.\n
Users practice reading clocks and tracking time.\n
It reinforces daily time awareness.\n
The activity improves time-management understanding.\n"""''',

    '''def story_description():
    return """This activity supports creative writing and storytelling.\n
Learners write stories using text and images.\n
It encourages imagination and language development.\n
The activity strengthens communication skills.\n"""''',

    '''def speak_description():
    return """This activity helps learners practice pronunciation and listening.\n
Text is converted into spoken audio.\n
Users hear correct pronunciation.\n
The activity supports language learning.\n"""''',

    '''def moon_description():
    return """This activity explains lunar phases and moon cycles.\n
Learners observe changes over time.\n
It connects astronomy concepts visually.\n
The activity improves understanding of celestial movements.\n"""''',

    '''def record_description():
    return """This activity allows capturing audio, photos, and videos.\n
Learners document observations or projects.\n
It supports multimedia learning.\n
The activity encourages creativity and documentation.\n"""'''
]



import os

def create_python_file(folder_name,filename, content):
    try:
        # Create the directory if it does not exist
        # 'exist_ok=True' prevents an error if the directory already exists
        os.makedirs(folder_name, exist_ok=True)
        print(f"Directory '{folder_name}' ensured to exist.")

        # Construct the full file path
        file_path = os.path.join(folder_name, filename)

        # Write the content to the file
        # 'w' mode opens for writing (and creates the file if it doesn't exist)
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"File '{filename}' created successfully in '{folder_name}'.")

    except OSError as e:
        print(f"Error creating file or directory: {e}")

for i in range(len(a)):
        create_python_file('Prompts\Activity_description',f'{b[i]}.py', a[i])

