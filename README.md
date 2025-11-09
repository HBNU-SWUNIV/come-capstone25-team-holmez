# 한밭대학교 컴퓨터공학과 team holmez팀

**팀 구성**
- 20197119 박준형
- 20211921 이성원
- 20222015 홍금비
- 20222016 황민호

## <u>Teamate</u> Project Background
- ### 필요성
  - 딥페이크 기반 사칭/협박/허위정보가 일상 서비스로 번져 검증 수요가 급증
  - 누구나 생성 도구를 쓸 수 있어 진위 판별의 일상화가 필요
  - 고사양 모델/복잡한 설치 없이 빠르게 판별 가능한 경량 서비스 요구
- ### 기존 해결책의 문제점
  - 고비용/고사양 : 대형 모델에 의존하여 실시간 및 대량 처리에 부적합함
  - 일반화 취약: 특정 데이터셋 과적합 → 생성기 바뀌면 성능 하락
  - 엔드투엔드 통합 부족: 웹·API·로그·권한이 분절
    
  
## System Design
-<img width="825" height="346" alt="캡스톤 구성도" src="https://github.com/user-attachments/assets/30ecbe15-70e5-4c94-b6fa-cf2f8e7c7206" />
  - ### System Requirements
    - Runtime: Python 3.10+ / Flask
    - DL Framework: PyTorch 2.x
    - Model: EfficientNet-B3 기반 이진분류(Real vs Fake)
    - Face Detector: Haar Cascade(기본) 또는 RetinaFace(옵션)
    - DB: MySQL / SQLite(개발용)
    - OS: Ubuntu 20.04+, Windows 10+
    - 리소스: CPU 4코어 이상, RAM 8GB 권장

  - ### System 
    - 1. 클라이언트 => 웹 업로드/REST 요청
   
    - 2. Backend(flask)
    - 입력 검증 및 확장자와 크기 체크
    - 얼굴 탐지 -> 크롭 및 정규화 진행
    - 딥러닝 추론(EfficientNet-B3)
    - 결과 반환 및 로그 적재
   
    - 3. DB/Storage
    - 요청 결과 로그
    - 업로드 한 이미지
   
  - ### 서버 설정 및 실행 방법
    
    1. 가상환경 생성 및 의존성 설치
    python3 -m venv venv source venv/bin/activate pip install -r requirements.txt
    
    2. 개발용 서버 실행 (수정 자동 반영) nohup gunicorn --reload -w 2 -b 0.0.0.0:5000 run:app > log.txt 2>&1 &
    
    3. 운영용 서비스 등록 (systemd + Gunicorn) 📄 deploy/gunicorn.service
    
    [Unit] Description=Gunicorn instance to serve Flask app After=network.target
    
    [Service] User=ubuntu Group=www-data WorkingDirectory=/home/ubuntu/deepfake-detector ExecStart=/home/ubuntu/deepfake-         detector/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 run:app
    
    [Install] WantedBy=multi-user.target
    
    ⏩ 등록 및 실행 sudo cp deploy/gunicorn.service /etc/systemd/system/ sudo systemctl daemon-reload sudo systemctl start        gunicorn sudo systemctl enable gunicorn
    
    4. Nginx 설정 (80포트 → 5000 포트 프록시) 📄 deploy/nginx.conf
    server { listen 80; server_name YOUR.DOMAIN.or.IP;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        include proxy_params;
        proxy_redirect off;
    }
    }
    
    ⏩ 활성화 sudo cp deploy/nginx.conf /etc/nginx/sites-available/deepfake sudo ln -s /etc/nginx/sites-available/deepfake /etc/nginx/sites-enabled sudo nginx -t sudo systemctl reload nginx
    
    📁 기타 참고 .gitignore에 instance/database.db, .env, pycache/ 등이 포함되어야 함.
    
    모델 파일 .pth는 로컬 업로드 필요 (현재 경로: test/models/)
        
    
## Case Study
  - ### Description

    본 프로젝트는 AI를 활용해 딥페이크(Deepfake) 이미지를 자동 탐지하는 경량 웹/API 서비스를 개발했습니다. 복잡한 설치나 고사양 GPU     없이도 일상 워크플로우에 적용 가능하도록 설계했으며, 업로드 즉시 얼굴별 진위 확률과 최종 판정(REAL/FAKE/REVIEW) 을 반환합니다. 반    복 의심 사례는 로그/리뷰 큐로 관리해 운영 효율을 높였습니다.


  - ### 기술적 특징

    경량 2-Tier: Web(UI) ↔ Flask API(PyTorch 추론)로 역할 명확화
    모델 파이프라인: EfficientNet-B3 기반 이진분류 + Haar(기본) / RetinaFace(옵션)
    설명가능성(옵션): Grad-CAM 유사 히트맵으로 의심 영역 가시화
    Threshold 운영: 목적별 오탐/미탐 균형(기본 0.5, 권장 0.6~0.8 튜닝)
    로그/관제: 업로드 이력·결과 메타 저장, 관리자 조회 엔드포인트
    컨테이너화: Docker(선택), Nginx 리버스 프록시로 배포 일관성 확보

   - ### 탐지 프로세스
    파일 검증: 확장자/MIME/용량 검사
    얼굴 탐지: Haar → (x,y,w,h) 크롭 & 정규화
    딥러닝 추론: EfficientNet-B3 → real_prob / fake_prob 산출
    후처리/판정: 임계값(예: THRESH=0.7) 적용, 다중 얼굴 집계(max_fake_prob)
    응답/로깅: JSON 결과 반환 + 결과/메타 DB 적재(처리시간, 얼굴 수 등)
      
## Conclusion
  프로젝트 성과 
    - 가벼운 추론 지연으로 일상 워크플로우에 실사용 가능 
    
    - API/웹/로그까지 갖춘 엔드투 엔드 프로토타입 완성
  향후 과제
    - 비디오 확장
    - 판단 근거 설명기능 추가 
    - 개인 정보보호 기능능
  
## Project Outcome
- ### 2025 년 학술대회

