import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# TogetherWherever App: Personalized community-focused schedules

st.title("Welcome to TogetherWherever!")  # Updated title

# Collect user input (interest, availability, location)
st.write("Find community-focused events and volunteering opportunities near you.")
interest = st.text_input("What is your main interest? (e.g., Healthcare, Environment, Sports): ").strip().lower()
availability = st.text_input("What is your availability? (e.g., Evenings, Weekends): ").strip().lower()
location = st.text_input("Where are you located? (e.g., City, Zip Code): ").strip().lower()

if st.button('Submit'):
    st.write("Searching for events... Please wait.")

    # Scrape event data from a sample event site
    url = 'https://www.eventbrite.com/d/online/community--events/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract event details
    events = soup.find_all('div', class_='search-event-card-wrapper')
    event_list = []

    for event in events:
        title = event.find('div', class_='eds-is-hidden-accessible').text.strip()
        date = event.find('div', class_='eds-text-color--grey-500').text.strip() if event.find('div', class_='eds-text-color--grey-500') else "No date available"
        location_name = event.find('div', class_='card-text--truncated').text.strip() if event.find('div', class_='card-text--truncated') else "Online"
        
        # Append event details to the list
        event_list.append({
            'Title': title,
            'Date': date,
            'Location': location_name,
        })

    # Convert the list of events into a DataFrame
    df = pd.DataFrame(event_list)

    # Function to filter events based on user preferences
    def filter_events(events, interest, availability, location):
        filtered = []
        for event in events:
            if interest in event['Title'].lower() and location in event['Location'].lower():
                filtered.append(event)
        return filtered

    matching_events = filter_events(df.to_dict(orient='records'), interest, availability, location)

    # Function to fill user availability slots with events
    def fill_schedule(user_availability, events, matching_events):
        schedule = {time_slot: None for time_slot in user_availability}

        # Fill with matching events first
        for time_slot in user_availability:
            for event in matching_events:
                if time_slot.lower() in event['Date'].lower():
                    schedule[time_slot] = event
                    matching_events.remove(event)  # Once assigned, remove event

        # For remaining empty slots, suggest a remote activity
        remote_activities = [
            {'Title': 'Walk for Charity', 'Date': 'Anytime', 'Location': 'Online'},
            {'Title': 'Donate to Food Bank', 'Date': 'Anytime', 'Location': 'Online'}
        ]
        
        for time_slot, event in schedule.items():
            if event is None:  # If no event was found for this time slot, suggest remote activity
                schedule[time_slot] = remote_activities.pop(0)  # Assign a remote activity
        
        return schedule

    # User availability input (could be dynamic, based on user data)
    user_availability = ['Evenings', 'Weekends']

    # Fill the schedule
    schedule = fill_schedule(user_availability, df.to_dict(orient='records'), matching_events)

    # Display the suggested schedule
    st.write("### Your Suggested TogetherWherever Schedule:")
    for time_slot, event in schedule.items():
        st.write(f"\n**{time_slot}:**")
        st.write(f"**Title**: {event['Title']}")
        st.write(f"**Date**: {event['Date']}")
        st.write(f"**Location**: {event['Location']}")
