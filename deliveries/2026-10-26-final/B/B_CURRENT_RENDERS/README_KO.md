# 현재 선택본 추가 렌더

현재 선택 revision에 대응하는 실제 렌더598장과 RENDERS_CATALOG.json, RENDER_FILES.json입니다. 과거 production-history가 아니며 새 종류 수는0입니다. 핵심 모델 패키지와 분리해 같은 배치에 포함할 수 있습니다. 핵심 FILES.json을 덮어쓰지 않습니다.

모든 조각과 PARTS.json을 이 폴더에 두고 `python REASSEMBLE.py --verify-only`로 검사 후 `python REASSEMBLE.py`로 재결합하세요. 기존 ZIP은 덮어쓰지 않습니다. 추가 렌더 ZIP을 핵심 패키지와 같은 압축 해제 폴더에 풀면 renders_additional/과 별도 렌더 카탈로그가 생깁니다. 제조사 사진·참고 PDF·원시 검사 JSON은 포함하지 않습니다.
