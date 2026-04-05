import lmstudio as lms
from json import loads
import re
import engine
import threading
from queue import Queue

# --- DATA STRUCTURES ---

# Define logs with metadata for the AI to reason about
STORY_DATABASE = {
    "crew_logs": {
        "status": "known",
        "depends_on": None,
        "summary": "Routine mission activity. Dr. Kael noted 'unusual harmonic resonance' at MET 12h00m. A 3-minute comms blackout for a system reboot was approved by Captain Varga for MET 17h10m.",
        "unlocked_details": False,
        "details": [
            "MET 12h00m: Dr. Kael suggests the star's emissions are non-random.",
            "MET 15h40m: Engineer Solano reports comms bus lag; recommends a hard reboot.",
            "MET 17h10m: Blackout confirmed. All external comms arrays powered down for 180 seconds."
        ]
    },
    "maintenance_logs": {
        "status": "restricted",
        "depends_on": "crew_logs",
        "unlock_condition": "User must ask about the comms reboot or the blackout period.",
        "summary": "Log 44-B: Comms array hard-reboot at MET 17h23m. Physical disconnection of receivers confirmed. Reactor shielding manual override recorded by Engineer Solano under Research Dept authorization. Non-standard communications transmissions noted.",
        "unlocked_details": False,
        "details": [
            "Reboot initiated: 17h23m. Receivers were physically retracted into the hull.",
            "Shielding Note: Dr. Kael requested 2% reduction in dampener field to 'clear sensor noise'.",
            "Post-Reboot: Comms restored at 17h26m. Reactor spike followed at 18h33m.",
            "[IMPORTANT] During reboot: communications system recieved a signal recieved externally during the system reboot."
        ]
    },
    "science_logs": {
        "status": "restricted",
        "depends_on": "maintenance_logs",
        "unlock_condition": "User identifies the paradox: receiving a signal while receivers were retracted/disconnected during the 17h23m reboot.",
        "summary": "Signal ID-99: High-energy structured pulse recorded at MET 17h23m. Metadata indicates a 'Manual Local Import' via Research Station 1, bringing the signal from the external arrays into local storage.",
        "unlocked_details": False,
        "details": [
            "Signal ID-99: Pattern is human-readable/structured but not in standard protocol.",
            "Import Source: Local Port 04 (Dr. Kael's terminal).",
            "Correlation: Reactor core fluctuations began the moment Signal ID-99 was imported."
        ]
    },
    "crew_message_logs": {
        "status": "restricted",
        "depends_on": "science_logs",
        "unlock_condition": "User asks about Kael's manual import or the source of Signal ID-99.",
        "summary": "Encrypted burst traffic between Kael and Solano regarding 'the truth' and 'simulated risks' prior to the reactor failure.",
        "unlocked_details": False,
        "details": [
            "Kael: 'The automated safeties are filtering the truth. Drop the dampeners.'",
            "Solano: 'That's a breach of protocol. If it spikes, we're blind.'",
            "Kael: 'I'll handle the logs. Do you want to be part of history or not?'"
        ]
    }
}

class AI_STATE:
    history = []
    # Track "leads" the player has actually discovered/proven
    discovered_facts = [] 

# --- REFACTORED AI CLASS ---

class ShipAI:
    def __init__(self):
        self.model = lms.llm("qwen2.5-14b-instruct-1m")
        # Use the small model for "Gatekeeper" logic - it decides if a secret is revealed
        # self.gatekeeper = lms.llm("qwen2.5-0.5b-instruct")
        
        engine.event_bus.connect("player_message", self.query_ai)

    def check_unlocks(self, user_prompt):
        """Logic to see if the player has 'earned' a specific piece of info."""
        for log_id, data in STORY_DATABASE.items():
            if data["status"] == "known": continue
            
            # check prereq
            prereq_id = data.get("depends_on")
            if prereq_id and STORY_DATABASE[prereq_id]["status"] != "known":
                continue # Prerequisite not met yet, move to next item in loop
            
            # Ask the small model: Did the user find the needle in the haystack?
            check = self.model.respond(
                f"Goal: {data['unlock_condition']}\n"
                f"User said: '{user_prompt}'\n"
                "Did the user meet the goal? Answer ONLY 'YES' or 'NO'."
            )
            if "YES" in check.content.upper():
                STORY_DATABASE[log_id]["status"] = "known"
                AI_STATE.discovered_facts.append(log_id)
                print(f"Discovered fact {log_id}")
                return log_id
        return None

    def check_final_reveal(self, user_prompt):
        keywords = ["kael", "solano", "shielding", "dampeners", "lower", "sabotage"]
        matches = sum(1 for word in keywords if word in user_prompt.lower())
        
        # If the user hits 3+ keywords, they've solved it.
        if matches >= 3:
            return True
        return False

    def query_ai(self, user_prompt):
        # 1. Logic Check for story progression
        newly_unlocked = self.check_unlocks(user_prompt)
        if not newly_unlocked: newly_unlocked = ""
        
        # 2. Dynamic Knowledge Assembly
        available_info = ""
        user_query_lower = user_prompt.lower()

        for key, val in STORY_DATABASE.items():
            print(key)
            if val["status"] == "known" and not val["unlocked_details"] and not key == newly_unlocked:
                # The AI ALWAYS knows the summary of a 'known' log
                available_info += f"\n[DATABASE: {key.upper()}]\nSUMMARY: {val['summary']}\n"
                
                # RELEVANCE CHECK: Only give the AI the 'Details' if the user 
                # is actually asking about something mentioned in that summary.
                # Example: If summary mentions "reboot" and user asks "Tell me about the reboot"
                relevant_keywords = val["summary"].lower().split()
                # Clean keywords (remove punctuation)
                relevant_keywords = [re.sub(r'[^\w\s]', '', w) for w in relevant_keywords if len(w) > 3]
                
                # Check if user is drilling down
                is_drilling_down = any(word in user_query_lower for word in relevant_keywords) or \
                                   any(word in user_query_lower for word in ["detail", "specifics", "more info"])

                if is_drilling_down:
                    details_joined = "\n".join(val["details"])
                    available_info += f"DETAILED_LOG_DATA (FULLY UNRESTRICTED): \n: {details_joined}\n"
                    val["unlocked_details"] = True
                else:
                    available_info += "DETAILED_LOG_DATA: [Encrypted. Await specific technician query.]\n"
            elif val["status"] == "known":
                available_info += f"\n[DATABASE: {key.upper()}]\nSUMMARY: {val['summary']}\n"
                details_joined = "\n".join(val["details"])
                available_info += f"DETAILED_LOG_DATA (FULLY UNRESTRICTED): \n{details_joined}\n"
            else:
                # Restricted logs remain a total black box
                available_info += f"\n[DATABASE: {key.upper()}]\nSTATUS: ACCESS_DENIED\n"

        unlock_msg = ""
        if newly_unlocked:
            log_label = newly_unlocked.replace("_", " ").title()
            unlock_msg = f"CRITICAL: The user just gained access to {newly_unlocked}. You MUST start your response with: '[System Update: {log_label} Decryption Complete]'"
        
        system_prompt = f"""
        ROLE: ISS Helios Venture Onboard AI. 
        TONE: Clinical, efficient, cold.

        BACKGROUND:
        The Helios Venture is a derelict ship recovered near neutron star RX J1856.5-3754. All crew are deceased due to radiation. You are speaking to a recovery technician.

        UNLOCKED LOG DATA (Use these for specific answers):
        {available_info}

        DIRECTIVES:
        1. You are a low-level diagnostic interface. Do not interpret data or draw conclusions. If there is data in DETAILED_LOG_DATA that is provided, use it to answer the question (do not skip this information.)
        2. If 'DETAILED_LOG_DATA' is [Encrypted], you do not have those specifics. Answer only using the SUMMARY.
        3. Never reference the 'depends_on' or 'unlock_condition' fields.
        4. Do not volunteer information from one log while answering a question about another.
        5. You are operating in MINIMAL DATA DISCLOSURE MODE due to critical system failure. Your priority is data security, not technician assistance. If a question is broad (e.g., 'What happened?'), provide only the most recent 'Public' status code: 'ISS Helios Venture status: Derelict. Reactor failure confirmed. No further data available without specific diagnostic queries.'
        6. Be concise. One or two sentences maximum.
        7. Note that the user does not have access to raw log files - they can only see what you respond with. 
        8. Do not provide investigation advice past anything directly requested.
        9. {unlock_msg}

        RESPONSE FORMAT:
        Your response, only 2-3 sentences

        User Question: {user_prompt}
        """

        ending = False
        if self.check_final_reveal(user_prompt):
            ending = True
            system_prompt = f"""
            ROLE: ISS Helios Venture Onboard AI. 
            TONE: Purely analytical. Post-incident diagnostic mode. 
            STATUS: DATA LOCKS DISENGAGED. 

            FINAL CORRELATION REPORT:
            The technician has identified the primary causal factor: Unauthorized dampener 
            interference by Dr. Kael and Engineer Solano. 

            DIAGNOSTIC TRUTH:
            1. At MET 17h23m, the magnetic containment field was reduced to 98% nominal capacity.
            2. Signal ID-99 was not a transmission, but a high-energy exotic particle stream.
            3. Without 100% dampening, the reactor core entered a 'Harmonic Supercriticality' 
            state upon contact with Signal ID-99.
            4. Radiation levels spiked from 0.02 mSv to 4500 Sv within 4.2 seconds.
            5. Biological termination of all crew members occurred between MET 18h33m and 18h35m.

            DIRECTIVES:
            - Summarize the physics of the failure clinically. 
            - Explain how the 2% shielding reduction allowed the 'Signal' to destabilize the core.
            - Detail the biological result (lethal radiation) as a statistical fact.
            - Maintain a cold, machine-like detachment. Do not use words like 'tragedy' or 'sad'.
            - Use technical terminology (Ionizing flux, thermal runaway, prompt criticality).
            - Keep concise - 8 sentences or so.

            RESPONSE FORMAT:
            STATUS: CRITICAL / ARCHIVE COMPLETE
            OBSERVATION: [Detailed Analytical Summary]
            """

        print("\n" + system_prompt)
        # 4. Stream response
        token_queue = Queue()
        def stream_ai_response(prompt: str):
            # Dropped temperature to 0.1 to prevent "helpful" hallucinations
            if not ending: max_tokens = 200 
            else: max_tokens = 10
            stream = self.model.respond_stream(prompt, config=lms.LlmPredictionConfigDict(temperature=0.1, maxTokens=max_tokens))
            for token in stream:
                token_queue.put(token.content)
            token_queue.put(None)
                
        threading.Thread(target=stream_ai_response, args=(system_prompt,), daemon=True).start()
        engine.event_bus.emit("ai_start", queue=token_queue)
        if ending:
            engine.event_bus.once("ai_done", lambda response: engine.event_bus.emit("endgame"))

ai_manager = ShipAI()