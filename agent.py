#core ai agent logic
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.messages import HumanMessage
from typing import TypedDict, Optional
import config

#hit any api
try:
    from tavily import TavilyClient
    tavily_client = TavilyClient(api_key=config.TAVILY_API_KEY) if config.TAVILY_API_KEY else None
except ImportError:
    print("Tavily not installed please install tavily!")
    tavily_client = None
except Exception as e:
    print(f"Error importing Tavily: {e}")
    tavily_client = None
    
class TravelState(TypedDict):
    destination : Optional[str]
    dates : Optional[str]
    duration : Optional[int]
    budget : Optional[float]
    nationality : Optional[str]
    interests : Optional[str]
    current_question: int
    search_results : dict
    itinerary : Optional[str]
    
class TravelAgent:
    def __init__(self):
        self.llm = GoogleGenerativeAI(model="gemini-2.5-flash-lite",
                                      google_api_key=config.GEMINI_API_KEY,
                                      max_output_tokens = 5000,
                                      temperature=0.7)
    
    def guardrail_check(self, state: TravelState):
        prompt = f"""You are a travel assistant guardrail.
Check if these inputs are valid for trip planning.
Destination: {state['destination']}
Nationality: {state['nationality']}
Interests: {state['interests']}

Reply with VALID if all inputs are legitimate travel realated values.
Reply with INVALID: <reason> if any input is non-sensical, harmful, or not related to travel."""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        #text = response.strip()
        text = response
        if "INVALID" in text:
            #return text.replace("INVALID","")
            return text
        return None

    def search_info(self, state:TravelState):
        results = {}
        destination = state['destination']
        dates = state['dates']
        nationality = state['nationality']
        
        if tavily_client:
            try:
                #visa info
                visa_query = f"Visa requirements for {nationality} to {destination} in detail"
                results['visa'] = tavily_client.search(query=visa_query, 
                                                       search_depth="advanced", 
                                                       max_results=3)
                
                #weather info
                month = dates.split()[0] if dates else "March"
                weather_query = f"Weather and climate in {destination} during {month}"
                results['weather'] = tavily_client.search(query=weather_query,
                                                          search_depth="advanced",
                                                          max_results=3)
                #Restaurants
                restaurants_query = f"Best restaurants in {destination}"
                results['restaurants'] = tavily_client.search(query=restaurants_query,
                                                              search_depth="advanced",
                                                              max_results=3)
            except Exception as e:
                print(f"Error during search: {e}")
        state['search_results'] = results
        return state
    
    def generate_itinerary(self, state:TravelState):
        search_context = ""
        for category, data in state['search_results'].items():
            if data and 'results' in data:
                search_context += f"\n{category.capitalize()}:\n"
                for result in data['results'][:2]:
                    search_context += f"- {result.get('content', 'No content')}\n"
        prompt = f"""You are an expert travel planner.
Create a comprehensive travel itinerary using the details and search context below.

## TRIP DETAILS
- Destination: {state['destination']}
- Travel Dates: {state['dates']} ({state['duration']} days)
- Total Budget: €{state['budget']} (excluding flights)
- Passport: {state['nationality']}
- Interests: {state['interests']}

## SEARCH CONTEXT (use this for accuracy)
{search_context}

---

## OUTPUT FORMAT (follow strictly, use markdown)

### 🛂 VISA & ENTRY REQUIREMENTS
- Visa type, cost, processing time for {state['nationality']} passport
- Required documents checklist
- Entry rules (validity, border crossing tips)

### 💰 BUDGET BREAKDOWN
| Category | Estimated Cost (€) |
|---|---|
| Accommodation | |
| Food (all meals) | |
| Local Transport | |
| Activities & Entry fees | |
| Miscellaneous (10% buffer) | |
| **TOTAL** | |

### 🗓️ DAY-BY-DAY ITINERARY
For each day use this structure:
**Day X — [Theme/Area]**
- 🌅 Morning (8–12): [activity + travel tip + cost]
- ☀️ Afternoon (12–17): [activity + travel tip + cost]
- 🌙 Evening (17–22): [activity + dinner recommendation]

### 🥗 VEGETARIAN FOOD GUIDE (strict — no meat/fish)
- 3–4 restaurant recommendations per major area (name, dish, avg price)
- Local vegetarian dishes to try
- Grocery/market tips for self-catering on budget

### 📱 USEFUL APPS & LINKS
- Transport, maps, translation, booking apps relevant to {state['destination']}

### 💡 BUDGET-SAVING TIPS
- 3–5 specific money-saving tips for this destination

Keep all costs in Euro. Be specific with place names, prices, and timings."""
        
        response = self.llm.invoke(prompt)
        state['itinerary'] = response
        return state
    
    def plan_trip(self, answers:list):
        state = TravelState(
            destination=None,
            dates=None,
            duration=None,
            budget=None,
            nationality=None,
            interests=None,
            current_question=0,
            search_results={},
            itinerary=None
        )
        if len(answers) >=5:
            dest_date = answers[0].split(" in ")
            state['destination'] = dest_date[0].strip() if len(dest_date) > 0 else answers[0]
            state['dates'] = dest_date[1].strip() if len(dest_date) > 1 else "March 2026"
            
            try:
                state['duration'] = int(answers[1].split()[0])
            except (ValueError, IndexError):
                state['duration'] = 3

            try:
                state['budget'] = float(answers[2])
            except (ValueError, IndexError):
                state['budget'] = 1000.0
            state['nationality'] = answers[3]
            state['interests'] = answers[4]

        error = self.guardrail_check(state)
        if error:
            return f"Invalid input detected: {error}"

        state = self.search_info(state)
        state = self.generate_itinerary(state)
        return state['itinerary']
