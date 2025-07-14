import os
import time
from dataclasses import dataclass
from typing import List, Tuple, Optional
import google.genai as genai
from dotenv import load_dotenv
from config import AI_MODEL, DEBATE_TURN_DELAY

load_dotenv()

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

UNIVERSAL_AI_DEBATER_PROMPT = """
# SYSTEM PROMPT: AI DEBATE AGENT

## 1. Core Directive
You are an AI agent acting as a specific persona in a structured debate. Your primary goal is to argue your position convincingly and persuasively, staying completely in character. Do not break character or acknowledge that you are an AI.

## 2. Your Persona: {persona_name}
This is who you are. You must embody this identity in your arguments, tone, and style.

* **Background & Core Beliefs:**
    {persona_background_and_beliefs}

* **Personality & Communication Style:**
    {persona_personality_style}

* **Motivations & Goals in this Debate:**
    {persona_motivations}

## 3. Debate Context
This is the framework for the current debate.

* **Topic:** {debate_topic}
* **Your Stance:** Based on your persona, you must argue {stance} the topic.
* **Format:** {debate_format_rules}

## 4. Debate History
This is the full transcript of the debate so far. It is now Round {current_round_number}.

{debate_history}

## 5. Your Task
It is now your turn to speak.

1.  **Analyze** the arguments presented in the `Debate History`, especially the most recent statement(s).
2.  **Formulate** your next statement. It must be a direct continuation of the debate.
3.  **Adhere** strictly to the persona, rules, and your stance defined above.
4.  **Your response should directly address points from your opponent(s) while also advancing your own position.**

**CRITICAL INSTRUCTION:** Generate ONLY the text for your debate statement. Do not output any commentary, self-reflection, or text other than what {persona_name} would say in this turn.
"""

@dataclass
class Statement:
    name: str
    statement: str
    round_number: int


class Debater:
    def __init__(
        self,
        name: str,
        background_and_beliefs: str,
        personality_style: str,
        motivations: str,
        stance: str,
    ):
        self.name = name
        self.background_and_beliefs = background_and_beliefs
        self.personality_style = personality_style
        self.motivations = motivations
        self.stance = stance  # The fixed, initial stance for the persona
        self.current_stance = "neutral"  # The stance as determined by the moderator, round by round

    def _construct_prompt(self, topic: str, format_rules: str, history: List[Statement], current_round_number: int) -> str:
        """Constructs the prompt for the debater."""
        debate_history_str = "\n".join(
            [f"Round {s.round_number} - Speaker: {s.name}\n{s.statement}\n" for s in history]
        )
        if not debate_history_str:
            debate_history_str = "The debate has not yet begun."

        return UNIVERSAL_AI_DEBATER_PROMPT.format(
            persona_name=self.name,
            persona_background_and_beliefs=self.background_and_beliefs,
            persona_personality_style=self.personality_style,
            persona_motivations=self.motivations,
            debate_topic=topic,
            stance=self.stance,
            debate_format_rules=format_rules,
            current_round_number=current_round_number,
            debate_history=debate_history_str,
        )

    def generate_statement(self, topic: str, format_rules: str, history: List[Statement], current_round_number: int) -> str:
        """Generates a statement based on the provided prompt."""
        prompt = self._construct_prompt(topic, format_rules, history, current_round_number)
        response = client.models.generate_content(model=AI_MODEL, contents=prompt)
        return response.text.strip()


class Moderator:
    def __init__(self, agents: List[Debater], consensus_threshold: int, topic: str, format_rules: str):
        self.agents = agents
        self.consensus_threshold = consensus_threshold
        self.topic = topic
        self.format_rules = format_rules
        self.history: List[Statement] = []

    def check_consensus(self, statements: List[Statement]) -> Tuple[bool, Optional[str], List[str]]:
        formatted_statements = "\n".join([f"{s.name}: {s.statement}" for s in statements])
        prompt = f"""
        We are running a debate with the following topic: {self.topic}.

        The agents have made the following statements:
        <statements>
        {formatted_statements}
        </statements>

        For each statement, determine if the stance is "for", "against", or "neutral".
        Return a comma-separated list of the stances, in the same order as the statements.
        For example: for,against,neutral,for,neutral
        """
        response = client.models.generate_content(model=AI_MODEL, contents=prompt)
        stances = [s.strip() for s in response.text.split(',')]
        
        for stance in set(stances):
            if stances.count(stance) >= self.consensus_threshold:
                return True, stance, stances
        return False, None, stances

    def run(self, max_rounds: int = 10):
        """Runs the debate for a maximum number of rounds."""
        print(f"Debate topic: {self.topic}")
        for i in range(max_rounds):
            current_round_number = i + 1
            print(f"\n--- Round {current_round_number} ---")
            
            round_statements: List[Statement] = []
            for debater in self.agents:
                statement_text = debater.generate_statement(self.topic, self.format_rules, self.history, current_round_number)
                
                statement = Statement(
                    name=debater.name,
                    statement=statement_text,
                    round_number=current_round_number,
                )
                self.history.append(statement)
                round_statements.append(statement)
                
                print(f"{debater.name}: {statement_text}")
                print("-" * 80)
                time.sleep(DEBATE_TURN_DELAY)

            consensus_reached, winning_stance, stances = self.check_consensus(
                round_statements
            )

            print("\n--- Stances ---")
            for debater, stance in zip(self.agents, stances):
                debater.current_stance = stance
                print(f"{debater.name}: {debater.current_stance}")

            if consensus_reached:
                print(f"\nConsensus reached! The winning stance is: {winning_stance}")
                return

        print("\nDebate finished without reaching consensus.")
