import os


class Settings:
    """Configuration from the environment: no secrets in the code."""

    def __init__(self) -> None:
        self.payment_api_key = os.environ.get("PAYMENT_API_KEY", "")
        self.payment_timeout_seconds = float(os.environ.get("PAYMENT_TIMEOUT_SECONDS", "5"))


settings = Settings()
