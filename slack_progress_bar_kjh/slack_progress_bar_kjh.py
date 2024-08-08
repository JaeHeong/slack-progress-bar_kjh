from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

class SlackProgressBarKjh:

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
            self.chat_update("*로딩 중...*")

    def update(self, value: int) -> None:
        """Update the current progress bar on Slack."""
        if value > self._total:
            value = self._total
        else:
            self._value = value
        self.chat_update()  # 진행 상황 갱신 후 Slack에 업데이트

    def add_progress(self, value: int) -> None:
        """Add to the current progress bar on Slack."""
        if self._value + value > self._total:
            self._value = self._total
        else:
            self._value += value
        self.chat_update()  # 진행 상황 갱신 후 Slack에 업데이트

    def get_progress(self) -> int:
        """Get the current progress."""
        return self._value

    def chat_update(self, message: str = "") -> None:
        """Send the progress bar with a message to Slack if notify is True."""
        if self.notify:
            text = self._as_string() + f" {message}" if message else self._as_string()
            if not self._ts:
                res = self._client.chat_postMessage(channel=self._channel_id, text=text)
                self._ts = res["ts"]
            else:
                self._client.chat_update(channel=self._channel_id, ts=self._ts, text=text)

    def error(self) -> None:
        """Set the bar to an error state to indicate loading has stopped."""
        self.chat_update(message=":warning: ERROR: Loading stopped!")

    def _as_string(self) -> str:
        """Get the progress bar visualized as a string with a walker, target, and progress."""
        amount_complete = round(self._bar_width * self._value / self._total)
        amount_incomplete = self._bar_width - amount_complete

        # 커스텀 이모지 설정
        walker = ':walking_amongus:'  # 걷고 있는 이모지
        left = ':left_spot:'  # 지나간 곳
        right = ':right_spot:'  # 아직 안 간 곳
        success = ':dead_amongus:'  # 완료 시 이모지
        target = ':monster_amongus:'  # 목표 지점

        # 현재 진행 상태 결정
        if self._value == self._total:
            # 100%에 도달했을 때 완료 이모지 표시
            bar = (left * (amount_complete - 1)) + success
        else:
            # 진행 바 생성
            bar = (left * (amount_complete - 1)) + walker + (right * amount_incomplete) + target

        return f"{bar} {self._value}/{self._total} ({int(self._value / self._total * 100)}%)"

