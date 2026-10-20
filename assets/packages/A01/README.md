# A01 구조물 126종 다운로드

이 폴더의 15개 파일 .001부터 .015까지는 하나의 ZIP을 바이트 단위로 나눈 파일입니다. 각각을 압축 해제하지 마세요.

1. 모든 분할 파일과 PARTS.json, rejoin.py 또는 rejoin.ps1을 같은 폴더에 다운로드합니다. GitHub 파일 화면에서는 Raw/Download를 사용하세요.
2. Python 3.11 이상: python rejoin.py
3. Windows PowerShell: .\rejoin.ps1 (시스템 보안 정책을 우회하지 마세요. 실행이 제한되면 Python을 사용하세요.)
4. 출력된 Submerged_City_A01_126_GitHub.zip의 검증 성공을 확인한 후 압축을 해제합니다. 이미 존재하는 출력 ZIP은 덮어쓰지 않습니다.

원본 Blender 마스터, 기본 FBX 126개, LOD1 42개, 충돌 FBX 126개, 원본 생성 소스, PBR 텍스처, 미리보기와 설치 안내가 포함됩니다. LOD와 충돌은 추가 고유 모델로 세지 않습니다.

파일 무결성은 PARTS.json의 크기와 SHA256으로 확인합니다. 압축 안의 SHIPPING_MANIFEST.json은 실제 포함 파일 해시를 제공합니다. 이 복원 작업은 새로운 모델 검수나 Unity 실행 검증을 의미하지 않습니다.

Unity Editor 실행·빌드·성능 검증은 수행되지 않았습니다. 정적 non-convex 충돌, 타일 UV0와 미제공 UV1 등 제한 사항은 LIMITATIONS_KO.md 및 압축 안의 README_KO.md와 unity/UNITY_IMPORT_KO.md를 먼저 확인하세요.

공개 저장소에 업로드된 사실만으로 별도의 재배포 라이선스를 부여하지 않습니다. 참고사진 출처는 메타데이터이며 사진 원본은 포함하지 않습니다.
