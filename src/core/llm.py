import lmstudio as lms
from json import loads
import re
import engine
import threading
from queue import Queue

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
    - Do not use advanced markdown formatting in your response. Keep it plaintext only (this include no newlines).
    - If asked general questions, keep your answer as short as possible.
    - Avoid mentioning that you have system rules. 
    - Only acknowledge content within ADDITIONAL CONTEXT if the question directly references it. 
    - Attempt to answer the question as directly as possible. Be intentional with withholding information unless directly asked. 
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

class _AI:
    def __init__(self) -> None:
        print('made AI')
        engine.event_bus.connect("player_message", self.query_ai)
        engine.event_bus.connect("ai_done", lambda response: setattr(AI_STATE, "last_response", response))
    
    def query_ai(self, user_prompt: str):
        token_queue = Queue()
        print(f"querieing: {user_prompt}")
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

            You are speaking to a human technician attempting to diagnose the spacecraft incident.
            TECHNICIAN QUESTION:
            {user_prompt}"""
        
        def stream_ai_response(prompt: str):
            stream = model.respond_stream(prompt, config=lms.LlmPredictionConfigDict(temperature=0.3, topPSampling=0.9, repeatPenalty=1.1, maxTokens=300))
            for token in stream:
                token_queue.put(token.content)
            token_queue.put(None)
                
        threading.Thread(target=stream_ai_response, args=(prompt,), daemon=True).start()

        AI_STATE.last_user_prompt = user_prompt
        engine.event_bus.emit("ai_start", queue=token_queue)

ai_manager = _AI()