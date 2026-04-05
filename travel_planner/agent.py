#core ai agent logic
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.messages import HumanMessage
from typing import TypedDict, Optional
from numpy import array
import config

try:
    from tavily import TavilyClient
    tavilily_client = TavilyClient(api_key=config.TAVILY_API_KEY) if config.TAVILY_API_KEY else None
except ImportError:
    print("Tavily client not installed. Please install tavily!")
    tavilily_client = None
except Exception as e:
    print(f"Error importing Tavily: {e}")
    tavilily_client = None

class TravelState(TypedDict):
    destination : Optional[str]
    dates : Optional[str]
    duration : Optional[int]
    budget : Optional[float]
    nationality : Optional[str]
    interests : Optional[str]
    current_question = int
    search_results : dict
    itinerary : Optional[str]

class TravelAgent:
    def __init__(self):
        self.llm = GoogleGenerativeAI(model="gemini-2.0-flash", 
                                      google_api_key=config.GEMINI_API_KEY,
                                      max_output_tokens = 1024,
                                      temperature=0.7)
        
    def search_info(self, state:TravelState):
        results = {}
        destination = state['destination']
        dates = state['dates']
        nationality = state['nationality']

        if tavilily_client:
            try:
                #visa info
                visa_query = f"Visa requirements {nationality} to {destination} 2026 in detail"
                results['visa'] = tavily_client.search(query=visa_query, 
                                                        search_depth="advanced", 
                                                        max_results=3)
                
                #weather info
                month = dates.split()[0] if dates else "March"
                weather_query = f"Weather and climate in {destination} during {month} 2026"
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
    
    def generate_itinerary(self, state: TravelState):
        search_context += f"- {result.get('content','No content')}\n"
        prompt = f"""Create a travel itinerary for:
Destination: {state['destination']}
Dates: {state['dates']}
Duration: {state['duration']} days
Budget: {state['budget']}
Nationality: {state['nationality']}
Interests: {state['interests']}

Search Results:
{search_context}

Please create a detailed day-by-day itinerary including:
- Visa Requirements in detail and depth
- Budget Breakdown
- Day-by-day plan (morning/afternoon/evening)
- Restaurant recommendations and local cuisine (Vegetarian only strictly!)
- Useful links (travel apps names etc)

Format the response as a structured itinerary with clear headings and bullet points.
Make it practical and budget-conscious"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        state['itinerary'] = response.content
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
        if len(answers) >= 5:
            dest_date = answers[0].split(" in ")
            state['destination'] = dest_date[0].strip() if len(dest_date) > 0 else answers[0]
            state['dates'] = dest_date[1].strip() if len(dest_date) > 1 else "October 2026"