"""
Get AI (chat-gpt-5) to explain the aerosol event
need apply for api with NAMS.

Meng Gao, Sep 30, 2025
"""
import openai
from tqdm import tqdm

def add_hemisphere(deg, is_latitude=True):
    """
    Add hemisphere indicators to the coordinate, formatted to two decimal places.
    
    Args:
        deg (float): The coordinate in decimal degrees.
        is_latitude (bool): True if the coordinate is latitude; False for longitude.
    
    Returns:
        str: A string showing the coordinate rounded to two decimals with hemisphere indication.
    """
    hemisphere = "N" if is_latitude and deg >= 0 else "S" if is_latitude else "E" if deg >= 0 else "W"
    return f"{abs(deg):.2f}° {hemisphere}"  # Limit to two decimals and add hemisphere indicator

def create_ai_input(info, words, requirements=None):
    """
    info contains location, aerosol info
    words: number of words used in output
    lat,lon: in original form can be interpreted in wrong hemisphere (add WE, NS to ensure accuracy)

    requirements: "Explain the aerosol type, event, sources, transport and impacts."

    requirements: "Summarize the aerosol event in terms of aerosol type, possible source and transport in one sentence. \
    Make the information as less vague as possible.
    
    """
    lat, lon = info['center']
    lats, lons = add_hemisphere(lat), add_hemisphere(lon, False)
    aod, aod_err = info['aot'][0], info['aot'][1]
    ssa, ssa_err = info['ssa'][0], info['ssa'][1]
    fvf, fvf_err = info['fvf'][0], info['fvf'][1]
    sph, sph_err = info['sph'][0], info['sph'][1]
    
    input1=(f"For a location near lat={lats}, lon={lons}, \
    with aerosol optical depth (aod)={aod:0.2f}±{aod_err:0.3f}, \
    single scattering albedo (ssa)={ssa:0.2f}±{ssa_err:0.3f}, \
    fine mode volume fraction(fvf)={fvf:0.2f}±{fvf_err:0.3f}, \
    spherical fraction(sph)={sph:0.2f}±{sph_err:0.3f}. \
    Consider the uncertainties (±) in these data. \
    {requirements}\
    Keep total number of words within {words}")
    
    return input1
    
def ask_ai_all(infov_dict, api_key, base_url):
    """
    infov_dict is a dictionary with timestamp as key
    """
    message1v={}
    message2v={}
    #for info in tqdm(infov):
    #for info in tqdm(infov_dict.values()):
    for timestamp1 in tqdm(infov_dict.keys()):
        info = infov_dict[timestamp1]
        try:
            requirements = "Explain the aerosol type, event, sources, transport and impacts."
            input1 = create_ai_input(info, 150, requirements)
            print(input1)
            message1 = call_ai_api_structure(api_key, base_url, input1)
        except:
            message1 = 'over budget'

        #try:
        #    input2 = create_ai_input(info, 70)
        #    print(input2)
        #    message2 = call_ai_api_structure(api_key, base_url, input2)
        #except:
        #    message2 = 'over budget'

        try:
            #shorrt summary
            requirements = "Summarize the aerosol event in terms of aerosol type, possible source and transport in two sentence. Make the information as specific as possible."
            input2 = create_ai_input(info, 30, requirements)
            print(input2)
            message2 = call_ai_api_simple(api_key, base_url, input2)
        except:
            message2 = 'over budget'
            
        message1v[timestamp1]=message1
        message2v[timestamp1]=message2
        
    return message1v, message2v
    
def call_ai_api_structure(api_key, base_url, aerosol_message, max_tokens=None):
    """
    max_tokens are the entire world, if input text is long, adjust the max_tokens accordingly

    remove: 3. **Possible Event**: describe what kind of event this represents (e.g., biomass burning, dust outbreak, sea spray).
    """
    
    client = openai.OpenAI(
       api_key=api_key,
       base_url=base_url
    )
    
    response = client.chat.completions.create(
        model="gpt-5",  
        messages=[
            {"role": "system", "content": 
             """You are an atmospheric scientist. Always respond with a clear structured summary:
             1. **Location**: state coordinates and region.
             2. **Aerosol Type**: describe the likely dominant aerosol. State the values in the format of (AOD x±x, SSA x±x, FVF x±x, sph x±x).
             3. **Sources & Transport**: identify possible sources and transport pathways.
             4. **Climate & Environment Impact**: note potential effects briefly.
             5. **Earth Science Grand Questions and Challenges**: propose potential earth science question and challenges regarding this aerosol event.
             Keep the format consistent every time. 
             For long message, if several points are given, specify them into different lines start with -."""},
            {"role": "user", "content": aerosol_message}
        ],
        max_tokens=max_tokens
    )
    
    output = response.choices[0].message.content
    return output

def call_ai_api_web(api_key, base_url, aerosol_message, max_tokens=None):
    """
    max_tokens are the entire world, if input text is long, adjust the max_tokens accordingly
    """
    client = openai.OpenAI(
       api_key=api_key,
       base_url=base_url
    )

    response = client.chat.completions.create(
        model="gpt-5",  # use GPT-5 (or gpt-4o-mini if faster/cheaper)
        tools=[{"type": "web_search"}],
        messages=[
            {"role": "system", "content": "You are an atmospheric scientist."},
            
            {"role": "user", "content": "serach the web and provide top 5 news about the aerosol event based on "+aerosol_message}
        ],
        max_tokens=max_tokens
    )
    output = response.choices[0].message.content
    return output
    
def call_ai_api_simple(api_key, base_url, aerosol_message, max_tokens=None):
    """
    max_tokens are the entire world, if input text is long, adjust the max_tokens accordingly
    """
    client = openai.OpenAI(
       api_key=api_key,
       base_url=base_url
    )
    
    response = client.chat.completions.create(
        model="gpt-5",  # use GPT-5 (or gpt-4o-mini if faster/cheaper)
        messages=[
            {"role": "system", "content": "You are an atmospheric scientist."},
            {"role": "user", "content": aerosol_message}
        ],
        max_tokens=max_tokens
    )
    output = response.choices[0].message.content
    return output