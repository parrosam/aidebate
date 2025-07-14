import os
from dataclasses import dataclass
from typing import List, Tuple, Optional
import google.generativeai as genai
from dotenv import load_dotenv
from config import AI_MODEL

load_dotenv()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel(AI_MODEL)

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

    def generate_statement(self, prompt: str) -> str:
        """Generates a statement based on the provided prompt."""
        response = model.generate_content(prompt)
        return response.text.strip()


class Moderator:
    def __init__(self, agents: List[Debater], consensus_threshold: int):
        self.agents = agents
        self.consensus_threshold = consensus_threshold

    def check_consensus(self, topic: str, statements: List[Statement]) -> Tuple[bool, Optional[str], List[str]]:
        formatted_statements = "\n".join([f"{s.name}: {s.statement}" for s in statements])
        prompt = f"""
        We are running a debate with the following topic: {topic}.

        The agents have made the following statements:
        <statements>
        {formatted_statements}
        </statements>

        For each statement, determine if the stance is "for", "against", or "neutral".
        Return a comma-separated list of the stances, in the same order as the statements.
        For example: for,against,neutral,for,neutral
        """
        response = model.generate_content(prompt)
        stances = [s.strip() for s in response.text.split(',')]
        
        for stance in set(stances):
            if stances.count(stance) >= self.consensus_threshold:
                return True, stance, stances
        return False, None, stances
