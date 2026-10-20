주거 건물 54종 ZIP 안전 결합 / Windows 안내

정확한 ZIP 부품 수: 7개
각 ZIP 크기 제한: 20,000,000바이트 이하
모든 ZIP과 EXTRACT_RELEASE.py, EXTRACT_RELEASE.ps1, EXTRACT_RELEASE_WINDOWS.cmd, chunk_inventory.json, SHA256SUMS.txt, EXTRACT_ALL_README.txt, WINDOWS_README_KO.txt를 같은 폴더에 두세요.

1. Windows 기본 PowerShell 5.1 및 .NET Framework 4.7.2 이상을 사용합니다. Python 설치가 필요 없으며 도구는 아무것도 다운로드하거나 설치하지 않습니다.
2. 본인이 관리하는 폴더를 사용하고, 실행 중 다른 프로그램이 부품/대상 폴더를 바꾸지 않게 하세요. EXTRACT_RELEASE_WINDOWS.cmd를 두 번 클릭하세요. 모든 부품과 내부 파일의 SHA256/크기를 먼저 확인합니다.
3. 검증 후 임시 폴더에 풀고, 모든 파일이 일치하면 A02_residential_54_v2 폴더를 한 번에 생성합니다.
4. 기존 결과가 완전히 동일하면 변경 없이 확인합니다. 다른 파일이나 불완전한 결과가 있으면 덮어쓰지 않고 중단합니다. 다른 빈 상위 폴더를 사용하세요.

ZIP 다운로드 이름에 정확히 ' (1)', ' (2)'처럼 숫자 접미사가 붙어도, 내용의 SHA256과 크기가 일치할 때만 인식합니다. 도우미 .py/.ps1/.cmd 및 JSON/TXT 파일은 아래/위에 적힌 정확한 이름으로 바꿔 주세요. 예: EXTRACT_RELEASE (1).py → EXTRACT_RELEASE.py, chunk_inventory (1).json → chunk_inventory.json.

검증만 실행: powershell -NoProfile -File .\EXTRACT_RELEASE.ps1 -VerifyOnly
다른 기존 상위 폴더로 추출: powershell -NoProfile -File .\EXTRACT_RELEASE.ps1 -Destination "D:\Assets"
Python 대안(이미 설치된 Python 3.9+ 필요): py -3 EXTRACT_RELEASE.py --verify-only 또는 --destination 옵션
PowerShell 스크립트는 정적 검토만 했고 이 제작 환경에서 실행하지 않았습니다. Python 대안은 별도 테스트 자료로 실제 검증했습니다.

실행 정책으로 차단되면 정책을 우회하지 마세요. 수동 대안: Windows PowerShell의 Get-FileHash -Algorithm SHA256 -LiteralPath 파일명으로 각 ZIP과 chunk_inventory.json을 SHA256SUMS.txt에 적힌 값과 비교하세요. ZIP 수/이름은 아래 목록과 모두 일치해야 합니다. 불일치하면 중단하세요. 일치한 모든 ZIP만 Explorer의 모두 압축 풀기로 같은 새 빈 상위 폴더에 순서대로 풀고, 덮어쓰기 요청이 뜨면 중단하세요. 그 다음 내부 FILE_SHA256SUMS.txt의 각 상대 경로도 Get-FileHash로 비교하세요. 자동 도우미의 원자적 검증을 수동 Explorer 작업이 대신 보장하는 것은 아닙니다.

해시 목록: SHA256SUMS.txt / 부품·파일 상세 목록: chunk_inventory.json
해시는 손상/잘못된 파일을 검출합니다. 발신자 확인이 필요하면 별도로 받은 inventory SHA256을 Python의 --expected-inventory-sha256 또는 PowerShell의 -ExpectedInventorySha256 옵션으로 지정하세요.

정확한 ZIP 파일 이름:
- A02_residential_54_v2_part01_of07.zip (19,999,911 bytes)
- A02_residential_54_v2_part02_of07.zip (19,999,961 bytes)
- A02_residential_54_v2_part03_of07.zip (19,999,755 bytes)
- A02_residential_54_v2_part04_of07.zip (19,999,761 bytes)
- A02_residential_54_v2_part05_of07.zip (19,999,814 bytes)
- A02_residential_54_v2_part06_of07.zip (19,999,857 bytes)
- A02_residential_54_v2_part07_of07.zip (15,499,769 bytes)
