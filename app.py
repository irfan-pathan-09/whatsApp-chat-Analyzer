import streamlit as st
import helper 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("WhatsApp chat Analyzer")
upload_file = st.sidebar.file_uploader("upload you chat file here:")

data = ''
if upload_file is not None:
    bytes_data = upload_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = helper.preprocessor(data)

    user_list = df['user'].unique().tolist()
    user_list.remove('group notification')
    user_list.sort()
    user_list.insert(0,'All')
    selected_user = st.sidebar.selectbox("Select user to Analyze:",user_list)

    if st.sidebar.button("Show Analysis"):

        # stats
        st.title('Top Statistics:')
        col1 , col2 , col3 , col4 = st.columns(4)
        total_msg , total_word , media_shared , total_links = helper.fetch_stat(selected_user,df)
        with col1:
            st.header("Total Messages")
            st.title(total_msg)
        with col2:
            st.header("Total Words")
            st.title(total_word)
        with col3:
            st.header("Total Media File Shared")
            st.title(media_shared)
        with col4:
            st.header("Total Links Shared")
            st.title(total_links)

        # timeline
        st.title('Monthly tiimeline:')
        timeline = helper.monthly_timeline(selected_user,df)
        fig , ax = plt.subplots()
        ax.plot(timeline['time'],timeline['message'],color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity_map
        st.title("Activity Map:")
        col1 , col2 = st.columns(2)

        busy_day ,  busy_month = helper.activity_map(selected_user,df)

        with col1:
            st.header("Most Busy Day:")
            fig,ax = plt.subplots()
            ax.bar(busy_day.index,busy_day.values,color='red')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        
        with col2:
            st.header("Most Busy month:")
            fig,ax = plt.subplots()
            ax.bar(busy_month.index,busy_month.values,color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        
        # activity heatmap
        activity_heatmap = helper.active_hours(selected_user,df)
        st.title("Activity heatmap:")
        fig, ax = plt.subplots()
        ax = sns.heatmap(data=activity_heatmap)
        st.pyplot(fig)

        # group level stats
        if selected_user == "All":
            col1,col2 = st.columns(2)
            fig , new_df = helper.busy_users(df)

            with col1:
                st.header("Most busy Users:")
                st.pyplot(fig)

            with col2:
                st.header("Message Contribution:")
                st.dataframe(new_df)

        # word cloud
        st.title("Word Cloud:")
        wc = helper.create_wordcloud(selected_user,df)
        fig, ax = plt.subplots() 
        ax.imshow(wc)
        st.pyplot(fig)

        col1 , col2 = st.columns(2)
        with col1:
        # Most frequent words
            word_count = helper.most_freq_words(selected_user,df)
            fig , ax = plt.subplots()
            ax.barh(word_count[0],word_count[1])
            st.title("Most common words:")
            st.pyplot(fig)

        with col2:
        # most frequent emojis
            emoji_count = helper.count_emoji(selected_user,df)
            st.title("Most common emojis:")
            st.dataframe(emoji_count)

            