from enum import Enum


class Intent(str, Enum):
    GREETING = "greeting"
    SMALL_TALK = "small_talk"
    GENERAL_QUESTION = "general_question"

    JOB_SEARCH = "job_search"
    RESUME_ANALYSIS = "resume_analysis"

    TOOL_CALL = "tool_call"

    UNKNOWN = "unknown"


class IntentRouter:

    def __init__(self):

        # -------------------------
        # FAST MATCH KEYWORDS
        # -------------------------
        self.greetings = {"hi", "hello", "hey", "yo", "salam"}

        self.small_talk = {"thanks", "thank you", "ok", "okay", "bye"}

        self.interview_keywords = {
            "interview",
            "hr questions",
            "technical questions"
        }

        self.career_keywords = {
            "career advice",
            "guidance",
            "career path"
        }

        self.job_keywords = {
            "job",
            "internship",
            "opening",
            "vacancy"
        }

        self.resume_keywords = {
            "resume",
            "cv"
        }

        self.application_keywords = {
            "application status",
            "applied jobs",
            "my applications"
        }

    # -------------------------
    # CLASSIFIER
    # -------------------------
    def classify(self, message: str):

        msg = message.lower().strip()

        # 1. GREETING
        if msg in self.greetings:
            return Intent.GREETING, 0.99

        # 2. SMALL TALK
        if msg in self.small_talk:
            return Intent.SMALL_TALK, 0.95

        # 3. RESUME ANALYSIS (strong intent)
        if any(word in msg for word in self.resume_keywords) and any(
            word in msg for word in ["analyze", "review", "check", "improve", "feedback"]
        ):
            return Intent.RESUME_ANALYSIS, 0.90

        # 4. JOB SEARCH (general)
        if any(word in msg for word in self.job_keywords):
            return Intent.JOB_SEARCH, 0.82

        # 5. TOOL CALL (strict action-based intent)
        if any(word in msg for word in ["apply", "update", "delete", "create"]):
            return Intent.TOOL_CALL, 0.85

        # 6. INTERVIEW / CAREER (general Qs)
        if any(word in msg for word in self.interview_keywords) or "interview" in msg:
            return Intent.GENERAL_QUESTION, 0.85

        if any(word in msg for word in self.career_keywords):
            return Intent.GENERAL_QUESTION, 0.80

        # 7. DEFAULT (treat as general question)
        return Intent.GENERAL_QUESTION, 0.70

    # -------------------------
    # LOGGING WRAPPER
    # -------------------------
    def classify_with_log(self, message: str):

        intent, confidence = self.classify(message)

        print(
            f"[INTENT ROUTER] message={message} "
            f"intent={intent.value} confidence={confidence}"
        )

        return intent, confidence