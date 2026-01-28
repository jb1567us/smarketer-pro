import streamlit as st
import asyncio
import time
from agents import InfluencerAgent

def render_influencer_scout():
    """Renders the Influencer Scout UI component."""
    st.header("🔥 Influencer & Creator Scout")
    st.caption("Find high-impact voices in your niche to promote your product.")
    
    with st.expander("🔍 Discovery Parameters", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            inf_niche = st.text_input("Niche / Topic", placeholder="e.g. Sustainable Fashion, AI Tools")
        with col2:
            inf_platform = st.selectbox("Platform", ["instagram", "tiktok", "twitter", "youtube"])
        with col3:
            inf_limit = st.slider("Results to Scout", 5, 50, 10)
        
        # Follower Filters
        col4, col5 = st.columns(2)
        with col4:
            inf_min_f = st.text_input("Min Followers (e.g. 10k)", placeholder="0")
        with col5:
            inf_max_f = st.text_input("Max Followers", placeholder="No limit")
        
        if st.button("🚀 Scout Influencers", type="primary"):
            agent = InfluencerAgent()
            
            # Parse follower counts
            try:
                min_followers = agent._parse_follower_count(inf_min_f)
                max_followers = agent._parse_follower_count(inf_max_f)
            except:
                 min_followers = 0
                 max_followers = 0

            with st.spinner(f"Scouting {inf_platform} for {inf_niche} creators..."):
                try:
                    results = asyncio.run(agent.scout_influencers(
                        inf_niche, 
                        inf_platform, 
                        inf_limit, 
                        min_followers=min_followers, 
                        max_followers=max_followers
                    ))
                    
                    if not results:
                        st.error("No influencers found. Try a broader niche or different platform.")
                    else:
                        st.session_state['influencer_results'] = results
                        st.success(f"Found {len(results)} potential partners!")
                        time.sleep(1) # Give time to read message
                        st.rerun()
                except ConnectionError as e:
                    st.error(f"🔌 Search Engine Unavailable: {e}")
                    st.info("💡 Solution: Please open Docker Desktop and wait for the 'searxng' container to start.")
                except Exception as e:
                    st.error(f"Error scouting: {e}")

    if 'influencer_results' in st.session_state:
        results = st.session_state['influencer_results']
        
        # Card Grid Layout
        cols = st.columns(3)
        for idx, item in enumerate(results):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.subheader(item.get('handle', 'Unknown'))
                    st.caption(f"{item.get('platform')} • {item.get('estimated_followers', '?')} followers")
                    st.markdown(f"**Bio Snippet:**_{item.get('bio_snippet', 'No bio found')}_")
                    st.markdown(f"[View Profile]({item.get('url')})")
                    
                    if st.button("Analyze & DM", key=f"inf_dm_{idx}"):
                        # Placeholder for future outreach
                        st.toast("added to outreach queue (Demo)")
