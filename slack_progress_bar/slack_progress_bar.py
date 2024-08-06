from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackProgressBar:
    def __init__(self, token: str, user_id: str, total: int, value: int = 0, bar_width: int = 20, notify: bool = True) -> None:
        """A progress bar to use with Slack."""
        self._client = WebClient(token=token)
        self._total = total
        self._value = value
        self._bar_width = bar_width
        self._ts = None
        self.notify = notify

        # Get channel id of user conversation (for posting and updating)
        try:
            res = self._client.conversations_open(users=user_id)
            self._channel_id = res["channel"]["id"]
        except SlackApiError:
            raise ValueError("Enter valid user_id (Slack Profile -> Copy member ID) or check token!")

        if self.notify:
            self.chat_update()

    def update(self, value: int) -> None:
        """Update the current progress bar on Slack."""
        if value > self._total:
            raise ValueError(f"Update value {value} too large for progress bar of size {self._total}")

        self._value = value

    def error(self) -> None:
        """Set the bar to an error state to indicate loading has stopped."""
        self.chat_update(message=":warning: ERROR: Loading stopped!")

    def chat_update(self, message: str = "") -> None:
        """Send the progress bar with a message to Slack if notify is True."""
        if self.notify:
            text = self._as_string() + f" {message}" if message else self._as_string()
            if not self._ts:
                res = self._client.chat_postMessage(channel=self._channel_id, text=text)
                self._ts = res["ts"]
            else:
                self._client.chat_update(channel=self._channel_id, ts=self._ts, text=text)

    def _as_string(self) -> str:
        """Get the progress bar visualized as a string."""
        amount_complete = round(self._bar_width * self._value / self._total)
        amount_incomplete = self._bar_width - amount_complete
        bar = amount_complete * chr(9608) + amount_incomplete * chr(9601)
        return f"{bar} {self._value}/{self._total} ({int(self._value / self._total * 100)}%)"
