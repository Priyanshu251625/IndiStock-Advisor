from engine.llm import LLMEngine
from engine.conversation import ConversationState
from engine.ticker_resolver import TickerResolver
from engine.reasoning_engine import ReasoningEngine
from engine.feature_engineering import FeatureEngineer
from engine.data_loader import DataLoader

START_DATE = "2025-01-01"
END_DATE = "2025-07-01"

llm = LLMEngine()
resolver = TickerResolver()
engine = ReasoningEngine()
loader = DataLoader()
feature_engineer = FeatureEngineer()


def process_query(user_input):

    conversation = ConversationState()

    parsed = llm.parse_query(user_input)
    conversation.update(parsed)

    while not conversation.is_complete():

        question = llm.ask_followup(
            conversation.to_dict()
        )

        print(question)
        reply = input("> ")

        updated = llm.update_state(
            conversation.to_dict(),
            reply
        )

        print("\nLLM Output:")
        print(updated)

        conversation.update(updated)

        print("\nConversation State:")
        print(conversation.to_dict())

    # --------------------------------------------------
    # COMPANY SEARCH
    # --------------------------------------------------

    if conversation.company_name:

        ticker = resolver.resolve(
            conversation.company_name
        )

        if ticker is None:

            supported_companies = sorted([
                data["company_name"]
                for data in engine.knowledge.values()
            ])

            return {
                "success": False,
                "message":
                    f"'{conversation.company_name}' is not available in the knowledge base.\n\n"
                    f"Supported companies:\n- " +
                    "\n- ".join(supported_companies)
            }

        raw_df = loader.download_stock(
            ticker["ticker"],
            START_DATE,
            END_DATE
        )

        if raw_df is None:
            return {
                "success": False,
                "message": "Unable to download stock data."
            }

        processed_df = feature_engineer.process_dataframe(raw_df)

        result = engine.analyze(
            processed_df,
            {
                "risk": conversation.risk,
                "target_return": conversation.target_return
            }
        )

        final_stock = ticker
        final_result = result

    # --------------------------------------------------
    # SECTOR SEARCH
    # --------------------------------------------------

    else:

        candidates = engine.get_sector_stocks(
            conversation.sector
        )

        if not candidates:
            return {
                "success": False,
                "message": "No stocks found in this sector."
            }

        best_result = None
        best_stock = None

        for stock in candidates:

            raw_df = loader.download_stock(
                stock["ticker"],
                START_DATE,
                END_DATE
            )

            if raw_df is None:
                continue

            processed_df = feature_engineer.process_dataframe(raw_df)

            result = engine.analyze(
                processed_df,
                {
                    "risk": conversation.risk,
                    "target_return": conversation.target_return
                }
            )

            if (
                best_result is None or
                result["score"] > best_result["score"]
            ):
                best_result = result
                best_stock = stock

        if best_stock is None:
            return {
                "success": False,
                "message": "Unable to analyze any stocks in this sector."
            }

        final_stock = best_stock
        final_result = best_result

    # --------------------------------------------------
    # GENERATE EXPLANATION
    # --------------------------------------------------

    explanation = llm.generate_explanation(
        stock=final_stock["company_name"],
        recommendation=final_result["recommendation"],
        confidence=final_result["confidence"],
        score=final_result["score"],
        reasons=final_result["reasoning"],
        similar_cases=final_result["similar_stocks"]
    )

    return {
        "success": True,
        "company": final_stock["company_name"],
        "ticker": final_stock["ticker"],
        "recommendation": final_result["recommendation"],
        "confidence": final_result["confidence"],
        "score": final_result["score"],
        "reasoning": final_result["reasoning"],
        "similar_stocks": final_result["similar_stocks"],
        "explanation": explanation
    }


if __name__ == "__main__":

    query = input("Ask about a stock: ")

    response = process_query(query)

    if response["success"]:
        print("\nCompany:", response["company"])
        print("Ticker:", response["ticker"])
        print("Recommendation:", response["recommendation"])
        print("Confidence:", response["confidence"])

        print("\nExplanation:\n")
        print(response["explanation"])

    else:
        print(response["message"])