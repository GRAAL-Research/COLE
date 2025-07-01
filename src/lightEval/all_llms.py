
llms = {
    "unsloth":[
    "unsloth/Llama-3.2-3B-unsloth-bnb-4bit",

    "unsloth/Llama-3.2-3B-Instruct-unsloth-bnb-4bit",

    "unsloth/mistral-7b-v0.3-bnb-4bit",

    "unsloth/mistral-7b-instruct-v0.3-bnb-4bit",

    "unsloth/phi-4-unsloth-bnb-4bit",

    "unsloth/gemma-2-9b-bnb-4bit",

    "unsloth/gemma-2-9b-it-bnb-4bit",

    "unsloth/gemma-2-27b-bnb-4bit",

    "unsloth/gemma-2-27b-it-bnb-4bit",

    "unsloth/Qwen2.5-1.5B-unsloth-bnb-4bit",

    "unsloth/Qwen2.5-1.5B-Instruct-unsloth-bnb-4bit",

    "unsloth/Qwen2.5-3B-unsloth-bnb-4bit",

    "unsloth/Qwen2.5-3B-Instruct-unsloth-bnb-4bit",

    "unsloth/Qwen2.5-7B-unsloth-bnb-4bit",

    "unsloth/Qwen2.5-7B-Instruct-unsloth-bnb-4bit",

    "unsloth/Qwen2.5-14B-unsloth-bnb-4bit",

    "unsloth/Qwen2.5-14B-Instruct-unsloth-bnb-4bit",

    "unsloth/DeepSeek-R1-Distill-Qwen-7B-unsloth-bnb-4bit",

    "unsloth/DeepSeek-R1-Distill-Llama-8B-unsloth-bnb-4bit",

    "unsloth/DeepSeek-R1-Distill-Qwen-14B-unsloth-bnb-4bit",

    "unsloth/DeepSeek-R1-Distill-Qwen-32B-unsloth-bnb-4bit",
    ],

    "jpacifico":["jpacifico/Chocolatine-14B-Instruct-DPO-v1.2",

    "jpacifico/French-Alpaca-Llama3-8B-Instruct-v1.0",],

    "openLLM-France":["OpenLLM-France/Lucie-7B",

    "OpenLLM-France/Lucie-7B-Instruct-v1.1",],

    "prithivMLmods":["prithivMLmods/Deepthink-Reasoning-7B",

    "prithivMLmods/Deepthink-Reasoning-14B"],

    "allenAI" : ["allenai/OLMo-2-1124-13B-Instruct",

    "allenai/OLMo-2-1124-13B",

    "allenai/OLMo-2-1124-7B-Instruct",

    "allenai/OLMo-2-1124-7B",],

    "mix" : [
        "simplescaling/s1.1-32B",

        "unsloth/granite-3.2-8b-instruct-bnb-4bit",

        "CohereForAI/aya-23-8B",

    ],
    "all": [],

}
for key in llms.keys():
    if isinstance(llms[key],list) and key != "all":
            llms["all"].extend(llms[key])

print(llms["all"])