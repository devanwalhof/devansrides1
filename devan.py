import streamlit as st
import sqlite3
import pandas as pd
from datetime import date


# Database setup
conn = sqlite3.connect("devans_rides.db", check_same_thread=False)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_name TEXT,
    vendor TEXT,
    cost REAL,
    date_ordered DATE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_name TEXT,
    mileage INTEGER,
    resale_value REAL,
    purchase_cost REAL,
    repair_cost REAL,
    part_cost REAL,
    misc_cost REAL,
    profit REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS vehicle_inquiries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    make TEXT,
    model TEXT,
    year INTEGER,
    miles INTEGER,
    damage TEXT,
    airbags TEXT,
    expected_expenses REAL,
    expected_resale_value REAL,
    distance_to_auction REAL,
    desired_profit REAL,
    max_bid REAL,
    auction_url TEXT
)
""")

conn.commit()



# Sidebar Navigation
st.sidebar.image("christisking.png", width=225)
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to:", ["Home","Rebuild Tutorial", "Vehicle Inquiry", "Vehicle Evaluation", "Parts Management", "Inventory & Accounting"])
# Clear all entries from the databases
if st.sidebar.button("Clear All Database Entries"):
    cursor.execute("DELETE FROM parts")
    cursor.execute("DELETE FROM vehicles")
    cursor.execute("DELETE FROM vehicle_inquiries")
    conn.commit()
    st.sidebar.success("All entries have been cleared from the databases!")
# Section: Home
if section == "Home":
    # Title and Introduction
    st.title("Devan's Rides: Rebuilt Vehicle Manager")

    st.write("""
    Welcome! This website is designed to help streamline vehicle evaluation, 
    parts searching, inventory management, and financial tracking. Devan's Rides is committed to providing quality used vehicles at affordable prices while sharing the love of Christ.
    """)

    # Displaying images side by side only on the home page
    col1, col2, col3 = st.columns(3)

    with col1:
        st.image("challenger.jpg", width=300)

    with col2:
        st.image("charger.jpg", width=300)

    with col3:
        st.image("silverado.jpg", width=300)

# Section: Rebuild Tutorial
if section == "Rebuild Tutorial":

    st.header("Rebuild Your Dream Vehicle with Devan's Rides")

    st.write("""
    Rebuilding vehicles involves several different steps:
    - Finding a great vehicle
    - Winning the auction
    - Getting the vehicle to your shop
    - Finding parts 
    - Rebuilding the vehicle
    - Inspections and titling
    
    At Devan's Rides, we'd love to help guide you through this process. We have several 
    different packages available for people of all experience levels. 
    
    Broker Package ($300)
    - Bid through our dealership at auctions sites around the U.S. 
    - Only charged for successful bids
    - Salvage Certificate issued in your name
    
    Tutorial Package ($1150)
    - Bid through our dealership at auctions sites around the U.S. 
    - We help the customer through the entire process
       - Picking up the vehicle
       - Sourcing parts
       - Mechanical tips
       - Inspection and Titling
       - Selling the vehicle (if desired)
    
    Full Rebuild Package (Price varies)
    - Customer picks a car from an auction and we rebuild it
    - Customer sets a budget and we handle the rest
    - Optional exhaust, suspension, paint, and wheel upgrades available
    - Customer purchases the vehicle for the budget price once it's rebuilt
    
    """)

# Section: Vehicle Inquiry
if section == "Vehicle Inquiry":
    st.header("Vehicle Inquiry")
    st.write("""
    Devan's Rides specializes in sourcing repairable vehicles. 
    If you're interested in a specific vehicle, input the details below, and I can help you bid and buy it from **Copart** or **IAA**.
    Please reach out to me at **406-539-6553** for further assistance.
    """)

    # Input fields for users to specify the vehicle they're interested in
    vehicle_make = st.text_input("Enter the make of the vehicle:")
    vehicle_model = st.text_input("Enter the model of the vehicle:")
    vehicle_year = st.number_input("Enter the year of the vehicle:", min_value=2000, max_value=2025, value=2020)
    vehicle_miles = st.number_input("Enter the mileage of the vehicle:", min_value=0, max_value=1000000)
    vehicle_damage = st.selectbox("Select the type of damage:",
                                  ["Front-End", "Rear-End", "Side", "Roof", "Flood", "Other"])
    airbags_blown = st.radio("Have the airbags been blown?", ["Yes", "No"])
    expected_expenses = st.number_input("Enter the expected expenses for repairs ($):", min_value=0.0)
    expected_resale_value = st.number_input("Enter the expected resale value ($):", min_value=0.0)
    distance_to_auction = st.number_input("Enter the distance to auction (miles):", min_value=0.0)
    desired_profit = st.number_input("Enter the desired profit ($):", min_value=0.0)

    # New input field for the auction URL
    auction_url = st.text_input("Enter the URL of the auction webpage:")

    # Max Bid Calculation
    max_bid = (expected_resale_value) - expected_expenses - (distance_to_auction * 0.4) - desired_profit
    st.write(f"### Maximum Bid: **${max_bid:,.2f}**")

    # Insert into the database
    if st.button("Submit Inquiry"):
        cursor.execute('''
        INSERT INTO vehicle_inquiries 
        (make, model, year, miles, damage, airbags, expected_expenses, expected_resale_value, distance_to_auction, desired_profit, max_bid, auction_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
        vehicle_make, vehicle_model, vehicle_year, vehicle_miles, vehicle_damage, airbags_blown, expected_expenses,
        expected_resale_value, distance_to_auction, desired_profit, max_bid, auction_url))
        conn.commit()
        st.success(f"Inquiry for {vehicle_year} {vehicle_make} {vehicle_model} submitted successfully!")

    # Display previous vehicle inquiries
    st.subheader("Previous Inquiries")
    inquiries_data = pd.read_sql("SELECT * FROM vehicle_inquiries", conn)
    if not inquiries_data.empty:
        st.dataframe(inquiries_data)

        # Option to delete an inquiry
        st.write("### Delete an Inquiry")
        # Create a selectbox with a description for each inquiry using its id and vehicle details.
        options = inquiries_data.apply(lambda row: f"{row['id']}: {row['year']} {row['make']} {row['model']}",
                                       axis=1).tolist()
        inquiry_to_delete = st.selectbox("Select an inquiry to delete:", options)
        # Parse the inquiry id from the selected option.
        inquiry_id = int(inquiry_to_delete.split(":")[0])
        if st.button("Delete Selected Inquiry"):
            cursor.execute("DELETE FROM vehicle_inquiries WHERE id=?", (inquiry_id,))
            conn.commit()
            st.success("Inquiry deleted successfully!")
    else:
        st.write("No inquiries available.")

# Section: Vehicle Evaluation
if section == "Vehicle Evaluation":
    st.header("Vehicle Evaluation")
    st.write("Evaluate potential auction vehicles to ensure profitability.")

    # Retrieve vehicle inquiries for evaluation
    inquiries_data = pd.read_sql("SELECT * FROM vehicle_inquiries", conn)
    if not inquiries_data.empty:
        # Calculate profit potential for display
        inquiries_data["Profit Potential"] = inquiries_data["expected_resale_value"] - inquiries_data[
            "expected_expenses"]

        # Input boxes for filtering
        st.sidebar.subheader("Filter Criteria")

        min_year = st.sidebar.number_input("Min Year", min_value=1950, max_value=int(inquiries_data["year"].max()),
                                           value=1950)
        max_year = st.sidebar.number_input("Max Year", min_value=1950, max_value=int(inquiries_data["year"].max()),
                                           value=int(inquiries_data["year"].max()))

        min_miles = st.sidebar.number_input("Min Mileage", min_value=1, max_value=200000, value=1)
        max_miles = st.sidebar.number_input("Max Mileage", min_value=1, max_value=200000, value=200000)

        min_profit = st.sidebar.number_input("Min Profit Potential ($)", min_value=1, max_value=50000, value=1)
        max_profit = st.sidebar.number_input("Max Profit Potential ($)", min_value=1, max_value=50000, value=50000)

        # Filter the dataframe based on the input values
        filtered_data = inquiries_data[
            (inquiries_data["year"] >= min_year) &
            (inquiries_data["year"] <= max_year) &
            (inquiries_data["miles"] >= min_miles) &
            (inquiries_data["miles"] <= max_miles) &
            (inquiries_data["Profit Potential"] >= min_profit) &
            (inquiries_data["Profit Potential"] <= max_profit)
            ]

        st.subheader("Filtered Vehicle Evaluation Table")
        st.dataframe(filtered_data)
    else:
        st.write("No vehicle inquiries available for evaluation.")

# Section: Parts Management
if section == "Parts Management":
    st.header("Parts Management")
    st.write("Track and optimize parts searching and ordering.")

    # Dropdown to select a vehicle for the part
    st.subheader("Add New Part")
    vehicles = pd.read_sql("SELECT id, make, model, year FROM vehicle_inquiries", conn)
    if not vehicles.empty:
        vehicles["vehicle_display"] = vehicles.apply(
            lambda x: f"{x['id']} - {x['make']} {x['model']} ({x['year']})", axis=1
        )
        selected_vehicle = st.selectbox("Select Vehicle:", vehicles["vehicle_display"], key="select_vehicle")
        selected_vehicle_id = int(selected_vehicle.split(" - ")[0])  # Extract the vehicle ID
    else:
        st.warning("No vehicles available. Please add a vehicle first.")
        selected_vehicle_id = None

    # Add part details
    part_name = st.text_input("Part Name:", key="part_name_input")
    vendor = st.selectbox(
        "Vendor:",
        ["Partify", "eBay", "CARiD", "Amazon", "Salvage Lot", "Other"],
        key="vendor_input",
    )
    cost = st.number_input("Cost ($):", min_value=0.0, key="cost_input")
    date_ordered = st.date_input("Date Ordered:", value=date.today(), key="date_ordered_input")
    part_notes = st.text_area("Notes:", placeholder="Add any additional details about the part...", key="notes_input")

    # Add part to the database
    if st.button("Add Part to Vehicle", key="add_part_button"):
        if selected_vehicle_id:
            # Create a vehicle-specific parts table if it doesn't exist
            vehicle_parts_table = f"vehicle_parts_{selected_vehicle_id}"

            # Create the table with the correct schema if it doesn't exist
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {vehicle_parts_table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    part_name TEXT,
                    vendor TEXT,
                    cost REAL,
                    date_ordered DATE,
                    notes TEXT
                )
            """)

            # Insert the part into the vehicle-specific table
            cursor.execute(f"""
                INSERT INTO {vehicle_parts_table} (part_name, vendor, cost, date_ordered, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (part_name, vendor, cost, date_ordered, part_notes))
            conn.commit()
            st.success(f"Part '{part_name}' added successfully to {selected_vehicle}!")
        else:
            st.error("Please select a vehicle first.")

    # Display parts inventory for each vehicle
    st.subheader("Parts Inventory")
    if not vehicles.empty:
        for index, row in vehicles.iterrows():
            vehicle_parts_table = f"vehicle_parts_{row['id']}"

            # Ensure the table exists and has the correct columns
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {vehicle_parts_table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    part_name TEXT,
                    vendor TEXT,
                    cost REAL,
                    date_ordered DATE,
                    notes TEXT
                )
            """)

            parts_data = pd.read_sql(f"SELECT * FROM {vehicle_parts_table}", conn)
            st.write(f"### Parts for {row['make']} {row['model']} ({row['year']})")
            if not parts_data.empty:
                st.dataframe(parts_data)
                total_parts_cost = parts_data["cost"].sum()
                # Swapped: Total Parts Cost now appears as a header (larger font)
                st.write(f"#### Total Parts Cost: ${total_parts_cost:.2f}")

                # Swapped: Delete a Part now appears as bold text (smaller font)
                st.write("**Delete a Part**")
                delete_options = parts_data.apply(
                    lambda x: f"{x['id']}: {x['part_name']} (Vendor: {x['vendor']})", axis=1
                ).tolist()
                selected_part_to_delete = st.selectbox(
                    "Select a part to delete:",
                    delete_options,
                    key=f"delete_part_{row['id']}"
                )
                selected_part_id = int(selected_part_to_delete.split(":")[0])
                if st.button("Delete Selected Part", key=f"delete_part_button_{row['id']}"):
                    cursor.execute(f"DELETE FROM {vehicle_parts_table} WHERE id=?", (selected_part_id,))
                    conn.commit()
                    st.success("Part deleted successfully! Please refresh the page so the database updates.")

            else:
                st.write("No parts added for this vehicle yet.")

# Section: Inventory & Accounting
if section == "Inventory & Accounting":
    st.header("Inventory & Accounting")
    st.write("Track expenses, profits, and vehicle inventory.")

    # Add Vehicle Details
    st.subheader("Add New Vehicle")
    vehicle_name = st.text_input("Vehicle Name:")
    mileage = st.number_input("Mileage (miles):", min_value=0)
    resale_value = st.number_input("Resale Value ($):", min_value=0.0)
    purchase_cost = st.number_input("Purchase Cost ($):", min_value=0.0)
    repair_cost = st.number_input("Repair Cost ($):", min_value=0.0)
    part_cost = st.number_input("Parts Cost ($):", min_value=0.0)
    misc_cost = st.number_input("Miscellaneous Expenses ($):", min_value=0.0)

    total_cost = purchase_cost + repair_cost + part_cost + misc_cost
    profit = resale_value - total_cost

    if st.button("Add Vehicle to Database"):
        cursor.execute("""
            INSERT INTO vehicles (vehicle_name, mileage, resale_value, purchase_cost, repair_cost, part_cost, misc_cost, profit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (vehicle_name, mileage, resale_value, purchase_cost, repair_cost, part_cost, misc_cost, profit))
        conn.commit()
        st.success(f"Vehicle '{vehicle_name}' added successfully with a profit of ${profit}!")

    # View Vehicle Inventory
    st.subheader("Vehicle Inventory")
    vehicles_data = pd.read_sql("SELECT * FROM vehicles", conn)
    st.dataframe(vehicles_data)

# Footer
st.write("---")

st.write("Rebuilding Vehicles since 2021")


