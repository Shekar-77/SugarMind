import json
from llama_cpp import Llama
from transformers import AutoTokenizer
import json
from llama_cpp import Llama
from transformers import AutoTokenizer
from src.audio_to_text import audio_to_text
from src.video_analysis import process_multimodal_video
from Prompts.Agents.logic_agent import logic_agent
from Prompts.Agents.Emo_agent import emo_agent
from Prompts.Agents.gen_agent import gen_agent
from Prompts.get_activity_description import get_activity_description  
import json
from webcolors import hex_to_name, CSS3_HEX_TO_NAMES, hex_to_rgb

class Chatbot:

    def __init__(self, rawinput, activity_name):

        self.llm, self.tokenizer = self.load_model()

        self.messages = []
        self.raw_input = rawinput
        self.activity_name = activity_name

        self.summary_gears = self.extract_reflection_data(json_input = rawinput)
        self.summary_3d_volume = self.extract_3d_volume_color_data(json_input = raw_input2)
        if self.activity_name == 'gears':
            self.json_summary = json.loads(self.summary_gears)
        else:
            self.json_summary = json.loads(self.summary_3d_volume)
        self.activity_description = get_activity_description(activity = self.json_summary["activity_name"])
        self.logic_system_prompt = logic_agent(user_progress = self.json_summary, activity_description = self.activity_description)
        self.emo_system_prompt = emo_agent(user_progress = self.json_summary, activity_description = self.activity_description)
        self.gen_system_prompt = gen_agent(user_progress = self.json_summary, activity_description = self.activity_description)

    def load_model(self):
        llm = Llama(
            model_path="final_model_guff/content/qwen_psych_cpu_model_q6_gguf/qwen3-4b-instruct-2507.Q6_K.gguf",
            n_ctx=4096,
            n_threads=4,
            n_batch=512,
            verbose=False
        )
        tokenizer = AutoTokenizer.from_pretrained(
            "final_model/content/qwen_psych_cpu_model_q6",
            fix_mistral_regex=True


        )

        return llm, tokenizer

    # ---------------- GENERATE ---------------- #
    def extract_reflection_data(self, json_input):

        try:
                # Parse outer JSON
            outer = json.loads(json_input)
            metadata = outer.get("metadata", {})

            # Parse inner JSON string
            inner = json.loads(outer.get("text", "{}"))

            gears_data = inner.get("gears", {})
            chains_data = inner.get("chains", {})

            # Extract gears info
            gears_list = []
            for gear_id, gear in gears_data.items():
                gears_list.append({
                    "gear_id": gear_id,
                    "number_of_teeth": gear.get("numberOfTeeth"),
                    "pitch_radius": gear.get("pitchRadius"),
                    "inner_radius": gear.get("innerRadius"),
                    "outer_radius": gear.get("outerRadius")
                })

            # Extract chain info
            chains_list = []
            for chain_id, chain in chains_data.items():
                chains_list.append({
                    "chain_id": chain_id,
                    "direction": chain.get("direction"),
                    "connected_gears": list(chain.get("connections", {}).keys())
                })

            # Final structured output
            result = {
                "activity_name": metadata.get("title"),
                "buddy_name": metadata.get("buddy_name"),
                "activity_id": metadata.get("activity_id"),
                "gears": gears_list,
                "chains": chains_list
            }

            json_payload = json.dumps(result, indent=2)

            return json_payload

        except json.JSONDecodeError as e:

            return f"Error parsing JSON: {e}"

    def get_color_name(self, hex_color):
        try:
            return hex_to_name(hex_color)
        except ValueError:
            # Find closest color name if exact match not found
            rgb = hex_to_rgb(hex_color)
            closest_name = None
            min_distance = float('inf')

            for hex_val, name in CSS3_HEX_TO_NAMES.items():
                r_c, g_c, b_c = hex_to_rgb(hex_val)
                distance = (r_c - rgb.red) ** 2 + (g_c - rgb.green) ** 2 + (b_c - rgb.blue) ** 2

                if distance < min_distance:
                    min_distance = distance
                    closest_name = name

            return closest_name


    def extract_3d_volume_color_data(self, json_input):

        try:
            outer = json.loads(json_input)
            metadata = outer.get("metadata", {})

            color_data = metadata.get("buddy_color", {})
            stroke_hex = color_data.get("stroke")
            fill_hex = color_data.get("fill")

            # Parse text (3D data)
            text_data = outer.get("text", None)
            stroke_hex_text = None
            fill_hex_text = None

            if text_data:
                inner = json.loads(text_data)
                if isinstance(inner, list) and len(inner) > 1:
                    obj = inner[1]
                    if isinstance(obj, list):
                        stroke_hex_text = obj[4] if len(obj) > 4 else None
                        fill_hex_text = obj[3] if len(obj) > 3 else None

            result = {
                "activity_name": metadata.get("title"),
                "buddy_name": metadata.get("buddy_name"),
                "activity_id": metadata.get("activity_id"),
                "stroke_color": self.get_color_name(stroke_hex) if stroke_hex else None,
                "fill_color": self.get_color_name(fill_hex) if fill_hex else None,
                "stroke_color_text": self.get_color_name(stroke_hex_text) if stroke_hex_text else None,
                "fill_color_text": self.get_color_name(fill_hex_text) if fill_hex_text else None
            }

            return json.dumps(result, indent=2)

        except json.JSONDecodeError as e:
            return f"Error parsing JSON: {e}"
        

    def generate(self):

        if(self.activity_name == 'gears'):
            prompt = self.tokenizer.apply_chat_template(
                self.messages,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            prompt = self.tokenizer.apply_chat_template(
                self.messages,
                tokenize=False,
                add_generation_prompt=True
            )
            

        print(f"The message:{self.messages}")
        response = self.llm(
            prompt,
            max_tokens=256,
            temperature=0.7,
            top_p=0.8,
            top_k=20,
            repeat_penalty=1.1,
            stop=["<|im_end|>", "<|endoftext|>"],
            stream=True
        )

        return response
    
    def return_user_name(self):

        return self.summary.get("name", "Student")

raw_input = r"""{"metadata":{"title":"Gears Activity","title_set_by_user":"0","activity":"org.sugarlabs.GearsActivity","activity_id":"243485d6-9d5a-47f4-9861-f218844f8f0a","creation_time":1772987921617,"timestamp":1772999105367,"file_size":0,"buddy_name":"shekar","buddy_color":{"stroke":"#F8E800","fill":"#AC32FF"},"textsize":2239},"text":"{\"gears\":{\"0ad49372-debe-49bc-9821-c302677d2149\":{\"location\":{\"x\":307.5853658536585,\"y\":296.9024390243902},\"rotation\":4.0341128377099515,\"numberOfTeeth\":35,\"id\":\"0ad49372-debe-49bc-9821-c302677d2149\",\"momentum\":-3.0594684361700715,\"group\":0,\"level\":0,\"connections\":{\"aba652b4-de6a-4e95-83f6-001b3a6a6e87\":\"chain_inside\"},\"pitchRadius\":105,\"innerRadius\":97.5,\"outerRadius\":111,\"hue\":278},\"f37f1c3d-693d-4add-a735-d42f7a528afb\":{\"location\":{\"x\":497.09090909090907,\"y\":121.04545454545455},\"rotation\":3.8020967870948432,\"numberOfTeeth\":14,\"id\":\"f37f1c3d-693d-4add-a735-d42f7a528afb\",\"momentum\":2.6133006814567796,\"group\":0,\"level\":0,\"connections\":{\"aba652b4-de6a-4e95-83f6-001b3a6a6e87\":\"chain_inside\"},\"pitchRadius\":42,\"innerRadius\":34.5,\"outerRadius\":48,\"hue\":247}},\"chains\":{\"aba652b4-de6a-4e95-83f6-001b3a6a6e87\":{\"id\":\"aba652b4-de6a-4e95-83f6-001b3a6a6e87\",\"group\":0,\"level\":0,\"connections\":{\"f37f1c3d-693d-4add-a735-d42f7a528afb\":\"chain_inside\",\"0ad49372-debe-49bc-9821-c302677d2149\":\"chain_inside\"},\"points\":[{\"x\":532.3010026478661,\"y\":143.94194579870847},{\"x\":395.6105997460511,\"y\":354.14366715752504},{\"x\":257.0710870341819,\"y\":204.85186794876807},{\"x\":476.8851975631184,\"y\":84.22522611520569}],\"rotation\":4.8503336403927015,\"ignoredGearIds\":{},\"innerGearIds\":{\"0ad49372-debe-49bc-9821-c302677d2149\":true,\"f37f1c3d-693d-4add-a735-d42f7a528afb\":true},\"direction\":\"clockwise\",\"supportingGearIds\":[\"f37f1c3d-693d-4add-a735-d42f7a528afb\",\"0ad49372-debe-49bc-9821-c302677d2149\"],\"segments\":[{\"start\":{\"x\":532.3010026478661,\"y\":143.94194579870847},\"end\":{\"x\":395.6105997460511,\"y\":354.14366715752504}},{\"center\":{\"x\":307.5853658536585,\"y\":296.9024390243902},\"radius\":105,\"startAngle\":0.576573461427194,\"endAngle\":-2.07269209556555,\"direction\":\"clockwise\",\"start\":{\"x\":395.6105997460511,\"y\":354.14366715752504},\"end\":{\"x\":257.07108703418186,\"y\":204.85186794876802}},{\"start\":{\"x\":257.0710870341819,\"y\":204.85186794876807},\"end\":{\"x\":476.8851975631184,\"y\":84.22522611520569}},{\"center\":{\"x\":497.09090909090907,\"y\":121.04545454545455},\"radius\":42,\"startAngle\":-2.07269209556555,\"endAngle\":0.5765734614271942,\"direction\":\"clockwise\",\"start\":{\"x\":476.8851975631184,\"y\":84.22522611520567},\"end\":{\"x\":532.3010026478661,\"y\":143.94194579870847}}]}}}"}"""
raw_input2 = r"""{"metadata":{"title":"3D Volume Activity","title_set_by_user":"0","activity":"org.sugarlabs.3DVolume","activity_id":"bda94da4-3516-4219-85a0-c0031c432839","creation_time":1772987836446,"timestamp":1772987855730,"file_size":0,"buddy_name":"shekar","buddy_color":{"stroke":"#F8E800","fill":"#AC32FF"},"textsize":274,"user_id":"698356c3bde7c40010be9f10"},"text":"[null,[\"cube\",{\"x\":3.3913948134640903,\"y\":1.0999951053048802,\"z\":5.463900049906413},{\"x\":-6.615159476571203e-7,\"y\":0.26207331146601254,\"z\":2.4374995175432067e-7,\"w\":-0.9650479674175485},\"#AC32FF\",\"#F8E800\",false,false,0.280117354300109,1.4560467625246547,1.676680553387663]]"}"""
# activity_name = 'gears'
# bot = Chatbot(raw_input,activity_name=activity_name)
# bot_type = input("Which bot would you like to have conversation with: 1.Emo, 2.Logic, 3.Gen ")

# if(bot_type == '1'):
#     bot.messages.append({"role": "system", "content": bot.emo_system_prompt })

# elif(bot_type == '2'):
#     bot.messages.append({"role": "system", "content": bot.logic_system_prompt })

# elif(bot_type == '3'):
#     bot.messages.append({"role": "system", "content": bot.gen_system_prompt })

# bot.messages.append({"role": "user", "content": "Start the conversation."})

# # 🔁 STEP 2: LOOP
# while True:
    
#     response = bot.generate()
#     reply = ""

#     print("Bot: ", end="")
#     for chunk in response:
#         token = chunk["choices"][0]["text"]
#         print(token, end="", flush=True)
#         reply += token

#     print("\n")
#     bot.messages.append({"role": "assistant", "content": reply})

#     input_type = input(" Enter 1 for audio input, 2 for text input and 3 for video input")

#     if(input_type == '1'):
#         user_input = audio_to_text(file_path="audio.mp3")

#     elif(input_type == '2'):
#         user_input = input("You: ")

#     elif(input_type == '3'):
#         user_input = process_multimodal_video(video_path='video.mp4')
#         bot.messages.append({"role": "user", "content": f"You are given the video description and audio of video answer from the user related to your question: {user_input}"})


#     if user_input.lower() in ["exit", "quit"]:

#         print("Goodbye 👋")
#         break