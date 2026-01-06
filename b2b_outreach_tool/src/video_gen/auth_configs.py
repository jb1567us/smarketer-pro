
# Configuration for automated account creation on video platforms

VIDEO_AUTH_CONFIGS = {
    "kling": {
        "registration_url": "https://klingai.com/login", # Usually redirects to login/signup
        "notes": "Often requires phone verification or Google Auth. Account Creator might struggle with CAPTCHA.",
        "selectors": {
            # Hints for the AI if we known them, otherwise it uses vision
            "email_input": "input[type='email']",
            "password_input": "input[type='password']"
        }
    },
    "luma": {
        "registration_url": "https://lumalabs.ai/dream-machine", 
        "notes": "Uses Google Auth primarily.",
        "selectors": {}
    },
    "runway": {
        "registration_url": "https://app.runwayml.com/signup",
        "notes": "Standard signup form available.",
        "selectors": {}
    }
}
