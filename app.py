import streamlit as st
import pandas as pd
import pickle
from tensorflow.keras.models import load_model

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="📊",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

.stButton>button {
    width: 100%;
    background: linear-gradient(90deg,#4F46E5,#9333EA);
    color: white;
    border-radius: 10px;
    height: 3em;
    font-size: 18px;
    border: none;
    font-weight: bold;
}

.stButton>button:hover {
    background: linear-gradient(90deg,#4338CA,#7E22CE);
    color: white;
}

.block-container {
    padding-top: 2rem;
}

.title {
    text-align: center;
    font-size: 45px;
    font-weight: bold;
    color: #FFFFFF;
}

.subtitle {
    text-align: center;
    color: #A1A1AA;
    font-size: 18px;
    margin-bottom: 40px;
}

.prediction-box {
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    font-size: 22px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOAD FILES ----------------
model = load_model("model.h5")

with open("label_encoder_gender.pkl", "rb") as file:
    gender_encoder = pickle.load(file)

with open("onehot_encoder_geo.pkl", "rb") as file:
    geo_encoder = pickle.load(file)

with open("scaler.pkl", "rb") as file:
    scaler = pickle.load(file)

# ---------------- HEADER ----------------
st.markdown('<div class="title">Customer Churn Prediction</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="subtitle">Predict whether a customer is likely to leave the bank</div>',
    unsafe_allow_html=True
)

# ---------------- LAYOUT ----------------
col1, col2 = st.columns(2)

with col1:

    credit_score = st.number_input(
        "Credit Score",
        min_value=300,
        max_value=900,
        value=600
    )

    geography = st.selectbox(
        "Geography",
        geo_encoder.categories_[0]
    )

    gender = st.selectbox(
        "Gender",
        gender_encoder.classes_
    )

    age = st.slider(
        "Age",
        18,
        100,
        40
    )

    tenure = st.slider(
        "Tenure",
        0,
        10,
        3
    )

with col2:

    balance = st.number_input(
        "Balance",
        value=60000.0
    )

    num_of_products = st.slider(
        "Number Of Products",
        1,
        4,
        2
    )

    has_cr_card = st.selectbox(
        "Has Credit Card",
        [0, 1]
    )

    is_active_member = st.selectbox(
        "Is Active Member",
        [0, 1]
    )

    estimated_salary = st.number_input(
        "Estimated Salary",
        value=50000.0
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- PREDICTION ----------------
if st.button("Predict Churn"):

    input_data = pd.DataFrame({
        'CreditScore': [credit_score],
        'Geography': [geography],
        'Gender': [gender],
        'Age': [age],
        'Tenure': [tenure],
        'Balance': [balance],
        'NumOfProducts': [num_of_products],
        'HasCrCard': [has_cr_card],
        'IsActiveMember': [is_active_member],
        'EstimatedSalary': [estimated_salary]
    })

    # Encode gender
    input_data['Gender'] = gender_encoder.transform(input_data['Gender'])

    # Geography encoding
    geo_encoded = geo_encoder.transform(
        input_data[['Geography']]
    ).toarray()

    geo_encoded_df = pd.DataFrame(
        geo_encoded,
        columns=geo_encoder.get_feature_names_out(['Geography'])
    )

    # Drop geography
    input_data.drop("Geography", axis=1, inplace=True)

    # Combine
    final_data = pd.concat(
        [input_data.reset_index(drop=True), geo_encoded_df],
        axis=1
    )

    # Scale
    final_data_scaled = scaler.transform(final_data)

    # Prediction
    prediction = model.predict(final_data_scaled)

    prediction_proba = prediction[0][0]

    st.markdown("<br>", unsafe_allow_html=True)

    st.metric(
        label="Churn Probability",
        value=f"{prediction_proba:.2%}"
    )

    # Result
    if prediction_proba > 0.5:

        st.markdown(f"""
        <div class="prediction-box" 
        style="background-color:#7F1D1D;color:#FCA5A5;">
            Customer is likely to churn
        </div>
        """, unsafe_allow_html=True)

    else:

        st.markdown(f"""
        <div class="prediction-box" 
        style="background-color:#052E16;color:#86EFAC;">
            Customer is likely to stay
        </div>
        """, unsafe_allow_html=True)