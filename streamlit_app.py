import streamlit as st

from engine.llm import LLMEngine
from engine.conversation import ConversationState
from engine.ticker_resolver import TickerResolver
from engine.reasoning_engine import ReasoningEngine
from engine.feature_engineering import FeatureEngineer
from engine.data_loader import DataLoader

START_DATE = "2025-01-01"
END_DATE = "2025-07-01"

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------

st.set_page_config(
    page_title="IndiStock Advisor",
    page_icon="📈",
    layout="centered"
)

st.title("📈 Welcome to IndiStock Advisor your AI Stock Recommendation Assistant")

st.markdown("""
Ask me about stocks or sectors.

### Examples
- Recommend Infosys
- Suggest banking stocks
- Analyze HDFC Bank
- Show supported companies
- Show supported sectors
""")

# -------------------------------------------------------
# SESSION STATE
# -------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation" not in st.session_state:
    st.session_state.conversation = ConversationState()

if "awaiting_followup" not in st.session_state:
    st.session_state.awaiting_followup = False

if "llm" not in st.session_state:
    st.session_state.llm = LLMEngine()

if "resolver" not in st.session_state:
    st.session_state.resolver = TickerResolver()

if "engine" not in st.session_state:
    st.session_state.engine = ReasoningEngine()

if "loader" not in st.session_state:
    st.session_state.loader = DataLoader()

if "feature_engineer" not in st.session_state:
    st.session_state.feature_engineer = FeatureEngineer()

# -------------------------------------------------------
# DISPLAY CHAT HISTORY
# -------------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------------------------------------------------------
# CHAT INPUT
# -------------------------------------------------------

prompt = st.chat_input("Ask about a stock...")

if prompt:
    normalized_prompt = prompt.lower().strip().rstrip("?.!,")
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)


    if not st.session_state.awaiting_followup:
        if normalized_prompt in [
            "show supported companies",
            "list supported companies",
            "supported companies",
            "what companies do you support",
            "which companies do you support",
        ]:

            companies = sorted(
                data["company_name"]
                for data in st.session_state.engine.knowledge.values()
            )

            response = (
                "### Supported Companies\n\n"
                + "\n".join(f"- {company}" for company in companies)
            )

            with st.chat_message("assistant"):
                st.markdown(response)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

            st.stop()
        
        if normalized_prompt in [
            "show supported sectors",
            "list supported sectors",
            "supported sectors",
            "what sectors do you support",
            "which sectors do you support",
        ]:

            sectors = sorted(
                set(
                    data["sector"]
                    for data in st.session_state.engine.knowledge.values()
                )
            )

            response = (
                "### Supported Sectors\n\n"
                + "\n".join(f"- {sector}" for sector in sectors)
            )

            with st.chat_message("assistant"):
                st.markdown(response)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

            st.stop()

   

    llm = st.session_state.llm
    conversation = st.session_state.conversation

    # ---------------------------------------------------
    # NEW QUERY
    # ---------------------------------------------------

    if not st.session_state.awaiting_followup:

        parsed = llm.parse_query(prompt)
        conversation.update(parsed)

    # ---------------------------------------------------
    # FOLLOW-UP RESPONSE
    # ---------------------------------------------------

    else:

        updated = llm.update_state(
            conversation.to_dict(),
            prompt
        )

        conversation.update(updated)

    # ---------------------------------------------------
    # ASK FOLLOW-UP
    # ---------------------------------------------------

    if not conversation.is_complete():

        response = llm.ask_followup(
            conversation.to_dict()
        )

        st.session_state.awaiting_followup = True

    # ---------------------------------------------------
    # RUN RECOMMENDATION
    # ---------------------------------------------------

    else:

        st.session_state.awaiting_followup = False

        with st.spinner("Analyzing stock data..."):
            user_profile = {
                "risk": conversation.risk,
                "target_return": conversation.target_return
            }

            # ---------------- COMPANY ----------------

            if conversation.company_name:

                ticker = st.session_state.resolver.resolve(
                    conversation.company_name
                )

                if ticker is None:

                    supported_companies = sorted([
                        data["company_name"]
                        for data in st.session_state.engine.knowledge.values()
                    ])

                    response = (
                        f"'{conversation.company_name}' is not available in the knowledge base.\n\n"
                        f"### Supported companies\n"
                        + "\n".join([f"- {company}" for company in supported_companies])
                    )

                    st.session_state.awaiting_followup = False
                    st.session_state.conversation = ConversationState()

                else:

                    raw_df = st.session_state.loader.download_stock(
                        ticker["ticker"],
                        START_DATE,
                        END_DATE
                    )

                    if raw_df is None:

                        response = "Unable to download stock data. Try again later."
                        st.session_state.awaiting_followup = False
                        st.session_state.conversation = ConversationState()

                    else:

                        processed_df = (
                            st.session_state.feature_engineer.process_dataframe(raw_df)
                        )

                        if processed_df is None:
                            response = "Unable to process stock data. Try again later."
                            st.session_state.awaiting_followup = False
                            st.session_state.conversation = ConversationState()

                        else:

                            result = st.session_state.engine.analyze(
                                processed_df,
                                user_profile
                            )

                            explanation = llm.generate_explanation(
                                stock=ticker["company_name"],
                                recommendation=result["recommendation"],
                                confidence=result["confidence"],
                                score=result["score"],
                                reasons=result["reasoning"],
                                similar_cases=result["similar_stocks"]
                            )

                            response = f"""
                                ## 📈 {ticker['company_name']}

                                **Ticker:** {ticker['ticker']}

                                **Recommendation:** {result['recommendation']}

                                **Confidence:** {result['confidence']:.2f}

                                ---

                                {explanation}
                            """

            # ---------------- SECTOR ----------------

            else:

                candidates = st.session_state.engine.get_sector_stocks(
                    conversation.sector
                )

                if not candidates:

                    supported_sectors = sorted(
                        set(
                            data["sector"]
                            for data in st.session_state.engine.knowledge.values()
                        )
                    )

                    response = (
                        f"No stocks found in the '{conversation.sector}' sector.\n\n"
                        "### Supported sectors\n"
                        + "\n".join(f"- {sector}" for sector in supported_sectors)
                    )
                    st.session_state.awaiting_followup = False
                    st.session_state.conversation = ConversationState()

                else:

                    best_result = None
                    best_stock = None

                    for stock in candidates:

                        raw_df = st.session_state.loader.download_stock(
                            stock["ticker"],
                            START_DATE,
                            END_DATE
                        )

                        if raw_df is None:
                            continue

                        processed_df = (
                            st.session_state.feature_engineer.process_dataframe(raw_df)
                        )

                        if processed_df is None:
                            continue

                        result = st.session_state.engine.analyze(
                            processed_df,
                            user_profile
                        )

                        if (
                            best_result is None or
                            result["score"] > best_result["score"]
                        ):
                            best_result = result
                            best_stock = stock

                    if best_stock is None:

                        supported_sectors = sorted(
                            set(
                                data["sector"]
                                for data in st.session_state.engine.knowledge.values()
                            )
                        )

                        response = (
                            f"Unable to analyse stock in '{conversation.sector}' sector. Please try with other supported sectors\n\n"
                            "### Supported sectors\n"
                            + "\n".join(f"- {sector}" for sector in supported_sectors)
                        )
                        st.session_state.awaiting_followup = False
                        st.session_state.conversation = ConversationState()

                    else:

                        explanation = llm.generate_explanation(
                            stock=best_stock["company_name"],
                            recommendation=best_result["recommendation"],
                            confidence=best_result["confidence"],
                            score=best_result["score"],
                            reasons=best_result["reasoning"],
                            similar_cases=best_result["similar_stocks"]
                        )

                        response = f"""
                        ## 📈 {best_stock['company_name']}

                        **Ticker:** {best_stock['ticker']}

                        **Recommendation:** {best_result['recommendation']}

                        **Confidence:** {best_result['confidence']:.2f}

                        ---

                        {explanation}
                        """

        # Reset conversation for the next query
        st.session_state.awaiting_followup = False
        st.session_state.conversation = ConversationState()

    # ---------------------------------------------------
    # DISPLAY RESPONSE
    # ---------------------------------------------------

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })