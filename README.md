# slack-progress-bar [[Downloads]](https://pypi.org/project/slack-progress-bar-kjh/)
진행상황을 시각화하여 슬랙으로 보여주는 파이썬 라이브러리 (파이썬 3.9이상)

![animated-gif](https://raw.githubusercontent.com/JaeHeong/slack-progress-bar_kjh/main/assets/slack-progress-bar.gif)

## 설치 방법
```bash
pip install slack-progress-bar-kjh
```

## 개요
- 슬랙으로 작업 진행 상황을 시각화하여 보여줄 수 있음
- 슬랙 커스텀 이모지를 활용하여 다양하게 표현 가능 (무엇이든 가능, 눈사람 굴리는 모습, 모래성 쌓는 모습 등...)
- 어떤 작업이 진행 중인지 함께 보여줄 수 있음


## 사용 방법
1. [Slack Apps API](https://api.slack.com/apps)에 접속하여 'Create New App'을 클릭한 후, 지시에 따라 새 앱을 처음부터 만드세요.
2. 'Features -> OAuth & Permissions'로 이동하여 다음 스코프를 'Bot Token Scopes'에 추가하세요: `chat:write`, `channels:manage`, `groups:write`, `im:write`, `mpim:write`.
3. 'Settings -> Install App'로 이동하여 'Install to Workspace'를 클릭하세요. 그런 다음 'Allow'를 클릭하세요.
4. 같은 페이지에서 생성된 'Bot User OAuth Token'을 복사하여 `SlackProgressBarKjh` 클래스의 `token` 필드에 사용하세요.
5. Slack 워크스페이스로 이동하여 회원 ID를 찾으세요(프로필을 클릭한 다음 '[...] -> Copy Member ID'를 클릭하여 찾을 수 있습니다). 이를 `SlackProgressBarKjh` 클래스의 `user_id` 필드에 사용하세요. (필요에 따라 채널ID도 사용 가능)
6. 위에서 찾은 `token`과 `user_id` 또는 채널 ID를 사용하여 진행 표시줄을 생성하고 업데이트하세요.
7. 커스텀 이모지를 추가하세요. [[기본 이모지 gif 다운로드]](https://github.com/JaeHeong/slack-progress-bar_kjh/tree/main/emoji)
    - ※ 필요 커스텀 이모지 (이름은 같아야 함)
        1. :walking_amongus: # 걷고 있는 이모지
        2. :left_spot: # 지나간 곳
        3. :right_spot: # 아직 안 간 곳
        4. :dead_amongus: # 완료 시 이모지
        5. :monster_amongus: # 목표 지점
```python
import os
from slack_progress_bar_kjh import SlackProgressBarKjh

BOT_TOKEN = os.getenv('BOT_TOKEN')
os.getenv('SLACK_MEMBER_ID')

# 작업 시작
progress_bar = SlackProgressBarKjh(token=self.BOT_TOKEN, user_id=self.SLACK_MEMBER_ID, total=100)

for i in range(100):
    try:
        # 작업 중...
        time.sleep(0.1)
        
        # 진행 상황 업데이트
        progress_bar.update(i+1)

        # 현재 상황 알려주기
        progress_bar.chat_update(f"{i}번 작업 완료")

        # 현재 진행률 가져오기
        progress_bar.get_progress()

    except Exception:
        progress_bar.error()
```


# 1.Docker를 활용하여 젠킨스 빌드 상황 실시간 추적
### 젠킨스 워커 노드에 Docker로 빌드 상황을 추적하는 서비스를 만듦 (실제 작업 Dockerfile과 구분하기 위해 Jenkins 폴더에 생성, 젠킨스에서 Jenkinsfile path를 변경해주어야 함)
- Jenkins/Dockerfile 생성
```Dockerfile
# Dockerfile
# Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy necessary files
COPY Jenkins/progress_tracker.py /app/

# Install dependencies
RUN pip install slack-progress-bar-kjh flask

# Expose port if needed
EXPOSE 5000

# Command to run the script
CMD ["python", "progress_tracker.py"]
```
- Jenkins/progress_tracker.py 생성
```python
# progress_tracker.py
import os
from flask import Flask, request
from slack_progress_bar_kjh import SlackProgressBarKjh

app = Flask(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
SLACK_MEMBER_ID = os.getenv('SLACK_MEMBER_ID')
progress_bar = SlackProgressBarKjh(token=BOT_TOKEN, user_id=SLACK_MEMBER_ID, total=100)
progress_state = {'progress': 0}

@app.route('/update-all', methods=['POST'])
def update_all():
    data = request.json
    progress = data.get('progress')
    message = data.get('message')
    update_progress(progress, message)
    return "Progress all updated", 200
    
@app.route('/update-progress', methods=['POST'])
def update_progress_route():
    data = request.json
    progress = data.get('progress')
    update_progress(progress=progress)
    return "Only progress updated", 200
    
@app.route('/update-message', methods=['POST'])
def update_message():
    data = request.json
    message = data.get('message')
    update_progress(message=message)
    return "Only message updated", 200
    
@app.route('/add-progress', methods=['POST'])
def add_progress():
    data = request.json
    progress = data.get('progress')
    add_progress_to_state(progress)
    return "Add progress updated", 200
    
@app.route('/get-progress', methods=['GET'])
def get_progress():
    return progress_state['progress']

def update_progress(progress=None, message=None):
    if progress is not None:
        progress_state['progress'] = progress
        progress_bar.update(progress)
    if message is not None:
        progress_bar.chat_update(message)
        
def add_progress_to_state(progress=0):
    progress_bar.add_progress(progress)
    progress_state['progress'] = progress_bar.get_progress()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
```
- Jenkins/Jenkinsfile 생성
```groovy
// Jenkinsfile
pipeline {
    agent any
    environment {
        BOT_TOKEN = credentials('SLACK_BOT_TOKEN') // Slack Bot Token
        SLACK_MEMBER_ID = credentials('SLACK_MEMBER_ID') // Slack ID
        TRACKER_IMAGE = 'progress-tracker:latest' // 빌드할 Docker 젠킨스 트래커 이미지 이름
    }
    stages {
        stage('Jenkins Tracker - Build Docker Image') {
            steps {
                script {
                    // 젠킨스 진행 상황 추적 컨테이너 이미지 빌드
                    sh '''
                        sudo yum install -y python3 python3-pip
                        docker build -t ${TRACKER_IMAGE} -f Jenkins/Dockerfile .
                    '''
                }
            }
        }
        stage('Jenkins Tracker - Start Tracker') {
            steps {
                script {
                    // 젠킨스 진행 상황 추적 컨테이너 시작
                    sh '''
                        sudo docker run -d --name progress_tracker \
                        -e BOT_TOKEN=${BOT_TOKEN} \
                        -e SLACK_MEMBER_ID=${SLACK_MEMBER_ID} \
                        -p 5000:5000 ${TRACKER_IMAGE}
                        sleep 5
                    '''
                }
            }
        }
        stage('Build') {
            steps {
                script {
                    // 초기화 단계 진행률 업데이트
                    sh '''
                        curl -X POST -H "Content-Type: application/json" \
                        -d '{"progress": 10, "message": "슬랙과"}' \
                        http://localhost:5000/update
                    '''
                    // 진행률 업데이트
                    sh '''
                        curl -X POST -H "Content-Type: application/json" \
                        -d '{"progress": 20, "message": "젠킨스"}' \
                        http://localhost:5000/update
                    '''
                    // 진행률 업데이트
                    sh '''
                        curl -X POST -H "Content-Type: application/json" \
                        -d '{"progress": 30, "message": "연동을"}' \
                        http://localhost:5000/update
                    '''
                    // 진행률 업데이트
                    sh '''
                        curl -X POST -H "Content-Type: application/json" \
                        -d '{"progress": 40, "message": "테스트하고"}' \
                        http://localhost:5000/update
                    '''
                    // 진행률 업데이트
                    sh '''
                        curl -X POST -H "Content-Type: application/json" \
                        -d '{"progress": 50, "message": "있는"}' \
                        http://localhost:5000/update
                    '''
                    // 진행률 업데이트
                    sh '''
                        curl -X POST -H "Content-Type: application/json" \
                        -d '{"progress": 60, "message": "중 입니다."}' \
                        http://localhost:5000/update
                    '''
                    // 진행률 업데이트
                    sh '''
                        curl -X POST -H "Content-Type: application/json" \
                        -d '{"progress": 70, "message": "잘"}' \
                        http://localhost:5000/update
                    '''
                    // 진행률 업데이트
                    sh '''
                        curl -X POST -H "Content-Type: application/json" \
                        -d '{"progress": 80, "message": "되는 것"}' \
                        http://localhost:5000/update
                    '''
                    // 진행률 업데이트
                    sh '''
                        curl -X POST -H "Content-Type: application/json" \
                        -d '{"progress": 90, "message": "같아요."}' \
                        http://localhost:5000/update
                    '''
                }
            }
        }
        stage('Complete and Cleanup') {
            steps {
                script {
                    // Build 성공 후 최종 진행률 업데이트
                    sh '''
                        curl -X POST -H "Content-Type: application/json" \
                        -d '{"progress": 100, "message": "테스트 끝!!!"}' \
                        http://localhost:5000/update
                    '''
                }
            }
            post {
                always {
                    // Docker 컨테이너 종료 및 정리
                    sh '''
                        docker stop progress_tracker
                        docker rm progress_tracker
                    '''
                }
            }
        }
    }
}
```
# 2.docker build 실시간 진행 상황 추적하기
### 젠킨스 워커 노드에 Docker로 빌드 상황을 추적하는 서비스를 만듦 (실제 작업 Dockerfile과 구분하기 위해 Jenkins 폴더에 생성, 젠킨스에서 Jenkinsfile path를 변경해주어야 함)
### sh "(docker build --progress=plain -t test:latest . 2>&1) | tee Jenkins/build.log"로 bulid.log에 로그를 기록하고 실시간으로 감시해서 위의 컨테이너에게 알려주는 서비스 추가
```Dockerfile
# docker-compose.yml

```
```Dockerfile
# Dockerfile.tracker

```
```Dockerfile
# Dockerfile.monitor

```
```python

```