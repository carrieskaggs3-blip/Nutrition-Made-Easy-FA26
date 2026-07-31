import base64
import io
import random
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="NUR3302 Nutrition Student Hub",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded",
)

FSC_RED = "#BA0C2F"
FSC_DARK = "#6E071C"
FSC_CREAM = "#F7F2EA"
FSC_CLAY = "#C49A6F"
FSC_TEXT = "#242424"

st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(180deg, #ffffff 0%, {FSC_CREAM} 100%);
        color: {FSC_TEXT};
    }}
    [data-testid="stSidebar"] {{
        background: {FSC_DARK};
    }}
    [data-testid="stSidebar"] * {{
        color: white;
    }}
    h1, h2, h3 {{
        color: {FSC_DARK};
    }}
    .hero {{
        border-left: 8px solid {FSC_RED};
        background: white;
        padding: 1.2rem 1.4rem;
        border-radius: 14px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,.08);
    }}
    .topic-card {{
        background: white;
        border: 1px solid #eadde0;
        border-radius: 14px;
        padding: 1rem;
        min-height: 150px;
        box-shadow: 0 2px 8px rgba(0,0,0,.05);
    }}
    .pearl {{
        background: #fff5f7;
        border-left: 5px solid {FSC_RED};
        padding: .85rem 1rem;
        border-radius: 8px;
        margin: .6rem 0;
    }}
    .warning {{
        background: #fff8e8;
        border-left: 5px solid {FSC_CLAY};
        padding: .85rem 1rem;
        border-radius: 8px;
    }}
    div.stButton > button {{
        background: {FSC_RED};
        color: white;
        border: 0;
        border-radius: 10px;
        font-weight: 600;
    }}
    div.stButton > button:hover {{
        background: {FSC_DARK};
        color: white;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Content data
# ----------------------------

MACROS = {
    "Carbohydrates": {
        "icon": "🌾",
        "functions": "Primary energy source, supports brain and red blood cell metabolism, and supplies fiber when minimally processed.",
        "sources": "Whole grains, fruits, vegetables, legumes, milk, and yogurt.",
        "nursing": "Match carbohydrate intake with glucose management plans. Watch for concentrated added sugars and inadequate fiber.",
        "energy": "4 kcal/g",
    },
    "Protein": {
        "icon": "🥚",
        "functions": "Supports tissue repair, enzymes, hormones, immune function, fluid balance, and transport.",
        "sources": "Fish, poultry, eggs, dairy, soy, beans, lentils, nuts, and seeds.",
        "nursing": "Needs rise with healing, burns, some infections, pregnancy, and growth. Kidney or liver disease can change the plan.",
        "energy": "4 kcal/g",
    },
    "Fat": {
        "icon": "🥑",
        "functions": "Provides energy, insulation, cell membranes, essential fatty acids, and absorption of vitamins A, D, E, and K.",
        "sources": "Olive oil, avocado, nuts, seeds, fatty fish, dairy, and meats.",
        "nursing": "Favor unsaturated fats. Consider fat tolerance in pancreatic, gallbladder, or malabsorptive disorders.",
        "energy": "9 kcal/g",
    },
    "Water": {
        "icon": "💧",
        "functions": "Supports circulation, temperature regulation, digestion, waste removal, and chemical reactions.",
        "sources": "Water, milk, soups, fruits, vegetables, and other beverages.",
        "nursing": "Assess intake, output, edema, mucous membranes, weight trends, sodium, kidney function, and swallowing safety.",
        "energy": "0 kcal/g",
    },
    "Fiber": {
        "icon": "🥦",
        "functions": "Supports bowel regularity, satiety, glycemic control, and cardiovascular health.",
        "sources": "Vegetables, fruits, whole grains, legumes, nuts, and seeds.",
        "nursing": "Increase gradually with adequate fluid. Some acute GI conditions or procedures require temporary restriction.",
        "energy": "Not fully digested",
    },
}

MICROS = {
    "Vitamin A": ("Vision, epithelial integrity, and immunity", "Liver, eggs, dairy, orange and dark-green produce", "Night blindness; excess can cause toxicity"),
    "Vitamin D": ("Calcium absorption, bone health, and muscle function", "Fortified milk, fatty fish, egg yolk, sunlight exposure", "Deficiency increases bone risk; excess can cause hypercalcemia"),
    "Vitamin E": ("Antioxidant protection", "Nuts, seeds, vegetable oils", "Deficiency is uncommon; high supplemental doses can increase bleeding risk"),
    "Vitamin K": ("Blood clotting and bone proteins", "Leafy greens and intestinal synthesis", "Keep intake consistent with warfarin therapy"),
    "Vitamin C": ("Collagen formation, wound healing, antioxidant activity, and iron absorption", "Citrus, berries, peppers, tomatoes, broccoli", "Deficiency can impair healing and cause bleeding gums"),
    "Thiamine (B1)": ("Carbohydrate metabolism and neurologic function", "Whole/enriched grains, pork, legumes", "Risk rises with chronic alcohol use, prolonged vomiting, and severe malnutrition"),
    "Folate (B9)": ("DNA synthesis and red blood cell formation", "Leafy greens, legumes, fortified grains", "Deficiency causes megaloblastic anemia; adequate intake matters before and during pregnancy"),
    "Vitamin B12": ("Neurologic function and red blood cell formation", "Animal foods and fortified products", "Deficiency can cause macrocytic anemia and neurologic changes"),
    "Calcium": ("Bone, muscle contraction, nerve transmission, and clotting", "Dairy, fortified alternatives, tofu, greens", "Vitamin D supports absorption"),
    "Iron": ("Hemoglobin and oxygen transport", "Meat, beans, fortified grains, leafy greens", "Vitamin C improves nonheme iron absorption"),
    "Magnesium": ("Muscle, nerve, enzyme, and cardiac function", "Nuts, seeds, legumes, whole grains, greens", "Low levels can contribute to weakness and dysrhythmias"),
    "Potassium": ("Fluid balance, nerve transmission, muscle and cardiac function", "Potatoes, beans, bananas, oranges, dairy, vegetables", "Kidney disease and certain medications can cause dangerous high levels"),
    "Sodium": ("Fluid balance and nerve and muscle function", "Processed foods, restaurant foods, salt", "Excess intake can worsen fluid retention and hypertension"),
    "Zinc": ("Wound healing, immunity, taste, and growth", "Meat, shellfish, dairy, legumes, nuts", "Deficiency can impair healing and taste"),
    "Iodine": ("Thyroid hormone production", "Iodized salt, seafood, dairy", "Both low and excessive intake can affect thyroid function"),
}

SPECIAL_DIETS = {
    "Cardiac / Heart-Healthy": {
        "focus": "Vegetables, fruits, whole grains, legumes, fish, lean proteins, unsaturated fats, and lower sodium.",
        "limit": "Processed meats, high-sodium foods, trans fat, excess saturated fat, and added sugars.",
        "case": "A patient with coronary artery disease asks which lunch best supports cardiovascular health.",
        "best": "Grilled salmon, quinoa, roasted vegetables, and fruit",
        "options": ["Fried chicken sandwich and fries", "Grilled salmon, quinoa, roasted vegetables, and fruit", "Pepperoni pizza", "Processed deli meat wrap and chips"],
    },
    "DASH": {
        "focus": "Fruits, vegetables, low-fat dairy, whole grains, nuts, legumes, and lower sodium.",
        "limit": "High-sodium processed foods and excess saturated fat.",
        "case": "A patient with hypertension wants a DASH-style breakfast.",
        "best": "Oatmeal with berries, walnuts, and low-fat milk",
        "options": ["Sausage biscuit", "Oatmeal with berries, walnuts, and low-fat milk", "Sugary pastry and energy drink", "Bacon, hash browns, and salted eggs"],
    },
    "Diabetes / Consistent Carbohydrate": {
        "focus": "Consistent carbohydrate distribution, high-fiber choices, portion awareness, and pairing carbohydrate with protein or healthy fat.",
        "limit": "Sugar-sweetened beverages and large portions of refined carbohydrate.",
        "case": "A patient with diabetes needs a balanced snack.",
        "best": "Apple slices with peanut butter",
        "options": ["Regular soda", "Apple slices with peanut butter", "Large candy bar", "Sweetened coffee drink"],
    },
    "Renal": {
        "focus": "Individualize sodium, potassium, phosphorus, protein, and fluid according to kidney function, dialysis status, and laboratory results.",
        "limit": "Do not apply one universal renal diet to every patient.",
        "case": "Which action is safest before teaching a patient with chronic kidney disease?",
        "best": "Review current kidney function, potassium, phosphorus, fluid status, and treatment plan",
        "options": ["Automatically ban all fruits", "Recommend high-protein supplements to everyone", "Review current kidney function, potassium, phosphorus, fluid status, and treatment plan", "Encourage salt substitutes without checking potassium"],
    },
    "Liver Disease": {
        "focus": "Adequate energy and protein are often important. Sodium restriction can help ascites. Plans vary with encephalopathy and disease severity.",
        "limit": "Alcohol and unnecessary severe protein restriction.",
        "case": "A patient with cirrhosis and ascites needs teaching.",
        "best": "Choose lower-sodium foods and follow the individualized protein and fluid plan",
        "options": ["Avoid all protein indefinitely", "Choose lower-sodium foods and follow the individualized protein and fluid plan", "Use salt substitutes freely", "Skip meals to reduce abdominal fullness"],
    },
    "Gluten-Free": {
        "focus": "Avoid wheat, barley, and rye. Use certified gluten-free products when cross-contact matters.",
        "limit": "Hidden gluten and cross-contact.",
        "case": "Which grain is naturally gluten-free?",
        "best": "Quinoa",
        "options": ["Barley", "Rye", "Quinoa", "Wheat berries"],
    },
    "Low-FODMAP": {
        "focus": "A structured short-term elimination followed by systematic reintroduction, ideally with dietitian guidance.",
        "limit": "Long-term unnecessary restriction.",
        "case": "What is the purpose of the reintroduction phase?",
        "best": "Identify individual triggers and expand the diet",
        "options": ["Maintain permanent maximal restriction", "Identify individual triggers and expand the diet", "Diagnose inflammatory bowel disease", "Eliminate all carbohydrates"],
    },
    "Bariatric": {
        "focus": "Small portions, protein first, slow eating, lifelong vitamin and mineral supplementation, and avoiding fluids with meals as directed.",
        "limit": "Large meals, concentrated sweets when dumping is a concern, and nonadherence to supplements.",
        "case": "Which behavior best supports recovery after bariatric surgery?",
        "best": "Eat small meals slowly and prioritize prescribed protein and supplements",
        "options": ["Drink large amounts with meals", "Eat small meals slowly and prioritize prescribed protein and supplements", "Stop vitamins once weight stabilizes", "Choose concentrated sweets for calories"],
    },
    "Dysphagia / Texture-Modified": {
        "focus": "Use the prescribed food texture and liquid thickness. Position upright and follow speech-language pathology recommendations.",
        "limit": "Unapproved mixed textures and thin liquids when contraindicated.",
        "case": "What is the nurse's priority before offering food?",
        "best": "Verify the prescribed texture, liquid consistency, positioning, and swallowing plan",
        "options": ["Offer water to test swallowing", "Verify the prescribed texture, liquid consistency, positioning, and swallowing plan", "Place the patient flat", "Add a straw automatically"],
    },
    "Enteral Nutrition": {
        "focus": "Use the GI tract when functional. Verify tube placement according to policy, maintain head elevation, monitor tolerance, and flush as ordered.",
        "limit": "Unsafe medication mixing and interrupting feeds without a plan.",
        "case": "Which action reduces aspiration risk during gastric tube feeding?",
        "best": "Maintain appropriate head-of-bed elevation and assess tolerance",
        "options": ["Position supine", "Maintain appropriate head-of-bed elevation and assess tolerance", "Add medications directly to the formula bag", "Use food coloring to test placement"],
    },
    "Parenteral Nutrition": {
        "focus": "Central or peripheral IV nutrition when the GI tract cannot be used adequately. Monitor glucose, electrolytes, infection risk, and line care.",
        "limit": "Abrupt changes without orders and breaks in aseptic technique.",
        "case": "Which complication requires close monitoring with parenteral nutrition?",
        "best": "Bloodstream infection and hyperglycemia",
        "options": ["Only constipation", "Bloodstream infection and hyperglycemia", "Gluten exposure", "Lactose intolerance"],
    },
}

QUESTIONS = [
    # Macronutrients
    {"topic":"Macronutrients","q":"A nurse is teaching a client about energy provided by nutrients. Which nutrient provides 9 kcal per gram?","options":["Carbohydrate","Protein","Fat","Water"],"answer":"Fat","rationale":"Fat provides 9 kcal/g. Carbohydrate and protein provide 4 kcal/g."},
    {"topic":"Macronutrients","q":"Which meal provides the best combination of complex carbohydrate and fiber?","options":["White toast and jelly","Oatmeal with berries","Candy and juice","Crackers and soda"],"answer":"Oatmeal with berries","rationale":"Whole oats and berries provide complex carbohydrate and dietary fiber."},
    {"topic":"Macronutrients","q":"Which patient has the greatest expected increase in protein needs?","options":["Stable adult with no illness","Patient with a large pressure injury","Adult with seasonal allergies","Patient receiving routine eye drops"],"answer":"Patient with a large pressure injury","rationale":"Protein supports tissue repair and needs often rise with significant wounds."},
    {"topic":"Macronutrients","q":"A client suddenly increases fiber intake and develops bloating. Which teaching is best?","options":["Stop all fiber permanently","Increase fiber gradually and drink adequate fluid","Use only fiber supplements","Restrict all fruits"],"answer":"Increase fiber gradually and drink adequate fluid","rationale":"Gradual increases with adequate fluid reduce GI discomfort and constipation risk."},
    {"topic":"Macronutrients","q":"Which assessment best reflects short-term fluid balance changes?","options":["Daily weight","Height","Hair color","Waist-to-hip ratio"],"answer":"Daily weight","rationale":"Daily weight under consistent conditions is sensitive to fluid gain or loss."},
    {"topic":"Macronutrients","q":"Which food is a source of unsaturated fat?","options":["Avocado","Stick butter","Shortening","Fatty processed meat"],"answer":"Avocado","rationale":"Avocado is rich in unsaturated fat."},
    {"topic":"Macronutrients","q":"Which nutrient is the primary fuel source for the brain under usual conditions?","options":["Carbohydrate","Vitamin C","Calcium","Water"],"answer":"Carbohydrate","rationale":"Glucose derived from carbohydrate is the brain's usual primary fuel."},
    {"topic":"Macronutrients","q":"Which protein source is plant-based?","options":["Lentils","Chicken","Eggs","Tuna"],"answer":"Lentils","rationale":"Lentils are legumes and provide plant protein and fiber."},
    # Micronutrients
    {"topic":"Micronutrients","q":"Which vitamin improves absorption of nonheme iron?","options":["Vitamin C","Vitamin K","Vitamin D","Vitamin B12"],"answer":"Vitamin C","rationale":"Vitamin C enhances absorption of iron from plant and fortified sources."},
    {"topic":"Micronutrients","q":"A client taking warfarin asks about leafy greens. Which response is best?","options":["Avoid all greens forever","Keep vitamin K intake consistent and follow monitoring instructions","Double greens on weekends","Take vitamin K supplements daily without guidance"],"answer":"Keep vitamin K intake consistent and follow monitoring instructions","rationale":"Consistency supports stable anticoagulation. Abrupt intake changes can alter warfarin effect."},
    {"topic":"Micronutrients","q":"Which finding is most concerning for vitamin B12 deficiency?","options":["Paresthesias and macrocytic anemia","Night blindness only","Bleeding gums only","Hyperactive reflexes after exercise"],"answer":"Paresthesias and macrocytic anemia","rationale":"B12 deficiency can produce neurologic changes and macrocytic anemia."},
    {"topic":"Micronutrients","q":"Which mineral is essential for thyroid hormone production?","options":["Iodine","Zinc","Iron","Calcium"],"answer":"Iodine","rationale":"The thyroid uses iodine to synthesize thyroid hormones."},
    {"topic":"Micronutrients","q":"A patient with chronic alcohol misuse and confusion is at risk for deficiency of which vitamin?","options":["Thiamine","Vitamin K","Vitamin A","Vitamin E"],"answer":"Thiamine","rationale":"Chronic alcohol misuse increases risk for thiamine deficiency and serious neurologic complications."},
    {"topic":"Micronutrients","q":"Which nutrient deficiency can cause impaired wound healing and reduced taste?","options":["Zinc","Sodium","Fluoride","Vitamin K"],"answer":"Zinc","rationale":"Zinc supports wound healing, immune function, and taste."},
    {"topic":"Micronutrients","q":"Which patient requires the most caution with potassium-rich foods or salt substitutes?","options":["Patient with advanced kidney disease","Healthy adolescent athlete","Adult with corrected vision","Patient with seasonal rhinitis"],"answer":"Patient with advanced kidney disease","rationale":"Reduced kidney excretion can cause dangerous hyperkalemia."},
    {"topic":"Micronutrients","q":"Which vitamin supports calcium absorption?","options":["Vitamin D","Vitamin C","Thiamine","Folate"],"answer":"Vitamin D","rationale":"Vitamin D promotes intestinal calcium absorption."},
    {"topic":"Micronutrients","q":"Which manifestation is associated with vitamin A deficiency?","options":["Night blindness","Scurvy","Pellagra","Goiter"],"answer":"Night blindness","rationale":"Vitamin A is required for normal visual function, especially in low light."},
    {"topic":"Micronutrients","q":"Which nutrient is especially important before and during early pregnancy to reduce neural tube defect risk?","options":["Folate","Sodium","Vitamin E","Phosphorus"],"answer":"Folate","rationale":"Adequate folate before conception and in early pregnancy supports neural tube development."},
    # Special diets
    {"topic":"Special Diets","q":"Which meal best fits a heart-healthy eating pattern?","options":["Grilled fish, brown rice, vegetables","Fried chicken, fries, soda","Processed meat pizza","Bacon cheeseburger"],"answer":"Grilled fish, brown rice, vegetables","rationale":"This option emphasizes lean protein, whole grain, and vegetables."},
    {"topic":"Special Diets","q":"Which breakfast best fits the DASH pattern?","options":["Oatmeal, berries, walnuts, low-fat milk","Sausage biscuit","Donut and sweetened coffee","Bacon and salted hash browns"],"answer":"Oatmeal, berries, walnuts, low-fat milk","rationale":"DASH emphasizes fruits, whole grains, nuts, and low-fat dairy."},
    {"topic":"Special Diets","q":"Which food must a client with celiac disease avoid?","options":["Barley","Rice","Corn","Quinoa"],"answer":"Barley","rationale":"Gluten is found in wheat, barley, and rye."},
    {"topic":"Special Diets","q":"What is the safest approach to a renal diet?","options":["Individualize it using labs, kidney function, and treatment status","Ban all protein","Ban all produce","Use potassium salt substitutes freely"],"answer":"Individualize it using labs, kidney function, and treatment status","rationale":"Renal restrictions differ by disease stage, dialysis status, labs, and symptoms."},
    {"topic":"Special Diets","q":"Which instruction is appropriate for prescribed dysphagia precautions?","options":["Use the ordered texture and liquid consistency","Give thin water routinely","Feed while supine","Use a straw for every patient"],"answer":"Use the ordered texture and liquid consistency","rationale":"The swallowing plan should follow the individualized speech-language pathology recommendations."},
    {"topic":"Special Diets","q":"Which action is appropriate during enteral feeding?","options":["Maintain prescribed head elevation","Mix all medications into the formula","Confirm placement by injecting air and listening","Keep the patient flat"],"answer":"Maintain prescribed head elevation","rationale":"Appropriate head elevation helps reduce aspiration risk."},
    {"topic":"Special Diets","q":"Which complication is a priority with central parenteral nutrition?","options":["Bloodstream infection","Gluten exposure","Dental caries only","Motion sickness"],"answer":"Bloodstream infection","rationale":"Central venous access increases bloodstream infection risk."},
    {"topic":"Special Diets","q":"Which snack best supports consistent-carbohydrate teaching?","options":["Apple with peanut butter","Regular soda","Large candy bar","Sweetened frozen drink"],"answer":"Apple with peanut butter","rationale":"The snack combines carbohydrate and fiber with protein and fat."},
    {"topic":"Special Diets","q":"Which statement about low-FODMAP eating is correct?","options":["Reintroduction identifies individual triggers","It should remain maximally restrictive forever","It diagnoses celiac disease","It eliminates all carbohydrate"],"answer":"Reintroduction identifies individual triggers","rationale":"Low-FODMAP plans use short-term restriction followed by structured reintroduction."},
    {"topic":"Special Diets","q":"Which instruction is most appropriate after bariatric surgery?","options":["Prioritize protein and prescribed supplements","Stop supplements when weight stabilizes","Drink large volumes with meals","Choose concentrated sweets"],"answer":"Prioritize protein and prescribed supplements","rationale":"Protein and lifelong prescribed micronutrient supplementation help prevent malnutrition."},
    # Clinical/nutrition support
    {"topic":"Clinical Nutrition","q":"Which finding most strongly suggests aspiration risk during a meal?","options":["Wet voice and coughing","Request for seasoning","Preference for cold food","Eating slowly"],"answer":"Wet voice and coughing","rationale":"Coughing and a wet or gurgly voice can signal impaired airway protection."},
    {"topic":"Clinical Nutrition","q":"Which action is best when a hospitalized patient eats less than 25% of meals for several days?","options":["Assess barriers and request nutrition evaluation","Document only","Remove snacks","Wait until discharge"],"answer":"Assess barriers and request nutrition evaluation","rationale":"Persistent poor intake needs prompt assessment and interdisciplinary intervention."},
    {"topic":"Clinical Nutrition","q":"Which anthropometric measure is most useful for monitoring acute nutrition and fluid trends?","options":["Serial weight","Adult height","Shoe size","Arm span once"],"answer":"Serial weight","rationale":"Weight trends help identify changes, though fluid status must be considered."},
    {"topic":"Clinical Nutrition","q":"Which patient is at greatest risk for refeeding complications?","options":["Severely malnourished patient beginning nutrition support","Healthy adult eating breakfast","Patient on a stable regular diet","Adult taking a multivitamin"],"answer":"Severely malnourished patient beginning nutrition support","rationale":"Rapid nutrition after severe deprivation can cause dangerous electrolyte shifts."},
    {"topic":"Clinical Nutrition","q":"Which electrolyte deserves close monitoring when refeeding risk is high?","options":["Phosphorus","Chloride only","Bicarbonate only","Calcium only"],"answer":"Phosphorus","rationale":"Hypophosphatemia is a hallmark concern in refeeding syndrome."},
    {"topic":"Clinical Nutrition","q":"Which intervention best supports a patient with poor appetite?","options":["Offer small nutrient-dense meals and address symptoms","Force large meals","Restrict preferred foods without reason","Skip oral care"],"answer":"Offer small nutrient-dense meals and address symptoms","rationale":"Small frequent nutrient-dense intake and symptom management can improve intake."},
    {"topic":"Clinical Nutrition","q":"A patient receiving tube feeding develops diarrhea. What should the nurse do first?","options":["Assess medications, rate, formula handling, infection, and other causes","Stop all nutrition permanently","Add antidiarrheals without assessment","Dilute formula with tap water"],"answer":"Assess medications, rate, formula handling, infection, and other causes","rationale":"Diarrhea has multiple causes and requires assessment before changing the feeding plan."},
    {"topic":"Clinical Nutrition","q":"Which nursing action best reduces medication-tube interactions?","options":["Follow medication-specific guidance and flush as ordered","Crush every medication together","Mix medications into the formula bag","Skip flushing"],"answer":"Follow medication-specific guidance and flush as ordered","rationale":"Medication administration through feeding tubes requires drug-specific review and appropriate flushing."},
    # Maternal/peds/older adult
    {"topic":"Lifespan Nutrition","q":"Which teaching is most important for a pregnant client?","options":["Follow prenatal folate and iron recommendations","Avoid all fish","Double calorie intake immediately","Use herbal supplements freely"],"answer":"Follow prenatal folate and iron recommendations","rationale":"Folate and iron needs rise in pregnancy and should follow prenatal guidance."},
    {"topic":"Lifespan Nutrition","q":"Which food is unsafe for an infant younger than 12 months?","options":["Honey","Iron-fortified cereal","Pureed vegetables","Breast milk or formula"],"answer":"Honey","rationale":"Honey can contain spores associated with infant botulism."},
    {"topic":"Lifespan Nutrition","q":"Which approach supports healthy toddler eating?","options":["Offer structured meals and repeated exposure without pressure","Force a clean plate","Use sweets as the main reward","Allow continuous juice sipping"],"answer":"Offer structured meals and repeated exposure without pressure","rationale":"Repeated neutral exposure and structured meals support healthy food acceptance."},
    {"topic":"Lifespan Nutrition","q":"Which factor commonly raises dehydration risk in older adults?","options":["Reduced thirst sensation","Increased total body water","Improved kidney concentration","Greater muscle mass"],"answer":"Reduced thirst sensation","rationale":"Older adults may have reduced thirst and impaired renal concentrating ability."},
    {"topic":"Lifespan Nutrition","q":"Which intervention supports an older adult with limited dexterity?","options":["Adaptive utensils and easy-open containers","Remove all finger foods","Serve only liquids","Limit meal time to five minutes"],"answer":"Adaptive utensils and easy-open containers","rationale":"Adaptive equipment can increase independence and intake."},
    # Food safety
    {"topic":"Food Safety","q":"Which action best prevents cross-contamination?","options":["Use separate cutting boards for raw meat and ready-to-eat foods","Rinse raw poultry in the sink","Use one knife without washing","Place cooked meat on the raw-meat plate"],"answer":"Use separate cutting boards for raw meat and ready-to-eat foods","rationale":"Separation reduces transfer of pathogens from raw animal foods."},
    {"topic":"Food Safety","q":"Which client should avoid unpasteurized milk and soft cheese made from unpasteurized milk?","options":["Pregnant client","Healthy adult runner only","Client with corrected myopia","Adult with seasonal allergies"],"answer":"Pregnant client","rationale":"Pregnancy increases risk from foodborne pathogens such as Listeria."},
    {"topic":"Food Safety","q":"What is the safest action with perishable food left at room temperature for an uncertain prolonged period?","options":["Discard it","Taste it first","Refrigerate and serve later","Reheat briefly"],"answer":"Discard it","rationale":"When time and temperature safety are uncertain, discarding is safest."},
    {"topic":"Food Safety","q":"Which hand hygiene moment is essential during food preparation?","options":["After handling raw meat and before touching ready-to-eat food","Only after the meal","Only when hands look dirty","After putting on jewelry"],"answer":"After handling raw meat and before touching ready-to-eat food","rationale":"Handwashing interrupts cross-contamination."},
    # Assessment and teaching
    {"topic":"Assessment","q":"Which question best assesses food access?","options":["Have you worried that food would run out before you had money to buy more?","Do you like vegetables?","What is your favorite restaurant?","Do you own a blender?"],"answer":"Have you worried that food would run out before you had money to buy more?","rationale":"This question screens for household food insecurity."},
    {"topic":"Assessment","q":"Which finding requires the fastest follow-up?","options":["Unintentional 10% weight loss with poor intake","Stable weight and appetite","Preference for vegetarian meals","Occasional restaurant meal"],"answer":"Unintentional 10% weight loss with poor intake","rationale":"Significant unintentional weight loss and poor intake raise malnutrition risk."},
    {"topic":"Assessment","q":"Which response uses teach-back correctly?","options":["Show me how you will choose your meals at home","Do you understand?","Read this later","Sign here to confirm understanding"],"answer":"Show me how you will choose your meals at home","rationale":"Teach-back asks the patient to explain or demonstrate the plan in their own words."},
    {"topic":"Assessment","q":"Which teaching plan is most culturally responsive?","options":["Ask about preferred foods and adapt recommendations","Replace all traditional foods","Assume everyone eats the same foods","Provide a generic list without discussion"],"answer":"Ask about preferred foods and adapt recommendations","rationale":"Effective teaching respects preferences, access, beliefs, and usual eating patterns."},
    {"topic":"Assessment","q":"Which referral is most appropriate for a patient needing individualized medical nutrition therapy?","options":["Registered dietitian nutritionist","Hospital transporter","Billing specialist","Radiology scheduler"],"answer":"Registered dietitian nutritionist","rationale":"An RDN provides individualized medical nutrition therapy and works with the clinical team."},


    # ---------------- Macronutrients (12) ----------------
    {"topic":"Macronutrients","q":"A nurse calculates the energy content of a meal containing 60 g carbohydrate, 25 g protein, and 20 g fat. Which total should the nurse document?","options":["340 kcal","520 kcal","480 kcal","620 kcal"],"answer":"520 kcal","rationale":"Carbohydrate and protein supply 4 kcal/g and fat supplies 9 kcal/g. (60 x 4) + (25 x 4) + (20 x 9) = 520 kcal."},
    {"topic":"Macronutrients","q":"A client asks which nutrient class supplies the most concentrated source of energy. Which response is correct?","options":["Fat","Protein","Carbohydrate","Vitamins"],"answer":"Fat","rationale":"Fat provides 9 kcal/g, more than twice the energy density of carbohydrate or protein."},
    {"topic":"Macronutrients","q":"Which client statement indicates correct understanding of a complete protein?","options":["It contains all nine essential amino acids in adequate amounts","It contains only plant amino acids","It is any food high in calories","It must be eaten raw to retain amino acids"],"answer":"It contains all nine essential amino acids in adequate amounts","rationale":"Complete proteins supply all essential amino acids in sufficient quantity. Most animal proteins and soy are complete."},
    {"topic":"Macronutrients","q":"A vegan client asks how to obtain adequate protein quality. Which teaching is best?","options":["Combine a variety of plant proteins across the day","Eat only soy at every meal","Take amino acid injections","Restrict legumes to avoid excess nitrogen"],"answer":"Combine a variety of plant proteins across the day","rationale":"Complementary plant proteins eaten over the course of the day supply all essential amino acids."},
    {"topic":"Macronutrients","q":"Which finding suggests inadequate protein intake in a hospitalized client?","options":["Generalized edema and poor wound healing","Elevated hemoglobin","Increased muscle strength","Rapid hair growth"],"answer":"Generalized edema and poor wound healing","rationale":"Low serum protein reduces oncotic pressure and impairs tissue repair, producing edema and delayed healing."},
    {"topic":"Macronutrients","q":"A client is prescribed a high-fiber diet. Which selection provides the most fiber?","options":["One-half cup black beans","One cup white rice","Two slices white bread","One cup whole milk"],"answer":"One-half cup black beans","rationale":"Legumes are among the richest fiber sources. Refined grains and dairy supply little or none."},
    {"topic":"Macronutrients","q":"Which type of fiber is most effective for lowering serum cholesterol?","options":["Soluble fiber","Insoluble fiber","Cellulose","Lignin"],"answer":"Soluble fiber","rationale":"Soluble fiber binds bile acids in the gut, increasing cholesterol excretion. Oats, barley, legumes, and psyllium are good sources."},
    {"topic":"Macronutrients","q":"A client asks which fat should be limited most for cardiovascular health. Which response is correct?","options":["Trans fat","Monounsaturated fat","Omega-3 fatty acids","Polyunsaturated fat"],"answer":"Trans fat","rationale":"Trans fat raises LDL and lowers HDL. Guidance is to limit intake as much as possible."},
    {"topic":"Macronutrients","q":"Which food is the best source of omega-3 fatty acids?","options":["Salmon","Skinless chicken breast","White rice","Cottage cheese"],"answer":"Salmon","rationale":"Fatty cold-water fish supply EPA and DHA, the marine omega-3 fatty acids."},
    {"topic":"Macronutrients","q":"A client following a very low carbohydrate diet reports fruity breath and fatigue. Which explanation is correct?","options":["The body is producing ketones from fat breakdown","Protein is being converted to glucose","Excess fiber is fermenting in the colon","Vitamin C is being oxidized"],"answer":"The body is producing ketones from fat breakdown","rationale":"Insufficient carbohydrate forces fat catabolism, generating ketone bodies that produce a characteristic acetone breath odor."},
    {"topic":"Macronutrients","q":"Which term describes the minimum carbohydrate intake generally needed to prevent ketosis in adults?","options":["Approximately 130 g per day","Approximately 20 g per day","Approximately 400 g per day","Carbohydrate is not required"],"answer":"Approximately 130 g per day","rationale":"The RDA for carbohydrate in adults is 130 g/day, based on brain glucose requirements."},
    {"topic":"Macronutrients","q":"A client on a weight-reduction plan asks which nutrient promotes the greatest satiety per calorie. Which response is best?","options":["Protein","Fat","Simple sugar","Alcohol"],"answer":"Protein","rationale":"Protein has the strongest effect on satiety and the highest thermic effect of the macronutrients."},

    # ---------------- Micronutrients (22) ----------------
    {"topic":"Micronutrients","q":"A client takes a fat-soluble vitamin supplement. Which vitamins should the nurse include in teaching about toxicity risk?","options":["Vitamins A, D, E, and K","Vitamins B and C","Vitamin C and folate","Thiamine and niacin"],"answer":"Vitamins A, D, E, and K","rationale":"Fat-soluble vitamins are stored in liver and adipose tissue and accumulate to toxic levels more readily than water-soluble vitamins."},
    {"topic":"Micronutrients","q":"Which instruction should the nurse give a client prescribed oral ferrous sulfate?","options":["Take with orange juice on an empty stomach if tolerated","Take with milk to reduce upset","Take with an antacid","Take with a calcium supplement"],"answer":"Take with orange juice on an empty stomach if tolerated","rationale":"Ascorbic acid enhances nonheme iron absorption. Calcium, dairy, and antacids inhibit it."},
    {"topic":"Micronutrients","q":"A client taking iron reports dark stools. Which nursing action is appropriate?","options":["Explain that dark stools are an expected effect","Hold the dose and notify the provider immediately","Obtain a stat hemoglobin","Instruct the client to stop the supplement"],"answer":"Explain that dark stools are an expected effect","rationale":"Unabsorbed iron darkens stool. This is expected and does not require discontinuation."},
    {"topic":"Micronutrients","q":"Which client is at highest risk for vitamin B12 deficiency?","options":["Client who had a total gastrectomy","Client who eats a mixed diet","Client taking vitamin C","Client with a high fiber intake"],"answer":"Client who had a total gastrectomy","rationale":"Loss of parietal cells eliminates intrinsic factor, preventing B12 absorption in the ileum. Lifelong parenteral or high-dose replacement is required."},
    {"topic":"Micronutrients","q":"A strict vegan client should be counseled to supplement or use fortified sources of which nutrient?","options":["Vitamin B12","Vitamin C","Fiber","Potassium"],"answer":"Vitamin B12","rationale":"Vitamin B12 occurs naturally only in animal foods, so vegans require fortified foods or supplements."},
    {"topic":"Micronutrients","q":"A client with a healing surgical wound asks which nutrients support tissue repair. Which response is best?","options":["Protein, vitamin C, and zinc","Vitamin K and fiber","Sodium and chloride","Vitamin E and iodine"],"answer":"Protein, vitamin C, and zinc","rationale":"Protein supplies building material, vitamin C is required for collagen synthesis, and zinc supports cell proliferation and immune function."},
    {"topic":"Micronutrients","q":"Which manifestation should the nurse associate with vitamin C deficiency?","options":["Bleeding gums and poor wound healing","Night blindness","Goiter","Rickets"],"answer":"Bleeding gums and poor wound healing","rationale":"Scurvy results from defective collagen synthesis, producing gingival bleeding, petechiae, and impaired healing."},
    {"topic":"Micronutrients","q":"A client with chronic kidney disease should be taught to limit which mineral found in dark colas and processed cheese?","options":["Phosphorus","Vitamin C","Fiber","Thiamine"],"answer":"Phosphorus","rationale":"Phosphate additives in colas, processed cheese, and processed meats are highly absorbable and worsen hyperphosphatemia."},
    {"topic":"Micronutrients","q":"Which laboratory finding is most consistent with iron deficiency anemia?","options":["Low mean corpuscular volume and low ferritin","High mean corpuscular volume","Elevated ferritin","Elevated vitamin B12"],"answer":"Low mean corpuscular volume and low ferritin","rationale":"Iron deficiency produces a microcytic hypochromic anemia with depleted iron stores reflected by low ferritin."},
    {"topic":"Micronutrients","q":"An older adult with limited sun exposure and low dietary intake is at risk for deficiency of which vitamin?","options":["Vitamin D","Vitamin K","Niacin","Vitamin C"],"answer":"Vitamin D","rationale":"Cutaneous synthesis declines with age and limited sun exposure, and few foods naturally contain vitamin D."},
    {"topic":"Micronutrients","q":"Which food provides the most bioavailable heme iron?","options":["Beef liver","Spinach","Fortified cereal","Lentils"],"answer":"Beef liver","rationale":"Heme iron from animal tissue is absorbed far more efficiently than nonheme iron from plant sources."},
    {"topic":"Micronutrients","q":"A client reports taking megadoses of vitamin A. Which finding should the nurse report?","options":["Headache, dry skin, and hepatomegaly","Increased night vision","Improved wound healing","Lower blood pressure"],"answer":"Headache, dry skin, and hepatomegaly","rationale":"Hypervitaminosis A causes headache, alopecia, dry skin, bone pain, and liver damage."},
    {"topic":"Micronutrients","q":"Which client requires the most careful teaching about consistent vitamin K intake?","options":["Client taking warfarin","Client taking a proton pump inhibitor","Client taking acetaminophen","Client taking a stool softener"],"answer":"Client taking warfarin","rationale":"Vitamin K antagonizes warfarin. Wide swings in intake destabilize the INR, so consistency matters more than avoidance."},
    {"topic":"Micronutrients","q":"A client with alcohol use disorder is admitted with confusion and ataxia. Which nutrient should be administered before glucose?","options":["Thiamine","Vitamin C","Calcium","Magnesium"],"answer":"Thiamine","rationale":"Giving glucose first in thiamine deficiency can precipitate Wernicke encephalopathy. Thiamine is given before or with dextrose."},
    {"topic":"Micronutrients","q":"Which nutrient deficiency causes pellagra, characterized by dermatitis, diarrhea, and dementia?","options":["Niacin","Riboflavin","Biotin","Vitamin K"],"answer":"Niacin","rationale":"Pellagra results from niacin deficiency and classically produces the three D presentation."},
    {"topic":"Micronutrients","q":"A client taking a calcium supplement asks how to improve absorption. Which teaching is best?","options":["Take in divided doses of 500 mg or less with adequate vitamin D","Take the entire daily dose at once","Take with a high-fiber bran cereal","Take with an iron supplement"],"answer":"Take in divided doses of 500 mg or less with adequate vitamin D","rationale":"Calcium absorption is saturable. Divided doses with adequate vitamin D maximize uptake, and fiber and iron reduce it."},
    {"topic":"Micronutrients","q":"Which client should be assessed most closely for hypomagnesemia?","options":["Client with chronic alcohol use and diarrhea","Client eating a regular diet","Client taking a multivitamin","Client with well-controlled hypertension"],"answer":"Client with chronic alcohol use and diarrhea","rationale":"Alcohol increases renal magnesium wasting and diarrhea causes GI losses, a common combination in clinical deficiency."},
    {"topic":"Micronutrients","q":"A client asks why iodized salt is recommended. Which response is correct?","options":["Iodine is required for thyroid hormone synthesis","Iodine lowers blood pressure","Iodine replaces potassium","Iodine prevents anemia"],"answer":"Iodine is required for thyroid hormone synthesis","rationale":"Iodine deficiency impairs thyroxine production and causes goiter and hypothyroidism."},
    {"topic":"Micronutrients","q":"Which finding indicates possible selenium deficiency?","options":["Cardiomyopathy and muscle weakness","Night blindness","Bleeding gums","Goiter"],"answer":"Cardiomyopathy and muscle weakness","rationale":"Severe selenium deficiency is associated with cardiomyopathy and skeletal muscle dysfunction."},
    {"topic":"Micronutrients","q":"A client takes a proton pump inhibitor long term. Which nutrient absorption is most likely reduced?","options":["Vitamin B12","Vitamin K","Sodium","Fiber"],"answer":"Vitamin B12","rationale":"Gastric acid is needed to release protein-bound B12. Prolonged acid suppression can reduce absorption."},
    {"topic":"Micronutrients","q":"Which teaching is appropriate for a client starting a folic acid supplement before pregnancy?","options":["Begin at least one month before conception and continue through early pregnancy","Start only after the first missed period","Take only if anemia develops","Take with an antacid for absorption"],"answer":"Begin at least one month before conception and continue through early pregnancy","rationale":"Neural tube closure occurs by week four, before many pregnancies are recognized, so preconception intake is essential."},
    {"topic":"Micronutrients","q":"A client with long-term total parenteral nutrition develops a scaly rash and poor healing. Which trace element deficiency is most likely?","options":["Zinc","Sodium","Chloride","Fluoride"],"answer":"Zinc","rationale":"Zinc deficiency causes a perioral and acral dermatitis, impaired healing, alopecia, and taste loss."},

    # ---------------- Special Diets (14) ----------------
    {"topic":"Special Diets","q":"A client is prescribed a clear liquid diet. Which item should the nurse remove from the tray?","options":["Cream of chicken soup","Apple juice","Beef broth","Lemon gelatin"],"answer":"Cream of chicken soup","rationale":"Clear liquids transmit light and leave minimal residue. Cream soup is opaque and belongs on a full liquid diet."},
    {"topic":"Special Diets","q":"Which food is appropriate on a full liquid diet?","options":["Vanilla ice cream","Scrambled eggs","Toast","Mashed potatoes"],"answer":"Vanilla ice cream","rationale":"Full liquid diets include foods that are liquid at body temperature, such as ice cream, milk, and strained cream soups."},
    {"topic":"Special Diets","q":"A client is placed on a mechanical soft diet after dental surgery. Which selection is appropriate?","options":["Ground meat with gravy","Raw carrot sticks","Whole apple","Crusty roll"],"answer":"Ground meat with gravy","rationale":"Mechanical soft diets modify texture only. Foods are chopped, ground, or moistened to reduce chewing effort."},
    {"topic":"Special Diets","q":"A client with a new colostomy asks about gas-producing foods. Which foods should the nurse mention?","options":["Cabbage, beans, and carbonated beverages","Rice and toast","Bananas and applesauce","Plain pasta"],"answer":"Cabbage, beans, and carbonated beverages","rationale":"Cruciferous vegetables, legumes, and carbonation commonly increase flatus in clients with an ostomy."},
    {"topic":"Special Diets","q":"Which teaching is correct for a client on a low-residue diet before bowel surgery?","options":["Choose white bread, refined pasta, and well-cooked vegetables without skins","Choose whole-grain bread and raw vegetables","Increase nuts and seeds","Add bran to every meal"],"answer":"Choose white bread, refined pasta, and well-cooked vegetables without skins","rationale":"Low-residue diets minimize fiber and undigested material to reduce stool bulk and bowel activity."},
    {"topic":"Special Diets","q":"A client follows a lacto-ovo vegetarian pattern. Which food is acceptable?","options":["Cheese omelet","Grilled chicken","Baked cod","Beef broth"],"answer":"Cheese omelet","rationale":"Lacto-ovo vegetarians consume dairy and eggs but exclude meat, poultry, and fish."},
    {"topic":"Special Diets","q":"A client with dumping syndrome after gastric surgery asks how to reduce symptoms. Which teaching is best?","options":["Eat small, dry meals and drink fluids between meals","Drink large volumes with meals","Increase simple sugars","Lie prone after eating"],"answer":"Eat small, dry meals and drink fluids between meals","rationale":"Separating fluids from solids and limiting simple sugars slows gastric emptying and reduces osmotic fluid shifts."},
    {"topic":"Special Diets","q":"Which position should a client with dumping syndrome assume after meals?","options":["Recumbent or reclining for 20 to 30 minutes","Standing and walking briskly","Sitting fully upright and leaning forward","High Fowler with the knees flexed"],"answer":"Recumbent or reclining for 20 to 30 minutes","rationale":"Lying down after meals slows gastric emptying and reduces the rapid delivery of hyperosmolar chyme to the jejunum."},
    {"topic":"Special Diets","q":"A client with celiac disease selects foods from a menu. Which choice indicates further teaching is needed?","options":["Barley soup","Corn tortilla","Baked potato","Rice pilaf"],"answer":"Barley soup","rationale":"Barley contains gluten, as do wheat and rye. Corn, rice, and potato are naturally gluten free."},
    {"topic":"Special Diets","q":"Which sodium level defines a typical 2-gram sodium restriction ordered for heart failure?","options":["2,000 mg sodium daily","2,000 mg salt daily","200 mg sodium daily","20,000 mg sodium daily"],"answer":"2,000 mg sodium daily","rationale":"A 2-gram sodium diet equals 2,000 mg of sodium per day, not grams of salt."},
    {"topic":"Special Diets","q":"A client on a potassium-restricted diet should avoid which food?","options":["Baked potato with skin","White rice","Green beans","Apple"],"answer":"Baked potato with skin","rationale":"Potatoes are among the highest potassium foods. Leaching or limiting portions is often required."},
    {"topic":"Special Diets","q":"Which teaching helps a client reduce the potassium content of vegetables?","options":["Peel, slice thinly, soak, and boil in a large volume of water","Steam whole with the skin on","Microwave in a sealed bag","Roast without added liquid"],"answer":"Peel, slice thinly, soak, and boil in a large volume of water","rationale":"Leaching draws potassium into the cooking water, which is then discarded."},
    {"topic":"Special Diets","q":"A client asks about the purpose of a high-calorie, high-protein diet. Which response is correct?","options":["It supports healing and prevents further loss of lean body mass","It promotes rapid weight loss","It lowers blood glucose","It reduces fluid retention"],"answer":"It supports healing and prevents further loss of lean body mass","rationale":"Increased energy and protein are indicated for wounds, burns, cancer cachexia, and other catabolic states."},
    {"topic":"Special Diets","q":"A client following a kosher diet is served a cheeseburger. Which nursing action is appropriate?","options":["Replace the tray because meat and dairy are not combined","Remove only the bun","Encourage the client to eat what is provided","Document refusal of nutrition"],"answer":"Replace the tray because meat and dairy are not combined","rationale":"Kosher law prohibits serving meat and dairy together. The nurse should obtain an appropriate replacement."},

    # ---------------- Clinical Nutrition (18) ----------------
    {"topic":"Clinical Nutrition","q":"A nurse prepares to administer an intermittent gastric tube feeding. Which action should be taken first?","options":["Verify tube placement per facility policy","Flush with 100 mL of water","Warm the formula in a microwave","Position the client supine"],"answer":"Verify tube placement per facility policy","rationale":"Placement verification precedes any instillation to prevent pulmonary administration of formula."},
    {"topic":"Clinical Nutrition","q":"A client receiving continuous enteral feeding must have the head of the bed elevated to which minimum position?","options":["30 to 45 degrees","10 degrees","Flat","Trendelenburg"],"answer":"30 to 45 degrees","rationale":"Elevation of at least 30 degrees reduces reflux and aspiration risk during and after feeding."},
    {"topic":"Clinical Nutrition","q":"A nurse finds a gastric residual volume higher than the facility threshold. Which action is appropriate?","options":["Hold the feeding, reassess, and notify the provider per protocol","Discard the aspirate and double the rate","Flush with 500 mL of water","Remove the tube immediately"],"answer":"Hold the feeding, reassess, and notify the provider per protocol","rationale":"Elevated residuals suggest delayed emptying. Protocols direct holding, reassessment, and provider notification."},
    {"topic":"Clinical Nutrition","q":"Which formula characteristic most often contributes to diarrhea during enteral feeding?","options":["High osmolality and rapid infusion rate","Low protein content","Room temperature storage under one hour","Isotonic formula at a slow rate"],"answer":"High osmolality and rapid infusion rate","rationale":"Hyperosmolar formula delivered rapidly draws fluid into the lumen and causes osmotic diarrhea."},
    {"topic":"Clinical Nutrition","q":"Open-system enteral formula hanging at room temperature should be discarded after how long?","options":["Within 4 to 8 hours per facility policy","24 hours","48 hours","When it appears cloudy"],"answer":"Within 4 to 8 hours per facility policy","rationale":"Open systems are prone to bacterial growth. Most policies limit hang time to 4 to 8 hours."},
    {"topic":"Clinical Nutrition","q":"A client receiving parenteral nutrition has an infusion that will finish before the next bag arrives. Which action is appropriate?","options":["Hang 10% dextrose in water as ordered to prevent hypoglycemia","Stop the infusion and flush with saline","Increase the rate to finish faster","Hang lactated Ringer solution"],"answer":"Hang 10% dextrose in water as ordered to prevent hypoglycemia","rationale":"Abrupt cessation of high dextrose can cause rebound hypoglycemia. Dextrose is infused until the next bag is available."},
    {"topic":"Clinical Nutrition","q":"Which assessment finding in a client on parenteral nutrition requires immediate action?","options":["Temperature of 38.9 C with chills","Blood glucose of 130 mg/dL","Weight gain of 0.2 kg in one week","Mild thirst"],"answer":"Temperature of 38.9 C with chills","rationale":"Fever and rigors in a client with a central line suggest catheter-related bloodstream infection, a medical emergency."},
    {"topic":"Clinical Nutrition","q":"Which laboratory value should the nurse monitor most frequently when parenteral nutrition is initiated?","options":["Blood glucose","Serum amylase","Uric acid","Serum lipase"],"answer":"Blood glucose","rationale":"High dextrose loads commonly cause hyperglycemia, so glucose is monitored frequently during initiation."},
    {"topic":"Clinical Nutrition","q":"A client with severe malnutrition begins nutrition support. Which electrolyte pattern indicates refeeding syndrome?","options":["Low phosphorus, low potassium, and low magnesium","High phosphorus and high calcium","High sodium and high chloride","Normal electrolytes with high glucose only"],"answer":"Low phosphorus, low potassium, and low magnesium","rationale":"Insulin release after refeeding drives phosphorus, potassium, and magnesium intracellularly, producing the classic triad."},
    {"topic":"Clinical Nutrition","q":"Which action best prevents refeeding syndrome in a high-risk client?","options":["Start nutrition at a low rate and advance slowly with electrolyte monitoring","Start at full goal rate immediately","Withhold nutrition for one week","Give a large glucose bolus first"],"answer":"Start nutrition at a low rate and advance slowly with electrolyte monitoring","rationale":"Cautious initiation with electrolyte repletion and monitoring prevents dangerous intracellular shifts."},
    {"topic":"Clinical Nutrition","q":"A client with a nasogastric feeding tube needs medication. Which action is correct?","options":["Give each medication separately and flush between doses","Mix all medications together in one syringe","Add medications to the formula bag","Crush enteric-coated tablets"],"answer":"Give each medication separately and flush between doses","rationale":"Separate administration with flushes prevents drug interactions, precipitation, and tube occlusion."},
    {"topic":"Clinical Nutrition","q":"Which medication form should never be crushed for administration through a feeding tube?","options":["Extended-release tablets","Immediate-release tablets","Powder for suspension","Liquid elixir"],"answer":"Extended-release tablets","rationale":"Crushing extended-release forms destroys the delivery mechanism and can cause dose dumping and toxicity."},
    {"topic":"Clinical Nutrition","q":"A client receiving continuous enteral feeding is prescribed phenytoin. Which nursing action is appropriate?","options":["Hold the feeding before and after the dose as ordered","Add phenytoin to the formula","Give with the feeding at goal rate","Double the dose to compensate"],"answer":"Hold the feeding before and after the dose as ordered","rationale":"Enteral formula binds phenytoin and markedly reduces absorption. Holding the feeding around the dose preserves levels."},
    {"topic":"Clinical Nutrition","q":"Which indicator best reflects longer-term protein status when inflammation is absent?","options":["Serum albumin trend with clinical context","Single random glucose","One-time blood pressure","Pulse oximetry"],"answer":"Serum albumin trend with clinical context","rationale":"Albumin has a long half-life and reflects chronic status, but it falls with inflammation and must be interpreted clinically."},
    {"topic":"Clinical Nutrition","q":"A client with cancer reports altered taste and early satiety. Which intervention is most appropriate?","options":["Offer small, frequent, nutrient-dense meals and use plastic utensils for metallic taste","Serve three large meals","Restrict all seasoning","Withhold food until appetite returns"],"answer":"Offer small, frequent, nutrient-dense meals and use plastic utensils for metallic taste","rationale":"Small frequent meals address early satiety, and plastic utensils reduce the metallic taste caused by some therapies."},
    {"topic":"Clinical Nutrition","q":"Which intervention reduces nausea related to chemotherapy at mealtime?","options":["Serve cool, bland foods and avoid strong odors","Serve hot, spicy foods","Encourage large fluid volumes with meals","Serve favorite foods during peak nausea"],"answer":"Serve cool, bland foods and avoid strong odors","rationale":"Cool bland foods generate less aroma. Favorite foods are avoided during nausea to prevent learned food aversions."},
    {"topic":"Clinical Nutrition","q":"A client with mucositis from chemotherapy needs dietary teaching. Which foods should be avoided?","options":["Citrus juice, spicy foods, and crackers","Milkshakes","Scrambled eggs","Oatmeal"],"answer":"Citrus juice, spicy foods, and crackers","rationale":"Acidic, spicy, rough, and dry foods irritate damaged oral mucosa. Soft, bland, moist foods are preferred."},
    {"topic":"Clinical Nutrition","q":"Which client is at greatest risk for aspiration during oral feeding?","options":["Client with left-sided stroke and dysarthria who pockets food","Client with a sprained ankle","Client with well-controlled asthma","Client recovering from a hernia repair"],"answer":"Client with left-sided stroke and dysarthria who pockets food","rationale":"Stroke with impaired oral motor control and food pocketing indicates unsafe swallowing and high aspiration risk."},

    # ---------------- Lifespan Nutrition (26) ----------------
    {"topic":"Lifespan Nutrition","q":"How many additional kilocalories per day are generally recommended during the second trimester of pregnancy?","options":["About 340 kcal","About 1,000 kcal","No increase","About 50 kcal"],"answer":"About 340 kcal","rationale":"Energy needs rise by roughly 340 kcal/day in the second trimester and 450 kcal/day in the third."},
    {"topic":"Lifespan Nutrition","q":"A pregnant client with a normal prepregnancy BMI asks about expected weight gain. Which range should the nurse state?","options":["25 to 35 pounds","10 to 15 pounds","40 to 50 pounds","No gain is expected"],"answer":"25 to 35 pounds","rationale":"Institute of Medicine guidance recommends 25 to 35 pounds for a normal prepregnancy BMI."},
    {"topic":"Lifespan Nutrition","q":"Which recommendation should the nurse give a pregnant client about fish?","options":["Avoid shark, swordfish, king mackerel, and tilefish","Avoid all fish entirely","Eat only raw fish","Limit salmon to once monthly"],"answer":"Avoid shark, swordfish, king mackerel, and tilefish","rationale":"These large predatory fish concentrate methylmercury, which harms fetal neurologic development. Lower-mercury fish are encouraged."},
    {"topic":"Lifespan Nutrition","q":"A pregnant client reports constipation. Which teaching is best?","options":["Increase fiber, fluids, and physical activity","Take a stimulant laxative daily","Reduce all fluid intake","Eliminate fruits and vegetables"],"answer":"Increase fiber, fluids, and physical activity","rationale":"Progesterone slows GI motility. Fiber, fluid, and activity are first-line and safe measures."},
    {"topic":"Lifespan Nutrition","q":"A client in the first trimester reports morning sickness. Which teaching is appropriate?","options":["Eat dry crackers before rising and take small frequent meals","Drink large amounts of fluid with meals","Skip breakfast entirely","Eat high-fat fried foods"],"answer":"Eat dry crackers before rising and take small frequent meals","rationale":"Dry carbohydrate before arising and small frequent low-fat meals reduce nausea. Fluids are taken between meals."},
    {"topic":"Lifespan Nutrition","q":"Which food should a pregnant client avoid to reduce listeriosis risk?","options":["Soft cheese made from unpasteurized milk","Cooked chicken","Pasteurized yogurt","Whole grain bread"],"answer":"Soft cheese made from unpasteurized milk","rationale":"Listeria monocytogenes crosses the placenta and can cause miscarriage, stillbirth, and neonatal sepsis."},
    {"topic":"Lifespan Nutrition","q":"A lactating client asks about additional energy needs. Which response is correct?","options":["About 330 to 400 additional kcal per day","No additional kcal","About 1,200 additional kcal","Fewer kcal than during pregnancy but no fluid change"],"answer":"About 330 to 400 additional kcal per day","rationale":"Milk production increases energy needs by roughly 330 to 400 kcal/day above prepregnancy requirements."},
    {"topic":"Lifespan Nutrition","q":"A breastfeeding client asks about alcohol. Which response is best?","options":["Wait about two hours per standard drink before nursing","Alcohol never enters breast milk","Pumping and discarding removes alcohol immediately","Any amount permanently harms milk supply"],"answer":"Wait about two hours per standard drink before nursing","rationale":"Alcohol equilibrates with blood levels and clears over time. Pumping and discarding does not speed clearance."},
    {"topic":"Lifespan Nutrition","q":"At what age should complementary solid foods generally be introduced?","options":["Around 6 months when developmental readiness is present","At 2 months","At 12 months","At 3 weeks"],"answer":"Around 6 months when developmental readiness is present","rationale":"Head control, sitting with support, and loss of the extrusion reflex signal readiness, typically near 6 months."},
    {"topic":"Lifespan Nutrition","q":"Which instruction should the nurse give about introducing new foods to an infant?","options":["Introduce one new single-ingredient food every 3 to 5 days","Introduce several new foods at once","Add honey to sweeten cereal","Begin with mixed dinners"],"answer":"Introduce one new single-ingredient food every 3 to 5 days","rationale":"Spacing introductions allows identification of the specific food if an allergic reaction occurs."},
    {"topic":"Lifespan Nutrition","q":"A parent asks when cow milk can be introduced. Which response is correct?","options":["After 12 months of age","At 6 months","At 3 months","Not until age 3 years"],"answer":"After 12 months of age","rationale":"Cow milk before 12 months provides excessive protein and minerals, is low in iron, and can cause occult GI blood loss."},
    {"topic":"Lifespan Nutrition","q":"Which food poses the greatest choking hazard for a toddler?","options":["Whole grapes","Applesauce","Mashed sweet potato","Soft scrambled egg"],"answer":"Whole grapes","rationale":"Round, firm, smooth foods occlude the airway. Grapes should be quartered lengthwise for young children."},
    {"topic":"Lifespan Nutrition","q":"A parent reports the toddler drinks 40 ounces of milk daily and refuses solid food. Which risk should the nurse identify?","options":["Iron deficiency anemia","Hypernatremia","Vitamin C toxicity","Zinc excess"],"answer":"Iron deficiency anemia","rationale":"Excessive milk displaces iron-rich foods and can cause occult GI blood loss, a classic toddler anemia pattern."},
    {"topic":"Lifespan Nutrition","q":"Which approach best addresses physiologic anorexia in a toddler?","options":["Offer small portions of nutritious foods and allow self-regulation","Force the child to finish each plate","Offer unlimited juice between meals","Withhold food until the next meal"],"answer":"Offer small portions of nutritious foods and allow self-regulation","rationale":"Growth slows in toddlerhood and appetite naturally decreases. Pressure-free structured feeding supports intake."},
    {"topic":"Lifespan Nutrition","q":"What is the recommended maximum daily juice intake for a child aged 1 to 3 years?","options":["4 ounces","16 ounces","24 ounces","Unlimited"],"answer":"4 ounces","rationale":"The American Academy of Pediatrics limits juice to 4 ounces daily for ages 1 to 3 to protect teeth and appetite."},
    {"topic":"Lifespan Nutrition","q":"Which teaching prevents baby bottle tooth decay?","options":["Do not put the infant to bed with a bottle of milk or juice","Use only warmed juice at bedtime","Add cereal to the bedtime bottle","Give the bottle in a dark room"],"answer":"Do not put the infant to bed with a bottle of milk or juice","rationale":"Pooled carbohydrate around the teeth during sleep causes early childhood caries."},
    {"topic":"Lifespan Nutrition","q":"A school-age child brings a lunch of chips, cookies, and soda. Which nursing action is most appropriate?","options":["Teach the child and caregiver about balanced lunch options","Confiscate the lunch","Report the family to child protective services","Ignore the finding"],"answer":"Teach the child and caregiver about balanced lunch options","rationale":"Education directed at both the child and the food purchaser is the appropriate first-level intervention."},
    {"topic":"Lifespan Nutrition","q":"Which nutrient is of greatest concern during the adolescent growth spurt in females?","options":["Iron","Vitamin K","Selenium","Biotin"],"answer":"Iron","rationale":"Rapid growth combined with menstrual losses makes iron the most commonly deficient nutrient in adolescent females."},
    {"topic":"Lifespan Nutrition","q":"Which nutrient is critical during adolescence for achieving peak bone mass?","options":["Calcium","Sodium","Vitamin E","Chloride"],"answer":"Calcium","rationale":"Roughly half of adult bone mass accrues during adolescence, making calcium and vitamin D intake essential."},
    {"topic":"Lifespan Nutrition","q":"An adolescent athlete asks about protein supplements. Which response is best?","options":["Most athletes meet protein needs through food without supplements","All athletes require double the RDA in powder form","Protein supplements build muscle without training","Protein needs decrease with training"],"answer":"Most athletes meet protein needs through food without supplements","rationale":"Typical dietary intake usually meets the modestly increased protein needs of athletes."},
    {"topic":"Lifespan Nutrition","q":"Which age-related change most affects nutrient intake in older adults?","options":["Decreased taste, smell, and dentition","Increased gastric acid production","Increased thirst sensation","Increased basal metabolic rate"],"answer":"Decreased taste, smell, and dentition","rationale":"Sensory decline and dental problems reduce food enjoyment and the ability to chew, lowering intake."},
    {"topic":"Lifespan Nutrition","q":"An older adult has decreased gastric acid production. Which nutrient absorption is most affected?","options":["Vitamin B12 and iron","Vitamin K only","Sodium","Fat-soluble vitamins only"],"answer":"Vitamin B12 and iron","rationale":"Gastric acid is required to free protein-bound B12 and to convert iron to its absorbable ferrous form."},
    {"topic":"Lifespan Nutrition","q":"Which intervention best supports adequate intake in an older adult who eats alone?","options":["Arrange congregate meals or shared mealtimes","Serve all meals in the bedroom","Limit food choices to one option","Discourage family visits at mealtime"],"answer":"Arrange congregate meals or shared mealtimes","rationale":"Social isolation is a major contributor to poor intake. Shared meals reliably improve consumption in older adults."},
    {"topic":"Lifespan Nutrition","q":"An older adult on a fixed income reports skipping meals at the end of the month. Which referral is most appropriate?","options":["Community nutrition program such as SNAP or Meals on Wheels","Physical therapy","Ophthalmology","Dermatology"],"answer":"Community nutrition program such as SNAP or Meals on Wheels","rationale":"Food insecurity requires connection to food assistance resources as part of the nursing plan of care."},
    {"topic":"Lifespan Nutrition","q":"Which finding in an older adult most strongly suggests dehydration?","options":["Confusion with dark concentrated urine","Moist mucous membranes","Bounding pulse with clear urine","Weight gain of 2 kg"],"answer":"Confusion with dark concentrated urine","rationale":"Acute confusion is often the first sign of dehydration in older adults, along with concentrated urine."},
    {"topic":"Lifespan Nutrition","q":"An older adult with dementia leaves most food untouched. Which intervention should the nurse try first?","options":["Offer finger foods and provide simple cueing during meals","Insert a feeding tube","Restrict the meal to 10 minutes","Serve all items at once with multiple utensils"],"answer":"Offer finger foods and provide simple cueing during meals","rationale":"Finger foods and step-by-step cueing compensate for apraxia and attention deficits before considering invasive options."},

    # ---------------- Food Safety (12) ----------------
    {"topic":"Food Safety","q":"What is the temperature range of the food danger zone?","options":["40 F to 140 F","0 F to 32 F","150 F to 200 F","32 F to 40 F"],"answer":"40 F to 140 F","rationale":"Bacteria multiply rapidly between 40 F and 140 F. Perishable food should not remain in this range beyond two hours."},
    {"topic":"Food Safety","q":"To what minimum internal temperature should ground beef be cooked?","options":["160 F","145 F","135 F","120 F"],"answer":"160 F","rationale":"Ground beef requires 160 F because grinding distributes surface pathogens throughout the product."},
    {"topic":"Food Safety","q":"To what minimum internal temperature should poultry be cooked?","options":["165 F","145 F","155 F","135 F"],"answer":"165 F","rationale":"All poultry requires a minimum internal temperature of 165 F to destroy Salmonella and Campylobacter."},
    {"topic":"Food Safety","q":"Which method is safe for thawing frozen chicken?","options":["In the refrigerator","On the kitchen counter","In warm standing water","In a sunny window"],"answer":"In the refrigerator","rationale":"Refrigerator thawing keeps the food out of the danger zone. Cold running water and microwave thawing are also acceptable."},
    {"topic":"Food Safety","q":"A client asks how long leftovers may be safely refrigerated. Which response is correct?","options":["Three to four days","Ten days","Two weeks","Until the odor changes"],"answer":"Three to four days","rationale":"Refrigerated leftovers should be used within three to four days or frozen for longer storage."},
    {"topic":"Food Safety","q":"Which client is at highest risk for severe foodborne illness?","options":["Client receiving chemotherapy","Healthy college student","Adult with controlled hypertension","Client with seasonal allergies"],"answer":"Client receiving chemotherapy","rationale":"Immunosuppression markedly increases susceptibility to and severity of foodborne infection."},
    {"topic":"Food Safety","q":"Which food is most commonly associated with Salmonella infection?","options":["Undercooked eggs and poultry","Canned peaches","Boiled rice","Pasteurized milk"],"answer":"Undercooked eggs and poultry","rationale":"Eggs and poultry are classic Salmonella vehicles when undercooked or cross-contaminated."},
    {"topic":"Food Safety","q":"Bulging cans and a foul odor should raise concern for which organism?","options":["Clostridium botulinum","Streptococcus pyogenes","Candida albicans","Vitamin degradation only"],"answer":"Clostridium botulinum","rationale":"Gas-producing anaerobic growth in improperly canned foods signals possible botulinum toxin. Discard without tasting."},
    {"topic":"Food Safety","q":"Which teaching prevents Escherichia coli O157:H7 infection?","options":["Cook ground beef thoroughly and avoid unpasteurized juice","Rinse ground beef before cooking","Store beef at room temperature","Use the same board for meat and salad"],"answer":"Cook ground beef thoroughly and avoid unpasteurized juice","rationale":"Undercooked ground beef and unpasteurized products are the main vehicles for this toxin-producing strain."},
    {"topic":"Food Safety","q":"A client is prescribed a neutropenic diet. Which food should be avoided?","options":["Fresh raw berries","Cooked carrots","Canned peaches","Baked chicken"],"answer":"Fresh raw berries","rationale":"Raw produce with irregular surfaces cannot be reliably cleaned and is restricted for severely neutropenic clients."},
    {"topic":"Food Safety","q":"Which action best prevents cross-contamination when preparing a salad and raw chicken?","options":["Prepare the salad first, then the chicken, using separate boards","Prepare the chicken first on the same board","Rinse the board with cold water between items","Use one knife for both"],"answer":"Prepare the salad first, then the chicken, using separate boards","rationale":"Preparing ready-to-eat foods before raw meat and using separate equipment prevents pathogen transfer."},
    {"topic":"Food Safety","q":"How long may a hot food item safely remain at room temperature at a summer picnic when the temperature exceeds 90 F?","options":["One hour","Four hours","Six hours","Until it cools completely"],"answer":"One hour","rationale":"Above 90 F, the safe holding window drops from two hours to one hour."},

    # ---------------- Assessment (12) ----------------
    {"topic":"Assessment","q":"Which method best captures a client's usual intake over time rather than a single day?","options":["Food frequency questionnaire","24-hour recall","Single calorie count","One observed meal"],"answer":"Food frequency questionnaire","rationale":"Food frequency tools capture habitual patterns, while a 24-hour recall reflects only one day and may not be typical."},
    {"topic":"Assessment","q":"A nurse performs a 24-hour dietary recall. Which limitation should be considered?","options":["It depends on memory and may not represent usual intake","It requires laboratory equipment","It takes several weeks","It cannot be used with adults"],"answer":"It depends on memory and may not represent usual intake","rationale":"Recall bias and day-to-day variability limit the accuracy of a single 24-hour recall."},
    {"topic":"Assessment","q":"Which body mass index value defines obesity in adults?","options":["30 or greater","25 to 29.9","18.5 to 24.9","Below 18.5"],"answer":"30 or greater","rationale":"BMI of 30 or above defines obesity, 25 to 29.9 overweight, 18.5 to 24.9 normal, and below 18.5 underweight."},
    {"topic":"Assessment","q":"A client has a BMI of 26.4. How should the nurse classify this result?","options":["Overweight","Normal weight","Obese class I","Underweight"],"answer":"Overweight","rationale":"A BMI between 25 and 29.9 falls in the overweight category."},
    {"topic":"Assessment","q":"Which waist circumference indicates increased cardiometabolic risk in an adult male?","options":["Greater than 40 inches","Greater than 30 inches","Greater than 35 inches","Waist circumference does not indicate risk"],"answer":"Greater than 40 inches","rationale":"Risk thresholds are greater than 40 inches for men and greater than 35 inches for women."},
    {"topic":"Assessment","q":"An adult reports losing 12 pounds unintentionally from 160 pounds over two months. How should the nurse interpret this?","options":["Significant weight loss requiring nutrition evaluation","Expected variation","Beneficial and needs no follow-up","Related only to fluid balance"],"answer":"Significant weight loss requiring nutrition evaluation","rationale":"Unintentional loss of 7.5% of body weight in two months exceeds significance thresholds and signals malnutrition risk."},
    {"topic":"Assessment","q":"Which physical finding suggests protein-energy malnutrition?","options":["Temporal muscle wasting and thin, sparse hair","Thick shiny hair","Firm muscle tone","Pink moist conjunctiva"],"answer":"Temporal muscle wasting and thin, sparse hair","rationale":"Loss of temporal and clavicular muscle mass with hair changes is a hallmark of protein-energy malnutrition."},
    {"topic":"Assessment","q":"A nurse notes spoon-shaped nails on a client. Which deficiency should be suspected?","options":["Iron","Vitamin K","Sodium","Vitamin E"],"answer":"Iron","rationale":"Koilonychia, or spoon nails, is a classic physical finding of chronic iron deficiency."},
    {"topic":"Assessment","q":"Which serum protein responds most rapidly to acute changes in nutrition status?","options":["Prealbumin","Albumin","Hemoglobin","Total cholesterol"],"answer":"Prealbumin","rationale":"Prealbumin has a half-life of about two days, making it more responsive than albumin to short-term change."},
    {"topic":"Assessment","q":"Why should serum albumin be interpreted cautiously in an acutely ill client?","options":["Inflammation and fluid status alter albumin independently of nutrition","Albumin is unaffected by illness","Albumin measures only carbohydrate intake","Albumin rises with malnutrition"],"answer":"Inflammation and fluid status alter albumin independently of nutrition","rationale":"Albumin is a negative acute phase reactant and falls with inflammation, overhydration, and liver or kidney disease."},
    {"topic":"Assessment","q":"Which question best screens for food insecurity?","options":["In the past 12 months, did the food you bought not last and you did not have money to get more?","Do you enjoy cooking?","How many restaurants are near you?","What is your favorite vegetable?"],"answer":"In the past 12 months, did the food you bought not last and you did not have money to get more?","rationale":"This is a validated two-item food insecurity screening question used in clinical settings."},
    {"topic":"Assessment","q":"A client's calorie count shows intake of about 40% of estimated needs for five days. Which action is the priority?","options":["Notify the provider and request a dietitian consult","Continue monitoring for another week","Remove the calorie count","Document only"],"answer":"Notify the provider and request a dietitian consult","rationale":"Sustained intake below half of estimated needs warrants prompt interdisciplinary intervention."},

    # ---------------- Diabetes Nutrition (14) ----------------
    {"topic":"Diabetes Nutrition","q":"Which carbohydrate amount is generally counted as one carbohydrate serving or exchange?","options":["15 grams","5 grams","30 grams","50 grams"],"answer":"15 grams","rationale":"One carbohydrate choice equals approximately 15 g of carbohydrate in the exchange system."},
    {"topic":"Diabetes Nutrition","q":"A client with type 1 diabetes eats a meal containing 60 g of carbohydrate. How many carbohydrate choices is this?","options":["4","2","6","8"],"answer":"4","rationale":"Dividing 60 g by 15 g per choice yields 4 carbohydrate choices."},
    {"topic":"Diabetes Nutrition","q":"A client with diabetes reports a blood glucose of 58 mg/dL and is alert. Which action is correct?","options":["Give 15 g of fast-acting carbohydrate and recheck in 15 minutes","Give a high-fat snack","Withhold food and observe","Administer additional insulin"],"answer":"Give 15 g of fast-acting carbohydrate and recheck in 15 minutes","rationale":"The rule of 15 directs 15 g of rapid carbohydrate followed by recheck in 15 minutes for conscious hypoglycemia."},
    {"topic":"Diabetes Nutrition","q":"Which item provides approximately 15 g of fast-acting carbohydrate for hypoglycemia?","options":["4 ounces of regular fruit juice","8 ounces of diet soda","A tablespoon of peanut butter","A slice of cheese"],"answer":"4 ounces of regular fruit juice","rationale":"Four ounces of juice, 4 glucose tablets, or one tablespoon of honey each supply about 15 g of rapid carbohydrate."},
    {"topic":"Diabetes Nutrition","q":"After treating hypoglycemia and confirming glucose has normalized, which action should follow if the next meal is more than an hour away?","options":["Provide a snack with carbohydrate and protein","Give another 15 g of simple sugar","Withhold all food","Administer insulin"],"answer":"Provide a snack with carbohydrate and protein","rationale":"A mixed snack sustains glucose and prevents recurrent hypoglycemia before the next meal."},
    {"topic":"Diabetes Nutrition","q":"A client with diabetes asks about the glycemic index. Which explanation is correct?","options":["It ranks how quickly a carbohydrate food raises blood glucose","It measures total calories","It measures fat content","It measures sodium content"],"answer":"It ranks how quickly a carbohydrate food raises blood glucose","rationale":"Glycemic index compares the postprandial glucose response of foods relative to a reference carbohydrate."},
    {"topic":"Diabetes Nutrition","q":"Which pairing best blunts the postprandial glucose rise?","options":["Whole grain crackers with cheese","White bread alone","Fruit juice alone","Regular soda with candy"],"answer":"Whole grain crackers with cheese","rationale":"Fiber, protein, and fat slow gastric emptying and moderate the glucose response."},
    {"topic":"Diabetes Nutrition","q":"A client with type 2 diabetes has a sick day and cannot eat solid food. Which teaching is correct?","options":["Continue medications as directed, sip carbohydrate-containing fluids, and monitor glucose frequently","Stop all diabetes medication","Avoid all fluids","Check glucose once daily"],"answer":"Continue medications as directed, sip carbohydrate-containing fluids, and monitor glucose frequently","rationale":"Illness raises counterregulatory hormones and glucose. Sick day rules maintain medication, hydration, and frequent monitoring."},
    {"topic":"Diabetes Nutrition","q":"Which statement by a client with gestational diabetes indicates correct understanding?","options":["I will eat smaller, evenly distributed meals with a bedtime snack","I will skip breakfast to lower my numbers","I will eliminate all carbohydrate","I will fast until my next appointment"],"answer":"I will eat smaller, evenly distributed meals with a bedtime snack","rationale":"Even carbohydrate distribution with a bedtime snack limits postprandial peaks and prevents overnight ketosis."},
    {"topic":"Diabetes Nutrition","q":"Which beverage is most appropriate for routine intake in a client with diabetes?","options":["Water","Regular soda","Sweetened iced tea","Fruit punch"],"answer":"Water","rationale":"Sugar-sweetened beverages cause rapid glucose elevation and provide no nutritional benefit."},
    {"topic":"Diabetes Nutrition","q":"A client with diabetes asks about alcohol. Which teaching is most important?","options":["Consume alcohol with food because it can cause delayed hypoglycemia","Alcohol always raises blood glucose","Alcohol may replace a meal","No monitoring is needed after drinking"],"answer":"Consume alcohol with food because it can cause delayed hypoglycemia","rationale":"Alcohol inhibits hepatic gluconeogenesis and can cause hypoglycemia hours after intake, especially without food."},
    {"topic":"Diabetes Nutrition","q":"Which laboratory value best reflects average glucose control over the previous three months?","options":["Hemoglobin A1c","Fasting glucose","Random glucose","Serum insulin"],"answer":"Hemoglobin A1c","rationale":"A1c reflects glycation over the lifespan of the red blood cell, roughly two to three months."},
    {"topic":"Diabetes Nutrition","q":"A client reads a label listing 45 g total carbohydrate and 8 g dietary fiber per serving. Which net carbohydrate value should be reported when the provider uses fiber subtraction?","options":["37 g","53 g","45 g","8 g"],"answer":"37 g","rationale":"Subtracting fiber from total carbohydrate yields 45 minus 8, or 37 g, when this method is prescribed."},
    {"topic":"Diabetes Nutrition","q":"Which meal pattern best supports a client with diabetes and diabetic gastroparesis?","options":["Small, low-fat, low-fiber meals eaten more frequently","Three large high-fiber meals","High-fat meals to slow absorption","One large evening meal"],"answer":"Small, low-fat, low-fiber meals eaten more frequently","rationale":"Fat and fiber further delay gastric emptying, so small, low-fat, low-fiber meals improve tolerance."},

    # ---------------- Cardiovascular Nutrition (12) ----------------
    {"topic":"Cardiovascular Nutrition","q":"What is the recommended daily sodium limit for most adults with hypertension?","options":["Less than 1,500 to 2,300 mg","Less than 5,000 mg","Less than 500 mg","No limit is needed"],"answer":"Less than 1,500 to 2,300 mg","rationale":"General guidance is below 2,300 mg daily, with further reduction toward 1,500 mg providing added benefit for hypertension."},
    {"topic":"Cardiovascular Nutrition","q":"Which food contributes the most sodium in a typical American diet?","options":["Processed and restaurant foods","The salt shaker at the table","Fresh fruit","Plain rice"],"answer":"Processed and restaurant foods","rationale":"Roughly 70% of dietary sodium comes from processed and restaurant foods rather than added table salt."},
    {"topic":"Cardiovascular Nutrition","q":"A client with heart failure gains 3 pounds in two days. Which action is the priority?","options":["Notify the provider because this suggests fluid retention","Encourage additional fluids","Document as expected","Increase sodium intake"],"answer":"Notify the provider because this suggests fluid retention","rationale":"A gain of 2 to 3 pounds in 24 to 48 hours indicates fluid accumulation and requires prompt evaluation."},
    {"topic":"Cardiovascular Nutrition","q":"Which food should a client on a low-sodium diet avoid?","options":["Canned soup","Fresh apple","Unsalted almonds","Plain brown rice"],"answer":"Canned soup","rationale":"Canned soups are among the highest sodium items in the retail food supply."},
    {"topic":"Cardiovascular Nutrition","q":"A client on a low-sodium diet asks about salt substitutes. Which nursing response is most important?","options":["Check with the provider because many substitutes contain potassium chloride","Use them freely on all foods","They contain no minerals","They lower potassium levels"],"answer":"Check with the provider because many substitutes contain potassium chloride","rationale":"Potassium-based substitutes are dangerous in renal impairment or with potassium-sparing diuretics and ACE inhibitors."},
    {"topic":"Cardiovascular Nutrition","q":"Which teaching helps a client reduce sodium without losing flavor?","options":["Use herbs, citrus, vinegar, and salt-free seasoning blends","Add more processed sauces","Use bouillon cubes","Use soy sauce instead of salt"],"answer":"Use herbs, citrus, vinegar, and salt-free seasoning blends","rationale":"Acid and aromatics enhance perceived flavor. Soy sauce and bouillon are high-sodium substitutes."},
    {"topic":"Cardiovascular Nutrition","q":"Which lipid change most directly reduces cardiovascular risk?","options":["Lowering LDL cholesterol","Lowering HDL cholesterol","Raising trans fat intake","Raising triglycerides"],"answer":"Lowering LDL cholesterol","rationale":"LDL is the primary atherogenic lipoprotein and the main target of dietary and pharmacologic therapy."},
    {"topic":"Cardiovascular Nutrition","q":"A client asks how to raise HDL cholesterol. Which recommendation is best?","options":["Increase regular physical activity and stop smoking","Increase saturated fat","Increase refined sugar","Decrease all dietary fat to zero"],"answer":"Increase regular physical activity and stop smoking","rationale":"Aerobic activity and smoking cessation are the most reliable lifestyle measures for raising HDL."},
    {"topic":"Cardiovascular Nutrition","q":"Which dietary change most effectively lowers elevated triglycerides?","options":["Reduce added sugars, refined carbohydrate, and alcohol","Reduce dietary fiber","Increase fruit juice","Increase alcohol with meals"],"answer":"Reduce added sugars, refined carbohydrate, and alcohol","rationale":"Hypertriglyceridemia responds strongly to reduction of simple sugars, refined starch, and alcohol."},
    {"topic":"Cardiovascular Nutrition","q":"Which food pattern is most consistent with the Mediterranean diet?","options":["Olive oil, vegetables, legumes, fish, and whole grains","Red meat daily with butter","Processed snack foods","High-sugar beverages"],"answer":"Olive oil, vegetables, legumes, fish, and whole grains","rationale":"The Mediterranean pattern emphasizes plant foods, olive oil, and fish, with limited red and processed meat."},
    {"topic":"Cardiovascular Nutrition","q":"A client reads a food label showing 480 mg sodium per serving with 2.5 servings per container. How much sodium is in the full container?","options":["1,200 mg","480 mg","960 mg","240 mg"],"answer":"1,200 mg","rationale":"Multiplying 480 mg by 2.5 servings gives 1,200 mg for the entire container."},
    {"topic":"Cardiovascular Nutrition","q":"A label states a food is sodium free. Which sodium content per serving does this indicate?","options":["Less than 5 mg","Less than 140 mg","Less than 35 mg","Less than 300 mg"],"answer":"Less than 5 mg","rationale":"Sodium free means under 5 mg, very low sodium under 35 mg, and low sodium 140 mg or less per serving."},

    # ---------------- Renal Nutrition (10) ----------------
    {"topic":"Renal Nutrition","q":"A client on hemodialysis asks about protein intake. Which teaching is correct?","options":["Protein needs increase because dialysis removes amino acids","Protein should be eliminated entirely","Protein needs are the same as before dialysis","Protein should be limited to 20 g daily"],"answer":"Protein needs increase because dialysis removes amino acids","rationale":"Dialysis causes amino acid losses, so protein needs rise compared with the predialysis restricted diet."},
    {"topic":"Renal Nutrition","q":"A client with stage 4 chronic kidney disease not on dialysis asks about protein. Which teaching is correct?","options":["Moderate protein restriction may slow disease progression","Unlimited protein is encouraged","Protein has no effect on the kidney","Only plant protein is prohibited"],"answer":"Moderate protein restriction may slow disease progression","rationale":"Before dialysis, moderating protein reduces nitrogenous waste and may slow the decline in kidney function."},
    {"topic":"Renal Nutrition","q":"Which food should a client with hyperkalemia avoid?","options":["Cantaloupe","White bread","Applesauce","Green beans"],"answer":"Cantaloupe","rationale":"Melons, bananas, oranges, potatoes, and tomatoes are high-potassium foods restricted in hyperkalemia."},
    {"topic":"Renal Nutrition","q":"Which fruit is appropriate for a client on a potassium-restricted renal diet?","options":["Apple","Banana","Orange","Kiwi"],"answer":"Apple","rationale":"Apples, berries, grapes, and pineapple are lower in potassium than bananas, oranges, and melons."},
    {"topic":"Renal Nutrition","q":"A client is prescribed a phosphate binder. When should it be taken?","options":["With meals and snacks","On an empty stomach at bedtime","Two hours after meals","Only in the morning"],"answer":"With meals and snacks","rationale":"Binders must be present in the gut with food to bind dietary phosphorus and prevent absorption."},
    {"topic":"Renal Nutrition","q":"Which laboratory result indicates the phosphate binder is effective?","options":["Serum phosphorus within the target range","Rising serum phosphorus","Rising serum potassium","Falling hemoglobin"],"answer":"Serum phosphorus within the target range","rationale":"The therapeutic goal of a binder is normalization of serum phosphorus."},
    {"topic":"Renal Nutrition","q":"A client on dialysis has a fluid restriction. Which teaching helps manage thirst?","options":["Suck on ice chips counted as fluid and use sugar-free hard candy","Drink large amounts quickly","Increase salty snacks","Rinse the mouth and swallow the water"],"answer":"Suck on ice chips counted as fluid and use sugar-free hard candy","rationale":"Ice chips count toward the fluid allowance, and hard candy stimulates saliva without adding volume. Sodium worsens thirst."},
    {"topic":"Renal Nutrition","q":"Which finding indicates a client on hemodialysis exceeded the interdialytic fluid allowance?","options":["Weight gain of 4 kg between treatments","Weight loss of 1 kg","Stable weight","Decreased blood pressure with dry mucous membranes"],"answer":"Weight gain of 4 kg between treatments","rationale":"Interdialytic weight gain reflects fluid accumulation. Gains beyond 1 to 2 kg indicate excess intake."},
    {"topic":"Renal Nutrition","q":"A client with a history of calcium oxalate kidney stones asks about prevention. Which teaching is most important?","options":["Increase fluid intake to produce dilute urine","Eliminate all dietary calcium","Increase oxalate-rich foods","Restrict all fluids in the evening"],"answer":"Increase fluid intake to produce dilute urine","rationale":"High fluid intake is the single most effective preventive measure. Restricting dietary calcium can paradoxically increase stone risk."},
    {"topic":"Renal Nutrition","q":"Which food should a client with calcium oxalate stones limit?","options":["Spinach and rhubarb","Chicken breast","White rice","Apples"],"answer":"Spinach and rhubarb","rationale":"Spinach, rhubarb, beets, nuts, and tea are high-oxalate foods that increase urinary oxalate excretion."},

    # ---------------- GI and Liver Nutrition (12) ----------------
    {"topic":"GI and Liver Nutrition","q":"Which teaching is appropriate for a client with gastroesophageal reflux disease?","options":["Avoid lying down for two to three hours after eating","Eat a large meal at bedtime","Increase caffeine intake","Wear a tight abdominal binder after meals"],"answer":"Avoid lying down for two to three hours after eating","rationale":"Remaining upright uses gravity to reduce reflux. Late large meals and abdominal pressure worsen symptoms."},
    {"topic":"GI and Liver Nutrition","q":"Which food should a client with GERD limit?","options":["Peppermint and chocolate","Oatmeal","Baked chicken","Green beans"],"answer":"Peppermint and chocolate","rationale":"Peppermint, chocolate, caffeine, alcohol, and fat reduce lower esophageal sphincter tone."},
    {"topic":"GI and Liver Nutrition","q":"A client with an acute exacerbation of diverticulitis is prescribed diet therapy. Which diet is appropriate initially?","options":["Clear liquid, advancing as symptoms resolve","High-fiber diet immediately","Regular diet with nuts","High-residue diet"],"answer":"Clear liquid, advancing as symptoms resolve","rationale":"Bowel rest with clear liquids is used during acute inflammation, with gradual fiber reintroduction after resolution."},
    {"topic":"GI and Liver Nutrition","q":"Which diet is recommended for a client with diverticulosis without acute inflammation?","options":["High-fiber diet with adequate fluid","Clear liquid diet","Low-residue diet permanently","Nothing by mouth"],"answer":"High-fiber diet with adequate fluid","rationale":"Fiber increases stool bulk, reduces intraluminal pressure, and helps prevent diverticulitis episodes."},
    {"topic":"GI and Liver Nutrition","q":"A client with an acute exacerbation of Crohn disease should follow which dietary approach?","options":["Low-residue, high-protein, high-calorie intake","High-fiber raw vegetables","Unrestricted diet","High-lactose intake"],"answer":"Low-residue, high-protein, high-calorie intake","rationale":"Reducing residue rests the inflamed bowel while increased protein and energy offset losses and support healing."},
    {"topic":"GI and Liver Nutrition","q":"Which nutrient deficiency is most likely after ileal resection?","options":["Vitamin B12","Vitamin C","Sodium","Folate"],"answer":"Vitamin B12","rationale":"The terminal ileum is the sole site of intrinsic factor-B12 complex absorption."},
    {"topic":"GI and Liver Nutrition","q":"A client with lactose intolerance asks about calcium. Which teaching is best?","options":["Choose lactose-free milk, fortified plant milk, or hard aged cheese","Eliminate all calcium sources","Drink large amounts of regular milk","Rely on vitamin C for bone health"],"answer":"Choose lactose-free milk, fortified plant milk, or hard aged cheese","rationale":"Lactose-free and fortified products and low-lactose aged cheeses maintain calcium intake without symptoms."},
    {"topic":"GI and Liver Nutrition","q":"A client with acute pancreatitis is advancing from NPO status. Which diet order is expected?","options":["Low-fat, small, frequent oral feedings","High-fat diet to slow secretion","Regular diet with alcohol permitted","High-fat parenteral emulsion only"],"answer":"Low-fat, small, frequent oral feedings","rationale":"Fat is the strongest stimulus for pancreatic enzyme secretion, so low-fat small meals are used during recovery."},
    {"topic":"GI and Liver Nutrition","q":"Which substance must a client with chronic pancreatitis avoid completely?","options":["Alcohol","Water","Whole grains","Lean protein"],"answer":"Alcohol","rationale":"Alcohol is a primary cause of chronic pancreatitis and accelerates further pancreatic destruction."},
    {"topic":"GI and Liver Nutrition","q":"A client with cirrhosis and ascites is placed on which dietary restriction?","options":["Sodium restriction","Protein elimination","Carbohydrate elimination","Vitamin restriction"],"answer":"Sodium restriction","rationale":"Sodium restriction with diuretics is the mainstay of ascites management. Routine severe protein restriction is not recommended."},
    {"topic":"GI and Liver Nutrition","q":"A client with cirrhosis develops hepatic encephalopathy. Which nutrition approach is appropriate?","options":["Maintain adequate protein with lactulose therapy as ordered","Eliminate all protein indefinitely","Increase sodium intake","Withhold all nutrition"],"answer":"Maintain adequate protein with lactulose therapy as ordered","rationale":"Current practice maintains protein to preserve muscle mass while treating encephalopathy pharmacologically."},
    {"topic":"GI and Liver Nutrition","q":"Which teaching is appropriate for a client with a new ileostomy?","options":["Increase fluid and sodium intake because output is high and watery","Restrict all fluids","Expect formed stool immediately","Avoid all salt"],"answer":"Increase fluid and sodium intake because output is high and watery","rationale":"Ileostomy output bypasses colonic absorption, producing significant fluid and sodium losses that must be replaced."},

    # ---------------- Drug and Nutrient Interactions (12) ----------------
    {"topic":"Drug and Nutrient Interactions","q":"A client takes a monoamine oxidase inhibitor. Which food must be avoided?","options":["Aged cheddar cheese","Fresh apple","White rice","Plain yogurt"],"answer":"Aged cheddar cheese","rationale":"Tyramine in aged, fermented, and cured foods can precipitate hypertensive crisis with MAOI therapy."},
    {"topic":"Drug and Nutrient Interactions","q":"Which additional food should a client taking a monoamine oxidase inhibitor avoid?","options":["Cured salami and draft beer","Fresh chicken","Steamed broccoli","Milk"],"answer":"Cured salami and draft beer","rationale":"Cured meats, tap beer, soy sauce, and fermented products are high in tyramine."},
    {"topic":"Drug and Nutrient Interactions","q":"A client is prescribed a statin. Which beverage should be avoided?","options":["Grapefruit juice","Orange juice","Water","Milk"],"answer":"Grapefruit juice","rationale":"Grapefruit inhibits intestinal CYP3A4, increasing serum levels of certain statins and the risk of myopathy."},
    {"topic":"Drug and Nutrient Interactions","q":"A client takes a tetracycline antibiotic. Which teaching is correct?","options":["Avoid dairy, antacids, and iron within two hours of the dose","Always take with milk","Take with a calcium supplement","Take with an antacid to reduce upset"],"answer":"Avoid dairy, antacids, and iron within two hours of the dose","rationale":"Divalent and trivalent cations chelate tetracyclines and markedly reduce absorption."},
    {"topic":"Drug and Nutrient Interactions","q":"A client takes levothyroxine. Which instruction is correct?","options":["Take on an empty stomach 30 to 60 minutes before breakfast","Take with a high-fiber breakfast","Take with a calcium supplement","Take with soy milk"],"answer":"Take on an empty stomach 30 to 60 minutes before breakfast","rationale":"Food, fiber, calcium, iron, and soy reduce levothyroxine absorption, so it is taken fasting and separated from these."},
    {"topic":"Drug and Nutrient Interactions","q":"A client takes a potassium-sparing diuretic. Which teaching is most important?","options":["Avoid salt substitutes and excessive high-potassium foods","Increase banana intake daily","Use potassium chloride substitutes freely","Add potassium supplements"],"answer":"Avoid salt substitutes and excessive high-potassium foods","rationale":"Potassium-sparing agents reduce excretion, so added potassium can cause dangerous hyperkalemia."},
    {"topic":"Drug and Nutrient Interactions","q":"A client takes a loop diuretic. Which nutrient should be monitored and often replaced?","options":["Potassium","Vitamin K","Fiber","Vitamin A"],"answer":"Potassium","rationale":"Loop diuretics increase renal potassium excretion and commonly cause hypokalemia."},
    {"topic":"Drug and Nutrient Interactions","q":"A client takes long-term corticosteroids. Which nutrients should be increased?","options":["Calcium and vitamin D","Sodium and simple sugar","Vitamin K only","Iron only"],"answer":"Calcium and vitamin D","rationale":"Corticosteroids reduce calcium absorption and increase bone resorption, raising osteoporosis risk."},
    {"topic":"Drug and Nutrient Interactions","q":"A client takes metformin long term. Which nutrient deficiency should be monitored?","options":["Vitamin B12","Vitamin K","Sodium","Vitamin E"],"answer":"Vitamin B12","rationale":"Metformin impairs ileal B12 absorption, and periodic monitoring is recommended with prolonged use."},
    {"topic":"Drug and Nutrient Interactions","q":"A client takes isoniazid for tuberculosis. Which vitamin is given to prevent peripheral neuropathy?","options":["Pyridoxine, vitamin B6","Vitamin K","Vitamin C","Folate"],"answer":"Pyridoxine, vitamin B6","rationale":"Isoniazid interferes with pyridoxine metabolism, and supplementation prevents peripheral neuropathy."},
    {"topic":"Drug and Nutrient Interactions","q":"A client takes an oral bisphosphonate for osteoporosis. Which instruction is correct?","options":["Take with a full glass of plain water and remain upright for 30 minutes","Take with orange juice at bedtime","Take with a calcium supplement","Lie down after taking the dose"],"answer":"Take with a full glass of plain water and remain upright for 30 minutes","rationale":"Food and minerals block absorption, and remaining upright prevents esophageal irritation and ulceration."},
    {"topic":"Drug and Nutrient Interactions","q":"A client taking warfarin plans to start a daily herbal supplement. Which nursing action is appropriate?","options":["Instruct the client to consult the provider before starting any supplement","Approve any product labeled natural","Recommend doubling the warfarin dose","Tell the client herbs do not interact with medications"],"answer":"Instruct the client to consult the provider before starting any supplement","rationale":"Many supplements including ginkgo, garlic, ginseng, and St. John wort alter anticoagulation and require provider review."},

    # ---------------- Cultural and Religious Food Practices (8) ----------------
    {"topic":"Cultural and Religious Practices","q":"A client who practices Islam is admitted during Ramadan. Which nursing action is most appropriate?","options":["Ask the client about fasting practice and coordinate meals and medications accordingly","Insist the client eat on the standard schedule","Assume the client will not fast while hospitalized","Withhold all food and fluid"],"answer":"Ask the client about fasting practice and coordinate meals and medications accordingly","rationale":"Individual practice varies and illness may exempt a client. Assessment guides individualized planning of meals and dosing."},
    {"topic":"Cultural and Religious Practices","q":"Which food would a client following halal dietary law avoid?","options":["Pork","Chicken","Lamb","Fish"],"answer":"Pork","rationale":"Pork and its byproducts are prohibited under halal law, along with alcohol and improperly slaughtered meat."},
    {"topic":"Cultural and Religious Practices","q":"A client who practices Hinduism refuses the dinner tray. Which food is most likely the concern?","options":["Beef","Lentils","Rice","Yogurt"],"answer":"Beef","rationale":"Cattle are sacred in Hinduism and beef is avoided. Many Hindus also follow vegetarian practice."},
    {"topic":"Cultural and Religious Practices","q":"Which practice is consistent with a kosher diet?","options":["Separating meat and dairy in preparation and service","Combining cheese with beef","Eating shellfish","Using the same utensils for all foods"],"answer":"Separating meat and dairy in preparation and service","rationale":"Kosher law requires separation of meat and dairy including cookware and utensils, and prohibits pork and shellfish."},
    {"topic":"Cultural and Religious Practices","q":"A client who is a Seventh-day Adventist is likely to follow which pattern?","options":["Vegetarian eating with avoidance of alcohol and caffeine","High red meat intake","Daily alcohol with meals","No dietary preferences"],"answer":"Vegetarian eating with avoidance of alcohol and caffeine","rationale":"Many Seventh-day Adventists follow ovo-lacto vegetarian patterns and avoid alcohol, tobacco, and caffeine."},
    {"topic":"Cultural and Religious Practices","q":"Which nursing approach best supports culturally responsive nutrition teaching?","options":["Assess usual foods and adapt recommendations to preserve them","Replace all traditional foods with standard menu items","Provide a printed list without discussion","Assume preferences from the client's surname"],"answer":"Assess usual foods and adapt recommendations to preserve them","rationale":"Adapting the therapeutic plan to familiar foods improves adherence and respects the client's identity."},
    {"topic":"Cultural and Religious Practices","q":"A client uses hot and cold theory to categorize foods during illness. Which nursing action is appropriate?","options":["Incorporate the client's beliefs into the plan when they are not harmful","Correct the client's beliefs","Ignore the information","Remove all food choices"],"answer":"Incorporate the client's beliefs into the plan when they are not harmful","rationale":"Health beliefs that do not conflict with safe care should be accommodated to support trust and adherence."},
    {"topic":"Cultural and Religious Practices","q":"Which population has the highest prevalence of lactose intolerance, requiring attention to alternative calcium sources?","options":["Adults of Asian, African, and Indigenous descent","Adults of Northern European descent only","Only infants","Only older adults"],"answer":"Adults of Asian, African, and Indigenous descent","rationale":"Lactase nonpersistence is most common in these populations, so alternate calcium sources should be planned."},

    # ---------------- Weight Management and Eating Disorders (8) ----------------
    {"topic":"Weight Management and Eating Disorders","q":"A client wants to lose weight safely. Which rate should the nurse recommend?","options":["1 to 2 pounds per week","5 to 6 pounds per week","10 pounds per week","No weight loss is safe"],"answer":"1 to 2 pounds per week","rationale":"Gradual loss of 1 to 2 pounds weekly preserves lean mass and improves long-term maintenance."},
    {"topic":"Weight Management and Eating Disorders","q":"Approximately what daily energy deficit produces a loss of one pound per week?","options":["500 kcal","100 kcal","2,000 kcal","50 kcal"],"answer":"500 kcal","rationale":"One pound of fat represents roughly 3,500 kcal, so a 500 kcal daily deficit yields about one pound weekly."},
    {"topic":"Weight Management and Eating Disorders","q":"Which behavioral strategy best supports long-term weight management?","options":["Self-monitoring intake and activity with realistic goals","Eliminating entire food groups","Fasting several days weekly","Relying on a single meal daily"],"answer":"Self-monitoring intake and activity with realistic goals","rationale":"Self-monitoring is among the strongest predictors of successful long-term weight management."},
    {"topic":"Weight Management and Eating Disorders","q":"A client with anorexia nervosa is admitted with a BMI of 14. Which complication is the greatest early concern during refeeding?","options":["Hypophosphatemia and cardiac dysrhythmia","Hyperglycemia only","Weight gain that is too rapid to measure","Vitamin C toxicity"],"answer":"Hypophosphatemia and cardiac dysrhythmia","rationale":"Refeeding syndrome causes intracellular phosphorus shifts that can precipitate fatal dysrhythmias and heart failure."},
    {"topic":"Weight Management and Eating Disorders","q":"Which nursing action is appropriate during mealtimes for a client with anorexia nervosa?","options":["Provide supervision during and for a period after meals","Allow the client to eat alone in the room","Permit unrestricted bathroom access after meals","Negotiate the meal plan at the table"],"answer":"Provide supervision during and for a period after meals","rationale":"Structured supervision limits food disposal and purging and supports adherence to the prescribed plan."},
    {"topic":"Weight Management and Eating Disorders","q":"Which physical finding is associated with self-induced vomiting in bulimia nervosa?","options":["Dental enamel erosion and parotid swelling","Improved dentition","Weight gain of 20 pounds weekly","Elevated serum potassium"],"answer":"Dental enamel erosion and parotid swelling","rationale":"Repeated gastric acid exposure erodes enamel and causes parotid hypertrophy. Hypokalemia is typical, not hyperkalemia."},
    {"topic":"Weight Management and Eating Disorders","q":"A client is being evaluated for bariatric surgery. Which preoperative teaching is essential?","options":["Lifelong vitamin and mineral supplementation will be required","Supplements can stop after one year","Normal portion sizes will resume in six weeks","No follow-up will be needed"],"answer":"Lifelong vitamin and mineral supplementation will be required","rationale":"Restrictive and malabsorptive procedures permanently reduce nutrient absorption, requiring lifelong supplementation and monitoring."},
    {"topic":"Weight Management and Eating Disorders","q":"Which nutrient deficiency is most common after Roux-en-Y gastric bypass?","options":["Iron, vitamin B12, calcium, and vitamin D","Sodium and chloride","Vitamin C only","Fiber"],"answer":"Iron, vitamin B12, calcium, and vitamin D","rationale":"Bypassing the duodenum and proximal jejunum reduces absorption of iron, calcium, and fat-soluble vitamins, and reduced acid and intrinsic factor impair B12."},

    # ---------------- Fluid and Electrolytes (8) ----------------
    {"topic":"Fluid and Electrolytes","q":"Which assessment finding is the most reliable indicator of fluid volume change in a hospitalized client?","options":["Daily weight measured under consistent conditions","Skin turgor alone","Reported thirst alone","Blood pressure alone"],"answer":"Daily weight measured under consistent conditions","rationale":"A change of 1 kg reflects roughly 1 liter of fluid, making daily weight the most sensitive routine measure."},
    {"topic":"Fluid and Electrolytes","q":"A client has a serum sodium of 122 mEq/L. Which manifestation should the nurse assess for?","options":["Confusion and seizure activity","Increased thirst with dry mucous membranes only","Hypertension with bounding pulse only","Constipation only"],"answer":"Confusion and seizure activity","rationale":"Hyponatremia causes cerebral cell swelling, producing neurologic changes that can progress to seizures."},
    {"topic":"Fluid and Electrolytes","q":"Which client is at greatest risk for hypernatremia?","options":["Older adult with fever and limited access to water","Client drinking large volumes of water","Client on a low-sodium diet","Client receiving hypotonic fluids"],"answer":"Older adult with fever and limited access to water","rationale":"Insensible losses combined with impaired thirst and restricted water access concentrate serum sodium."},
    {"topic":"Fluid and Electrolytes","q":"A client taking digoxin develops hypokalemia. Why is this significant?","options":["Hypokalemia increases the risk of digoxin toxicity","Hypokalemia inactivates digoxin","Hypokalemia has no effect on digoxin","Hypokalemia increases digoxin excretion"],"answer":"Hypokalemia increases the risk of digoxin toxicity","rationale":"Low potassium enhances digoxin binding at the sodium-potassium pump, potentiating toxicity at therapeutic levels."},
    {"topic":"Fluid and Electrolytes","q":"Which food should be increased for a client with hypokalemia who can eat normally?","options":["Baked potato, banana, and orange juice","White bread and butter","Boiled egg white","Plain gelatin"],"answer":"Baked potato, banana, and orange juice","rationale":"Potatoes, bananas, citrus, tomatoes, and legumes are among the highest potassium foods."},
    {"topic":"Fluid and Electrolytes","q":"Which manifestation should the nurse assess for in a client with hypercalcemia?","options":["Lethargy, constipation, and muscle weakness","Tetany and positive Chvostek sign","Hyperactive reflexes","Seizure with muscle spasm"],"answer":"Lethargy, constipation, and muscle weakness","rationale":"Excess calcium depresses neuromuscular excitability. Tetany and Chvostek sign indicate hypocalcemia instead."},
    {"topic":"Fluid and Electrolytes","q":"A client is prescribed a 1,500 mL daily fluid restriction. Which nursing action best supports adherence?","options":["Distribute the allowance across the day and count all liquid foods","Give the full amount at breakfast","Exclude gelatin and ice cream from the count","Allow unlimited ice chips"],"answer":"Distribute the allowance across the day and count all liquid foods","rationale":"Foods liquid at room temperature count toward the restriction, and even distribution prevents concentrated thirst."},
    {"topic":"Fluid and Electrolytes","q":"An athlete exercising vigorously for more than one hour in heat should be advised to consume which beverage?","options":["A carbohydrate-electrolyte sports beverage","Plain water only in unlimited amounts","A caffeinated energy drink","A carbonated soft drink"],"answer":"A carbohydrate-electrolyte sports beverage","rationale":"Prolonged sweating loses sodium as well as water. Replacing water alone increases the risk of exercise-associated hyponatremia."},
]

# Verify the bank loaded and every item is well formed.
# The count is intentionally dynamic so new questions can be added without editing this block.
assert len(QUESTIONS) > 0, "Question bank is empty."
for _q in QUESTIONS:
    assert _q["answer"] in _q["options"], f"Answer not in options: {_q['q'][:60]}"

TOTAL_QUESTIONS = len(QUESTIONS)

PHOTO_URLS = {
    "produce": "https://images.unsplash.com/photo-1610348725531-843dff563e2c?auto=format&fit=crop&w=1200&q=80",
    "grains": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=1200&q=80",
    "meal": "https://images.unsplash.com/photo-1543353071-873f17a7a088?auto=format&fit=crop&w=1200&q=80",
}

def plate_svg():
    return f"""
    <svg viewBox="0 0 600 360" width="100%" role="img" aria-label="Balanced plate diagram">
      <rect width="600" height="360" rx="24" fill="#ffffff"/>
      <circle cx="230" cy="180" r="135" fill="#fafafa" stroke="{FSC_DARK}" stroke-width="8"/>
      <path d="M230 45 A135 135 0 0 0 95 180 L230 180 Z" fill="#dfead8" stroke="white" stroke-width="4"/>
      <path d="M95 180 A135 135 0 0 0 230 315 L230 180 Z" fill="#f2d6c5" stroke="white" stroke-width="4"/>
      <path d="M230 45 A135 135 0 0 1 365 180 L230 180 Z" fill="#f2e4b7" stroke="white" stroke-width="4"/>
      <path d="M365 180 A135 135 0 0 1 230 315 L230 180 Z" fill="#d8e4ef" stroke="white" stroke-width="4"/>
      <text x="145" y="125" font-size="23" fill="#243124">Vegetables</text>
      <text x="145" y="240" font-size="23" fill="#4d2d22">Fruit</text>
      <text x="270" y="125" font-size="23" fill="#554915">Grains</text>
      <text x="265" y="240" font-size="23" fill="#243b52">Protein</text>
      <circle cx="455" cy="115" r="62" fill="#eef3f8" stroke="{FSC_DARK}" stroke-width="6"/>
      <text x="420" y="122" font-size="22" fill="#243b52">Dairy</text>
      <rect x="400" y="220" width="110" height="65" rx="15" fill="#e3f0fa" stroke="{FSC_DARK}" stroke-width="5"/>
      <text x="420" y="260" font-size="22" fill="#243b52">Water</text>
    </svg>
    """

def show_macro_chart():
    """Energy density bar chart drawn as inline SVG so the app needs no plotting library."""
    bars = [
        ("Carbohydrate", 4, "#f2e4b7"),
        ("Protein", 4, "#d8e4ef"),
        ("Fat", 9, "#f2d6c5"),
    ]
    chart_height = 210
    baseline = 250
    max_value = 10

    rects = []
    for index, (label, value, fill) in enumerate(bars):
        x = 70 + index * 130
        height = value / max_value * chart_height
        y = baseline - height
        rects.append(
            f'<rect x="{x}" y="{y:.0f}" width="80" height="{height:.0f}" rx="6" '
            f'fill="{fill}" stroke="{FSC_DARK}" stroke-width="2"/>'
            f'<text x="{x + 40}" y="{y - 10:.0f}" font-size="19" font-weight="600" '
            f'text-anchor="middle" fill="{FSC_DARK}">{value}</text>'
            f'<text x="{x + 40}" y="{baseline + 25}" font-size="15" '
            f'text-anchor="middle" fill="{FSC_TEXT}">{label}</text>'
        )

    gridlines = []
    for tick in range(0, max_value + 1, 2):
        y = baseline - (tick / max_value * chart_height)
        gridlines.append(
            f'<line x1="60" y1="{y:.0f}" x2="470" y2="{y:.0f}" stroke="#e8e0e2" stroke-width="1"/>'
            f'<text x="52" y="{y + 5:.0f}" font-size="13" text-anchor="end" fill="#7a7a7a">{tick}</text>'
        )

    st.markdown(
        f"""
        <svg viewBox="0 0 500 300" width="100%" role="img"
             aria-label="Bar chart of kilocalories per gram for carbohydrate, protein, and fat">
          <rect width="500" height="300" rx="14" fill="#ffffff"/>
          <text x="250" y="28" font-size="17" font-weight="600" text-anchor="middle"
                fill="{FSC_DARK}">Energy Density of Macronutrients</text>
          {''.join(gridlines)}
          <line x1="60" y1="{baseline}" x2="470" y2="{baseline}" stroke="{FSC_DARK}" stroke-width="2"/>
          {''.join(rects)}
          <text x="18" y="150" font-size="13" fill="#7a7a7a"
                transform="rotate(-90 18 150)" text-anchor="middle">Kilocalories per gram</text>
        </svg>
        """,
        unsafe_allow_html=True,
    )

def immediate_question(question, key_prefix):
    st.write(question["q"])
    choice = st.radio(
        "Select one answer:",
        question["options"],
        key=f"{key_prefix}_choice",
        index=None,
    )
    if st.button("Check answer", key=f"{key_prefix}_check"):
        if choice is None:
            st.warning("Select an answer first.")
        elif choice == question["answer"]:
            st.success("Correct.")
            st.info(question["rationale"])
        else:
            st.error(f"Incorrect. Correct answer: {question['answer']}")
            st.info(question["rationale"])

def reset_full_quiz():
    for key in list(st.session_state.keys()):
        if key.startswith("fullquiz_"):
            del st.session_state[key]


MIME_TYPES = {
    "pdf": "application/pdf",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "ppt": "application/vnd.ms-powerpoint",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "doc": "application/msword",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xls": "application/vnd.ms-excel",
    "csv": "text/csv",
    "txt": "text/plain",
    "md": "text/markdown",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
}


def render_file(data, name):
    """Preview a file when the browser can display it, and always offer a download."""
    extension = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    mime = MIME_TYPES.get(extension, "application/octet-stream")

    if extension == "pdf":
        encoded = base64.b64encode(data).decode("utf-8")
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{encoded}" '
            f'width="100%" height="700" style="border:1px solid #eadde0;border-radius:10px;"></iframe>',
            unsafe_allow_html=True,
        )
        st.caption("If the preview does not load, use the download button below.")

    elif extension in ("png", "jpg", "jpeg", "gif"):
        st.image(data, width="stretch")

    elif extension == "csv":
        try:
            import pandas as pd

            frame = pd.read_csv(io.BytesIO(data))
            st.dataframe(frame, width="stretch")
            st.caption(f"{len(frame)} rows, {len(frame.columns)} columns.")
        except ImportError:
            # pandas is optional. Fall back to the standard library reader.
            import csv

            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = data.decode("latin-1")
            rows = list(csv.reader(io.StringIO(text)))
            if rows:
                st.table(rows[:200])
                st.caption(f"{len(rows) - 1} data rows shown as plain text.")
            else:
                st.info("This file is empty.")
        except Exception:
            st.info("This file could not be read as a table. Download it to open in a spreadsheet program.")

    elif extension in ("txt", "md"):
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("latin-1")
        if extension == "md":
            st.markdown(text)
        else:
            st.text(text)

    elif extension in ("pptx", "ppt", "docx", "doc", "xlsx", "xls"):
        labels = {
            "pptx": "PowerPoint", "ppt": "PowerPoint",
            "docx": "Word", "doc": "Word",
            "xlsx": "Excel", "xls": "Excel",
        }
        st.info(
            f"{labels[extension]} files cannot display inside a browser. Download the file to open it. "
            "To make slides readable without downloading, export the deck to PDF and post the PDF instead."
        )

    else:
        st.info("No preview is available for this file type. Use the download button below.")

    st.download_button(
        label=f"Download {name}",
        data=data,
        file_name=name,
        mime=mime,
        key=f"dl_{name}_{len(data)}",
    )

# ----------------------------
# Sidebar navigation
# ----------------------------

st.sidebar.markdown("## NUR3302")
st.sidebar.caption("Nutrition Student Hub")
page = st.sidebar.radio(
    "Navigate",
    [
        "Home",
        "Macronutrients",
        "Micronutrients",
        "Special Diets",
        "Clinical Cases",
        "NCLEX Review",
        "Calculators",
        "Course Files",
        "Study Resources",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Question bank: {TOTAL_QUESTIONS} items")

st.sidebar.markdown("---")
st.sidebar.caption("Anonymous learning tool. Responses remain in the current browser session and are not saved.")

# ----------------------------
# Pages
# ----------------------------

if page == "Home":
    st.markdown(
        """
        <div class="hero">
          <h1>NUR3302 Nutrition Student Hub</h1>
          <p><strong>Florida Southern College</strong></p>
          <p>Build nutrition knowledge, connect nutrients to patient care, and practice nursing decisions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="topic-card"><h3>Learn</h3><p>Review macronutrients, micronutrients, special diets, and nutrition support.</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="topic-card"><h3>Practice</h3><p>Work through matching activities, calculators, and unfolding clinical cases.</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="topic-card"><h3>Prepare</h3><p>Practice by topic or build a mixed NCLEX-style exam from {TOTAL_QUESTIONS} questions.</p></div>', unsafe_allow_html=True)

    st.subheader("Build a balanced plate")
    st.markdown(plate_svg(), unsafe_allow_html=True)
    st.caption("Use this visual as a general meal-planning framework. Individual clinical diets may differ.")

    st.subheader("Food gallery")
    p1, p2, p3 = st.columns(3)
    p1.image(PHOTO_URLS["produce"], caption="Colorful produce", width="stretch")
    p2.image(PHOTO_URLS["grains"], caption="Whole grains", width="stretch")
    p3.image(PHOTO_URLS["meal"], caption="Balanced meal preparation", width="stretch")

    st.markdown(
        '<div class="warning"><strong>Educational use only:</strong> This app supports course learning. It does not replace clinical judgment, current evidence, facility policy, provider orders, or individualized consultation with a registered dietitian nutritionist.</div>',
        unsafe_allow_html=True,
    )

elif page == "Macronutrients":
    st.header("Macronutrients")
    tabs = st.tabs(list(MACROS.keys()))
    for tab, (name, item) in zip(tabs, MACROS.items()):
        with tab:
            left, right = st.columns([2, 1])
            with left:
                st.subheader(f"{item['icon']} {name}")
                st.markdown(f"**Main functions:** {item['functions']}")
                st.markdown(f"**Food sources:** {item['sources']}")
                st.markdown(f"**Nursing connection:** {item['nursing']}")
                st.markdown(f'<div class="pearl"><strong>Energy:</strong> {item["energy"]}</div>', unsafe_allow_html=True)
            with right:
                if name in ["Carbohydrates", "Protein", "Fat"]:
                    show_macro_chart()
                else:
                    st.markdown(plate_svg(), unsafe_allow_html=True)

    st.subheader("Quick knowledge check")
    macro_q = [q for q in QUESTIONS if q["topic"] == "Macronutrients"]
    selected = st.selectbox("Choose a question", range(len(macro_q)), format_func=lambda i: f"Question {i+1}")
    immediate_question(macro_q[selected], f"macro_{selected}")

elif page == "Micronutrients":
    st.header("Micronutrients")
    st.write("Select a nutrient to review its function, sources, and nursing priority.")

    nutrient = st.selectbox("Nutrient", list(MICROS.keys()))
    function, sources, nursing = MICROS[nutrient]
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="topic-card"><h3>Function</h3><p>{function}</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="topic-card"><h3>Sources</h3><p>{sources}</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="topic-card"><h3>Nursing priority</h3><p>{nursing}</p></div>', unsafe_allow_html=True)

    st.subheader("Flashcard mode")
    flash_name = st.selectbox("Choose a flashcard", list(MICROS.keys()), key="flash_name")
    if st.button("Reveal answer"):
        f, s, n = MICROS[flash_name]
        st.success(f"{flash_name}: {f}")
        st.write(f"Sources: {s}")
        st.write(f"Nursing priority: {n}")

    st.subheader("Micronutrient matching")
    match_items = {
        "Vitamin C": "Improves nonheme iron absorption",
        "Vitamin K": "Supports clotting proteins",
        "Vitamin D": "Supports calcium absorption",
        "Thiamine (B1)": "High-priority deficiency risk with chronic alcohol misuse",
        "Vitamin B12": "Deficiency can cause neurologic changes",
    }
    answers = []
    options = list(match_items.values())
    for nutrient_name, correct in match_items.items():
        answers.append(
            st.selectbox(
                nutrient_name,
                ["Choose..."] + options,
                key=f"match_{nutrient_name}",
            ) == correct
        )
    if st.button("Check matching activity"):
        score = sum(answers)
        st.write(f"Score: {score}/{len(match_items)}")
        if score == len(match_items):
            st.success("All matches are correct.")
        else:
            st.info("Review the micronutrient cards and try again.")

elif page == "Special Diets":
    st.header("Special Diets")
    selected_diet = st.selectbox("Choose a diet or nutrition-support plan", list(SPECIAL_DIETS.keys()))
    diet = SPECIAL_DIETS[selected_diet]

    a, b = st.columns(2)
    a.markdown(f'<div class="topic-card"><h3>Primary focus</h3><p>{diet["focus"]}</p></div>', unsafe_allow_html=True)
    b.markdown(f'<div class="topic-card"><h3>Important caution</h3><p>{diet["limit"]}</p></div>', unsafe_allow_html=True)

    st.subheader("Clinical decision")
    st.write(diet["case"])
    answer = st.radio("Choose the best response:", diet["options"], key=f"diet_{selected_diet}", index=None)
    if st.button("Check clinical decision"):
        if answer == diet["best"]:
            st.success("Correct.")
        elif answer is None:
            st.warning("Select an answer first.")
        else:
            st.error(f"Best answer: {diet['best']}")
        st.info(f"Key point: {diet['focus']}")

elif page == "Clinical Cases":
    st.header("Clinical Cases")

    cases = [
        {
            "title": "Pressure Injury and Poor Intake",
            "stem": "An older adult has a stage 3 pressure injury and eats about 25% of meals.",
            "question": "Which action is the priority?",
            "options": ["Request nutrition assessment and evaluate barriers to intake", "Restrict protein", "Wait one week", "Offer only clear liquids"],
            "answer": "Request nutrition assessment and evaluate barriers to intake",
            "feedback": "The patient has wound-healing demands and inadequate intake. Prompt interdisciplinary assessment is appropriate.",
        },
        {
            "title": "Heart Failure and Sodium",
            "stem": "A patient with heart failure reports eating canned soup and deli meat most days.",
            "question": "Which teaching is most relevant?",
            "options": ["Compare sodium labels and choose lower-sodium alternatives", "Avoid all carbohydrate", "Increase processed meat", "Use unlimited salt substitutes"],
            "answer": "Compare sodium labels and choose lower-sodium alternatives",
            "feedback": "Processed foods are major sodium sources. Salt substitutes require caution when potassium is a concern.",
        },
        {
            "title": "Dysphagia Safety",
            "stem": "A patient coughs during meals and has a wet voice after drinking water.",
            "question": "What should the nurse do first?",
            "options": ["Stop oral intake and follow swallowing-safety procedures", "Offer a straw", "Place the patient flat", "Encourage rapid drinking"],
            "answer": "Stop oral intake and follow swallowing-safety procedures",
            "feedback": "Coughing and a wet voice suggest aspiration risk and require immediate swallowing-safety action.",
        },
        {
            "title": "Refeeding Risk",
            "stem": "A severely malnourished patient begins aggressive nutrition support.",
            "question": "Which laboratory value is a priority?",
            "options": ["Phosphorus", "Hemoglobin A1c only", "LDL only", "Bilirubin only"],
            "answer": "Phosphorus",
            "feedback": "Rapid feeding can cause profound intracellular shifts, especially hypophosphatemia.",
        },
    ]

    case_index = st.selectbox("Choose a case", range(len(cases)), format_func=lambda i: cases[i]["title"])
    case = cases[case_index]
    st.markdown(f"### {case['title']}")
    st.write(case["stem"])
    response = st.radio(case["question"], case["options"], key=f"case_{case_index}", index=None)
    rationale = st.text_area("Explain your reasoning before checking the answer.", key=f"case_reason_{case_index}")
    if st.button("Review case"):
        if response == case["answer"]:
            st.success("Correct.")
        elif response is None:
            st.warning("Select an answer.")
        else:
            st.error(f"Best answer: {case['answer']}")
        st.info(case["feedback"])
        if rationale.strip():
            st.caption("Your reasoning remains in this browser session only.")

elif page == "NCLEX Review":
    st.header("NCLEX-Style Review")
    st.caption(f"Question bank: {TOTAL_QUESTIONS} items across {len(set(q['topic'] for q in QUESTIONS))} topics.")

    mode = st.radio(
        "Choose a mode",
        ["Topic practice with immediate feedback", "Mixed practice exam"],
    )

    if mode == "Topic practice with immediate feedback":
        topics = sorted(set(q["topic"] for q in QUESTIONS))
        topic = st.selectbox("Topic", topics)
        pool = [q for q in QUESTIONS if q["topic"] == topic]
        st.caption(f"{len(pool)} questions in this topic.")
        number = st.selectbox(
            "Question",
            range(len(pool)),
            format_func=lambda i: f"{i + 1} of {len(pool)}",
        )
        immediate_question(pool[number], f"topic_{topic}_{number}")

    else:
        st.info(
            "Answers remain only in the current browser session. The app does not save names or scores."
        )

        setup1, setup2 = st.columns(2)
        with setup1:
            length_choice = st.selectbox(
                "Exam length",
                [10, 25, 50, 75, 100, TOTAL_QUESTIONS],
                index=2,
                format_func=lambda n: (
                    f"All {TOTAL_QUESTIONS} questions" if n == TOTAL_QUESTIONS else f"{n} questions"
                ),
            )
        with setup2:
            all_topics = sorted(set(q["topic"] for q in QUESTIONS))
            chosen_topics = st.multiselect(
                "Limit to topics (leave empty for all)",
                all_topics,
                default=[],
            )

        eligible = [
            i for i, q in enumerate(QUESTIONS)
            if not chosen_topics or q["topic"] in chosen_topics
        ]
        exam_length = min(length_choice, len(eligible))

        signature = (exam_length, tuple(sorted(chosen_topics)))
        if st.session_state.get("fullquiz_signature") != signature:
            reset_full_quiz()
            st.session_state.fullquiz_signature = signature
            st.session_state.fullquiz_order = random.sample(eligible, exam_length)

        if "fullquiz_order" not in st.session_state:
            st.session_state.fullquiz_order = random.sample(eligible, exam_length)

        order = st.session_state.fullquiz_order
        st.subheader(f"{len(order)}-question exam")

        for display_num, q_index in enumerate(order, start=1):
            q = QUESTIONS[q_index]
            st.markdown(f"**{display_num}. {q['q']}**")
            st.caption(q["topic"])
            st.radio(
                "Answer",
                q["options"],
                key=f"fullquiz_answer_{q_index}",
                index=None,
                label_visibility="collapsed",
            )
            st.markdown("---")

        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"Submit {len(order)}-question exam"):
                score = 0
                unanswered = 0
                missed_topics = {}
                for q_index in order:
                    selected_answer = st.session_state.get(f"fullquiz_answer_{q_index}")
                    if selected_answer is None:
                        unanswered += 1
                    elif selected_answer == QUESTIONS[q_index]["answer"]:
                        score += 1
                    else:
                        topic_name = QUESTIONS[q_index]["topic"]
                        missed_topics[topic_name] = missed_topics.get(topic_name, 0) + 1
                percent = score / len(order) * 100 if order else 0
                st.session_state.fullquiz_result = (score, percent, unanswered, missed_topics)
        with c2:
            if st.button("Reset and reshuffle exam"):
                reset_full_quiz()
                st.rerun()

        if "fullquiz_result" in st.session_state:
            score, percent, unanswered, missed_topics = st.session_state.fullquiz_result
            st.subheader(f"Score: {score}/{len(order)} ({percent:.0f}%)")
            if unanswered:
                st.warning(f"Unanswered questions: {unanswered}")

            if missed_topics:
                st.markdown("**Topics to review, ranked by number missed**")
                for topic_name, count in sorted(missed_topics.items(), key=lambda x: -x[1]):
                    st.write(f"{topic_name}: {count} missed")

            with st.expander("Review answers and rationales"):
                for display_num, q_index in enumerate(order, start=1):
                    q = QUESTIONS[q_index]
                    selected_answer = st.session_state.get(f"fullquiz_answer_{q_index}")
                    status = "Correct" if selected_answer == q["answer"] else "Review"
                    st.markdown(f"**{display_num}. {status}**  \n{q['q']}")
                    st.write(f"Your answer: {selected_answer or 'No answer'}")
                    st.write(f"Correct answer: {q['answer']}")
                    st.caption(q["rationale"])
                    st.markdown("---")

elif page == "Calculators":
    st.header("Nutrition Calculators")
    st.write(
        "Each calculator below includes what the value measures, how to enter the numbers, "
        "how to interpret the result, and how nurses use that number in patient care. "
        "Read the instructions before you use the tool."
    )
    st.markdown(
        '<div class="warning"><strong>Classroom use:</strong> These calculators teach the reasoning behind common '
        'nutrition estimates. They do not replace provider orders, facility protocols, or an individualized '
        'assessment by a registered dietitian nutritionist.</div>',
        unsafe_allow_html=True,
    )

    calc1, calc2, calc3, calc4 = st.tabs(
        ["BMI", "Energy from Macros", "Protein Estimate", "Fluid Estimate"]
    )

    # ---------------------------------------------------------------- BMI
    with calc1:
        st.subheader("Body Mass Index")

        with st.expander("Instructions and clinical use", expanded=True):
            st.markdown(
                """
**What it measures**

BMI compares weight to height. It produces a single number that screens for underweight,
healthy weight, overweight, and obesity in adults.

**How to use this calculator**

1. Choose US or Metric units.
2. Enter the patient's current weight. Use a measured weight, not a reported one.
3. Enter height without shoes.
4. Read the BMI value and the category shown below it.

**How to interpret the result**

| BMI | Category |
| --- | --- |
| Below 18.5 | Underweight |
| 18.5 to 24.9 | Healthy weight |
| 25.0 to 29.9 | Overweight |
| 30.0 to 34.9 | Obesity class I |
| 35.0 to 39.9 | Obesity class II |
| 40.0 and above | Obesity class III |

**How nurses use this value in patient care**

- Screen for nutrition risk on admission and trigger a dietitian referral when BMI is low or dropping.
- Identify cardiometabolic risk. A rising BMI raises the risk of type 2 diabetes, hypertension,
  dyslipidemia, obstructive sleep apnea, and osteoarthritis.
- Support pressure injury risk assessment. Low BMI reduces tissue padding and raises risk.
- Guide surgical and anesthesia planning, wound healing expectations, and mobility planning.
- Track response over time. The trend matters more than any single reading.

**Know the limits**

BMI does not measure body composition. It overestimates fat in a muscular athlete and
underestimates it in an older adult who has lost muscle. Edema, ascites, amputation, pregnancy,
and large tumors all distort the number. Pair BMI with waist circumference, physical assessment,
and weight history before you draw a conclusion. For children and teens, use age- and
sex-specific BMI percentiles instead of these adult categories.
                """
            )

        units = st.radio("Units", ["US", "Metric"], horizontal=True)
        if units == "US":
            weight_lb = st.number_input("Weight (lb)", min_value=1.0, value=150.0)
            height_in = st.number_input("Height (inches)", min_value=1.0, value=65.0)
            bmi = 703 * weight_lb / (height_in ** 2)
        else:
            weight_kg = st.number_input("Weight (kg)", min_value=1.0, value=68.0)
            height_cm = st.number_input("Height (cm)", min_value=1.0, value=165.0)
            bmi = weight_kg / ((height_cm / 100) ** 2)

        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Healthy weight"
        elif bmi < 30:
            category = "Overweight"
        elif bmi < 35:
            category = "Obesity class I"
        elif bmi < 40:
            category = "Obesity class II"
        else:
            category = "Obesity class III"

        m1, m2 = st.columns(2)
        m1.metric("BMI", f"{bmi:.1f}")
        m2.metric("Category", category)

        st.subheader("Waist circumference")
        st.write(
            "Waist circumference adds information BMI cannot provide. It estimates central adiposity, "
            "which drives cardiometabolic risk independently of BMI."
        )
        wc_sex = st.radio("Sex assigned at birth for risk threshold", ["Female", "Male"], horizontal=True)
        wc = st.number_input("Waist circumference (inches)", min_value=10.0, value=34.0)
        threshold = 35.0 if wc_sex == "Female" else 40.0
        if wc > threshold:
            st.warning(
                f"Above the {threshold:.0f} inch threshold. This indicates increased cardiometabolic risk "
                "and supports closer screening for glucose, lipids, and blood pressure."
            )
        else:
            st.success(f"At or below the {threshold:.0f} inch threshold.")
        st.caption(
            "Measure at the top of the iliac crest, at the end of a normal exhalation, with the tape "
            "snug but not compressing the skin."
        )

    # -------------------------------------------------- Energy from macros
    with calc2:
        st.subheader("Energy from Macronutrients")

        with st.expander("Instructions and clinical use", expanded=True):
            st.markdown(
                """
**What it measures**

This tool converts grams of carbohydrate, protein, and fat into kilocalories and shows what
percentage of total energy each macronutrient supplies.

**The conversion factors**

- Carbohydrate: 4 kcal per gram
- Protein: 4 kcal per gram
- Fat: 9 kcal per gram
- Alcohol: 7 kcal per gram

**How to use this calculator**

1. Read the grams of each macronutrient from a Nutrition Facts label, a diet recall, or a tube
   feeding formula sheet.
2. Multiply label values by the number of servings actually consumed before you enter them.
3. Enter the grams and read the total energy and the percentage breakdown.

**How to interpret the result**

Compare the percentages to the Acceptable Macronutrient Distribution Ranges for adults:

| Macronutrient | Percent of total energy |
| --- | --- |
| Carbohydrate | 45 to 65 percent |
| Protein | 10 to 35 percent |
| Fat | 20 to 35 percent |

**How nurses use this value in patient care**

- Verify that a tube feeding or oral supplement meets the prescribed energy goal.
- Complete a calorie count and compare actual intake against estimated needs.
- Teach carbohydrate counting to a patient with diabetes by connecting label grams to servings.
- Explain why a high-fat food is calorie dense during weight management teaching.
- Identify a diet that is disproportionately high in fat or low in carbohydrate before symptoms appear.
                """
            )

        carb_g = st.number_input("Carbohydrate grams", min_value=0.0, value=200.0)
        protein_g = st.number_input("Protein grams", min_value=0.0, value=70.0)
        fat_g = st.number_input("Fat grams", min_value=0.0, value=60.0)
        alcohol_g = st.number_input("Alcohol grams (optional)", min_value=0.0, value=0.0)

        carb_kcal = carb_g * 4
        protein_kcal = protein_g * 4
        fat_kcal = fat_g * 9
        alcohol_kcal = alcohol_g * 7
        kcal = carb_kcal + protein_kcal + fat_kcal + alcohol_kcal

        st.metric("Estimated energy", f"{kcal:,.0f} kcal")

        if kcal > 0:
            e1, e2, e3 = st.columns(3)
            e1.metric("Carbohydrate", f"{carb_kcal:,.0f} kcal", f"{carb_kcal / kcal * 100:.0f}%")
            e2.metric("Protein", f"{protein_kcal:,.0f} kcal", f"{protein_kcal / kcal * 100:.0f}%")
            e3.metric("Fat", f"{fat_kcal:,.0f} kcal", f"{fat_kcal / kcal * 100:.0f}%")
            if alcohol_kcal:
                st.write(f"Alcohol: {alcohol_kcal:,.0f} kcal ({alcohol_kcal / kcal * 100:.0f}%)")

            notes = []
            carb_pct = carb_kcal / kcal * 100
            protein_pct = protein_kcal / kcal * 100
            fat_pct = fat_kcal / kcal * 100
            if not 45 <= carb_pct <= 65:
                notes.append(f"Carbohydrate at {carb_pct:.0f}% falls outside the 45 to 65 percent range.")
            if not 10 <= protein_pct <= 35:
                notes.append(f"Protein at {protein_pct:.0f}% falls outside the 10 to 35 percent range.")
            if not 20 <= fat_pct <= 35:
                notes.append(f"Fat at {fat_pct:.0f}% falls outside the 20 to 35 percent range.")
            if notes:
                for note in notes:
                    st.info(note)
            else:
                st.success("All three macronutrients fall within the acceptable distribution ranges.")

    # ------------------------------------------------------- Protein needs
    with calc3:
        st.subheader("Protein Estimate")

        with st.expander("Instructions and clinical use", expanded=True):
            st.markdown(
                """
**What it measures**

This tool estimates a daily protein target by multiplying body weight in kilograms by a
grams-per-kilogram factor that reflects the patient's clinical condition.

**How to use this calculator**

1. Convert weight to kilograms. Divide pounds by 2.2.
2. Select the factor that matches the clinical situation using the reference below.
3. Read the estimated grams per day and compare it to what the patient actually eats.

**Classroom reference factors**

| Situation | Approximate g/kg/day |
| --- | --- |
| Healthy adult, RDA | 0.8 |
| Older adult, preserving muscle | 1.0 to 1.2 |
| Acute illness or mild stress | 1.2 to 1.5 |
| Pressure injury or wound healing | 1.2 to 1.5 |
| Major surgery, trauma, or sepsis | 1.5 to 2.0 |
| Hemodialysis | 1.2 or higher |
| Chronic kidney disease before dialysis | Reduced, often 0.6 to 0.8 |
| Hepatic encephalopathy | Individualized, do not restrict routinely |

**How nurses use this value in patient care**

- Judge whether a patient with a stage 3 pressure injury is eating enough to heal.
- Recognize when intake is far below need and escalate for a dietitian consult.
- Teach a postoperative patient why protein foods come first on the tray.
- Understand why the target rises after dialysis starts and falls in earlier kidney disease.
- Anticipate that protein needs increase during pregnancy, lactation, burns, and catabolic illness.

**Know the limits**

Use actual body weight for most patients. In obesity, clinicians often use an adjusted weight, and
in significant edema or ascites they use a dry weight. Kidney and liver disease change the target in
opposite directions. Confirm the individualized goal with the dietitian and the provider before you
teach it to a patient.
                """
            )

        weight_kg = st.number_input("Weight (kg)", min_value=1.0, value=70.0, key="protein_weight")
        st.caption(f"Equivalent to {weight_kg * 2.2:.0f} lb")
        factor = st.slider("Classroom factor (g/kg/day)", 0.6, 2.0, 0.8, 0.1)
        estimate = weight_kg * factor
        p1, p2 = st.columns(2)
        p1.metric("Estimated protein", f"{estimate:.0f} g/day")
        p2.metric("Energy from that protein", f"{estimate * 4:,.0f} kcal")
        st.caption(
            "For reference, 3 ounces of cooked chicken supplies about 26 g, one large egg about 6 g, "
            "one cup of milk about 8 g, and one-half cup of cooked lentils about 9 g."
        )
        st.warning(
            "This is a classroom estimate. Actual needs vary with age, pregnancy, wounds, critical "
            "illness, kidney or liver disease, dialysis, and the care plan."
        )

    # --------------------------------------------------------- Fluid needs
    with calc4:
        st.subheader("Fluid Estimate")

        with st.expander("Instructions and clinical use", expanded=True):
            st.markdown(
                """
**What it measures**

This tool estimates baseline daily fluid needs for a patient without abnormal losses or
prescribed restrictions. It uses milliliters per kilogram of body weight.

**How to use this calculator**

1. Convert weight to kilograms.
2. Select the factor that matches the patient's age and condition.
3. Read the estimate, then adjust upward for fever, drainage, or other losses.

**Classroom reference factors**

| Situation | Approximate mL/kg/day |
| --- | --- |
| Young adult, ages 18 to 55 | 30 to 35 |
| Adult, ages 56 to 75 | 30 |
| Older adult, over 75 | 25 |
| Fever | Add roughly 12 percent for each degree Celsius above normal |
| Heart failure, kidney failure, SIADH | Restricted, follow the prescribed limit |

**How nurses use this value in patient care**

- Set a realistic hydration goal for a patient at risk for dehydration or constipation.
- Interpret intake and output records. Compare what went in against the estimated need.
- Recognize dehydration early in older adults, where confusion is often the first sign.
- Support kidney stone prevention, where high fluid intake is the single most effective measure.
- Reconcile the estimate against a prescribed restriction and teach the patient how to spread the
  allowance across the day.

**What counts as fluid**

Water, milk, juice, coffee, tea, broth, and any food that is liquid at room temperature. Gelatin,
ice cream, sherbet, popsicles, and ice chips all count. Ice chips count as roughly half their
volume in water.

**Know the limits**

Never apply a generic estimate to a patient with heart failure, kidney failure, liver failure with
ascites, SIADH, or a prescribed restriction. In those conditions the order overrides the formula.
The best single indicator that the fluid plan is working is a daily weight measured at the same
time, on the same scale, in the same clothing.
                """
            )

        weight_kg = st.number_input("Weight (kg)", min_value=1.0, value=70.0, key="fluid_weight")
        st.caption(f"Equivalent to {weight_kg * 2.2:.0f} lb")
        factor = st.slider("Classroom factor (mL/kg/day)", 20, 40, 30)
        estimate = weight_kg * factor
        f1, f2 = st.columns(2)
        f1.metric("Estimated fluid", f"{estimate:,.0f} mL/day")
        f2.metric("Equivalent", f"{estimate / 240:.1f} cups")
        st.caption("One cup equals about 240 mL. One liter equals about 4.2 cups.")
        st.warning(
            "Do not use a generic fluid estimate for patients with heart failure, kidney failure, "
            "major fluid losses, critical illness, or prescribed restrictions."
        )

elif page == "Course Files":
    st.header("Course Files")
    st.write(
        "Upload PowerPoints, handouts, PDFs, worksheets, and images. "
        "Preview them here or download them for offline study."
    )

    st.markdown(
        '<div class="warning"><strong>Read this first:</strong> Files you upload below stay in your own '
        'browser session only. They disappear when you close the tab or the app restarts, and other users '
        'cannot see them. To post files that every student can open, add them to the '
        '<code>course_files</code> folder of the GitHub repository. Instructions are at the bottom of this page.'
        '</div>',
        unsafe_allow_html=True,
    )

    tab_posted, tab_upload, tab_howto = st.tabs(
        ["Posted course files", "Upload files (this session)", "How to post files for students"]
    )

    # ------------------------------------------------ Files committed to repo
    with tab_posted:
        st.subheader("Files posted by the instructor")
        course_dir = Path(__file__).parent / "course_files"

        if not course_dir.exists():
            st.info(
                "No course_files folder exists yet. Create one in the repository and add files to it. "
                "See the How to post files tab."
            )
        else:
            posted = sorted(
                [p for p in course_dir.iterdir() if p.is_file() and not p.name.startswith(".")],
                key=lambda p: p.name.lower(),
            )
            if not posted:
                st.info("The course_files folder exists but is empty.")
            else:
                st.caption(f"{len(posted)} file(s) available.")
                for path in posted:
                    size_kb = path.stat().st_size / 1024
                    with st.expander(f"{path.name}  ({size_kb:,.0f} KB)"):
                        render_file(path.read_bytes(), path.name)

    # -------------------------------------------------------- Session uploads
    with tab_upload:
        st.subheader("Upload files")
        uploaded = st.file_uploader(
            "Choose one or more files",
            type=[
                "pptx", "ppt", "pdf", "docx", "doc", "xlsx", "xls",
                "csv", "txt", "md", "png", "jpg", "jpeg", "gif",
            ],
            accept_multiple_files=True,
            help="PowerPoint, Word, Excel, PDF, images, and plain text are supported.",
        )

        if not uploaded:
            st.info("No files uploaded yet. Use the box above to add them.")
        else:
            st.success(f"{len(uploaded)} file(s) loaded into this session.")
            for file in uploaded:
                data = file.getvalue()
                size_kb = len(data) / 1024
                with st.expander(f"{file.name}  ({size_kb:,.0f} KB)", expanded=len(uploaded) == 1):
                    render_file(data, file.name)

    # ------------------------------------------------------------ Instructions
    with tab_howto:
        st.subheader("Posting files so every student can see them")
        st.markdown(
            """
Streamlit Community Cloud rebuilds this app from GitHub each time it starts, and it does not keep
anything written to disk while the app runs. That is why session uploads vanish. Files stored in
the repository itself are rebuilt with the app every time, so they persist.

**Steps**

1. Open the repository on GitHub.
2. Click **Add file**, then **Create new file**.
3. Type `course_files/README.md` in the filename box. Typing the slash creates the folder.
4. Put any text in the file, such as `Course files folder`, and commit it.
5. Open the new `course_files` folder, click **Add file**, then **Upload files**.
6. Drag your PowerPoints, PDFs, and handouts in and commit.
7. The app redeploys on its own within a minute or two. The files appear on the Posted course files tab.

**Practical notes**

- Keep each file under about 25 MB. GitHub warns above 50 MB and blocks at 100 MB.
- PowerPoint and Word files cannot render inside a browser. Students get a download button instead.
- To let students read slides without downloading, export the deck to PDF and upload the PDF.
  In PowerPoint, choose File, then Export, then Create PDF. PDFs preview directly in the app.
- Use plain filenames without spaces or special characters. Use `Week3_Macronutrients.pdf`
  rather than `Week 3 - Macronutrients (final).pdf`.
- Post only material you own or have the right to distribute. Do not upload scanned textbook
  chapters, publisher test banks, or ATI proprietary content to a public repository.
- If the repository is public, anything you commit is visible to anyone on the internet. Never post
  student names, grades, exam keys, or any protected information.
            """
        )

elif page == "Study Resources":
    st.header("Study Resources")
    st.markdown(
        """
        ### How to use this app
        1. Review one content section.
        2. Answer that topic's questions with rationales until you can explain each answer.
        3. Work the matching and clinical decision activities on the content pages.
        4. Finish with a clinical case that uses the same content.
        5. Build a mixed exam once you have reviewed several topics.
        6. Use the missed-topic summary after each exam to decide what to review next.

        ### Recommended evidence sources
        - Current course materials and assigned ATI Nutrition readings
        - USDA MyPlate and Dietary Guidelines resources
        - Centers for Disease Control and Prevention nutrition resources
        - National Institutes of Health Office of Dietary Supplements
        - Current facility policies and clinical practice guidelines

        ### Study prompts
        - What is the nutrient's main function?
        - What happens when the patient receives too little or too much?
        - Which patients have the highest risk?
        - What should the nurse assess?
        - What teaching is safe, realistic, and culturally responsive?
        """
    )

    st.markdown(
        '<div class="warning"><strong>Copyright note:</strong> This app uses original summaries and practice questions. Add your own course-specific notes, but do not paste copyrighted textbook chapters into a public repository.</div>',
        unsafe_allow_html=True,
    )
