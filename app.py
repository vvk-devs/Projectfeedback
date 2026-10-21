import html
import os

import requests
import streamlit as st


API_URL = os.getenv("PROJECTFEEDBACK_API_URL", "http://127.0.0.1:8000/analyze")
SAMPLES = {
	"Late delivery": "The food was delicious but the delivery took over an hour. Not happy.",
	"Great experience": "Amazing taste and the order arrived hot and early. Will order again!",
}

st.set_page_config(
	page_title="Fieldnotes | Review desk",
	page_icon="✳",
	layout="wide",
	initial_sidebar_state="collapsed",
)

st.markdown(
	"""
	<style>
	  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
	  :root { --ink: #202a27; --muted: #7b8580; --green: #147d68; --line: #e5eae6; }
	  .stApp { background: #f2f5f2; color: var(--ink); font-family: 'DM Sans', sans-serif; }
	  [data-testid="stHeader"] { background: rgba(242,245,242,.86); }
	  [data-testid="stMainBlockContainer"] { max-width: 1060px; padding-top: 1.5rem; }
	  .brand { display: flex; align-items: center; gap: 10px; color: var(--ink); font: 800 17px 'Manrope', sans-serif; }
	  .brand-mark { display: inline-flex; align-items: end; gap: 3px; width: 23px; height: 23px; padding: 4px; border-radius: 7px; background: var(--green); }
	  .brand-mark i { display: block; width: 3px; border-radius: 3px; background: white; }
	  .brand-mark i:nth-child(1) { height: 7px; opacity: .72; }
	  .brand-mark i:nth-child(2) { height: 12px; }
	  .brand-mark i:nth-child(3) { height: 9px; opacity: .85; }
	  .eyebrow { margin: 0 0 8px; color: var(--muted); font-size: 10px; font-weight: 700; }
	  h1 { margin: 0 !important; color: var(--ink); font: 700 31px 'Manrope', sans-serif !important; letter-spacing: 0 !important; }
	  .subhead { margin: 4px 0 0; color: var(--muted); font-size: 14px; }
	  [data-testid="stVerticalBlockBorderWrapper"] { border-color: #e8ece9 !important; border-radius: 7px !important; background: white; box-shadow: 0 3px 12px rgba(31,47,39,.025); }
	  .section-kicker { margin: 0; color: #929c96; font-size: 10px; font-weight: 700; }
	  .stMarkdown h3 { margin: 5px 0 18px; color: var(--ink); font: 700 17px 'Manrope', sans-serif; }
	  .result-label { margin: 0; color: #929c96; font-size: 9px; font-weight: 700; }
	  .result-value { margin: 3px 0 0; color: var(--ink); font: 700 20px 'Manrope', sans-serif; text-transform: capitalize; }
	  .theme-value { display: inline-block; margin-top: 5px; padding: 7px 10px; border-radius: 4px; background: #eef5f1; color: #106452; font-weight: 700; text-transform: capitalize; }
	  .stTextArea textarea { min-height: 145px; border-color: #e3e9e5; border-radius: 4px; background: #fbfcfb; color: var(--ink); font-size: 14px; line-height: 1.6; }
	  .stTextArea textarea:focus { border-color: #78b6a5; box-shadow: 0 0 0 2px rgba(20,125,104,.1); }
	  .stButton > button, .stFormSubmitButton > button { min-height: 40px; border: 1px solid #e1e8e3; border-radius: 4px; background: white; color: #526159; font-weight: 600; }
	  .stButton > button:hover { border-color: #94c4b2; color: #106452; }
	  .stFormSubmitButton > button { border: 0; background: var(--green); color: white; }
	  .stFormSubmitButton > button:hover { background: #106452; color: white; }
	  [data-testid="stMetric"] { padding: 12px 14px; border: 1px solid #e9eeea; border-radius: 5px; background: #fbfcfb; }
	  [data-testid="stMetricLabel"] { color: #929c96; font-size: 10px; }
	  [data-testid="stMetricValue"] { color: var(--ink); font-family: 'Manrope', sans-serif; }
	  hr { border-color: var(--line); }
	  .footer { display: flex; justify-content: space-between; margin-top: 25px; color: #9ba49f; font-size: 9px; font-weight: 600; }
	  @media (max-width: 700px) { [data-testid="stMainBlockContainer"] { padding: 1rem 1rem 2rem; } h1 { font-size: 27px !important; } }
	</style>
	""",
	unsafe_allow_html=True,
)

if "review_text" not in st.session_state:
	st.session_state.review_text = ""
if "analysis" not in st.session_state:
	st.session_state.analysis = None
if "history" not in st.session_state:
	st.session_state.history = []

st.markdown(
	'<div class="brand"><span class="brand-mark"><i></i><i></i><i></i></span>fieldnotes</div>',
	unsafe_allow_html=True,
)
st.write("")
st.markdown('<p class="eyebrow">CUSTOMER VOICE &nbsp;·&nbsp; WORKSPACE</p>', unsafe_allow_html=True)
st.title("Review desk")
st.markdown('<p class="subhead">Turn a customer review into a clear signal.</p>', unsafe_allow_html=True)
st.write("")

input_column, result_column = st.columns([1.15, 0.85], gap="medium")

with input_column:
	with st.container(border=True):
		st.markdown('<p class="section-kicker">01 / INPUT</p><h3>Paste a review</h3>', unsafe_allow_html=True)
		sample_columns = st.columns(2)
		for column, (label, sample) in zip(sample_columns, SAMPLES.items()):
			with column:
				if st.button(label, use_container_width=True):
					st.session_state.review_text = sample
					st.rerun()

		with st.form("review_form"):
			review_text = st.text_area(
				"Customer review",
				key="review_text",
				max_chars=2000,
				placeholder="What did your customer say? Paste their review here...",
				label_visibility="collapsed",
			)
			st.caption(f"{len(review_text)} / 2,000 characters · One review at a time")
			submitted = st.form_submit_button("Analyze review", use_container_width=True)

		if submitted:
			if not review_text.strip():
				st.warning("Add a review before analyzing.")
			else:
				try:
					with st.spinner("Reading the review..."):
						response = requests.post(
							API_URL,
							json={"text": review_text.strip()},
							timeout=45,
						)
					if response.ok:
						analysis = response.json()
						if (
							analysis.get("label") not in {"positive", "negative", "neutral"}
							or not 1 <= int(analysis.get("score", 0)) <= 5
							or not analysis.get("theme")
						):
							st.error("The analysis service returned an unexpected result.")
						else:
							item = {
								"text": review_text.strip(),
								"label": analysis["label"],
								"score": int(analysis["score"]),
								"theme": analysis["theme"],
							}
							st.session_state.analysis = item
							st.session_state.history = [
								item,
								*[
									saved
									for saved in st.session_state.history
									if saved["text"] != item["text"]
								],
							][:8]
					else:
						st.error(f"Analysis failed ({response.status_code}). Check that the FastAPI service is running.")
				except requests.exceptions.ConnectionError:
					st.error("Can't reach the analysis service. Start FastAPI, then try again.")
				except requests.exceptions.Timeout:
					st.error("The analysis took too long. Please try again.")
				except requests.exceptions.RequestException as error:
					st.error(f"Could not analyze this review: {error}")
				except (ValueError, TypeError):
					st.error("The analysis service returned an invalid response.")

with result_column:
	with st.container(border=True):
		st.markdown('<p class="section-kicker">02 / INSIGHT</p><h3>Analysis</h3>', unsafe_allow_html=True)
		analysis = st.session_state.analysis
		if analysis:
			sentiment = html.escape(analysis["label"])
			theme = html.escape(analysis["theme"])
			st.markdown(
				f'<p class="result-label">SENTIMENT</p><p class="result-value">{sentiment}</p>',
				unsafe_allow_html=True,
			)
			st.write("")
			st.metric("Customer score", f'{analysis["score"]} / 5')
			st.progress(analysis["score"] / 5)
			st.markdown('<p class="result-label">MAIN THEME</p>', unsafe_allow_html=True)
			st.markdown(f'<span class="theme-value">#{theme}</span>', unsafe_allow_html=True)
		else:
			st.info("Your insight will appear here after you analyze a review.")
			st.caption("Sentiment, customer score, and the main theme in one glance.")

st.write("")
st.markdown('<p class="section-kicker">YOUR WORKSPACE</p>', unsafe_allow_html=True)
st.subheader("Recent reviews")
if st.session_state.history:
	for item in st.session_state.history:
		with st.container(border=True):
			review_column, sentiment_column, score_column = st.columns([6, 2, 1])
			with review_column:
				st.write(item["text"])
				st.caption(f'Theme: {item["theme"]}')
			with sentiment_column:
				st.write(item["label"].capitalize())
			with score_column:
				st.write(f'{item["score"]}/5')
else:
	st.caption("Your analyzed reviews will collect here during this session.")

st.markdown(
	'<div class="footer"><span>FIELDNOTES / REVIEW INTELLIGENCE</span><span>Private to this session</span></div>',
	unsafe_allow_html=True,
)
