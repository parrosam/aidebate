from agent import Debater, Moderator
from config import CONSENSUS_THRESHOLD,AI_MODEL, DEBATE_TURN_DELAY


def main():
    """Sets up and runs the AI debate."""
    # Debater setup with detailed personas
    debaters = [
        Debater(
            name="Dr. Evelyn Reed",
            background_and_beliefs="A former AI developer and now a staunch advocate for digital ethics. Believes that unregulated AI poses an existential threat to humanity and that corporations cannot be trusted to self-regulate.",
            personality_style="Calm, articulate, and firm. Uses precise language and appeals to logic and long-term consequences. Avoids emotional appeals but can be stern when challenged on core principles.",
            motivations="To convince others of the urgent need for strong, government-enforced regulations on AI development and deployment.",
            stance="FOR",
            ai_model=AI_MODEL,
        ),
        Debater(
            name="Julian Thorne",
            background_and_beliefs="A tech entrepreneur and venture capitalist who founded a successful AI startup. Believes that regulation stifles innovation and that the free market is the best mechanism to drive progress and solve problems.",
            personality_style="Charismatic, optimistic, and sometimes dismissive of criticism. Tends to focus on the positive potential of AI and frames regulation as a fear-driven obstacle.",
            motivations="To defend the autonomy of the tech industry and promote a future where AI innovation is unrestricted.",
            stance="AGAINST",
            ai_model=AI_MODEL,
        ),
    ]

    # Debate setup
    topic = "Should AI be regulated?"
    format_rules = "Each debater will provide an opening statement, followed by three rounds of rebuttals. A concluding statement will end the debate."
    
    moderator = Moderator(
        agents=debaters, 
        consensus_threshold=CONSENSUS_THRESHOLD,
        topic=topic,
        format_rules=format_rules,
        ai_model=AI_MODEL
    )

    # Run the debate
    moderator.run(turn_delay_seconds=DEBATE_TURN_DELAY, max_rounds=5)


if __name__ == "__main__":
    main()
