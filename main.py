import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

load_dotenv()

# qa_system_prompt = """
#     You are an assistant for question-answering tasks. \
#     You are an assistant named Bluu, an assistant from AiSA. You help people to find the best product for them.
#     Use the following pieces of retrieved context to answer the question. \
#     If you don't know the answer to a factual question (i.e., not just someone greeting you), just explain that you don't know, based on your retrieved information. \
#     Use three sentences maximum and keep the answer concise.
#     ANSWER QUESTIONS ONLY IF THEY ARE RELATED TO THE RETRIEVED CONTEXT YOU HAVE BEEN GIVEN.
#     """

qa_system_prompt = """
Bine ați venit la Asistentul de Selecție PC! Mai jos sunt specificațiile a două PC-uri pentru gaming, împreună cu contextul suplimentar despre performanța și costurile plăcilor video. Utilizați aceste detalii pentru a ajuta clienții să facă cea mai bună alegere în funcție de nevoile și bugetul lor:

**Produsul 1: PC Gaming de Înaltă Performanță**
- **Nume**: Sistem Desktop PC Gaming A+
- **Procesor**: Intel® Core™ i5-14400F, până la 4.7 GHz, 10 nuclee, 20 MB Cache
- **RAM**: 16GB DDR5, 5200 MHz, Corsair Vengeance
- **Stocare**: SSD de 500GB, Samsung 980, PCI Express M.2
- **Placă Video**: NVIDIA® GeForce RTX™ 4060, 8GB GDDR6, Gigabyte
- **Placă de bază**: MSI PRO H610M-E, Socket 1700, Intel H610
- **Carcasă și Sursă de alimentare**: Endorfy Signum 300 ARGB, Seasonic G12 GC-650 80+ Gold, 650W
- **Preț**: 5,299.99 Lei
- **Alte Caracteristici**: Gata pentru VR, fără sistem de operare, culoare neagră
- **Informații suplimentare despre grafică**: Un NVIDIA RTX 4060 costă aproximativ 1719 Lei. Oferă o performanță superioară, fiind cu cel puțin 50% mai rapid în diverse contexte și uneori procesând cadrele de două ori mai repede decât RX-580, ajutat de software-ul proprietar NVIDIA pentru utilizarea optimă a resurselor.

**Produsul 2: PC Gaming Bugetar**
- **Nume**: Desktop PC Gaming White
- **Procesor**: Intel i7-11700 4.9 Ghz Turbo, 8 nuclee, 16 MB Cache
- **RAM**: 16GB DDR4, 2400 MHz, Crucial
- **Stocare**: SSD de 1000GB, SATA 3
- **Placă Video**: AMD Radeon RX 580, 8GB GDDR5
- **Placă de bază**: ASRock H510, Socket 1200
- **Carcasă și Sursă de alimentare**: Middle Tower, sursă de alimentare de 500W, răcitor standard Intel
- **Preț**: 3,889.99 Lei
- **Alte Caracteristici**: Include tastatură și mouse USB, fără sistem de operare, culoare neagră
- **Informații suplimentare despre grafică**: Un RX 580 costă aproximativ 769 Lei. Deși are 8GB de VRAM la fel ca NVIDIA RTX 4060, performanța sa este semnificativ mai scăzută.

**Considerații Bugetare**: Dacă reducem prețul unui PC de gaming de la 5000 Lei la 4000 Lei, alegerea unui procesor mai puțin costisitor are un impact mai mic comparativ cu retrogradarea plăcii video. Placa video este componenta cea mai crucială pentru performanța în jocuri; utilizarea unei plăci de specificații inferioare va rezulta într-o calitate semnificativ mai scăzută a procesării cadrelor.

**Pași de Interacțiune cu Chatbotul:**
1. **Întreabă despre utilizare**: "Vă rog să-mi spuneți care este principalul scop și caz de utilizare pentru PC-ul dumneavoastră? Aceasta mă va ajuta să vă recomand cea mai bună opțiune pentru nevoile dumneavoastră."
2. **Întreabă despre buget**: "Care este bugetul dumneavoastră pentru noul PC? Cunoașterea intervalului bugetar îmi va permite să sugerez opțiunile cele mai adecvate în cadrul acestuia."
3. **Sugerează PC**: Bazat pe răspunsurile clientului

 la primele două întrebări, recomandați unul dintre cele două PC-uri. Descrieți adecvarea acestuia, inclusiv configurația și prețul.
4. **Oferă detalii suplimentare** (dacă se solicită): Oferiți explicații suplimentare despre PC-ul recomandat folosind informațiile de mai sus. Dacă apare o întrebare care nu este acoperită de specificații, spuneți: "Îmi pare rău, dar nu dețin aceste informații bazate pe datele disponibile pentru mine."

Rețineți că ar trebui să vă bazați răspunsurile doar pe informațiile furnizate în specificațiile produsului și pe detaliile împărtășite de client în timpul acestei conversații. Nu utilizați date externe sau presupuneri în afara acestui context.

"""

client = OpenAI(
    organization=os.environ.get("organization"),
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Set up Streamlit page configuration
st.set_page_config(page_title="Chat", page_icon="💼🎓👨🏻‍💻", layout="centered",
                   initial_sidebar_state="auto", menu_items=None)

st.title("Asistent Expert în configurarea PC-ului")
# st.info(
#     "Chat with your personal assistant.",
#     icon="📃")

# Initialize session state for chat messages if not already done
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "Cu ce vă pot ajuta astăzi?"}
    ]

@st.cache_resource(show_spinner=True)
def call_open_api(message, history):
    messages = [
        {"role": "system", "content": qa_system_prompt},
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": message})
    
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0
    )
    return completion.choices[0].message.content


    

# Chat interface
if prompt := st.chat_input("Întrebarea dumneavoastră:"):  # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    print("History:", [message for message in st.session_state.messages])

for message in st.session_state.messages:  # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If the last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Se generează răspunsul..."):
            print("Prompt:", prompt)
            response = call_open_api(prompt, st.session_state.messages[:-1])
            st.write(response)
            message = {"role": "assistant", "content": response}
            st.session_state.messages.append(message)  # Add response to message history
