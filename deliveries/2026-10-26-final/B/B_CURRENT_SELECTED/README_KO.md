# B 현재 선택 에셋 분할 패키지

이 폴더의 PARTS.json, REASSEMBLE.py와 모든 B_CURRENT_ASSETS.zip.001 이후 조각을 같은 폴더에 받으세요. Python 3에서 `python REASSEMBLE.py --verify-only`로 조각 및 합친 ZIP 해시를 검사하고, `python REASSEMBLE.py`로 재결합합니다. 기존 ZIP은 덮어쓰지 않습니다. 새 폴더에 압축을 풀고 `python tools/check_files.py`로 파일별 해시를 검사할 수 있습니다.

조각 하나는 최대20MiB입니다. 재결합 ZIP과 압축 해제본을 동시에 둘 공간을 고려해 최소5GB 여유를 권장합니다. 생성 실패 시 부분 파일도 자동 삭제하지 않으므로 재시도 전에 상태를 확인하세요.

기존 선택973개 ID, 새 디자인12개, 별도 해초 연구4개를 구분합니다. 메타데이터만인134개, 선택 미승격 수리/복구 후보, 실패·과거 버전·원본 아카이브, 외부 참고사진/PDF, 대화/내부 보고/인증정보는 포함하지 않았습니다. 전체 프로젝트 완료나 Unity·실사용 인증은 아닙니다.

ALLOWLIST.json은 패키지 내부의 정확한 공개 파일명·바이트·SHA256 목록입니다. 원본의 절대 작업 경로는 들어 있지 않습니다. VERIFICATION.json은 모든 ZIP 멤버 CRC/SHA256과 조각/전체 ZIP SHA256 검사 결과입니다. 이 폴더는 업로드 준비 산출물이며 현재 GitHub 업로드를 의미하지 않습니다.
