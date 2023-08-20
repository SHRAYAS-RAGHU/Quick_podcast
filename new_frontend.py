# import streamlit as st

# def newsletter_tab():
#     st.write("Welcome to the Newsletter tab!")
    
#     # Get RSS feed URL from user
#     rss_feed_url = st.text_input("Enter RSS Feed URL:")
#     st.write("You entered:", rss_feed_url)

# def search_podcast_tab():
#     st.write("Welcome to the Search Podcast tab!")
    
#     # Search bar and button
#     st.write("Search for a podcast:")
#     search_query = st.text_input("Enter podcast name:")
#     search_button = st.button("Search")

#     if search_button:
#         # Perform API call to retrieve RSS URL based on search_query
#         rss_url = perform_api_call(search_query)
#         st.write("RSS URL for search query:", rss_url)

# def perform_api_call(search_query):
#     # Perform your API call here and return the RSS URL
#     # This is just a placeholder function
#     # Replace this with your actual API call code
#     rss_url = "https://example.com/api/rss?q=" + search_query
#     return rss_url
    
# def main():
#     st.title("PodBot - Podcast Summaries")
#     st.sidebar.header("Podcast RSS Feeds")
#     st.sidebar.subheader("Available Podcasts Feeds")
#     selected_podcast = st.sidebar.selectbox("Select Podcast", options=["1", "2", "3"])

#     st.sidebar.subheader("Add and Process New Podcast Feed")
#     url = st.sidebar.text_input("Link to RSS Feed")

#     process_button = st.sidebar.button("Process Podcast Feed")
#     st.sidebar.markdown("**Note**: Podcast processing can take upto 5 mins, please be patient.")
    
#     # Create tabs with a horizontal bar
#     tabs = ["Newsletter", "Search Podcast"]
#     tab1, tab2 = st.tabs(tabs)

#     with tab1:
#         newsletter_tab()
#     with tab2:
#         search_podcast_tab()

# if __name__ == "__main__":
#     main()
# def url = https://access.acast.com/rss/d556eb54-6160-4c85-95f4-47d9f5216c49


import streamlit as st
import modal
import json
import os

def newsletter_tab():

    available_podcast_info = create_dict_from_json_files('.')

    # Left section - Input fields
    st.header("Podcast RSS Feeds")

    # Dropdown box
    st.subheader("Available Podcasts Feeds")
    selected_podcast = st.selectbox("Select Podcast", options=available_podcast_info.keys())

    if selected_podcast:

        podcast_info = available_podcast_info[selected_podcast]

        # Right section - Newsletter content
        st.header("Newsletter Content")

        # Display the podcast title
        st.subheader("Episode Title")
        st.write(podcast_info['podcast_details']['episode_title'])

        # Display the podcast summary and the cover image in a side-by-side layout
        col1, col2 = st.columns([7, 3])

        with col1:
            # Display the podcast episode summary
            st.subheader("Podcast Episode Summary")
            st.write(podcast_info['podcast_summary'])

        with col2:
            st.image(podcast_info['podcast_details']['episode_image'], caption="Podcast Cover", width=300, use_column_width=True)

        # Display the podcast guest and their details in a side-by-side layout
        col3, col4 = st.columns([3, 7])

        with col3:
            st.subheader("Podcast Guest")
            st.write(podcast_info['podcast_guest']['name'])

        with col4:
            st.subheader("Podcast Guest Details")
            st.write(podcast_info["podcast_guest"]['summary'])

        # Display the five key moments
        st.subheader("Key Moments")
        key_moments = podcast_info['podcast_highlights']
        for moment in key_moments.split('\n'):
            st.markdown(
                f"<p style='margin-bottom: 5px;'>{moment}</p>", unsafe_allow_html=True)
        


def search_podcast_tab():
    # User Input box
    st.subheader("Add and Process New Podcast Feed")
    url = st.text_input("Link to RSS Feed")

    process_button = st.button("Process Podcast Feed")
    st.markdown("**Note**: Podcast processing can take upto 5 mins, please be patient.")

    if process_button:

        # Call the function to process the URLs and retrieve podcast guest information
        with st.spinner('Transcribing your audio and summarizing it. Wait for a while'):
            podcast_info = process_podcast_info(url)
    
    # Right section - Newsletter content
        st.header("Newsletter Content")

        # Display the podcast title
        st.subheader("Episode Title")
        st.write(podcast_info['podcast_details']['episode_title'])

        # Display the podcast summary and the cover image in a side-by-side layout
        col1, col2 = st.columns([7, 3])

        with col1:
            # Display the podcast episode summary
            st.subheader("Podcast Episode Summary")
            st.write(podcast_info['podcast_summary'])

        with col2:
            st.image(podcast_info['podcast_details']['episode_image'], caption="Podcast Cover", width=300, use_column_width=True)

        # Display the podcast guest and their details in a side-by-side layout
        col3, col4 = st.columns([3, 7])

        with col3:
            st.subheader("Podcast Guest")
            st.write(podcast_info['podcast_guest']['name'])

        with col4:
            st.subheader("Podcast Guest Details")
            st.write(podcast_info["podcast_guest"]['summary'])

        # Display the five key moments
        st.subheader("Key Moments")
        key_moments = podcast_info['podcast_highlights']
        for moment in key_moments.split('\n'):
            st.markdown(
                f"<p style='margin-bottom: 5px;'>{moment}</p>", unsafe_allow_html=True)
            
        # import json
        # with open(f"/content/podcast/{podcast_info['podcast_details']['episode_title']}.json", "w") as outfile:
        #     json.dump(podcast_info, outfile)
            


def main():
    st.title("PodBot - Podcast Summaries")

    tabs = ["Newsletter", "Search Podcast"]
    tab1, tab2 = st.tabs(tabs)

    with st.sidebar:
        st.header('What is this app')
        st.write('This is a podcast transcribing app, which gives you a short summary on what the podcast is about. Adding further Guest details and highlights of the podcasts are listed')
        st.markdown(
                f"<p style='margin-bottom: 5px;'>Currently there are 2 features :</p><ul><li>Viewing the existing newsletter</li><li>Searching for an podcast using RSS url</li></ul><p>The podcast transcribed then gets added to the existing list</p>", unsafe_allow_html=True)        

    with tab1:
        newsletter_tab()    
    with tab2:
        search_podcast_tab()
    


def create_dict_from_json_files(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    f = modal.Function.lookup("corise-podcast-project", "get_stored_podcast")
    output = f.call()

    data_dict = {}

    for file_name in json_files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as file:
            podcast_info = json.load(file)
            podcast_name = podcast_info['podcast_details']['podcast_title']
            # Process the file data as needed
            data_dict[podcast_name] = podcast_info
    
    for file in output:
        podcast_name = file['podcast_details']['podcast_title']
        data_dict[podcast_name] = file

    return data_dict

def process_podcast_info(url):
    f = modal.Function.lookup("corise-podcast-project", "process_podcast")
    output = f.call(url, '/cache/content/')
    return output

if __name__ == '__main__':
    main()

