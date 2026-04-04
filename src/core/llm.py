import lmstudio as lms
from json import loads
import re

model = lms.llm("qwen2.5-14b-instruct-1m", config=lms.LlmLoadModelConfig(context_length=5120))
intent_model = lms.llm("qwen2.5-0.5b-instruct")

class AI_STATE:
    last_user_prompt = ""
    last_response = ""
    
    ship_bio = """
    ISS Helios Venture
    Status: Derelict
    """
    
    ai_rules = """
    - Only use information provided in KNOWLEDGE.
    - Never invent new facts.
    - Some information may be restricted by your directives.
    - If restricted, politely refuse access.
    - Use appropriate terminology for a sci-fi artifical intelligence.
    - Do not offer follow-up questions.
    - If there is provided additional context, only refer to that context. 
    - Do not mention restricted information unless directly asked.
    - Keep responses short and concise, and avoid providing insight or mentioning information not directly asked for.
    """

    background_info = """
    The ship ISS Helios Venture was sent to the Neutron Star RX J1856.5-3754 to conduct research on the star. 
    It jumped into the system on 2118 1/12 at 6:06 GST and lowered it's periapsis to within 250,000km of the star to begin initial measurements.
    At approximately 18 hours and 33 minutes MET a major spike in reactor power output was detected by automated on-board ship systems.
    After automated systems failed to mitigate this spike in power output, a major breach in containment was detected. 
    Radiation readings within the ship after this incident indicate highly lethal levels of radiation.
    After recovery of the ship at GST 2118 3/26 at 16:12 GST (approximately 73 days after last data log), the ship was returned to incorporated space for analysis and inspection.
    The human speaking to the ship's AI is a technician with the goal of determining what happened on this ship.
    """
    
    crew = ["Captain Varga", "Engineer Solano", "Pilot Okoye", "Scientist Chen"]
    current_culprit = "Reactor Failure"
    
    known_data = [
        "crew_logs", "performance_logs"
    ]
    
    restricted_data = [
        "science_logs"
    ]

def query_ai(user_prompt: str):
    intent = intent_model.respond(
    f"""Classify the player's statement.
    Statement: '{user_prompt}'

    Possible classifications:
    - normal_question
    - investigating_signal_anomaly
    - requesting_logs
    Only respond as one of these classifications.
    """)
    
    print(f"Intent: {re.sub(r'<think>.*?</think>', '', intent.content)}")
    
    additional_context = []
    for item in AI_STATE.known_data:
        try:
            with open(f"assets/story/{item}.txt") as f:
                additional_context.append(f.readlines())
        except OSError:
            continue
    
    prompt = f"""
        BACKGROUND:
        {AI_STATE.background_info}
        SYSTEM RULES:
        {AI_STATE.ai_rules}
        
        CREW: {AI_STATE.crew}
        
        KNOWN DATA:
        {AI_STATE.known_data}
        
        ADDITIONAL CONTEXT:
        {additional_context}
        
        CONVERSATION HISTORY:
        USER: {AI_STATE.last_user_prompt}
        RESPONSE: {AI_STATE.last_response}
        
        RESTRICTED DATA: {AI_STATE.restricted_data}
        
        Respond in this format:
        STATUS: [answer/refusal/unknown]
        RESPONSE: <message>

        You are speaking to a human technician attempting to diagnose the spacecraft incident.
        TECHNICIAN QUESTION:
        {user_prompt}"""
    
    output = ""
    for token in model.respond_stream(prompt, config=lms.LlmPredictionConfigDict(temperature=0.3, topPSampling=0.9, repeatPenalty=1.1, maxTokens=300)):
        print(token.content, end="", flush = True)
        output += token.content

    AI_STATE.last_user_prompt = user_prompt
    AI_STATE.last_response = output
    
# print("\n> What happened to the ISS Helios Venture?")
# query_ai("What happened to the ISS Helios Venture?")
# print("\n> What logs are available to you?")
# query_ai("What logs are available to you?")
# print("\n> Is there anything of note in the performance logs?")
# query_ai("Is there anything of not in the performance logs?")

while True:
    try:
        user = input("\n> ")
        query_ai(user)
    except KeyboardInterrupt:
        break