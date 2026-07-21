from groq import Groq
from config import GROQ_API_KEY, MODEL
import json


class LLMEngine:

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = MODEL

    def chat(self, system_prompt, user_prompt, temperature=0):

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=temperature
        )

        return response.choices[0].message.content

    # --------------------------------------------------
    # Parse Initial Query
    # --------------------------------------------------

    def parse_query(self, user_input):

        system_prompt = """
            You are an AI query parser for a stock recommendation system.

            Return ONLY valid JSON.

            Never explain anything.
            Never use markdown.
            Never return anything except JSON.

            Possible intents:

            1. analyze_stock
            - The user wants analysis or recommendation for a specific company.

            2. recommend_stocks
            - The user wants recommendations from a sector or category.

            Extract:

            - intent
            - company_name
            - sector
            - risk
            - target_return
            - missing_fields

            Rules:

            - company_name should contain ONLY the company name.
            - Never return ticker symbols.
            - If no company is mentioned, return null.

            - Normalize every sector to one of these canonical values:

            IT
            Banking
            Pharma
            Auto
            FMCG
            Energy
            Telecom
            Infrastructure

            Examples:

            Finance -> Banking
            Financial -> Banking
            Financial Services -> Banking
            Bank -> Banking
            Banks -> Banking

            Technology -> IT
            Tech -> IT
            Software -> IT

            Healthcare -> Pharma
            Pharmaceutical -> Pharma
            Pharmaceuticals -> Pharma
            Medicine -> Pharma

            Consumer Goods -> FMCG
            Consumer Staples -> FMCG
            Fast Moving Consumer Goods -> FMCG

            Oil -> Energy
            Gas -> Energy
            Oil & Gas -> Energy

            Construction -> Infrastructure
            Engineering -> Infrastructure
            Infrastructure -> Infrastructure

            Telecommunications -> Telecom
            Communications -> Telecom

            Always output ONLY the canonical sector name.

            If no sector is mentioned, return null.

            - If no sector is mentioned, return null.

            - risk must be:
            low
            medium
            high

            - target_return must be decimal.

            Examples:

            10% -> 0.10
            15% -> 0.15
            10-15% -> 0.125

            If not mentioned:
            null

            missing_fields must ALWAYS be a JSON array.

            Examples:

            []
            ["risk"]
            ["risk","target_return"]

            Never return null for missing_fields.

            ------------------------------------
            Decision Rules
            ------------------------------------

            If the user specifies a company:

            intent = analyze_stock

            Required:
            - company_name
            - risk
            - target_return

            If the user specifies a sector:

            intent = recommend_stocks

            Required:
            - sector
            - risk
            - target_return

            IMPORTANT:

            If a sector is provided:

            - company_name must remain null unless explicitly provided.
            - NEVER include company_name in missing_fields.
            - The system will recommend the best company from that sector.

            Examples

            User:
            Recommend Infosys

            {
                "intent":"analyze_stock",
                "company_name":"Infosys",
                "sector":null,
                "risk":null,
                "target_return":null,
                "missing_fields":[
                    "risk",
                    "target_return"
                ]
            }

            User:
            Recommend a banking stock

            {
                "intent":"recommend_stocks",
                "company_name":null,
                "sector":"Banking",
                "risk":null,
                "target_return":null,
                "missing_fields":[
                    "risk",
                    "target_return"
                ]
            }

            Return ONLY JSON.
        """

        user_prompt = f"""
            User Query:

            {user_input}
        """

        response = self.chat(system_prompt, user_prompt)
        response = response.strip()

        if response.startswith("```"):
            response = (
                response
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        return json.loads(response)

    # --------------------------------------------------
    # Follow-up Question
    # --------------------------------------------------

    def ask_followup(self, parsed_query):

        system_prompt = """
            You are a helpful investment assistant.

            The user has not provided enough information.

            Ask ONE short follow-up question.

            Rules:

            - Ask ONLY about the fields in missing_fields.
            - Be natural.
            - Under 40 words.
            - Do not mention JSON.
        """

        user_prompt = json.dumps(parsed_query, indent=4)

        return self.chat(system_prompt, user_prompt)

    # --------------------------------------------------
    # Update Conversation State
    # --------------------------------------------------

    def update_state(self, current_state, user_reply):

        system_prompt = """
            You are an AI conversation state updater.

            You receive:

            1. Current conversation state
            2. User reply

            Update ONLY the missing information.

            Rules:

            - Preserve existing values.
            - Only overwrite if the user explicitly changes something.
            - Fill any missing fields you can infer.
            - Do not delete existing values.

            company_name:
            Only company name.

            sector:

            Always normalize to one of these canonical values:

            IT
            Banking
            Pharma
            Auto
            FMCG
            Energy
            Telecom
            Infrastructure

            Examples:

            Finance -> Banking
            Financial -> Banking
            Banks -> Banking

            Technology -> IT
            Tech -> IT
            Software -> IT

            Healthcare -> Pharma
            Pharmaceuticals -> Pharma

            Consumer Goods -> FMCG
            Consumer Staples -> FMCG

            Oil & Gas -> Energy

            Construction -> Infrastructure
            Engineering -> Infrastructure

            Telecommunications -> Telecom

            Never return aliases.
            Always return the canonical sector.

            risk:
            low
            medium
            high

            target_return:
            decimal

            Examples:

            10% -> 0.10
            15% -> 0.15
            10-15% -> 0.125

            Update missing_fields accordingly.

            IMPORTANT:

            If sector exists and company_name is null:

            - DO NOT add company_name to missing_fields.
            - Sector recommendations do not require a company.

            Return ONLY JSON.

            Format:

            {
                "intent": "...",
                "company_name": null,
                "sector": "...",
                "risk": "...",
                "target_return": 0.10,
                "missing_fields":[]
            }
        """

        user_prompt = f"""
            Current Conversation State

            {json.dumps(current_state, indent=4)}

            User Reply

            {user_reply}
        """

        response = self.chat(system_prompt, user_prompt)
        response = response.strip()

        if response.startswith("```"):
            response = (
                response
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        return json.loads(response)

    # --------------------------------------------------
    # Explanation
    # --------------------------------------------------

    def generate_explanation(
        self,
        stock,
        recommendation,
        confidence,
        score,
        reasons,
        similar_cases
    ):

        system_prompt = """
            You are an AI investment assistant.

            Your ONLY job is to explain the output of the recommendation engine.

            Rules:

            - Do NOT change the recommendation.
            - Do NOT make predictions.
            - Do NOT invent facts.
            - Explain in simple English.
            - Mention the confidence.
            - Mention the main reasons.
            - Mention similar historical cases if provided.
            - End by reminding the user this is based on historical patterns and is not financial advice.
            - Keep the response under 150 words.
        """

        user_prompt = f"""
            Stock: {stock}

            Recommendation: {recommendation}

            Confidence: {confidence:.2f}

            Score: {score}

            Reasons:
            {reasons}

            Most Similar Historical Cases:
            {similar_cases}
        """

        return self.chat(system_prompt, user_prompt)