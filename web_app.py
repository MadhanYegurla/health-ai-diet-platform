import streamlit as st
import matplotlib.pyplot as plt
import datetime
import pandas as pd
import plotly.graph_objects as go

from database import (
    create_table,
    add_user,
    create_log_table,
    add_log,
    get_logs,
    get_user
)

create_table()
create_log_table()

st.set_page_config(page_title="NutriAI", layout="wide")

# ================= PREMIUM DARK THEME =================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

.main {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
}

section[data-testid="stSidebar"] {
    background: #111827;
}

.stButton>button {
    background: linear-gradient(45deg, #00f5c4, #00c6ff);
    color: black;
    border-radius: 12px;
    height: 3em;
    font-weight: bold;
}

h1, h2, h3 {
    color: #00f5c4;
}
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
st.sidebar.title("🥗 NutriAI")
page = st.sidebar.selectbox(
    "Navigation",
    ["User Registration", "Health Dashboard", "Calorie Tracker", "Analytics"]
)

# =====================================================
# USER REGISTRATION
# =====================================================
if page == "User Registration":

    st.title("👤 User Registration")

    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1)
    gender = st.selectbox("Gender", ["Male", "Female"])
    height = st.number_input("Height (cm)", min_value=0.0)
    weight = st.number_input("Weight (kg)", min_value=0.0)
    activity_level = st.selectbox(
        "Activity Level",
        ["Sedentary", "Light", "Moderate", "Active"]
    )
    goal = st.selectbox(
        "Goal",
        ["Weight Loss", "Maintain Weight", "Weight Gain"]
    )

    if st.button("Save User Data"):
        if name != "":
            add_user(name, age, gender, height, weight, activity_level, goal)
            st.success("User Data Saved Successfully!")
        else:
            st.error("Please enter your name")

# =====================================================
# HEALTH DASHBOARD
# =====================================================
elif page == "Health Dashboard":

    st.title("📊 Health Dashboard")

    height = st.number_input("Height (cm)", min_value=0.0)
    weight = st.number_input("Weight (kg)", min_value=0.0)

    if height > 0 and weight > 0:
        bmi = weight / ((height / 100) ** 2)

        col1, col2 = st.columns(2)
        col1.metric("BMI", round(bmi, 2))

        if bmi < 18.5:
            col2.metric("Category", "Underweight")
        elif 18.5 <= bmi < 25:
            col2.metric("Category", "Normal")
        elif 25 <= bmi < 30:
            col2.metric("Category", "Overweight")
        else:
            col2.metric("Category", "Obese")

# =====================================================
# CALORIE TRACKER
# =====================================================
elif page == "Calorie Tracker":

    st.title("🔥 Smart Calorie Tracker")

    name = st.text_input("Enter Your Name")

    if name != "":
        user = get_user(name)

        if user:

            age = user["age"]
            gender = user["gender"]
            height = user["height"]
            weight = user["weight"]
            activity_level = user["activity_level"]
            goal = user["goal"]

            # BMR
            if gender == "Male":
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161

            activity_multiplier = {
                "Sedentary": 1.2,
                "Light": 1.375,
                "Moderate": 1.55,
                "Active": 1.725
            }

            daily_calories = bmr * activity_multiplier[activity_level]

            if goal == "Weight Loss":
                daily_calories -= 500
            elif goal == "Weight Gain":
                daily_calories += 500

            total_consumed = 0
            food_breakdown = {}

            # Predefined Foods
            food_database = {
                "Rice (1 cup)": 200,
                "Egg (1)": 70,
                "Chicken (100g)": 250,
                "Milk (1 glass)": 120,
                "Banana (1)": 105,
                "Apple (1)": 95,
                "Roti (1)": 100,
                "Dal (1 bowl)": 150
            }

            selected_foods = st.multiselect("Select Foods", list(food_database.keys()))

            for food in selected_foods:
                qty = st.number_input(f"Quantity of {food}", 1, key=food)
                calories = food_database[food] * qty
                total_consumed += calories
                food_breakdown[food] = calories

            # Custom Food Auto Estimate
            st.divider()
            st.subheader("➕ Add Custom Food")

            custom_food = st.text_input("Enter Food Name")

            custom_estimates = {
                "pizza": 285,
                "burger": 295,
                "dosa": 168,
                "biryani": 350,
                "paneer": 265,
                "idli": 58,
                "chapati": 100
            }

            if custom_food:
                estimated_cal = custom_estimates.get(custom_food.lower(), 150)
                st.info(f"Estimated Calories per serving: ~{estimated_cal}")

                qty_custom = st.number_input("Quantity", 1, key="custom_qty")
                custom_total = estimated_cal * qty_custom

                total_consumed += custom_total
                food_breakdown[custom_food] = custom_total

                st.write(f"Calories from {custom_food}: {custom_total}")

            # Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Required", int(daily_calories))
            col2.metric("Consumed", total_consumed)

            difference = total_consumed - int(daily_calories)
            col3.metric("Difference", difference)

            # Progress
            progress = min(total_consumed / daily_calories, 1.0)
            st.subheader("Daily Goal Progress")
            st.progress(progress)
            st.write(f"{int(progress*100)}% of daily target reached")

            # Gauge
            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=total_consumed,
                title={'text': "Calories Consumed"},
                gauge={'axis': {'range': [0, daily_calories]}}
            ))
            st.plotly_chart(gauge, use_container_width=True)

            # Pie Chart
            if food_breakdown:
                fig2, ax2 = plt.subplots()
                ax2.pie(food_breakdown.values(),
                        labels=food_breakdown.keys(),
                        autopct='%1.1f%%')
                st.subheader("Food Breakdown")
                st.pyplot(fig2)

            # Smart Recommendation
            st.divider()
            st.subheader("🤖 Smart Food Recommendation")

            if difference < 0:
                remaining = abs(difference)
                st.success(f"You need {remaining} more calories.")

                for food, cal in food_database.items():
                    if cal <= remaining:
                        st.write(f"• {food} ({cal} calories)")

            elif difference > 0:
                st.warning(f"You exceeded by {difference} calories.")
                st.write("Next time try lighter options:")
                for food, cal in food_database.items():
                    if cal < 120:
                        st.write(f"• {food}")

            else:
                st.info("Perfect calorie balance today! 🎉")

            if st.button("Save Today's Log"):
                today = str(datetime.date.today())
                add_log(name, today, int(daily_calories), total_consumed)
                st.success("Log Saved Successfully!")

        else:
            st.error("User not found.")

# =====================================================
# ANALYTICS
# =====================================================
elif page == "Analytics":

    st.title("📈 Analytics Dashboard")

    name = st.text_input("Enter Your Name")

    if name != "":
        logs = get_logs(name)

        if logs:
            df = pd.DataFrame(logs)
            df.columns = ["Date", "Required", "Consumed"]
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")

            st.dataframe(df)

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(df["Date"], df["Required"], marker="o")
            ax.plot(df["Date"], df["Consumed"], marker="o")
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

        else:
            st.info("No records found.")