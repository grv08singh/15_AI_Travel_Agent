# front end capability
import streamlit as st
from agent import TravelAgent
import config


@st.cache_resource
def get_agent():
    return TravelAgent()


def main():
    st.set_page_config(page_title="AI Travel Planner", page_icon="✈️")
    st.title("✈️ AI Travel Planner Agent")

    agent = get_agent()

    #initialize a session state
    if 'answers' not in st.session_state:
        st.session_state.answers = []
        st.session_state.current_q = 0
        st.session_state.planning_done = False
    
    #show questions:
    if not st.session_state.planning_done:
        current_q = st.session_state.current_q

        if current_q < len(config.QUESTIONS):
            st.subheader(f"Question {current_q + 1} of {len(config.QUESTIONS)}")
            st.write(config.QUESTIONS[current_q])

            answer = ""

            if current_q == 0:
                col1, col2 = st.columns(2)
                with col1:
                    dest = st.text_input("Destination")
                with col2:
                    dates = st.text_input("Dates: e.g. October 20-26, 2026")
                answer = f"{dest} in {dates}" if dest and dates else ""

            elif current_q == 1:
                answer = str(st.number_input("Days", min_value=1, max_value=30, value=5))

            elif current_q == 2:
                budget = st.number_input("Budget in Euro", min_value=100, value=1000)
                answer = str(budget)

            elif current_q == 3:
                answer = st.text_input("Nationality", value="Indian")

            elif current_q == 4:
                st.write("Select your interests (choose multiple):")
                col1, col2 = st.columns(2)
                with col1:
                    culture = st.checkbox("Culture")
                    food = st.checkbox("Food")
                with col2:
                    nature = st.checkbox("Nature")
                    nightlife = st.checkbox("Nightlife")
                custom_interest = st.text_input("Or type your own interests:")

                #combine all in one place
                selected = []
                if culture:
                    selected.append("culture")
                if food:
                    selected.append("food")
                if nature:
                    selected.append("nature")
                if nightlife:
                    selected.append("nightlife")
                if custom_interest:
                    for cust_int in custom_interest.split(","):
                        selected.append(cust_int.strip())

                answer = ", ".join(selected) if selected else ""

            if st.button("Next") and answer:
                st.session_state.answers.append(answer)
                st.session_state.current_q += 1
                st.rerun() #always do this else it won't work

        elif current_q >= len(config.QUESTIONS) and not st.session_state.planning_done:
            with st.spinner("Planning your trip..."):
                itinerary = agent.plan_trip(st.session_state.answers)
                st.session_state.itinerary = itinerary
                st.session_state.planning_done = True
            st.rerun()

    else:
        st.success("Your itinerary is ready!")
        st.markdown(st.session_state.itinerary)

        st.download_button(
            "Download Itinerary",
            st.session_state.itinerary,
            file_name="travel_itinerary.md",
            mime="text/markdown",
        )

        if st.button("Plan another trip"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    main()