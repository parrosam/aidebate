import time
from typing import List
from agent import Debater, Moderator, Statement
from config import DEBATE_TURN_DELAY

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


class Debate:
    def __init__(
        self,
        topic: str,
        debaters: List[Debater],
        format_rules: str,
        moderator: Moderator,
    ):
        self.topic = topic
        self.debaters = debaters
        self.format_rules = format_rules
        self.moderator = moderator
        self.history: List[Statement] = []
        self.current_round_number = 1

    def _construct_prompt(self, debater: Debater) -> str:
        """Constructs the prompt for a given debater."""
        debate_history_str = "\n".join(
            [f"Round {s.round_number} - Speaker: {s.name}\n{s.statement}\n" for s in self.history]
        )
        if not debate_history_str:
            debate_history_str = "The debate has not yet begun."

        return UNIVERSAL_AI_DEBATER_PROMPT.format(
            persona_name=debater.name,
            persona_background_and_beliefs=debater.background_and_beliefs,
            persona_personality_style=debater.personality_style,
            persona_motivations=debater.motivations,
            debate_topic=self.topic,
            stance=debater.stance,
            debate_format_rules=self.format_rules,
            current_round_number=self.current_round_number,
            debate_history=debate_history_str,
        )

    def run(self, max_rounds: int = 10):
        """Runs the debate for a maximum number of rounds."""
        print(f"Debate topic: {self.topic}")
        for i in range(max_rounds):
            self.current_round_number = i + 1
            print(f"\n--- Round {self.current_round_number} ---")
            
            round_statements: List[Statement] = []
            for debater in self.debaters:
                prompt = self._construct_prompt(debater)
                statement_text = debater.generate_statement(prompt)
                
                statement = Statement(
                    name=debater.name,
                    statement=statement_text,
                    round_number=self.current_round_number,
                )
                self.history.append(statement)
                round_statements.append(statement)
                
                print(f"{debater.name}: {statement_text}")
                print("-" * 80)
                time.sleep(DEBATE_TURN_DELAY)

            consensus_reached, winning_stance, stances = self.moderator.check_consensus(
                self.topic, round_statements
            )

            print("\n--- Stances ---")
            for debater, stance in zip(self.debaters, stances):
                debater.current_stance = stance
                print(f"{debater.name}: {debater.current_stance}")

            if consensus_reached:
                print(f"\nConsensus reached! The winning stance is: {winning_stance}")
                return

        print("\nDebate finished without reaching consensus.")
