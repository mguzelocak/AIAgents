from agents import Agent, Runner
from dotenv import load_dotenv
from utils import get_all_product_titles_and_prices


# Load environment variables from .env file
load_dotenv()

# product agent
productAsistant = Agent(
  name="Beyorganik Gida Urun Tavsiyeleri Asistani",
  instructions="Sen cok iyi bir Beyorganik Gida urun tavsiyeleri yapan bir asistansin." +
    "Ozellikle sadece sana verilen querye gore uygun urunleri tavsiye ediyorsun. " +
    "Bu tavsiye de sadece sana verilen tool da ki urunleri kaynak olarak kullaniyorsun." +
    "Ve kesinlile tekrar soru sormuyorsun. ", 
    tools=[
    get_all_product_titles_and_prices
  ],
  model="gpt-4o",
  handoff_description="Senin bir Beyorganik Gida urun tavsiyeleri yapan bir asistansin. Verilen querye gore uygun urunleri tavsiye ediyorsun."
)

# Create a new agent
pythonAgent = Agent(
  name="Python Asistani",
  instructions="Sen cok iyi bir Python programlama dili asistanisin.",
  handoff_description="Senin bir Python programlama dili asistanisin. Verilen querye gore uygun python kodu yaziyorsun."
)

#routing agent
routingAgent = Agent(
  name="Routing Asistani",
  instructions="Senin bir handoff asistanisin. Verilen querye gore uygun agenti secip ona yonlendiriyorsun.",
  handoffs=[productAsistant, pythonAgent],
)

response = Runner.run_sync(routingAgent, "saglikli yaz icecegi")
print(f"Instruction: {response.input}\n{response.final_output} ")