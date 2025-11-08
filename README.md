# 한밭대학교 컴퓨터공학과 team holmez팀

**팀 구성**
- 20197119 박준형
- 20211921 이성원
- 20222015 홍금비
- 20222016 황민호

## <u>Teamate</u> Project Background
- ### 필요성
  - 최근 딥페이크 기반 범죄( 사칭, 협박, 금융사기)가 저비용, 대규모로 확산됨 -> 신뢰가 붕괴되고 
  - 생성형 AI를 활용하여 누구나 딥페이크 이미지와 영상을 만들수 있기 때문에 진위 판별의 일상화가 필요하다
  - 조직 및 개인 사용자를 위해 가볍고 빠른 실사용형 탐지 서비스가 요구된다
- ### 기존 해결책의 문제점
  - 고비용/고사양 : 대형 모델에 의존하여 실시간 및 대량 처리에 부적합함
  - 
  
## System Design
  - ### System Requirements
    - Runtime: Python 3.10+ / Flask
    - DL Framework: PyTorch 2.x
    - Model: EfficientNet-B3 기반 이진분류(Real vs Fake)
    - Face Detector: Haar Cascade(기본) 또는 RetinaFace(옵션)
    - DB: MySQL / SQLite(개발용)
    - OS: Ubuntu 20.04+, Windows 10+
    - 리소스: CPU 4코어 이상, RAM 8GB 권장

  - ### System 
    - 클라이언트 => 웹 업로드/REST 요청
   
    - Backend(flask)
    - 입력 검증 및 확장자와 크기 체크
    - 얼굴 탐지 -> 크롭 및 정규화 진행
    - 딥러닝 추론(EfficientNet-B3)
    - 결과 반환 및 로그 적재
   
    - DB/Storage
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
  
  
## Conclusion
  프로젝트 성과 
    - 가벼운 추론 지연으로 일상 워크플로우에 실사용 가능 
    
    - API/웹/로그까지 갖춘 엔드투 엔드 프로토타입 완성
  
## Project Outcome
- ### 2025 년 학술대회

