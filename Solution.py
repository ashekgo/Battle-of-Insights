import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
transactions_path = "./Transactions.xlsx"
transactions_df = pd.ExcelFile(transactions_path).parse("Sheet1")

# Convert 'Date' to datetime for easier manipulation
transactions_df['Date'] = pd.to_datetime(transactions_df['Date'])

# Add a 'Month' column for analysis
transactions_df['Month'] = transactions_df['Date'].dt.month

# --- Question 1: Average Transaction Amount Across Store Types by Season ---
average_transaction_by_store_season = transactions_df.groupby(['Store_Type', 'Season'])['Amount($)'].mean().reset_index()
average_transaction_by_store_season.columns = ['Store Type', 'Season', 'Average Transaction Amount ($)']
average_transaction_by_store_season = average_transaction_by_store_season.sort_values(by=['Store Type', 'Season'])

# --- Question 2: Most Common Payment Method for High-Value Transactions Across Cities ---
average_transaction_amount = transactions_df['Amount($)'].mean()
high_value_transactions = transactions_df[transactions_df['Amount($)'] > average_transaction_amount]
payment_method_by_city = (
    high_value_transactions.groupby(['City', 'Payment_Method'])
    .size()
    .reset_index(name='Count')
)
most_common_payment_method = payment_method_by_city.loc[
    payment_method_by_city.groupby('City')['Count'].idxmax()
].sort_values(by='City')

# --- Question 3: Sales Amounts With and Without Discounts Over the Month ---
sales_with_without_discount = (
    transactions_df.groupby(['Month', 'Discount_Applied'])['Amount($)']
    .sum()
    .reset_index()
    .pivot(index='Month', columns='Discount_Applied', values='Amount($)')
    .fillna(0)
)
sales_with_without_discount.columns = ['No Discount', 'With Discount']

# --- Question 4: Top Cities with Highest Average Items Per Transaction ---
average_items_per_city = transactions_df.groupby('City')['Total_Items'].mean().reset_index()
top_cities = average_items_per_city.nlargest(3, 'Total_Items')
sales_by_city_season = (
    transactions_df[transactions_df['City'].isin(top_cities['City'])]
    .groupby(['City', 'Season'])['Amount($)']
    .sum()
    .reset_index()
)

# --- Question 5: Effectiveness of Promotions in Driving Higher Transaction Amounts ---
promotion_effectiveness = (
    transactions_df.groupby(['Promotion', 'Season'])['Amount($)']
    .mean()
    .reset_index()
    .sort_values(by=['Season', 'Amount($)', 'Promotion'], ascending=[True, False, True])
)

# Streamlit layout
st.title("Business Insights Dashboard")

# Problem Statement Section
st.subheader("Problem Statement")
st.write(""" 
This business insights dashboard provides an in-depth analysis of various transaction-related metrics. 
By exploring the dataset, we can understand customer behavior, payment methods, sales trends, 
and promotion effectiveness, with a focus on improving strategic decisions for business growth.
""")

# Sidebar for filter options with color customization
st.sidebar.title(""" 
**🚀 Battle of Insight**
""")

# Select for store types (Multiple selection allowed)
store_type = st.sidebar.multiselect(
    'Select Store Type(s):',
    options=transactions_df['Store_Type'].unique(),
    default=transactions_df['Store_Type'].unique()
)

# Select for seasons (Multiple selection allowed)
season = st.sidebar.multiselect(
    'Select Season(s):',
    options=transactions_df['Season'].unique(),
    default=transactions_df['Season'].unique()
)

# Select for cities (Multiple selection allowed)
city = st.sidebar.multiselect(
    'Select City(s):',
    options=transactions_df['City'].unique(),
    default=transactions_df['City'].unique()
)

# Range selector for Amount ($)
min_amount, max_amount = st.sidebar.slider(
    "Select Transaction Amount Range ($)",
    min_value=int(transactions_df['Amount($)'].min()),
    max_value=int(transactions_df['Amount($)'].max()),
    value=(int(transactions_df['Amount($)'].min()), int(transactions_df['Amount($)'].max())),
    step=1
)

# Filter data based on selections
filtered_data = transactions_df[ 
    (transactions_df['Store_Type'].isin(store_type)) & 
    (transactions_df['Season'].isin(season)) & 
    (transactions_df['City'].isin(city)) & 
    (transactions_df['Amount($)'] >= min_amount) & 
    (transactions_df['Amount($)'] <= max_amount)
]

# --- Show All Questions and Answers on Homepage ---
st.header("All Questions and Answers")

# Question 1: Average Transaction Amount Across Store Types by Season
st.subheader("📊 1. What is the average transaction amount ($) across different store types, and how does it vary by season?")
st.write("""
This section shows the average transaction amounts across different store types and seasons.
By understanding these trends, businesses can identify which store types perform best in each season.
""")
st.dataframe(average_transaction_by_store_season, use_container_width=True)

# Visualization for Question 1
# Set a professional theme
sns.set_theme(style="whitegrid")

# Define color palettes for each chart
color_palettes = [
    sns.color_palette(["#dae9e4"]), 
    sns.color_palette(["#dfecfd"]),  
    sns.color_palette(["#e2caec"]),
    sns.color_palette(["#eac2e4"]), 
    sns.color_palette(["#fcd5ce"]), 
    sns.color_palette(["#fdeed7"]),  
]

# Get unique store types
store_types = average_transaction_by_store_season['Store Type'].unique()

# Ensure we only plot the first 6 charts
store_types = store_types[:6]

# Define insights for each chart
chart_insights = [
    "Perform best in spring (53.54) and summer (53.35), with a noticeable dip in winter (51.60). Seasonality plays a significant role in customer activity.",
    "Exhibit stable performance across all seasons, with summer (52.78) and winter (52.58) being slightly stronger than fall (51.38).",
    "Winter shows the highest performance (53.22), likely driven by seasonal demand for healthcare products, while summer (52.05) is the weakest.",
    "Thrive in summer (53.59) and spring (53.52), indicating customer preference for niche products during warmer months, while winter and fall show similar lower performance levels (~51.8).",
    "Experience consistent demand year-round, peaking slightly in spring (52.69), while summer dips (51.44).",
    "Perform best in summer (53.01) and fall (52.03), with slightly lower performance in spring and winter (~51.6–51.8).",
]

# Create individual charts for each store type
for idx, store_type in enumerate(store_types, start=1):
    # Create the plot for the current store type
    fig, ax = plt.subplots(figsize=(8, 5))
    store_data = average_transaction_by_store_season[average_transaction_by_store_season['Store Type'] == store_type]
    
    # Create the barplot
    sns.barplot(
        data=store_data,
        x='Season',
        y='Average Transaction Amount ($)',
        ax=ax,
        palette=color_palettes[idx - 1]  # Use a unique color for each chart
    )
    
    # Add data points on bars
    for bar in ax.patches:
        value = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 1,  # Slightly above the bar
            f"${value:.2f}",
            ha='center',
            va='bottom',
            fontsize=15,
            color="white",
            weight='bold',
            bbox=dict(boxstyle="round,pad=0.2", edgecolor="none", facecolor="black")
        )
    
    # Set the title and adjust axes
    ax.set_title(f"Chart {idx:02}: Average Transaction Amount for {store_type}", fontsize=17, weight='bold')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_ylim(0, average_transaction_by_store_season['Average Transaction Amount ($)'].max() * 1.2)  # Consistent y-axis

    # Remove y-axis labels and ticks
    ax.set_yticks([])  # Hide y-axis ticks
    ax.tick_params(left=False)  # Hide left axis

    # Customize x-axis labels
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=15, fontweight='bold')  # Make x-axis text bold and larger

    # Adjust layout for spacing
    fig.tight_layout()
    
    # Show the plot
    st.pyplot(fig)
    
    # Display insights specific to the chart
    st.write(f"""
    **Insights for Chart {idx}: ({store_type})**
    
    {chart_insights[idx - 1]}
    """)



# Question 2: Most Common Payment Method for High-Value Transactions Across Cities
st.subheader("💳 2. Which payment method is most commonly used in high-value transactions (above the average transaction amount), and how does it differ across cities?")
st.write("""
This section highlights the most common payment methods for transactions exceeding the average transaction amount across various cities.
Understanding this can help businesses refine their payment method strategies.
""")
st.dataframe(most_common_payment_method, use_container_width=True)

# Visualization for Question 2
# Set a professional theme
sns.set_theme(style="whitegrid")

# Define the custom color palette
custom_palette = ['#dae9e4', '#dfecfd', '#e2caec', '#fdeed7']

# Visualization for Most Common Payment Methods for High-Value Transactions Across Cities
fig, ax = plt.subplots(figsize=(10, 6))

# Adjust city labels to display two-word names on separate lines
most_common_payment_method['City'] = most_common_payment_method['City'].apply(lambda x: "\n".join(x.split()))

# Create the barplot with the custom color palette
sns.barplot(
    data=most_common_payment_method,
    x='City',
    y='Count',
    hue='Payment_Method',
    ax=ax,
    palette=custom_palette
)

# Add data points on bars
for bar in ax.patches:
    value = bar.get_height()
    if value > 0:  # Avoid labels for empty bars
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 10,  # Adjust space above the bars (increase if needed)
            f"{int(value)}",  # Display count as an integer
            ha='center',
            va='bottom',
            fontsize=12,
            color="white",
            weight='bold',
            bbox=dict(boxstyle="round,pad=0.2", edgecolor="none", facecolor="black")
        )

# Add title and labels
ax.set_title('Most Common Payment Methods for High-Value Transactions Across Cities', fontsize=17, weight='bold')
ax.set_xlabel('', fontsize=14, weight='bold')  # No explicit label for the x-axis
ax.set_ylabel('', fontsize=14, weight='bold')  # No explicit label for the y-axis

# Remove y-axis ticks for a cleaner look
ax.set_yticks([])
ax.tick_params(left=False)

# Customize x-axis labels (keep bold styling and adjust size)
ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=12, fontweight='bold')

# Customize legend
ax.legend(title="Payment Method", fontsize=12, title_fontsize=13)

# Adjust the ylim to create space above the bars
ax.set_ylim(0, ax.get_ylim()[1] * 1.2)  # Add extra space at the top of the bars

# Adjust layout to prevent label overlap
fig.tight_layout()

# Show the plot in Streamlit
st.pyplot(fig)


# Insights for the chart
st.write("""
**Insights for Question 2:**

- **Mobile Payments:** Dominant in cities like Atlanta (506) and New York (510), reflecting a tech-savvy customer base and growing adoption of digital solutions for high-value transactions.

- **Cash Payments:** Significant in Boston (485), Chicago (516), and Houston (492), highlighting the continued preference for traditional payment methods in these cities.

- **Debit Cards:** Preferred in Dallas (538) and Seattle (512), showcasing a trend toward secure and direct payment methods for substantial purchases.

- **Credit Cards:** Common in Miami (489) and San Francisco (504), likely driven by their flexibility, rewards, and credit benefits, making them a top choice for high-spending customers.
""")

# Question 3: Sales Amounts With and Without Discounts Over the Month
st.subheader("💸 3. Sales Amounts With and Without Discounts Over the Month")
st.write("""
This section compares the total sales amounts for transactions with and without discounts across the months.
The goal is to identify the impact of discounts on sales and how it fluctuates throughout the year.
""")
st.dataframe(sales_with_without_discount, use_container_width=True)

# Visualization for Question 3
# Create the plot
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the data with customization
sales_with_without_discount.plot(kind='line', marker='o', ax=ax, 
                                 linewidth=2, markersize=10, linestyle='--', 
                                 color=['#a6c7b6', '#f8d28b'], markerfacecolor='black')

# Set title and labels
ax.set_title('Sales Amounts With and Without Discounts Over the Months', fontsize=17, weight='bold')
ax.set_ylabel('Sales Amount ($)')

# Set x-ticks and labels
ax.set_xticks(range(12))  # Set fixed ticks
ax.set_xticklabels(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
ax.set_xlabel('')
# Remove gridlines (both horizontal and vertical)
ax.grid(False)

# Display the plot
st.pyplot(fig)

st.write("""
**Insights for Question 3:**

- **Sales with Discount:** Generally higher than sales without discount, indicating that discounts have a positive impact on boosting sales. The largest difference in sales between the two categories occurs in March, where the discount led to a significant increase in sales.

- **Sales without Discount:** Although lower than sales with discount, the sales without discount maintain a relatively stable trend, suggesting a consistent level of interest in the products even without price reductions.

- **Key Months for Growth:** The months of March and December show the highest sales values in both categories, indicating peak shopping periods, possibly due to seasonal promotions or end-of-year buying behavior.

- **Stable Performance in Mid-Year:** Between May and September, both sales categories show a slight dip, potentially reflecting a quieter sales period before the busy holiday season or due to external factors such as market conditions or consumer sentiment.
""")

# Question 4: Top Cities with Highest Average Items Per Transaction
st.subheader("🏙️ 4. What are the top three cities with the highest average number of items per transaction, and how do their sales amounts vary across seasons?")
st.write("""
This section displays the top cities with the highest average items per transaction, and how their sales vary across different seasons.
""")
st.dataframe(top_cities, use_container_width=True)
st.write("Seasonal Sales for Top Cities")
st.dataframe(sales_by_city_season, use_container_width=True)

# Visualization for Question 4
fig, ax = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={'height_ratios': [1, 2]})

custom_palette4 = ['#dae9e4', '#dfecfd', '#e2caec', '#eac2e4', '#fcd5ce', '#fdeed7']
# Average Items per Transaction
sns.barplot(data=top_cities, x='City', y='Total_Items', ax=ax[0], palette=custom_palette4, hue='City')
ax[0].set_title('Top Cities with Highest Average Items per Transaction', fontsize=17, weight='bold')
ax[0].set_xlabel('')
ax[0].set_ylabel('Total Items')
ax[0].grid(False)

st.write("""
**Insights for Question 4 - Chart 1:**

- **Chicago:** Leads the list with the highest total items at 5.55, suggesting that customers in Chicago tend to purchase or interact with more items compared to those in other cities. This could indicate a higher demand or a more engaged consumer base in Chicago.

- **Houston:** Follows closely with 5.53 total items, showing that Houston also has a strong market but slightly trails Chicago. This may point to a competitive market in Houston where consumers are still engaging with a large number of items.

- **Miami:** Has the lowest total items at 5.52, but the difference is minimal compared to Chicago and Houston. This suggests that while Miami's market may be slightly less active, the overall engagement in the city is still comparable to the other two cities.

- **Overall Trend:** The total items across these three cities are quite close, indicating a relatively balanced market presence, with only slight variations between each city's consumer behavior.
""")


# Seasonal Sales
sns.barplot(data=sales_by_city_season, x='City', y='Amount($)', hue='Season', ax=ax[1], palette=custom_palette4)
ax[1].set_title('Seasonal Sales Amounts for Top Cities', fontsize=17, weight='bold')
ax[1].legend(title="Season", loc="upper right")
ax[1].set_xlabel('')
ax[1].grid(False)
st.pyplot(fig)

st.write("""
**Insights for Question 4 - Chart 2:**

- **Chicago:** The highest sales occur in the Spring season, with $51,831.02, followed closely by Winter ($51,710). Fall and Summer sales are similar but slightly lower, at $50,343.27 and $51,261.90, respectively. This indicates that Chicago's consumers are most active in the Spring, which could be linked to seasonal promotions or increased purchasing activity during that time.

- **Houston:** Fall leads in sales for Houston, with $52,117.66, followed by Spring ($50,387.61). Summer and Winter show the lowest figures, at $50,155.51 and $50,564.55, respectively. The seasonal trends suggest a strong preference for Fall, possibly due to factors like regional weather or local events that boost consumer spending.

- **Miami:** Fall again shows the highest sales for Miami, at $52,999.92, with Spring following at $50,267.66. Miami's sales in Summer and Winter are noticeably lower, with Winter sales dropping to $47,964.04. This indicates that Miami’s consumers are more likely to purchase in the Fall, with less activity in the Winter, possibly due to holiday-related shifts in buying behavior.

- **Overall Trends:** Fall is consistently the top-performing season across all cities, while Winter appears to be the weakest in Miami. Chicago and Houston show a more even distribution across seasons, with Miami having a distinct preference for Fall over the other seasons. This data suggests that seasonal factors and regional preferences play a significant role in sales trends.
""")


# Question 5: Effectiveness of Promotions in Driving Higher Transaction Amounts
st.subheader("🎯 5. How effective are different promotions in driving higher transaction amounts, and which promotion type performs best in each season?")
st.write("""
This section assesses how different promotions influence transaction amounts across various seasons.
The goal is to identify which promotions are most effective at driving higher sales.
""")
st.dataframe(promotion_effectiveness, use_container_width=True)
custom_palette5 = ['#dae9e4', '#dfecfd', '#e2caec', '#eac2e4', '#fcd5ce', '#fdeed7']
# Visualization for Question 5
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=promotion_effectiveness, x='Season', y='Amount($)', hue='Promotion', ax=ax, palette=custom_palette5)
ax.set_title('Effectiveness of Promotions in Driving Higher Transaction Amounts', fontsize=17, weight='bold')
ax.set_xlabel('Season')
ax.set_ylabel('Average Transaction Amount ($)')
ax.legend(title="Promotion Type")
ax.grid(False)
ax.set_xlabel('')
st.pyplot(fig)

st.write("""
**Insights for Question 5:**

- **BOGO (Buy One Get One) Promotion:**
    - **Summer** shows the highest sales for BOGO at $53,271.76, followed by **Winter** with $52,872.20. This suggests that BOGO promotions are most effective in the summer and winter, potentially due to heightened consumer demand during these seasons, such as summer shopping sprees or winter holidays.
    - **Fall** and **Spring** show slightly lower sales for BOGO promotions, at $52,678.44 and $52,519.02, respectively. These promotions still drive significant sales, but are slightly less impactful compared to Summer and Winter.

- **Discount on Selected Items:**
    - **Spring** sees the highest sales for discounts at $53,177.15, which may be tied to seasonal clearances or special events boosting consumer spending during this time.
    - **Fall** follows closely with $51,997.05, indicating that discounts on selected items are also highly effective during this season.
    - **Summer** and **Winter** show similar sales, with Winter at $52,012.39 and Summer at $51,842.83. While still performing well, these seasons show a slight dip compared to Spring and Fall, suggesting that other factors may be influencing consumer purchasing behavior.

- **Overall Trends:**
    - **BOGO promotions** tend to drive slightly higher sales in **Summer** and **Winter**, while **Discounts on Selected Items** see the highest performance in **Spring** and **Fall**.
    - The data suggests that specific promotions perform better during different seasons, highlighting the importance of aligning promotional strategies with seasonal trends to maximize sales.
""")


# Profile Section
st.header("Profile")

# Add biodata without image
st.markdown(""" 
### Who Am I?  
My name is Ashek Rahman Anik. I am a data enthusiast with a passion for analyzing business data and providing actionable insights to drive growth. 
With a background in data analytics and visualization, I specialize in using tools like Python, Power BI, and Streamlit to transform raw data into meaningful visual stories.
""")


# Add biodata without image
st.markdown(""" 
### Who Am I?
👨‍💻 I am a data analyst with experience in business intelligence and data visualization. I specialize in analyzing large datasets and providing actionable insights that help businesses make informed decisions.

#### Skills:
- Data Analysis
- Business Intelligence
- Visualization (Power BI, Tableau, Streamlit)

#### Contact:
📧 Email: ashekgo@gmail.com
🌍 Bangladesh
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        /* Apply background to all st.write content */
        .streamlit-expanderHeader {
            background-color: #f0f0f0;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        /* Ensure the text is readable */
        .stMarkdown, .stText {
            background-color: #f0f0f0;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            color: #333;
        }
    </style>
""", unsafe_allow_html=True)
