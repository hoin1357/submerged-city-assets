# GitHub 분할 백업 복원

이 폴더의 ZIP.001, ZIP.002 등은 GitHub 전송용 바이트 분할 파일입니다. 개별 분할 파일을 압축 해제하지 마세요.

1. 모든 분할 파일과 BACKUP_PARTS.json, RESTORE_ARCHIVES.py 또는 RESTORE_ARCHIVES.ps1을 같은 폴더에 내려받습니다. 함께 제공된 원래 설치·복원 안내 파일도 받으세요.
2. Python 3.11 이상에서 python RESTORE_ARCHIVES.py를 실행하거나 Windows PowerShell에서 .\RESTORE_ARCHIVES.ps1을 실행합니다. 보안 정책을 우회하지 마세요. 제한되면 Python을 사용하세요.
3. 각 분할과 복원된 모든 ZIP의 크기·SHA256 검증이 성공했는지 확인합니다. 기존 일치 파일은 재사용하고, 불일치 파일은 덮어쓰지 않습니다.
4. 이제 원래 전달본의 설치 안내를 따릅니다. EXTRACT_RELEASE 도구가 있으면 이를 사용해 ZIP 내부의 추가 청크를 복원하세요. 여러 ZIP은 한 세트이며 하나만 받으면 불완전합니다.

이 백업은 실제 모델의 Unity 런타임·빌드·성능 검증을 새로 수행했다는 뜻이 아닙니다. 원래 README 및 검수 범위·한계 문서를 확인하세요. LOD·충돌·미리보기는 별도 고유 에셋으로 세지 않습니다. 공개 업로드만으로 추가 재배포 라이선스를 부여하지 않습니다.
